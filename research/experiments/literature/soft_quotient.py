"""Exact rational graphon screen; independent tiny ordered-tuple audit."""
import hashlib,itertools,json,random,subprocess,time
from fractions import Fraction
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/literature-soft-quotient-001'
BIN=OUT/'counter'

def count(matrix):
    payload=str(len(matrix))+'\n'+'\n'.join(' '.join(map(str,r)) for r in matrix)+'\n'
    return tuple(map(int,subprocess.check_output([str(BIN)],input=payload,text=True).split()))

def literal(a):
    sums=[0,0]
    for vertices in itertools.product(range(len(a)),repeat=4):
        ps=[a[vertices[i]][vertices[j]] for i,j in itertools.combinations(range(4),2)]
        for color in range(2):
            term=1
            for p in ps:term*=p if color==0 else 4-p
            sums[color]+=term
    return (*sums,sum(sums))

def main():
    started=time.monotonic();OUT.mkdir(exist_ok=False,parents=True)
    source=ROOT/'research/experiments/literature/soft_quotient.cpp'
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(BIN)],check=True)
    rng=random.Random(20260927)
    for n in range(1,7):
        for rep in range(10):
            a=[[0]*n for _ in range(n)]
            for i in range(n):
                for j in range(i+1):a[i][j]=a[j][i]=rng.randrange(5)
            assert count(a)==literal(a)
    data=json.loads((ROOT/'data/published_cayley_768.json').read_text())
    fibers=json.loads((ROOT/'reports/pilot-algebraic-lift-001/quotient.json').read_text())['fibers']
    rows=data['red_rows'];a=[]
    for f in fibers:
        row=[]
        for g in fibers:
            total=sum(rows[i][j]=='1' for i in f for j in g)
            assert total%4==0
            row.append(total//4)
        a.append(row)
    sums=count(a);denominator=4**6*len(a)**4
    report=dict(hypothesis='Large independent random fibers improve the finite four-sheet template',
        evidence='C++ exact rational sum, audited on60 tiny random matrices against literal ordered tuples; no Lean certificate',
        red_numerator=sums[0],blue_numerator=sums[1],numerator=sums[2],denominator=denominator,
        density=str(Fraction(sums[2],denominator)),decimal=float(Fraction(sums[2],denominator)),
        equivalent_768_numerator=str(Fraction(sums[2]*768**4,denominator)),
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),seconds=time.monotonic()-started,
        scope='192 equal-mass blocks; independent graphon edge probabilities from block densities; blue within fibers')
    (OUT/'matrix.json').write_text(json.dumps(a))
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
