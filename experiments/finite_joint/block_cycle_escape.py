"""Exact eight-edge matching-cycle moves on a locally polished graph."""
import argparse
from itertools import combinations
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def edges(fibers, block, p, q):
    i, j = block[:2]
    return [(fibers[i][a], fibers[j][a ^ shift])
            for a in range(4) for shift in (p, q)]


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
        raise RuntimeError("matching-cycle rollback failed")
    return delta


def main():
    p = argparse.ArgumentParser()
    for name in ("input", "output", "config"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    model = json.loads(Path(config["model_path"]).read_text())
    max_sweeps = config.get("max_sweeps", 3)
    data = load(args.input)
    graph = Graph(data)
    graph.enable_cache()
    initial = value = graph.counts()["numerator"]
    write_json(args.output, graph.export())
    fibers, blocks = model["fibers"], model["blocks"]
    moves = [[edges(fibers, block, p, q) for p, q in combinations(range(4), 2)]
             for block in blocks]
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
                    raise RuntimeError("accepted matching-cycle delta changed")
                value += actual
                accepted += 1
                count += 1
                if accepted % 20 == 0:
                    if graph.counts()["numerator"] != value:
                        raise RuntimeError("checkpoint count drift")
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
        "hypothesis": "H-FJ-002", "numerator": value,
        "initial_numerator": initial, "delta": value - initial,
        "accepted": accepted, "evaluations": evaluations, "history": history,
        "termination": termination, "seconds": time.monotonic() - start,
        "note": "Strict exact eight-edge matching-cycle moves on the fixed discovered quotient blocks."
    })


if __name__ == "__main__":
    main()
