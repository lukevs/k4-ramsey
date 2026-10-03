"""Shared-endpoint two-edge neighborhoods with exact pair interactions."""
import argparse
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def masks(rows):
    n=len(rows)
    full=(1<<n)-1
    red=[sum(1<<j for j,c in enumerate(row) if c=='1') for row in rows]
    blue=[full ^ row ^ (1<<i) for i,row in enumerate(red)]
    return red,blue


def interaction(rows, red, blue, u, v, w):
    """Mixed finite difference for flipping uv and uw, with v != w."""
    if len({u,v,w}) != 3: raise ValueError('need three distinct vertices')
    neighbors=red if rows[v][w]=='1' else blue
    triples=(neighbors[u]&neighbors[v]&neighbors[w]).bit_count()
    magnitude=24*triples+(36 if rows[v][w]=='0' else 0)
    return magnitude if rows[u][v]==rows[u][w] else -magnitude


def native_interaction(graph, u, v, w):
    baseline=graph.delta(u,w)
    graph.flip(u,v)
    try:
        return graph.delta(u,w)-baseline
    finally:
        graph.flip(u,v)


def screen(rows, red, blue, costs, rng, per_color, random_per_color, deadline):
    best, move, examined, complete=0,None,0,True
    for u in range(len(rows)):
        if time.monotonic()>=deadline:
            complete=False
            break
        selected=[]
        for color in '01':
            options=sorted((costs[u][v],v) for v in range(len(rows)) if u!=v and rows[u][v]==color)
            chosen=options[:per_color]
            remainder=options[per_color:]
            chosen+=rng.sample(remainder,min(len(remainder),random_per_color))
            selected.append(chosen)
        # Opposite-color pairs have negative interactions. Same-color pairs
        # cannot improve a single-flip local minimum, and are not this family.
        for ca,v in selected[0]:
            for cb,w in selected[1]:
                examined+=1
                delta=ca+cb+interaction(rows,red,blue,u,v,w)
                if delta<best:
                    best,move=delta,(u,v,w)
    return dict(delta=best,move=move,pairs=examined,complete=complete)


def main():
    parser=argparse.ArgumentParser()
    for name in ['input','output','config']: parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--seconds',type=float,required=True)
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    if set(config)-{'per_color','random_per_color','max_rounds'}: raise ValueError('unknown config key')
    per_color=config.get('per_color',16)
    random_per_color=config.get('random_per_color',4)
    maximum=config.get('max_rounds',1000)
    if type(per_color)is not int or not 1<=per_color<=128: raise ValueError('per_color must be 1..128')
    if type(random_per_color)is not int or not 0<=random_per_color<=128: raise ValueError('random_per_color must be 0..128')
    if type(maximum)is not int or maximum<1: raise ValueError('max_rounds must be positive')
    start=time.monotonic()
    deadline=start+args.seconds
    rng=random.Random(args.seed)
    graph=Graph(load(args.input))
    initial=value=graph.counts()['numerator']
    write_json(args.output,graph.export())
    edges=[(u,v) for u in range(graph.n) for v in range(u+1,graph.n)]
    history=[]
    dirty=True
    accepted=pairs=rounds=0
    minimum=None
    for _ in range(maximum):
        if time.monotonic()>=deadline or graph.n<3: break
        if dirty:
            rows=graph.export()['red_rows']
            red,blue=masks(rows)
            deltas=graph.deltas(edges)
            minimum=min(deltas,default=0)
            costs=[[0]*graph.n for _ in range(graph.n)]
            for (u,v),delta in zip(edges,deltas): costs[u][v]=costs[v][u]=delta
            dirty=False
        if time.monotonic()>=deadline: break
        result=screen(rows,red,blue,costs,rng,per_color,random_per_color,deadline)
        rounds+=1
        pairs+=result['pairs']
        diagnostic=dict(round=rounds,pairs=result['pairs'],screen_complete=result['complete'],
                        delta=result['delta'],minimum_single_delta=minimum,seconds=time.monotonic()-start)
        if result['move'] is not None:
            u,v,w=result['move']
            predicted=interaction(rows,red,blue,u,v,w)
            if native_interaction(graph,u,v,w)!=predicted: raise RuntimeError('pair interaction mismatch')
            # Sequential current-state deltas independently check the joint gain.
            actual=graph.delta(u,v)
            graph.flip(u,v)
            actual+=graph.delta(u,w)
            graph.flip(u,w)
            if actual!=result['delta']: raise RuntimeError('joint delta mismatch')
            value+=actual
            if graph.counts()['numerator']!=value: raise RuntimeError('full count drift')
            accepted+=1
            dirty=True
            diagnostic.update(move=[u,v,w],interaction=predicted,numerator=value)
            write_json(args.output,graph.export())
        history.append(diagnostic)
        if not result['complete'] or (result['move'] is None and random_per_color==0): break
    if graph.counts()['numerator']!=value: raise RuntimeError('final count drift')
    write_json(args.output,graph.export())
    write_json(args.output.parent/'search.json',dict(numerator=value,initial_numerator=initial,
        rounds=rounds,pairs=pairs,accepted=accepted,last_scanned_minimum_single_delta=minimum,
        seconds=time.monotonic()-start,history=history,rng_state=rng.getstate(),
        termination='time_limit' if time.monotonic()>=deadline else 'screen_or_round_limit',
        note='Only screened opposite-color shared-endpoint pairs; no unrestricted pair or global optimality claim.'))


if __name__=='__main__': main()
