"""Cached exact single-flip descent with optional shared-endpoint escapes."""

import time

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import FastNeighborhoodConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated FastNeighborhoodConfig configuration."""
    config = FastNeighborhoodConfig.model_validate(read_json(args.config))
    mode = config.mode
    per_color = config.per_color
    maximum = config.max_moves
    checkpoint = config.checkpoint_moves
    start = time.monotonic()
    deadline = start + args.seconds
    graph = Graph(read_certificate(args.input))
    initial = value = graph.count_subgraphs()["numerator"]
    write_json(args.output, graph.export_certificate())
    graph.enable_cache()
    setup = time.monotonic() - start
    history = []
    singles = stars = steps = 0
    local = False
    minimum = None
    for step in range(maximum):
        if time.monotonic() >= deadline:
            break
        best = graph.find_best_cached_flip()
        if best is None:
            local = True
            break
        minimum = best[2]
        if best[2] < 0:
            u, v, delta = best
            graph.flip(u, v)
            value += delta
            singles += 1
            move = [u, v]
        else:
            local = True
            if mode == "single":
                break
            star = graph.find_best_cached_star(per_color)
            if star is None:
                break
            u, v, w, delta = star
            actual = graph.calculate_cached_delta(u, v)
            graph.flip(u, v)
            actual += graph.calculate_cached_delta(u, w)
            graph.flip(u, w)
            if actual != delta:
                raise RuntimeError("cached joint delta mismatch")
            value += actual
            stars += 1
            move = [u, v, w]
        local = False
        steps += 1
        if steps % 10 == 0 or len(move) == 3:
            history.append(
                dict(
                    step=steps,
                    numerator=value,
                    move=move,
                    seconds=time.monotonic() - start,
                )
            )
        if steps % checkpoint == 0:
            if graph.count_subgraphs()["numerator"] != value:
                raise RuntimeError("checkpoint count drift")
            write_json(args.output, graph.export_certificate())
    if graph.count_subgraphs()["numerator"] != value:
        raise RuntimeError("final count drift")
    write_json(args.output, graph.export_certificate())
    write_json(
        args.output.parent / "search.json",
        dict(
            numerator=value,
            initial_numerator=initial,
            singles=singles,
            stars=stars,
            steps=steps,
            single_edge_local_minimum=local,
            last_scanned_minimum_single_delta=minimum,
            setup_seconds=setup,
            seconds=time.monotonic() - start,
            history=history,
            termination="time_limit"
            if time.monotonic() >= deadline
            else ("restricted_local_minimum" if local else "move_limit"),
            note="Seed unused: deterministic tie-breaking. Star checks use low-cost shortlists, not global optimality.",
        ),
    )


if __name__ == "__main__":
    main()
