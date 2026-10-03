"""Fixed-order integer mass transfers via blue-twin vertex replacement.

Standalone runner strategy. Every trial is exact sequential edge deltas, with
rollback, not a sum of deltas computed on an unchanged graph.
"""

import random
import time

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import CloneConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated CloneConfig configuration."""
    config = CloneConfig.model_validate(read_json(args.config))
    max_moves = config.max_moves
    pool_size = config.pool_size
    selection = config.selection
    rng = random.Random(args.seed)
    start = time.monotonic()
    data = read_certificate(args.input)
    graph = Graph(data)
    rows = [list(row) for row in data["red_rows"]]
    initial = value = graph.count_subgraphs()["numerator"]
    write_json(args.output, data)
    attempted = accepted = zero_moves = total_edges = 0
    best_delta = worst_delta = None
    history, diagnostics = [], []
    while (
        graph.n > 1
        and attempted < max_moves
        and time.monotonic() - start < args.seconds
    ):
        (u, v), surrogate = select_pair(graph, rows, rng, selection, pool_size)
        delta, edges = evaluate_clone(graph, rows, u, v)
        attempted += 1
        zero_moves += not edges
        total_edges += len(edges)
        best_delta = delta if best_delta is None else min(best_delta, delta)
        worst_delta = delta if worst_delta is None else max(worst_delta, delta)
        if len(diagnostics) < 100:
            diagnostics.append(
                dict(u=u, v=v, delta=delta, edges=len(edges), surrogate=surrogate)
            )
        if delta < 0:
            apply_edges(graph, rows, edges)
            value += delta
            accepted += 1
            history.append(
                dict(
                    move=attempted,
                    u=u,
                    v=v,
                    delta=delta,
                    numerator=value,
                    seconds=time.monotonic() - start,
                )
            )
            write_json(args.output, graph.export_certificate())
    if graph.count_subgraphs()["numerator"] != value:
        raise RuntimeError("incremental numerator drift")
    write_json(args.output, graph.export_certificate())
    write_json(
        args.output.parent / "search.json",
        dict(
            numerator=value,
            initial_numerator=initial,
            attempted=attempted,
            accepted=accepted,
            zero_moves=zero_moves,
            total_changed_edges_tested=total_edges,
            best_trial_delta=best_delta,
            worst_trial_delta=worst_delta,
            selection=selection,
            pool_size=pool_size,
            history=history,
            diagnostics=diagnostics,
            seconds=time.monotonic() - start,
            termination="move_limit" if attempted >= max_moves else "time_limit",
            rng_state=rng.getstate(),
            note="Exact clone trials, sampled pairs only. No claim of local or global optimality.",
        ),
    )


def evaluate_clone(graph, rows, u, v):
    """Return exact delta and flip list; leave the graph unchanged, even on error."""
    edges = clone_edges(rows, u, v)
    completed = []
    delta = 0
    try:
        for edge in edges:
            delta += graph.calculate_delta(*edge)
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
        scores = [sum(graph.calculate_deltas(es)) for es in edges]
    else:
        raise ValueError("unknown pair selection")
    best = min(range(len(pairs)), key=lambda i: scores[i])
    return pairs[best], scores[best]


def clone_edges(rows, u, v):
    n = len(rows)
    if not 0 <= u < n or not 0 <= v < n or u == v:
        raise ValueError("expected two different vertex indices")
    # row v is blue at v, so uv becomes blue. The diagonal uu remains blue.
    return [(u, w) for w in range(n) if w != u and rows[u][w] != rows[v][w]]


# Compatibility aliases for historical research imports.
trial_clone = evaluate_clone


if __name__ == "__main__":
    main()
