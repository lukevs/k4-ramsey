"""Standalone exact weighted-XOR lift optimization, with a final full recount."""
import argparse
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph,certificate,load
from k4_ramsey.lab import write_json


def main():
    p=argparse.ArgumentParser()
    for name in ('input','output','config'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--seconds',type=float,required=True);p.add_argument('--seed',type=int,required=True)
    args=p.parse_args()
    model=json.loads(args.config.read_text())
    rows=load(args.input)['red_rows']
    start=time.monotonic();rng=random.Random(args.seed)
    terms=model['terms'];m=len(model['shifts'])
    incidence=[[] for _ in range(m)]
    for k,t in enumerate(terms):
        for e in t['edges']:incidence[e].append(k)
    constant=model['baseline_numerator']-sum(t['delta']*t['baseline_parity'] for t in terms)
    best=model['baseline_numerator'];best_bits=[s&1 for s in model['shifts']]
    history=[]
    for restart in range(16):
        if time.monotonic()>start+args.seconds-1:break
        bits=best_bits[:] if restart==0 else [rng.randrange(2) for _ in range(m)]
        parities=[sum(bits[e] for e in t['edges'])%2 for t in terms]
        value=constant+sum(t['delta']*p for t,p in zip(terms,parities))
        moves=0
        while time.monotonic()<start+args.seconds-1:
            gains=[sum(terms[k]['delta']*(1-2*parities[k]) for k in incidence[e]) for e in range(m)]
            minimum=min(gains)
            if minimum>=0:break
            chosen=rng.choice([e for e,gain in enumerate(gains) if gain==minimum])
            bits[chosen]^=1;value+=minimum;moves+=1
            for k in incidence[chosen]:parities[k]^=1
        if value<best:best=value;best_bits=bits[:]
        history.append(dict(restart=restart,numerator=value,moves=moves))
    result=[list(row) for row in rows]
    for e,(i,j,_) in enumerate(model['blocks']):
        shift=(model['shifts'][e]&2)|best_bits[e]
        for a,u in enumerate(model['fibers'][i]):
            for b,v in enumerate(model['fibers'][j]):
                result[u][v]=result[v][u]=str(int(a^shift!=b))
    data=certificate([''.join(row) for row in result])
    graph=Graph(data);actual=graph.counts()['numerator'];graph.close()
    if actual!=best:raise RuntimeError(f'cycle-model disagreement: {best} vs {actual}')
    write_json(args.output,data)
    write_json(args.output.parent/'search.json',dict(numerator=best,initial_numerator=model['baseline_numerator'],
        history=history,seconds=time.monotonic()-start,best_bits=best_bits,
        note='Exact four-cycle parity model under checked gauge hypotheses; strict variable descent with16 restarts, not global optimality.'))


if __name__=='__main__':main()
