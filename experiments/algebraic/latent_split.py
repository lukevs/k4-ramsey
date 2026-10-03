"""Exact latent-sign split expansion with independent ordered-tuple recount."""
from fractions import Fraction
from itertools import combinations,product
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


def coefficients(p,d):
    n=len(p)
    support=[{j for j in range(n) if j!=i and 0<p[i][j]<d} for i in range(n)]
    a=0;triangles=0
    for i in range(n):
        for j in support[i]:
            if j<=i:continue
            for k in support[i]&support[j]:
                if k<=j:continue
                triangles+=1
                a+=24*sum(p[i][l]*p[j][l]*p[k][l]-(d-p[i][l])*(d-p[j][l])*(d-p[k][l]) for l in range(n))
    b=0
    for i in range(n):
        for k in range(n):
            common=support[i]&support[k]
            # Repeated base indices j=l and i=k MUST remain in this sum.
            total=sum(p[j][l] for j in common for l in common)
            b+=3*((d-p[i][k])*d*len(common)**2+(2*p[i][k]-d)*total)
    return a,b,support,triangles


def split(p,d,q):
    n=len(p)
    return [[p[i//2][j//2]+(q if (i+j)%2==0 else -q)*int(
        i//2!=j//2 and 0<p[i//2][j//2]<d) for j in range(2*n)] for i in range(2*n)]


def literal(p,d):
    answer=0
    for vs in product(range(len(p)),repeat=4):
        red=blue=1
        for i,j in combinations(range(4),2):
            value=p[vs[i]][vs[j]];red*=value;blue*=d-value
        answer+=red+blue
    return Fraction(answer,len(p)**4*d**6)


def main():
    start=time.monotonic()
    out=ROOT/'reports/pilot-algebraic-latent-split-001'
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,out/'source_snapshot.py')
    tests=[]
    for p,d in [([[0,2],[2,0]],5),([[0,2,3],[2,0,2],[3,2,0]],5),
                ([[0,1,2],[1,0,3],[2,3,0]],4)]:
        a,b,_,_=coefficients(p,d)
        baseline=literal(p,d)
        for q in (-1,1):
            predicted=baseline+Fraction(a*q**3+b*q**4,len(p)**4*d**6)
            actual=literal(split(p,d,q),d)
            assert predicted==actual
            tests.append(dict(n=len(p),q=q,predicted=str(predicted),actual=str(actual)))
    parent=ROOT/'reports/literature-simple-graphon-001'
    candidate=json.loads((parent/'graphon-candidate.json').read_text())
    parent_report=json.loads((parent/'report.json').read_text())
    p=candidate['red_probability_numerators'];d=candidate['edge_probability_denominator'];n=len(p)
    a,b,support,triangles=coefficients(p,d)
    limit=min(min(p[i][j],d-p[i][j]) for i in range(n) for j in support[i])
    optimum=Fraction(-3*a,4*b) if b else Fraction(0)
    # One analytic proposal, rounded to the original rational grid; neighbors
    # are needed because the optimum is not generally an integer.
    floor=optimum.numerator//optimum.denominator
    choices={max(-limit,min(limit,floor)),max(-limit,min(limit,floor+1)),0}
    q=min(choices,key=lambda q:a*q**3+b*q**4)
    predicted=Fraction(parent_report['density'])+Fraction(a*q**3+b*q**4,n**4*d**6)
    matrix=split(p,d,q);m=len(matrix)
    assert all(0<=v<=d for row in matrix for v in row)
    # Bound every sum and scalar product for the existing signed128 kernel;
    # its long-long pair products are separately bounded.
    maximum=2*m**4*d**6
    assert maximum<2**127 and d*d<2**63
    data=dict(schema='rational-step-graphon-v1',block_weights=[1]*m,
              edge_probability_denominator=d,red_probability_numerators=matrix)
    write_json(out/'graphon-candidate.json',data)
    payload=f'{m} {d}\n'+'\n'.join(' '.join(map(str,row)) for row in matrix)+'\n'
    checker=ROOT/'reports/literature-simple-graphon-001/ordered_counter'
    if not checker.exists():checker=ROOT/'reports/literature-precision-graphon-001/ordered_counter'
    shutil.copy2(checker,out/'ordered_counter')
    shutil.copy2(ROOT/'experiments/literature/ordered_graphon_check.cpp',out/'ordered_checker_snapshot.cpp')
    partial=dict(hypothesis='H-ALG-008',parent=str(parent),n=n,split_order=m,denominator=d,
        cubic_integer_coefficient=a,quartic_integer_coefficient=b,triangle_count=triangles,
        epsilon=str(Fraction(q,d)),analytic_grid_coordinate=str(optimum),grid_coordinate=q,
        predicted_density=str(predicted),predicted_decimal=float(predicted),tiny_tests=tests,
        overflow_bound=str(maximum),overflow_limit=str(2**127),
        expansion='F(q/d)=F0+(Aint*q^3+Bint*q^4)/(n^4*d^6)',
        candidate_sha256=hashlib.sha256((out/'graphon-candidate.json').read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        status='awaiting_independent_ordered_recount')
    write_json(out/'expansion.json',partial)
    print(json.dumps(partial),flush=True)
    red,blue,total=map(int,subprocess.check_output([str(out/'ordered_counter')],input=payload,text=True,timeout=100).split())
    actual=Fraction(total,m**4*d**6)
    assert actual==predicted
    partial.update(status='independent_ordered_recount_passed',red=red,blue=blue,numerator=total,
        normalization=m**4*d**6,actual_density=str(actual),seconds=time.monotonic()-start,
        checker_sha256=hashlib.sha256((out/'ordered_counter').read_bytes()).hexdigest(),
        trust='Independent exact C++128 ordered-index recount; no Lean certificate or kernel-only graphon-limit theorem')
    write_json(out/'report.json',partial)
    print(json.dumps({k:partial[k] for k in ['status','epsilon','actual_density','predicted_decimal','seconds']}),flush=True)


if __name__=='__main__':main()
