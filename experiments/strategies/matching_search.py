"""Exactly optimize selected disjoint edge flips; no global optimality claim."""

import random
import time

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import MatchingConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated MatchingConfig configuration."""
    config = MatchingConfig.model_validate(read_json(args.config))
    size = config.size
    pool_size = config.pool_size
    maximum = config.max_neighborhoods
    mode = config.mode
    rng = random.Random(args.seed)
    start = time.monotonic()
    deadline = start + args.seconds
    graph = Graph(read_certificate(args.input))
    initial = value = graph.count_subgraphs()["numerator"]
    write_json(args.output, graph.export_certificate())
    all_edges = [(i, j) for i in range(graph.n) for j in range(i + 1, graph.n)]
    ranked, rows, dirty = [], [], True
    history, screened, exact, total_nodes, accepted, seen = [], 0, 0, 0, 0, set()
    min_single = None
    pair_examined, pair_exhausted = 0, False
    for step in range(maximum):
        if time.monotonic() >= deadline or not all_edges:
            break
        if dirty:
            rows = graph.export_certificate()["red_rows"]
            if mode != "random":
                deltas = graph.calculate_deltas(all_edges)
                ranked = sorted(zip(deltas, all_edges))
                min_single = min(deltas)
            dirty, seen = False, set()
        if time.monotonic() >= deadline:
            break
        if mode == "pair":
            edges, examined, pair_exhausted = find_improving_pair(
                rows, ranked, deadline
            )
            pair_examined += examined
            if not edges:
                break
        else:
            edges = choose_matching(
                rows, ranked, rng, min(size, graph.n // 2), mode, pool_size
            )
        identity = tuple(sorted(tuple(sorted(e)) for e in edges))
        if identity in seen:
            continue
        seen.add(identity)
        linear, matrix = build_quadratic_model(graph, edges, rows)
        result = solve(linear, matrix, deadline)
        screened += 1
        exact += result["complete"]
        total_nodes += result["nodes"]
        diagnostic = dict(
            neighborhood=screened,
            size=len(edges),
            delta=result["delta"],
            exact=result["complete"],
            nodes=result["nodes"],
            negative_interactions=sum(
                matrix[i][j] < 0 for i in range(len(edges)) for j in range(i)
            ),
            minimum_linear=min(linear, default=0),
        )
        if result["delta"] < 0:
            flips = [edge for i, edge in enumerate(edges) if result["mask"] >> i & 1]
            for edge in flips:
                graph.flip(*edge)
            value += result["delta"]
            if graph.count_subgraphs()["numerator"] != value:
                raise RuntimeError("quadratic numerator drift")
            accepted += 1
            dirty = True
            diagnostic.update(
                numerator=value, flips=flips, seconds=time.monotonic() - start
            )
            write_json(args.output, graph.export_certificate())
        # Bounded diagnostics retain all gains and first 1000 screens.
        if len(history) < 1000 or result["delta"] < 0:
            history.append(diagnostic)
        if not result["complete"]:
            break
    if graph.count_subgraphs()["numerator"] != value:
        raise RuntimeError("final numerator drift")
    write_json(args.output, graph.export_certificate())
    write_json(
        args.output.parent / "search.json",
        dict(
            numerator=value,
            initial_numerator=initial,
            neighborhoods=screened,
            exact_neighborhoods=exact,
            nodes=total_nodes,
            accepted=accepted,
            last_scanned_minimum_single_delta=min_single,
            seconds=time.monotonic() - start,
            pair_examined=pair_examined,
            pair_neighborhood_exhausted=pair_exhausted,
            history=history,
            rng_state=rng.getstate(),
            termination="pair_neighborhood_exhausted"
            if pair_exhausted
            else (
                "time_limit" if time.monotonic() >= deadline else "neighborhood_limit"
            ),
            note="Exactness is only over each selected matching, never a global optimality claim.",
        ),
    )


def build_quadratic_model(graph, edges, rows=None):
    if len({v for edge in edges for v in edge}) != 2 * len(edges):
        raise ValueError("free edges must form a matching")
    rows = graph.export_certificate()["red_rows"] if rows is None else rows
    linear = graph.calculate_deltas(edges)
    matrix = [[0] * len(edges) for _ in edges]
    for i, edge in enumerate(edges):
        for j in range(i):
            matrix[i][j] = matrix[j][i] = calculate_interaction(rows, edge, edges[j])
    return linear, matrix


def solve(linear, matrix, deadline=float("inf")):
    """Branch-and-bound exact if complete; always returns a feasible best mask.

    Lower bound: sum min(0, residual linear) plus every negative remaining
    pair interaction. This may be loose but cannot prune a genuine improvement.
    """
    n = len(linear)
    best, mask, nodes, complete = 0, 0, 0, True
    tail_negative = [0] * (n + 1)
    for i in reversed(range(n)):
        tail_negative[i] = tail_negative[i + 1] + sum(
            min(0, matrix[i][j]) for j in range(i + 1, n)
        )
    marginal = list(linear)

    def visit(i, value, selected):
        nonlocal best, mask, nodes, complete
        nodes += 1
        if nodes % 128 == 1 and time.monotonic() >= deadline:
            complete = False
            return
        if value < best:
            best, mask = value, selected
        if (
            i == n
            or value + sum(min(0, marginal[j]) for j in range(i, n)) + tail_negative[i]
            >= best
        ):
            return
        # Try the immediately cheaper branch first; both are explored as needed.
        for chosen in [1, 0] if marginal[i] < 0 else [0, 1]:
            if not complete:
                return
            if chosen:
                for j in range(i + 1, n):
                    marginal[j] += matrix[i][j]
                visit(i + 1, value + marginal[i], selected | (1 << i))
                for j in range(i + 1, n):
                    marginal[j] -= matrix[i][j]
            else:
                visit(i + 1, value, selected)

    visit(0, 0, 0)
    return dict(delta=best, mask=mask, nodes=nodes, complete=complete)


def choose_matching(rows, ranked, rng, size, mode, pool_size):
    if mode == "random":
        vertices = list(range(len(rows)))
        rng.shuffle(vertices)
        return list(zip(vertices[::2], vertices[1::2]))[:size]
    # Shuffle low-cost pool for diversity across successive neighborhoods.
    pool = list(ranked[:pool_size])
    rng.shuffle(pool)
    selected, used = [], set()
    while pool and len(selected) < size:
        if mode == "interaction":

            def score_edge(item):
                return item[0] + sum(
                    min(0, calculate_interaction(rows, item[1], e)) for e in selected
                )

            item = min(pool, key=score_edge)
        else:
            # Draw from the top half of the candidate pool, rather than repeat
            # the identical cheapest matching at every iteration.
            shortlist = sorted(pool, key=lambda item: item[0])[: max(1, len(pool) // 2)]
            item = rng.choice(shortlist)
        edge = item[1]
        selected.append(edge)
        used.update(edge)
        pool = [item for item in pool if not any(v in used for v in item[1])]
    return selected


def find_improving_pair(rows, ranked, deadline):
    """Find a strict matching pair gain, or exhaust this pair neighborhood.

    With nonnegative singles and b >= -24, only pairs with sum(a)<24 matter.
    Negative singles are returned first; exhaustion then has its exact scope.
    """
    if ranked and ranked[0][0] < 0:
        return [ranked[0][1]], 0, False
    eligible = [item for item in ranked if item[0] < 24]
    examined = 0
    for i, (cost, edge) in enumerate(eligible):
        for other_cost, other in eligible[i + 1 :]:
            if cost + other_cost >= 24:
                break
            examined += 1
            if examined % 1024 == 1 and time.monotonic() >= deadline:
                return [], examined, False
            if (
                len(set(edge + other)) == 4
                and calculate_interaction(rows, edge, other) + cost + other_cost < 0
            ):
                return [edge, other], examined, False
    return [], examined, True


def calculate_interaction(rows, first, second):
    u, v = first
    x, y = second
    if len({u, v, x, y}) != 4:
        raise ValueError("free edges must be vertex-disjoint")
    color = rows[u][x]
    if any(rows[a][b] != color for a, b in [(u, y), (v, x), (v, y)]):
        return 0
    return 24 if rows[u][v] == rows[x][y] else -24


# Compatibility aliases for historical research imports.
interaction = calculate_interaction
quadratic = build_quadratic_model
improving_pair = find_improving_pair


if __name__ == "__main__":
    main()
