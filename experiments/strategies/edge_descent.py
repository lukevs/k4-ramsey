"""Baseline strategy and example of the single-experiment script protocol."""
import argparse
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--input', type=Path, required=True)
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--config', type=Path, required=True)
    p.add_argument('--seed', type=int, required=True)
    p.add_argument('--seconds', type=float, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    if set(config)-{'max_moves','checkpoint_moves'}:
        raise ValueError('unknown strategy configuration key')
    max_moves = config.get('max_moves', 100000000)
    checkpoint_moves = config.get('checkpoint_moves', 50000)
    if type(max_moves) is not int or max_moves < 0:
        raise ValueError('max_moves must be a nonnegative integer')
    if type(checkpoint_moves) is not int or checkpoint_moves <= 0:
        raise ValueError('checkpoint_moves must be a positive integer')
    rng = random.Random(args.seed)
    start = time.monotonic()
    graph = Graph(load(args.input))
    initial = graph.counts()['numerator']
    value = initial
    attempted = accepted = 0
    history = []
    write_json(args.output, graph.export())
    while graph.n > 1 and attempted < max_moves and time.monotonic()-start < args.seconds:
        u, v = rng.sample(range(graph.n),2)
        delta = graph.delta(u,v)
        attempted += 1
        if delta < 0:
            graph.flip(u,v)
            value += delta
            accepted += 1
            history.append(dict(move=attempted,numerator=value,seconds=time.monotonic()-start))
        if attempted % checkpoint_moves == 0:
            write_json(args.output, graph.export())
    if graph.counts()['numerator'] != value:
        raise RuntimeError('incremental numerator drift')
    write_json(args.output, graph.export())
    write_json(args.output.parent/'search.json', dict(numerator=value, initial_numerator=initial,
        attempted=attempted, accepted=accepted, seconds=time.monotonic()-start,
        termination='move_limit' if attempted>=max_moves else 'time_limit',
        history=history, rng_state=rng.getstate(),
        note='Sampled strict descent; does not certify a single-edge local optimum.'))


if __name__ == '__main__':
    main()
