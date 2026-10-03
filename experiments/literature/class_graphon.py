"""Motif-refined probability classes, exact rational search and tiny audits."""
import argparse,collections,hashlib,itertools,json,random,subprocess,time
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

class Counter:
    def __init__(self,binary,matrix,k):
        self.p=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        self.p.stdin.write(f'{len(matrix)} {k}\n'+'\n'.join(' '.join(map(str,r))for r in matrix)+'\n');self.p.stdin.flush()
    def __call__(self,den,x):
        self.p.stdin.write(' '.join(map(str,[den,*x]))+'\n');self.p.stdin.flush()
        return int(self.p.stdout.readline())
    def close(self):self.p.stdin.close();self.p.wait(timeout=10)

def tiny_audit(binary):
    rng=random.Random(26927)
    for n in range(1,7):
        for rep in range(5):
            a=[[0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i+1):a[i][j]=a[j][i]=rng.randrange(-2,4)
            den=17;x=[rng.randrange(18)for _ in range(4)]
            counter=Counter(binary,a,4);actual=counter(den,x);counter.close();expected=0
            for vertices in itertools.product(range(n),repeat=4):
                values=[]
                for i,j in itertools.combinations(range(4),2):
                    c=a[vertices[i]][vertices[j]];values.append(0 if c==-1 else den if c==-2 else x[c])
                for color in [0,1]:
                    term=1
                    for value in values:term*=value if not color else den-value
                    expected+=term
            assert actual==expected,(n,rep,actual,expected)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);parser.add_argument('--denominator',type=int,default=4096)
    args=parser.parse_args();out=ROOT/args.out;out.mkdir(exist_ok=False,parents=True);start=time.monotonic()
    source=ROOT/'experiments/literature/class_graphon.cpp';binary=out/'counter'
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True);tiny_audit(binary)
    matrix=json.loads((ROOT/'reports/literature-soft-quotient-001/matrix.json').read_text());n=len(matrix)
    classes=[[-1]*n for _ in range(n)];frequencies=collections.Counter();participation=collections.Counter()
    for i in range(n):
        classes[i][i]=3
        for j in range(i):
            c=matrix[i][j]
            if c==3:
                triangles=sum((matrix[i][k]==3 and matrix[j][k]==2)or(matrix[i][k]==2 and matrix[j][k]==3)for k in range(n))
                participation[triangles]+=1
                assert triangles in [0,2]
                c=0 if triangles==0 else 1
            else:c={0:-1,2:2,4:-2}[c]
            classes[i][j]=classes[j][i]=c;frequencies[c]+=1
    counter=Counter(binary,classes,4);den=args.denominator;trials=[];cache={}
    def evaluate(x):
        key=tuple(x)
        if key not in cache:
            value=counter(den,x);cache[key]=value;trials.append(dict(parameters=list(x),numerator=value))
        return cache[key]
    best=[round(195*den/256),round(195*den/256),round(134*den/256),0]
    original=evaluate([3*den//4,3*den//4,den//2,0])
    assert Fraction(original,den**6*n**4)==Fraction(9103117,301989888)
    steps=[];step=den//4
    while step:steps.append(step);step//=2
    for step in steps:
        for sweep in range(12):
            previous=list(best)
            for coordinate in range(4):
                options=sorted(set([0,den,best[coordinate],max(0,best[coordinate]-step),min(den,best[coordinate]+step)]))
                candidates=[]
                for value in options:
                    x=list(best);x[coordinate]=value;candidates.append((evaluate(x),x))
                best=min(candidates)[1]
            if best==previous:break
    numerator=evaluate(best);counter.close();denominator=den**6*n**4
    report=dict(hypothesis='Split defect probabilities by D-D-H triangle participation',parameters=best,
      parameter_denominator=den,parameter_names=['defect_without_triangles','defect_in_two_triangles','half_blocks','within_fiber'],
      class_counts=dict(frequencies),triangle_participation=dict(participation),numerator=numerator,denominator=denominator,
      density=str(Fraction(numerator,denominator)),decimal=float(Fraction(numerator,denominator)),
      equivalent_768_numerator=str(Fraction(numerator*768**4,denominator)),trials=len(trials),seconds=time.monotonic()-start,
      evidence='Exact128-bit partition count;30 independent tiny literal ordered-tuple audits passed; no Lean certificate',
      source_sha256=hashlib.sha256(source.read_bytes()).hexdigest())
    (out/'source_snapshot.cpp').write_bytes(source.read_bytes());(out/'driver_snapshot.py').write_bytes(Path(__file__).read_bytes())
    (out/'report.json').write_text(json.dumps(report,indent=2)+'\n');(out/'trials.json').write_text(json.dumps(trials,indent=2)+'\n')
    (out/'classes.json').write_text(json.dumps(classes)+'\n');print(json.dumps(report,indent=2))
if __name__=='__main__':main()
