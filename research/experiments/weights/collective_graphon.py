"""Exact graphon mass derivatives; numerical curvature screening, not certification."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import time

from research.experiments.weights.collective_curvature import dot,project,quantize
from k4_ramsey.lab import write_json


def positive_restricted_hessian(h,seconds=45):
    """Exact Sylvester criterion in basis e_i-e_last, with fraction-free LDL."""
    started=time.monotonic()
    n=len(h)-1
    matrix=[[h[i][j]-h[i][-1]-h[-1][j]+h[-1][-1]for j in range(n)]for i in range(n)]
    divisor=0
    for row in matrix:
        for value in row: divisor=math.gcd(divisor,value)
    if not divisor: return dict(status='zero_hessian',dimension=n)
    matrix=[[value//divisor for value in row]for row in matrix]
    pivots=[];previous=1
    for k in range(n):
        if time.monotonic()-started>seconds:
            return dict(status='timeout_incomplete',pivots_checked=k,seconds=time.monotonic()-started)
        pivot=matrix[k][k]
        if pivot<=0:
            return dict(status='not_strictly_positive_by_this_test',pivot_index=k,pivot_hex=hex(pivot))
        pivots.append(hex(pivot))
        for i in range(k+1,n):
            for j in range(i,n):
                numerator=pivot*matrix[i][j]-matrix[i][k]*matrix[k][j]
                value,remainder=divmod(numerator,previous)
                if remainder: raise RuntimeError('fraction-free determinant exact-division failure')
                matrix[i][j]=matrix[j][i]=value
        previous=pivot
    return dict(status='exact_positive_definite_on_zero_sum_subspace',dimension=n,
                positive_scale_divisor=divisor,leading_principal_determinants_hex=pivots,
                seconds=time.monotonic()-started,
                trust='Exact integer Sylvester criterion via fraction-free elimination, not a Lean theorem')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--certify',action='store_true')
    args=parser.parse_args()
    started=time.monotonic()
    args.out.mkdir(parents=True,exist_ok=False)
    data=json.loads(args.input.read_text())
    matrix=data['red_probability_numerators'];n=len(matrix);den=data['edge_probability_denominator']
    if data['block_weights']!=[1]*n: raise ValueError('derivative screen at unit block mass only')
    source=Path(__file__).with_suffix('.cpp')
    shutil.copy2(source,args.out/'derivative_source.cpp')
    shutil.copy2(Path(__file__),args.out/'driver_source.py')
    shutil.copy2(args.input,args.out/'input.json')
    binary=args.out/'derivatives'
    subprocess.run(['c++','-O3','-std=c++17',str(source),'-o',str(binary)],check=True,timeout=30)
    payload=f'{n} {den}\n'+'\n'.join(' '.join(map(str,row))for row in matrix)+'\n'
    numbers=list(map(int,subprocess.check_output([str(binary.resolve())],input=payload,text=True,timeout=30).split()))
    if len(numbers)!=1+n+n*n: raise RuntimeError('bad derivative output')
    numerator=numbers[0];gradient=numbers[1:1+n]
    h=[numbers[1+n+i*n:1+n+(i+1)*n]for i in range(n)]
    if sum(gradient)!=4*numerator or any(sum(h[i])!=3*gradient[i]for i in range(n)):
        raise RuntimeError('homogeneous quartic derivative checks failed')
    write_json(args.out/'hessian.json',h)
    # Double centering removes the fixed-mass null direction. Float eigen-screen
    # proposes directions only; every reported quadratic value below is exact.
    means=[sum(row)/n for row in h];mean=sum(means)/n
    projected=[[h[i][j]-means[i]-means[j]+mean for j in range(n)]for i in range(n)]
    scale=max(sum(abs(v)for v in row)for row in projected)
    rng=random.Random(1729)
    trials=[]
    if scale:
        for seed in range(4):
            v=project([rng.uniform(-1,1)for _ in range(n)])
            for _ in range(120):
                hv=[dot(row,v)/scale for row in projected]
                v=project([a-b for a,b in zip(v,hv)])
                norm=dot(v,v)**.5
                if not norm: break
                v=[x/norm for x in v]
            direction=quantize(v,32)
            curvature=sum(direction[i]*h[i][j]*direction[j]for i in range(n)for j in range(n))
            trials.append(dict(seed=seed,direction=direction,exact_curvature=curvature,
                               exact_derivative=sum(g*d for g,d in zip(gradient,direction))))
    report=dict(schema='graphon-mass-screen-v1',status='completed',hypothesis='H-CW3: graphon has improving collective block-mass directions',
                started_at=datetime.now(timezone.utc).isoformat(),total_seconds=time.monotonic()-started,
                input=str(args.input.resolve()),input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
                source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                density=str(Fraction(numerator,den**6*n**4)),numerator=numerator,
                denominator=den**6*n**4,gradient_min=min(gradient),gradient_max=max(gradient),
                gradient=gradient,curvature_trials=trials,
                evidence='Exact ordered-index mass derivatives plus integer curvature values; no weighted witness yet',
                limitation='Numerical eigenvector search cannot establish PSD or global/local optimality.')
    if args.certify:
        report['exact_curvature_certificate']=positive_restricted_hessian(h)
        report['total_seconds']=time.monotonic()-started
    write_json(args.out/'report.json',report)
    print(json.dumps({k:v for k,v in report.items()if k not in ('gradient','curvature_trials')},indent=2))
    print('Exact curvature trials:',[trial['exact_curvature']for trial in trials])


if __name__=='__main__':main()
