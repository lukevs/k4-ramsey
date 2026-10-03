"""Bounded class-probability search with exact 128-bit candidate evaluations."""
import hashlib,json,subprocess,time
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/'reports/literature-soft-family-001'

def main():
    start=time.monotonic();OUT.mkdir(exist_ok=False,parents=True)
    source=ROOT/'research/experiments/literature/soft_family.cpp';binary=OUT/'counter'
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True)
    matrix=json.loads((ROOT/'reports/literature-soft-quotient-001/matrix.json').read_text())
    process=subprocess.Popen([str(binary)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
    process.stdin.write(str(len(matrix))+'\n'+'\n'.join(' '.join(map(str,r))for r in matrix)+'\n');process.stdin.flush()
    trials=[];cache={};den=256
    def evaluate(x):
        key=tuple(x)
        if key not in cache:
            process.stdin.write(' '.join(map(str,[den,*x]))+'\n');process.stdin.flush()
            value=int(process.stdout.readline());cache[key]=value
            trials.append(dict(parameters=list(key),numerator=value,density=str(Fraction(value,den**6*len(matrix)**4))))
        return cache[key]
    best=[192,128,0];base=evaluate(best)
    assert Fraction(base,den**6*len(matrix)**4)==Fraction(9103117,301989888)
    # Greedy coordinate multiscale screen, including large moves and endpoints.
    for step in [64,32,16,8,4,2,1]:
        for sweep in range(8):
            old=list(best)
            for coordinate in range(3):
                options=sorted(set([0,256,best[coordinate],max(0,best[coordinate]-step),min(256,best[coordinate]+step)]))
                candidates=[]
                for value in options:
                    x=list(best);x[coordinate]=value;candidates.append((evaluate(x),x))
                best=min(candidates)[1]
            if old==best:break
    process.stdin.close();process.wait(timeout=10)
    value=evaluate(best)
    report=dict(hypothesis='Optimize defect, half-block and diagonal graphon probabilities',
      parameters=best,parameter_denominator=den,numerator=value,denominator=den**6*len(matrix)**4,
      density=str(Fraction(value,den**6*len(matrix)**4)),decimal=float(Fraction(value,den**6*len(matrix)**4)),
      equivalent_768_numerator=str(Fraction(value*768**4,den**6*len(matrix)**4)),
      trials=len(trials),seconds=time.monotonic()-start,source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
      evidence='Exact arithmetic search with partition formula; only baseline audited independently on tiny matrices; no Lean certificate')
    (OUT/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    (OUT/'trials.json').write_text(json.dumps(trials,indent=2)+'\n')
    print(json.dumps(report,indent=2))
if __name__=='__main__':main()
