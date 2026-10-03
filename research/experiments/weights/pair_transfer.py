"""Exact rational pair-weight screens; no weighted-certificate promotion."""
import argparse
from datetime import datetime,timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from k4_ramsey.engine import Graph,load
from k4_ramsey.lab import write_json
from k4_ramsey.verify import verify


def induced_edges(neighbors,mask):
    twice=0
    remaining=mask
    while remaining:
        bit=remaining & -remaining
        v=bit.bit_length()-1
        twice+=(neighbors[v]&mask).bit_count()
        remaining-=bit
    return twice//2


def features(graph):
    rows=graph.export()['red_rows']
    n=graph.n
    red=[sum(1<<j for j,c in enumerate(row) if c=='1') for row in rows]
    blue=[((1<<n)-1)^mask^(1<<i) for i,mask in enumerate(red)]
    db=[mask.bit_count() for mask in blue]
    tb=[induced_edges(blue,mask) for mask in blue]
    counts=graph.counts()
    eb=n*(n-1)//2-counts['red_edges']
    triangles=counts['blue_triangles']
    incidence=[]
    # Isolating u in red and then restoring recovers its total K4 incidence.
    # This uses independent uncached deltas, not the new landscape cache.
    for u in range(n):
        changed=[]
        delta=0
        try:
            for v,c in enumerate(rows[u]):
                if c=='1':
                    delta+=graph.delta(u,v)
                    graph.flip(u,v)
                    changed.append(v)
        finally:
            for v in reversed(changed): graph.flip(u,v)
        numerator=14*(n-1-db[u])+36*(eb-db[u]-tb[u])+24*(triangles-tb[u])-delta
        if numerator%24: raise RuntimeError('nonintegral K4 incidence')
        incidence.append(numerator//24)
    if graph.export()['red_rows']!=rows: raise RuntimeError('feature extraction changed input')
    if sum(incidence)!=4*(counts['red_k4']+counts['blue_k4']): raise RuntimeError('K4 incidence checksum')
    return dict(rows=rows,red=red,blue=blue,db=db,tb=tb,k4=incidence,numerator=counts['numerator'])


def coefficients(f,u,v):
    if u==v: raise ValueError('distinct vertices required')
    edge_blue=f['rows'][u][v]=='0'
    color=f['blue'] if edge_blue else f['red']
    common=color[u]&color[v]
    shared_k4=induced_edges(color,common)
    shared_tri=(f['blue'][u]&f['blue'][v]).bit_count() if edge_blue else 0
    degree_difference=f['db'][v]-f['db'][u]
    a=28*degree_difference+48*(f['tb'][v]-f['tb'][u])+24*(f['k4'][v]-f['k4'][u])
    b=(12+18*(f['db'][u]+f['db'][v])-48*edge_blue
       +12*(f['tb'][u]+f['tb'][v]-5*shared_tri)-24*shared_k4)
    return a,b,4*degree_difference,2-2*edge_blue


def grid_minimum(coefficients,denominator):
    a,b,c,d=coefficients
    best=0
    step=0
    # Exclude t=1: every emitted block weight must stay strictly positive.
    for s in range(1,denominator):
        value=s*(a*denominator**3+s*(b*denominator**2+s*(c*denominator+s*d)))
        if value<best: best,step=value,s
    return Fraction(best,denominator**4),Fraction(step,denominator)


def screen(input_path,out,*,pool=24,denominator=1024):
    start=time.monotonic()
    started_at=datetime.now(timezone.utc).isoformat()
    out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(Path(__file__),out/'source_snapshot.py')
    data=load(Path(input_path))
    graph=Graph(data)
    f=features(graph)
    baseline_check=verify(data,f['numerator'])
    gradient=[28*f['db'][i]+48*f['tb'][i]+24*f['k4'][i] for i in range(graph.n)]
    ranking=sorted(range(graph.n),key=lambda i:gradient[i])
    donors=ranking[-pool:]
    recipients=ranking[:pool]
    best=Fraction(0)
    best_move=None
    screened=0
    trials=[]
    for u in donors:
        for v in recipients:
            if u==v: continue
            coef=coefficients(f,u,v)
            gain,t=grid_minimum(coef,denominator)
            screened+=1
            if gain<best:
                best=gain
                best_move=(u,v,t)
                trials.append(dict(donor=u,recipient=v,t=str(t),delta=str(gain),coefficients=coef))
    weights=[denominator]*graph.n
    if best_move:
        u,v,t=best_move
        shift=int(t*denominator)
        weights[u]-=shift
        weights[v]+=shift
    candidate=dict(data,weights=weights)
    write_json(out/'candidate-weighted.json',candidate)
    report=dict(schema='k4-weight-screen-v1',status='completed',started_at=started_at,
        hypothesis='H11: a small rational mass transfer improves an asymmetric unit-weight incumbent',
        evidence='exact_quartic_screen_with_tiny_oracle_tests_not_independent_weighted_check',
        input=str(Path(input_path).resolve()),input_sha256=hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),baseline_check=baseline_check,
        baseline_numerator=f['numerator'],n=graph.n,gradient_min=min(gradient),gradient_max=max(gradient),
        gradient=gradient,pool=pool,grid_denominator=denominator,pairs_screened=screened,
        best_delta=str(best),best_density=str((Fraction(f['numerator'])+best)/graph.n**4),
        best_move=[best_move[0],best_move[1],str(best_move[2])] if best_move else None,
        exact_integer_weighted_numerator=int((Fraction(f['numerator'])+best)*denominator**4),
        exact_integer_weighted_denominator=(graph.n*denominator)**4,
        history=trials,seconds=time.monotonic()-start,
        promotion='STOP: changed weights require separately versioned independent weighted verification before promotion.')
    write_json(out/'report.json',report)
    graph.close()
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--pool',type=int,default=24)
    parser.add_argument('--denominator',type=int,default=1024)
    args=parser.parse_args()
    if args.pool<1 or args.denominator<1: raise ValueError('positive pool/denominator required')
    result=screen(args.input,args.out,pool=args.pool,denominator=args.denominator)
    print(json.dumps({k:result[k] for k in ['best_move','best_delta','best_density','pairs_screened','gradient_min','gradient_max','seconds']},indent=2))


if __name__=='__main__': main()
