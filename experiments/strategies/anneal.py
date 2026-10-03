"""Seeded Metropolis cycles, retaining the best exact-count checkpoint."""
import argparse
import json
import math
from pathlib import Path
import random
import time
from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def main():
    p = argparse.ArgumentParser()
    for name in ['input','output','config']:
        p.add_argument('--'+name, type=Path, required=True)
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--seconds', type=float, required=True)
    args = p.parse_args()
    c = json.loads(args.config.read_text())
    if set(c)-{'temperature','cycle_moves','max_moves','restart'}:
        raise ValueError('unknown configuration')
    temperature = c.get('temperature', 12)
    cycle_moves = c.get('cycle_moves', 300000)
    max_moves = c.get('max_moves', 1000000000)
    restart = c.get('restart', True)
    if type(temperature) not in (int,float) or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError('temperature must be positive and finite')
    if any(type(x) is not int or x <= 0 for x in [cycle_moves,max_moves]):
        raise ValueError('move limits must be positive integers')
    if type(restart) is not bool:
        raise ValueError('restart must be boolean')
    start = time.monotonic()
    rng = random.Random(args.seed)
    best_data = load(args.input)
    graph = Graph(best_data)
    initial = best = value = graph.counts()['numerator']
    history = []
    attempted = accepted = uphill = cycles = 0
    write_json(args.output,best_data)
    while graph.n > 1 and attempted < max_moves and time.monotonic()-start < args.seconds:
        if attempted and attempted % cycle_moves == 0:
            if graph.counts()['numerator'] != value:
                raise RuntimeError('cycle count drift')
            if restart:
                graph.close()
                graph = Graph(best_data)
                value = best
            cycles += 1
            write_json(args.output,best_data)
        phase = (attempted % cycle_moves) / cycle_moves
        # Last quarter is strict descent, not a claim of local optimality.
        temp = temperature * max(0, 1-phase/.75)
        u,v = rng.sample(range(graph.n),2)
        change = graph.delta(u,v)
        attempted += 1
        if change < 0 or (temp > 0 and rng.random() < math.exp(-max(0,change)/temp)):
            graph.flip(u,v)
            value += change
            accepted += 1
            uphill += change > 0
            if value < best:
                best = value
                best_data = graph.export()
                history.append(dict(move=attempted,numerator=best,seconds=time.monotonic()-start))
    if graph.counts()['numerator'] != value:
        raise RuntimeError('final count drift')
    graph.close()
    with_best = Graph(best_data)
    if with_best.counts()['numerator'] != best:
        raise RuntimeError('best checkpoint drift')
    write_json(args.output,best_data)
    write_json(args.output.parent/'search.json',dict(numerator=best,initial_numerator=initial,
        final_walk_numerator=value,attempted=attempted,accepted=accepted,uphill=uphill,
        cycles=cycles,history=history,seconds=time.monotonic()-start,
        termination='move_limit' if attempted >= max_moves else 'time_limit',
        note='Metropolis exploratory screen, not a local or global optimality certificate.'))


if __name__ == '__main__':
    main()
