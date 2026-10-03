"""Cached exact single-flip descent with optional shared-endpoint escapes."""
import argparse
import json
from pathlib import Path
import time

from k4_ramsey.engine import Graph,load
from k4_ramsey.lab import write_json


def main():
    parser=argparse.ArgumentParser()
    for name in ['input','output','config']: parser.add_argument('--'+name,type=Path,required=True)
    parser.add_argument('--seed',type=int,required=True)
    parser.add_argument('--seconds',type=float,required=True)
    args=parser.parse_args()
    config=json.loads(args.config.read_text())
    if set(config)-{'mode','per_color','max_moves','checkpoint_moves'}: raise ValueError('unknown config')
    mode=config.get('mode','star')
    per_color=config.get('per_color',16)
    maximum=config.get('max_moves',100000)
    checkpoint=config.get('checkpoint_moves',100)
    if mode not in {'single','star'}: raise ValueError('mode must be single or star')
    if type(per_color)is not int or not 1<=per_color<=128: raise ValueError('per_color must be 1..128')
    if type(maximum)is not int or maximum<1: raise ValueError('max_moves must be positive')
    if type(checkpoint)is not int or checkpoint<1: raise ValueError('checkpoint_moves must be positive')
    start=time.monotonic()
    deadline=start+args.seconds
    graph=Graph(load(args.input))
    initial=value=graph.counts()['numerator']
    write_json(args.output,graph.export())
    graph.enable_cache()
    setup=time.monotonic()-start
    history=[]
    singles=stars=steps=0
    local=False
    minimum=None
    for step in range(maximum):
        if time.monotonic()>=deadline: break
        best=graph.best_cached_flip()
        if best is None:
            local=True
            break
        minimum=best[2]
        if best[2]<0:
            u,v,delta=best
            graph.flip(u,v)
            value+=delta
            singles+=1
            move=[u,v]
        else:
            local=True
            if mode=='single': break
            star=graph.best_cached_star(per_color)
            if star is None: break
            u,v,w,delta=star
            actual=graph.cached_delta(u,v)
            graph.flip(u,v)
            actual+=graph.cached_delta(u,w)
            graph.flip(u,w)
            if actual!=delta: raise RuntimeError('cached joint delta mismatch')
            value+=actual
            stars+=1
            move=[u,v,w]
        local=False
        steps+=1
        if steps%10==0 or len(move)==3:
            history.append(dict(step=steps,numerator=value,move=move,seconds=time.monotonic()-start))
        if steps%checkpoint==0:
            if graph.counts()['numerator']!=value: raise RuntimeError('checkpoint count drift')
            write_json(args.output,graph.export())
    if graph.counts()['numerator']!=value: raise RuntimeError('final count drift')
    write_json(args.output,graph.export())
    write_json(args.output.parent/'search.json',dict(numerator=value,initial_numerator=initial,
        singles=singles,stars=stars,steps=steps,single_edge_local_minimum=local,
        last_scanned_minimum_single_delta=minimum,setup_seconds=setup,
        seconds=time.monotonic()-start,history=history,
        termination='time_limit' if time.monotonic()>=deadline else ('restricted_local_minimum' if local else 'move_limit'),
        note='Seed unused: deterministic tie-breaking. Star checks use low-cost shortlists, not global optimality.'))


if __name__=='__main__': main()
