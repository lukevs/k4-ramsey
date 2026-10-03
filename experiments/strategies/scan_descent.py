"""Full-edge screening with fresh deltas before every accepted flip."""
import argparse
import json
import time
from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def main():
    p = argparse.ArgumentParser()
    for name in ['input', 'output', 'config']:
        p.add_argument('--'+name, required=True)
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--seconds', type=float, required=True)
    args = p.parse_args()
    from pathlib import Path
    config = json.loads(Path(args.config).read_text())
    if set(config)-{'max_passes'}:
        raise ValueError('unknown configuration')
    max_passes = config.get('max_passes', 1000000)
    if type(max_passes) is not int or max_passes < 1:
        raise ValueError('max_passes must be positive')
    start = time.monotonic()
    graph = Graph(load(Path(args.input)))
    initial = value = graph.counts()['numerator']
    pairs = [(u,v) for u in range(graph.n) for v in range(u+1,graph.n)]
    history = []
    scans = []
    local = False
    write_json(Path(args.output), graph.export())
    for step in range(max_passes):
        if time.monotonic()-start >= args.seconds:
            break
        deltas = graph.deltas(pairs)
        candidates = sorted((d,u,v) for (u,v),d in zip(pairs,deltas) if d < 0)
        scans.append(dict(pass_index=step, minimum=min(deltas,default=0),
                          improving=len(candidates), numerator=value))
        if not candidates:
            local = True
            break
        # A full scan's deltas become stale after the first flip. Recheck each
        # shortlisted edge against the current graph; rescan on the next pass.
        for _,u,v in candidates:
            if time.monotonic()-start >= args.seconds:
                break
            change = graph.delta(u,v)
            if change < 0:
                graph.flip(u,v)
                value += change
                history.append(dict(u=u,v=v,numerator=value,seconds=time.monotonic()-start))
        write_json(Path(args.output), graph.export())
    if graph.counts()['numerator'] != value:
        raise RuntimeError('incremental drift')
    write_json(Path(args.output), graph.export())
    write_json(Path(args.output).parent/'search.json', dict(numerator=value,
        initial_numerator=initial, accepted=len(history), history=history, scans=scans,
        single_edge_local_minimum=local, seconds=time.monotonic()-start,
        termination='full_scan_no_improvement' if local else 'budget',
        note='Local-minimum statement uses native exhaustive delta scan, not a formal Lean theorem.'))


if __name__ == '__main__':
    main()
