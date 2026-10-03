"""Exact selected star subcubes via cubic finite differences and Gray codes."""

import random
import time

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import CubicStarConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated CubicStarConfig configuration."""
    config = CubicStarConfig.model_validate(read_json(args.config))
    size = config.size
    diversity = config.random_per_color
    maximum = config.max_neighborhoods
    start = time.monotonic()
    deadline = start + args.seconds
    rng = random.Random(args.seed)
    graph = Graph(read_certificate(args.input))
    initial = value = graph.count_subgraphs()["numerator"]
    write_json(args.output, graph.export_certificate())
    graph.enable_cache()
    rows = graph.export_certificate()["red_rows"]
    red, blue = build_color_masks(rows)
    centers = list(range(graph.n))
    rng.shuffle(centers)
    history = []
    accepted = exact = assignments = neighborhoods = 0
    for attempt in range(maximum):
        if time.monotonic() >= deadline or graph.n < 4:
            break
        if attempt and attempt % graph.n == 0:
            rng.shuffle(centers)
        center = centers[attempt % graph.n]
        leaves = select_leaves(
            graph, rows, center, min(size, graph.n - 1), diversity, rng
        )
        linear, pair, triples = compile_star(graph, rows, red, blue, center, leaves)
        result = solve(linear, pair, triples, deadline)
        neighborhoods += 1
        exact += result["complete"]
        assignments += result["assignments"]
        record = dict(
            neighborhood=neighborhoods,
            center=center,
            size=len(leaves),
            delta=result["delta"],
            exact=result["complete"],
            assignments=result["assignments"],
            cubic_terms=len(triples),
        )
        if result["delta"] < 0:
            selected = [v for i, v in enumerate(leaves) if result["mask"] >> i & 1]
            actual = 0
            for v in selected:
                actual += graph.calculate_cached_delta(center, v)
                graph.flip(center, v)
            if actual != result["delta"]:
                raise RuntimeError("cubic prediction mismatch")
            value += actual
            if graph.count_subgraphs()["numerator"] != value:
                raise RuntimeError("full count drift")
            accepted += 1
            rows = graph.export_certificate()["red_rows"]
            red, blue = build_color_masks(rows)
            record.update(
                numerator=value, leaves=selected, seconds=time.monotonic() - start
            )
            write_json(args.output, graph.export_certificate())
        if len(history) < 1000 or result["delta"] < 0:
            history.append(record)
        if not result["complete"]:
            break
    if graph.count_subgraphs()["numerator"] != value:
        raise RuntimeError("final count drift")
    write_json(args.output, graph.export_certificate())
    write_json(
        args.output.parent / "search.json",
        dict(
            numerator=value,
            initial_numerator=initial,
            neighborhoods=neighborhoods,
            exact_neighborhoods=exact,
            assignments=assignments,
            accepted=accepted,
            seconds=time.monotonic() - start,
            history=history,
            rng_state=rng.getstate(),
            termination="time_limit"
            if time.monotonic() >= deadline
            else "neighborhood_limit",
            note="Exact optimization only within each selected incident-edge subcube; not all stars or global optimality.",
        ),
    )


def build_color_masks(rows):
    full = (1 << len(rows)) - 1
    red = [sum(1 << j for j, c in enumerate(row) if c == "1") for row in rows]
    return red, [full ^ row ^ (1 << i) for i, row in enumerate(red)]


def compile_star(graph, rows, red, blue, center, leaves):
    if center in leaves or len(set(leaves)) != len(leaves):
        raise ValueError("distinct star vertices required")
    linear = graph.calculate_cached_deltas([(center, v) for v in leaves])
    k = len(leaves)
    pair = [[0] * k for _ in range(k)]
    triples = []
    for i, v in enumerate(leaves):
        for j in range(i):
            w = leaves[j]
            color = rows[v][w]
            neighbors = red if color == "1" else blue
            magnitude = 24 * (
                neighbors[center] & neighbors[v] & neighbors[w]
            ).bit_count() + (36 if color == "0" else 0)
            pair[i][j] = pair[j][i] = (
                magnitude if rows[center][v] == rows[center][w] else -magnitude
            )
            for h in range(j):
                x = leaves[h]
                if rows[v][x] == color and rows[w][x] == color:
                    coefficient = 24
                    for leaf in (v, w, x):
                        coefficient *= -1 if rows[center][leaf] == color else 1
                    triples.append((h, j, i, coefficient))
    return linear, pair, triples


def solve(linear, pair, triples, deadline=float("inf")):
    """Exact full enumeration if complete; best feasible mask otherwise."""
    k = len(linear)
    gradient = list(linear)
    hessian = [row[:] for row in pair]
    third = [[] for _ in range(k)]
    for i, j, h, c in triples:
        third[i].append((j, h, c))
        third[j].append((i, h, c))
        third[h].append((i, j, c))
    value = best = mask = visited = 0
    complete = True
    for step in range(1, 1 << k):
        if step % 256 == 1 and time.monotonic() >= deadline:
            complete = False
            break
        i = (step & -step).bit_length() - 1
        gray = step ^ (step >> 1)
        sign = 1 if gray >> i & 1 else -1
        value += sign * gradient[i]
        for j in range(k):
            if j != i:
                gradient[j] += sign * hessian[i][j]
        for j, h, c in third[i]:
            hessian[j][h] += sign * c
            hessian[h][j] += sign * c
        visited += 1
        if value < best:
            best, mask = value, gray
    return dict(delta=best, mask=mask, assignments=visited + 1, complete=complete)


def select_leaves(graph, rows, center, k, random_per_color, rng):
    selected = []
    for color, count in [("0", k // 2), ("1", k - k // 2)]:
        candidates = [
            v for v in range(graph.n) if v != center and rows[center][v] == color
        ]
        costs = graph.calculate_cached_deltas([(center, v) for v in candidates])
        ranked = [v for _, v in sorted(zip(costs, candidates))]
        low = max(0, count - random_per_color)
        chosen = ranked[:low]
        remainder = ranked[low:]
        chosen += rng.sample(remainder, min(len(remainder), count - len(chosen)))
        selected += chosen
    return selected


# Compatibility aliases for historical research imports.
masks = build_color_masks


if __name__ == "__main__":
    main()
