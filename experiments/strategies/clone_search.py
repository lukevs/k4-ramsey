"""Fixed-order integer mass transfers via blue-twin vertex replacement.

Standalone runner strategy. Every trial is exact sequential edge deltas, with
rollback, not a sum of deltas computed on an unchanged graph.
"""
import argparse
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def clone_edges(rows, u, v):
    n = len(rows)
    if not 0 <= u < n or not 0 <= v < n or u == v:
        raise ValueError("expected two different vertex indices")
    # row v is blue at v, so uv becomes blue. The diagonal uu remains blue.
    return [(u, w) for w in range(n) if w != u and rows[u][w] != rows[v][w]]


def trial_clone(graph, rows, u, v):
    """Return exact delta and flip list; leave the graph unchanged, even on error."""
    edges = clone_edges(rows, u, v)
    completed = []
    delta = 0
    try:
        for edge in edges:
            delta += graph.delta(*edge)
            graph.flip(*edge)
            completed.append(edge)
    finally:
        for edge in reversed(completed):
            graph.flip(*edge)
    return delta, edges


def apply_edges(graph, rows, edges):
    for u, v in edges:
        graph.flip(u, v)
        rows[u][v] = rows[v][u] = "1" if rows[u][v] == "0" else "0"


def select_pair(graph, rows, rng, selection, pool_size):
    pairs = [tuple(rng.sample(range(graph.n), 2)) for _ in range(pool_size)]
    if selection == "random":
        return pairs[0], None
    edges = [clone_edges(rows, *pair) for pair in pairs]
    if selection == "closest":
        scores = [len(es) for es in edges]
    elif selection == "linear":
        # Deliberately a surrogate: star interactions make this non-exact.
        scores = [sum(graph.deltas(es)) for es in edges]
    else:
        raise ValueError("unknown pair selection")
    best = min(range(len(pairs)), key=lambda i: scores[i])
    return pairs[best], scores[best]


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--config", type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    if set(config) - {"max_moves", "selection", "pool_size"}:
        raise ValueError("unknown configuration key")
    max_moves = config.get("max_moves", 100000000)
    pool_size = config.get("pool_size", 8)
    selection = config.get("selection", "random")
    if type(max_moves) is not int or max_moves < 0:
        raise ValueError("max_moves must be a nonnegative integer")
    if type(pool_size) is not int or pool_size < 1:
        raise ValueError("pool_size must be a positive integer")
    if selection not in {"random", "closest", "linear"}:
        raise ValueError("unknown selection")
    rng = random.Random(args.seed)
    start = time.monotonic()
    data = load(args.input)
    graph = Graph(data)
    rows = [list(row) for row in data["red_rows"]]
    initial = value = graph.counts()["numerator"]
    write_json(args.output, data)
    attempted = accepted = zero_moves = total_edges = 0
    best_delta = worst_delta = None
    history, diagnostics = [], []
    while graph.n > 1 and attempted < max_moves and time.monotonic() - start < args.seconds:
        (u, v), surrogate = select_pair(graph, rows, rng, selection, pool_size)
        delta, edges = trial_clone(graph, rows, u, v)
        attempted += 1
        zero_moves += not edges
        total_edges += len(edges)
        best_delta = delta if best_delta is None else min(best_delta, delta)
        worst_delta = delta if worst_delta is None else max(worst_delta, delta)
        if len(diagnostics) < 100:
            diagnostics.append(dict(u=u, v=v, delta=delta, edges=len(edges), surrogate=surrogate))
        if delta < 0:
            apply_edges(graph, rows, edges)
            value += delta
            accepted += 1
            history.append(dict(move=attempted, u=u, v=v, delta=delta, numerator=value,
                                seconds=time.monotonic() - start))
            write_json(args.output, graph.export())
    if graph.counts()["numerator"] != value:
        raise RuntimeError("incremental numerator drift")
    write_json(args.output, graph.export())
    write_json(args.output.parent / "search.json", dict(
        numerator=value, initial_numerator=initial, attempted=attempted, accepted=accepted,
        zero_moves=zero_moves, total_changed_edges_tested=total_edges,
        best_trial_delta=best_delta, worst_trial_delta=worst_delta,
        selection=selection, pool_size=pool_size, history=history, diagnostics=diagnostics,
        seconds=time.monotonic() - start,
        termination="move_limit" if attempted >= max_moves else "time_limit",
        rng_state=rng.getstate(),
        note="Exact clone trials, sampled pairs only. No claim of local or global optimality."))


if __name__ == "__main__":
    main()
