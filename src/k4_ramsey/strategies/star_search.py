"""Shared-endpoint two-edge neighborhoods with exact pair interactions."""

import random
import time

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import StarConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated StarConfig configuration."""
    config = StarConfig.model_validate(read_json(args.config))
    per_color = config.per_color
    random_per_color = config.random_per_color
    maximum = config.max_rounds
    start = time.monotonic()
    deadline = start + args.seconds
    rng = random.Random(args.seed)
    graph = Graph(read_certificate(args.input))
    initial = value = graph.count_subgraphs()["numerator"]
    write_json(args.output, graph.export_certificate())
    edges = [(u, v) for u in range(graph.n) for v in range(u + 1, graph.n)]
    history = []
    dirty = True
    accepted = pairs = rounds = 0
    minimum = None
    for _ in range(maximum):
        if time.monotonic() >= deadline or graph.n < 3:
            break
        if dirty:
            rows = graph.export_certificate()["red_rows"]
            red, blue = build_color_masks(rows)
            deltas = graph.calculate_deltas(edges)
            minimum = min(deltas, default=0)
            costs = [[0] * graph.n for _ in range(graph.n)]
            for (u, v), delta in zip(edges, deltas):
                costs[u][v] = costs[v][u] = delta
            dirty = False
        if time.monotonic() >= deadline:
            break
        result = screen(
            rows, red, blue, costs, rng, per_color, random_per_color, deadline
        )
        rounds += 1
        pairs += result["pairs"]
        diagnostic = dict(
            round=rounds,
            pairs=result["pairs"],
            screen_complete=result["complete"],
            delta=result["delta"],
            minimum_single_delta=minimum,
            seconds=time.monotonic() - start,
        )
        if result["move"] is not None:
            u, v, w = result["move"]
            predicted = calculate_interaction(rows, red, blue, u, v, w)
            if calculate_native_interaction(graph, u, v, w) != predicted:
                raise RuntimeError("pair interaction mismatch")
            # Sequential current-state deltas independently check the joint gain.
            actual = graph.calculate_delta(u, v)
            graph.flip(u, v)
            actual += graph.calculate_delta(u, w)
            graph.flip(u, w)
            if actual != result["delta"]:
                raise RuntimeError("joint delta mismatch")
            value += actual
            if graph.count_subgraphs()["numerator"] != value:
                raise RuntimeError("full count drift")
            accepted += 1
            dirty = True
            diagnostic.update(move=[u, v, w], interaction=predicted, numerator=value)
            write_json(args.output, graph.export_certificate())
        history.append(diagnostic)
        if not result["complete"] or (result["move"] is None and random_per_color == 0):
            break
    if graph.count_subgraphs()["numerator"] != value:
        raise RuntimeError("final count drift")
    write_json(args.output, graph.export_certificate())
    write_json(
        args.output.parent / "search.json",
        dict(
            numerator=value,
            initial_numerator=initial,
            rounds=rounds,
            pairs=pairs,
            accepted=accepted,
            last_scanned_minimum_single_delta=minimum,
            seconds=time.monotonic() - start,
            history=history,
            rng_state=rng.getstate(),
            termination="time_limit"
            if time.monotonic() >= deadline
            else "screen_or_round_limit",
            note="Only screened opposite-color shared-endpoint pairs; no unrestricted pair or global optimality claim.",
        ),
    )


def build_color_masks(rows):
    n = len(rows)
    full = (1 << n) - 1
    red = [sum(1 << j for j, c in enumerate(row) if c == "1") for row in rows]
    blue = [full ^ row ^ (1 << i) for i, row in enumerate(red)]
    return red, blue


def calculate_native_interaction(graph, u, v, w):
    baseline = graph.calculate_delta(u, w)
    graph.flip(u, v)
    try:
        return graph.calculate_delta(u, w) - baseline
    finally:
        graph.flip(u, v)


def screen(rows, red, blue, costs, rng, per_color, random_per_color, deadline):
    best, move, examined, complete = 0, None, 0, True
    for u in range(len(rows)):
        if time.monotonic() >= deadline:
            complete = False
            break
        selected = []
        for color in "01":
            options = sorted(
                (costs[u][v], v)
                for v in range(len(rows))
                if u != v and rows[u][v] == color
            )
            chosen = options[:per_color]
            remainder = options[per_color:]
            chosen += rng.sample(remainder, min(len(remainder), random_per_color))
            selected.append(chosen)
        # Opposite-color pairs have negative interactions. Same-color pairs
        # cannot improve a single-flip local minimum, and are not this family.
        for ca, v in selected[0]:
            for cb, w in selected[1]:
                examined += 1
                delta = ca + cb + calculate_interaction(rows, red, blue, u, v, w)
                if delta < best:
                    best, move = delta, (u, v, w)
    return dict(delta=best, move=move, pairs=examined, complete=complete)


def calculate_interaction(rows, red, blue, u, v, w):
    """Mixed finite difference for flipping uv and uw, with v != w."""
    if len({u, v, w}) != 3:
        raise ValueError("need three distinct vertices")
    neighbors = red if rows[v][w] == "1" else blue
    triples = (neighbors[u] & neighbors[v] & neighbors[w]).bit_count()
    magnitude = 24 * triples + (36 if rows[v][w] == "0" else 0)
    return magnitude if rows[u][v] == rows[u][w] else -magnitude


# Compatibility aliases for historical research imports.
masks = build_color_masks
interaction = calculate_interaction
native_interaction = calculate_native_interaction


if __name__ == "__main__":
    main()
