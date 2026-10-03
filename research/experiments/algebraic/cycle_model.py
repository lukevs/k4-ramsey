"""Exact four-cycle parity model for second-bit V4 voltages at fixed first bits."""
import argparse
from collections import Counter
import hashlib
from itertools import combinations,product
import json
from pathlib import Path
import time

from research.experiments.algebraic.lift import discover_fibers,decompose
from k4_ramsey.engine import Graph,load
from k4_ramsey.lab import write_json


def build_model(rows,fibers=None):
    fibers=discover_fibers(rows) if fibers is None else fibers
    blocks,_=decompose(rows,fibers)
    shifts=[]
    adjacency=[set() for _ in fibers]
    lookup={}
    for e,(i,j,p) in enumerate(blocks):
        if tuple(p)!=tuple(a^p[0] for a in range(4)):
            raise ValueError('requires V4 translation voltages')
        shifts.append(p[0])
        adjacency[i].add(j);adjacency[j].add(i)
        lookup[tuple(sorted((i,j)))]=e
    if any(adjacency[i]&adjacency[j] for i,j,_ in blocks):
        raise ValueError('defect graph must be triangle-free')
    # All other blocks must be invariant under an independent second-bit flip
    # in either fiber; this is the gauge-invariance hypothesis of the model.
    for i in range(len(fibers)):
        for j in range(i):
            if (j,i) in lookup: continue
            if any(rows[fibers[i][a]][fibers[j][b]] != rows[fibers[i][a^1]][fibers[j][b]] or
                   rows[fibers[i][a]][fibers[j][b]] != rows[fibers[i][a]][fibers[j][b^1]]
                   for a in range(4) for b in range(4)):
                raise ValueError('fixed block breaks second-bit gauge invariance')
    cycles={}
    for i,j in combinations(range(len(fibers)),2):
        for k,l in combinations(sorted(adjacency[i]&adjacency[j]),2):
            cycles[tuple(sorted((i,j,k,l)))]=(i,k,j,l)
    terms=[]
    for cycle in cycles.values():
        edges=[lookup[tuple(sorted((cycle[a],cycle[(a+1)%4])))] for a in range(4)]
        parity=sum(shifts[e]&1 for e in edges)%2
        changed=edges[0]
        ci,cj,_=blocks[changed]
        local=[]
        for toggle in (0,1):
            count=0
            for sheets in product(range(4),repeat=4):
                colors=[]
                for a,b in combinations(range(4),2):
                    i,j=cycle[a],cycle[b]
                    if {i,j}=={ci,cj}:
                        colors.append(int(sheets[a] != (sheets[b] ^ shifts[changed] ^ toggle)))
                    else:
                        colors.append(int(rows[fibers[i][sheets[a]]][fibers[j][sheets[b]]]))
                count+=len(set(colors))==1
            local.append(count)
        delta=24*(local[1]-local[0])*(1 if parity==0 else -1)
        if delta: terms.append(dict(edges=edges,delta=delta,baseline_parity=parity,fibers=cycle))
    return dict(fibers=fibers,blocks=blocks,shifts=shifts,terms=terms,
                total_cycles=len(cycles),coefficient_histogram=dict(Counter(t['delta'] for t in terms)))


def main():
    p=argparse.ArgumentParser()
    p.add_argument('--input',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    args=p.parse_args()
    args.out.mkdir(parents=True,exist_ok=False)
    start=time.monotonic()
    rows=load(args.input)['red_rows']
    model=build_model(rows)
    g=Graph(load(args.input));model['baseline_numerator']=g.counts()['numerator'];g.close()
    model.update(input=str(args.input.resolve()),input_sha256=hashlib.sha256(args.input.read_bytes()).hexdigest(),
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.monotonic()-start)
    write_json(args.out/'model.json',model)
    print(json.dumps({k:model[k] for k in ['total_cycles','coefficient_histogram','baseline_numerator','seconds']}))


if __name__=='__main__':main()
