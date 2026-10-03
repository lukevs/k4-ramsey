"""Exact regular degree-two 4x4 block moves on an arbitrary finite graph."""
import argparse
from itertools import combinations, product
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


REGULAR_TWO = tuple(tuple(sum(1 << j for j in pair) for pair in rows)
                    for rows in product(tuple(combinations(range(4), 2)), repeat=4)
                    if all(sum(j in pair for pair in rows) == 2 for j in range(4)))


def move_edges(fibers, block, target):
    i, j, base = block
    return [(fibers[i][a], fibers[j][b]) for a in range(4) for b in range(4)
            if ((base[a] >> b) & 1) != ((target[a] >> b) & 1)]


def apply(graph, move):
    delta = 0
    for u, v in move:
        delta += graph.cached_delta(u, v)
        graph.flip(u, v)
    return delta


def trial(graph, move):
    delta = apply(graph, move)
    rollback = apply(graph, list(reversed(move)))
    if rollback != -delta:
        raise RuntimeError("half-block rollback failed")
    return delta


def main():
    p = argparse.ArgumentParser()
    for name in ("input", "output", "config"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    quotient = json.loads(Path(config["quotient_path"]).read_text())
    max_sweeps = config.get("max_sweeps", 2)
    data = load(args.input)
    graph = Graph(data)
    graph.enable_cache()
    initial = value = graph.counts()["numerator"]
    write_json(args.output, graph.export())
    fibers, blocks = quotient["fibers"], quotient["half_blocks"]
    moves = [[move_edges(fibers, block, target) for target in REGULAR_TWO
              if list(target) != block[2]] for block in blocks]
    if any(len(bank) != 89 for bank in moves):
        raise RuntimeError("expected all alternate regular degree-two patterns")
    start = time.monotonic()
    deadline = start + args.seconds
    rng = random.Random(args.seed)
    accepted = evaluations = 0
    history = []
    termination = "sweep_limit"
    for sweep in range(max_sweeps):
        count = 0
        order = list(range(len(blocks)))
        rng.shuffle(order)
        for e in order:
            if time.monotonic() >= deadline:
                termination = "time_limit"
                break
            best_delta, best_move = 0, None
            for move in moves[e]:
                delta = trial(graph, move)
                evaluations += 1
                if delta < best_delta:
                    best_delta, best_move = delta, move
            if best_move is not None:
                actual = apply(graph, best_move)
                if actual != best_delta:
                    raise RuntimeError("accepted half-block delta changed")
                value += actual
                accepted += 1
                count += 1
                if accepted % 10 == 0:
                    if graph.counts()["numerator"] != value:
                        raise RuntimeError("checkpoint recount failed")
                    write_json(args.output, graph.export())
        history.append({"sweep": sweep, "accepted": count, "numerator": value,
                        "evaluations": evaluations, "seconds": time.monotonic() - start})
        if termination == "time_limit":
            break
        if count == 0:
            termination = "restricted_local_minimum"
            break
    if graph.counts()["numerator"] != value:
        raise RuntimeError("final full recount mismatch")
    write_json(args.output, graph.export())
    graph.close()
    write_json(args.output.parent / "search.json", {
        "hypothesis": "H-FJ-003", "numerator": value,
        "initial_numerator": initial, "delta": value - initial,
        "accepted": accepted, "evaluations": evaluations, "history": history,
        "termination": termination, "seconds": time.monotonic() - start,
        "note": "Strict exact regular degree-two block scaffold moves on a polished graph."
    })


if __name__ == "__main__":
    main()
