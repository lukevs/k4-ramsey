"""Guided exact degree-preserving graph 2-switch neighborhood."""
import argparse
from itertools import combinations
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


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
        raise RuntimeError("2-switch rollback failed")
    return delta


def edge_key(u, v):
    # Match all_edges' lower-triangle convention: larger endpoint first.
    return (u, v) if u > v else (v, u)


def main():
    p = argparse.ArgumentParser()
    for name in ("input", "output", "config"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    shortlist = config.get("red_edge_shortlist", 192)
    max_trials = config.get("max_trials_per_sweep", 12000)
    max_sweeps = config.get("max_sweeps", 3)
    data = load(args.input)
    rows = [bytearray(map(int, row)) for row in data["red_rows"]]
    n = len(rows)
    graph = Graph(data)
    graph.enable_cache()
    initial = value = graph.counts()["numerator"]
    write_json(args.output, graph.export())
    all_edges = [(u, v) for u in range(n) for v in range(u)]
    start = time.monotonic()
    deadline = start + args.seconds
    rng = random.Random(args.seed)
    accepted = evaluations = 0
    history = []
    termination = "sweep_limit"
    for sweep in range(max_sweeps):
        single = graph.cached_deltas(all_edges)
        delta_map = dict(zip(all_edges, single))
        red = sorted((delta_map[e], e) for e in all_edges if rows[e[0]][e[1]])[:shortlist]
        proposals = {}
        for (_, (a, b)), (_, (c, d)) in combinations(red, 2):
            if len({a, b, c, d}) != 4:
                continue
            for x, y in (((a, c), (b, d)), ((a, d), (b, c))):
                x, y = edge_key(*x), edge_key(*y)
                if rows[x[0]][x[1]] or rows[y[0]][y[1]]:
                    continue
                removals = (edge_key(a, b), edge_key(c, d))
                additions = (x, y)
                key = tuple(sorted(removals + additions))
                score = sum(delta_map[e] for e in key)
                proposals.setdefault(key, (score, removals, additions))
        bank = list(proposals.values())
        rng.shuffle(bank)
        bank.sort(key=lambda item: item[0])
        count = tried = 0
        for _, removals, additions in bank[:max_trials]:
            if time.monotonic() >= deadline:
                termination = "time_limit"
                break
            if not all(rows[u][v] for u, v in removals) or any(rows[u][v] for u, v in additions):
                continue
            move = list(removals + additions)
            delta = trial(graph, move)
            evaluations += 1
            tried += 1
            if delta < 0:
                actual = apply(graph, move)
                if actual != delta:
                    raise RuntimeError("accepted 2-switch delta changed")
                for u, v in move:
                    rows[u][v] ^= 1
                    rows[v][u] ^= 1
                value += actual
                accepted += 1
                count += 1
                if accepted % 20 == 0:
                    if graph.counts()["numerator"] != value:
                        raise RuntimeError("checkpoint recount failed")
                    write_json(args.output, graph.export())
        history.append({"sweep": sweep, "red_shortlist": len(red),
                        "proposals": len(bank), "tried": tried,
                        "accepted": count, "numerator": value,
                        "seconds": time.monotonic() - start})
        if termination == "time_limit":
            break
        if count == 0:
            termination = "restricted_local_minimum"
            break
    if graph.counts()["numerator"] != value:
        raise RuntimeError("final full recount mismatch")
    if any(sum(row) != sum(map(int, data["red_rows"][i])) for i, row in enumerate(rows)):
        raise RuntimeError("2-switch changed degree sequence")
    write_json(args.output, graph.export())
    graph.close()
    write_json(args.output.parent / "search.json", {
        "hypothesis": "H-FJ-004", "numerator": value,
        "initial_numerator": initial, "delta": value - initial,
        "accepted": accepted, "evaluations": evaluations, "history": history,
        "termination": termination, "seconds": time.monotonic() - start,
        "note": "Exact degree-preserving red-edge 2-switches proposed from a cached single-delta shortlist."
    })


if __name__ == "__main__":
    main()
