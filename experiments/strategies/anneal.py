"""Seeded Metropolis cycles, retaining the best exact-count checkpoint."""

import math
import random
import time

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import AnnealConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated AnnealConfig configuration."""
    config = AnnealConfig.model_validate(read_json(args.config))
    temperature = config.temperature
    cycle_moves = config.cycle_moves
    max_moves = config.max_moves
    restart = config.restart
    start = time.monotonic()
    rng = random.Random(args.seed)
    best_data = read_certificate(args.input)
    graph = Graph(best_data)
    initial = best = value = graph.count_subgraphs()["numerator"]
    history = []
    attempted = accepted = uphill = cycles = 0
    write_json(args.output, best_data)
    while (
        graph.n > 1
        and attempted < max_moves
        and time.monotonic() - start < args.seconds
    ):
        if attempted and attempted % cycle_moves == 0:
            if graph.count_subgraphs()["numerator"] != value:
                raise RuntimeError("cycle count drift")
            if restart:
                graph.close()
                graph = Graph(best_data)
                value = best
            cycles += 1
            write_json(args.output, best_data)
        phase = (attempted % cycle_moves) / cycle_moves
        # Last quarter is strict descent, not a claim of local optimality.
        temp = temperature * max(0, 1 - phase / 0.75)
        u, v = rng.sample(range(graph.n), 2)
        change = graph.calculate_delta(u, v)
        attempted += 1
        if change < 0 or (temp > 0 and rng.random() < math.exp(-max(0, change) / temp)):
            graph.flip(u, v)
            value += change
            accepted += 1
            uphill += change > 0
            if value < best:
                best = value
                best_data = graph.export_certificate()
                history.append(
                    dict(
                        move=attempted, numerator=best, seconds=time.monotonic() - start
                    )
                )
    if graph.count_subgraphs()["numerator"] != value:
        raise RuntimeError("final count drift")
    graph.close()
    with_best = Graph(best_data)
    if with_best.count_subgraphs()["numerator"] != best:
        raise RuntimeError("best checkpoint drift")
    write_json(args.output, best_data)
    write_json(
        args.output.parent / "search.json",
        dict(
            numerator=best,
            initial_numerator=initial,
            final_walk_numerator=value,
            attempted=attempted,
            accepted=accepted,
            uphill=uphill,
            cycles=cycles,
            history=history,
            seconds=time.monotonic() - start,
            termination="move_limit" if attempted >= max_moves else "time_limit",
            note="Metropolis exploratory screen, not a local or global optimality certificate.",
        ),
    )


if __name__ == "__main__":
    main()
