"""Baseline strategy and example of the single-experiment script protocol."""

import random
import time

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import DescentConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated DescentConfig configuration."""
    config = DescentConfig.model_validate(read_json(args.config))
    max_moves = config.max_moves
    checkpoint_moves = config.checkpoint_moves
    rng = random.Random(args.seed)
    start = time.monotonic()
    graph = Graph(read_certificate(args.input))
    initial = graph.count_subgraphs()["numerator"]
    value = initial
    attempted = accepted = 0
    history = []
    write_json(args.output, graph.export_certificate())
    while (
        graph.n > 1
        and attempted < max_moves
        and time.monotonic() - start < args.seconds
    ):
        u, v = rng.sample(range(graph.n), 2)
        delta = graph.calculate_delta(u, v)
        attempted += 1
        if delta < 0:
            graph.flip(u, v)
            value += delta
            accepted += 1
            history.append(
                dict(move=attempted, numerator=value, seconds=time.monotonic() - start)
            )
        if attempted % checkpoint_moves == 0:
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
            seconds=time.monotonic() - start,
            termination="move_limit" if attempted >= max_moves else "time_limit",
            history=history,
            rng_state=rng.getstate(),
            note="Sampled strict descent; does not certify a single-edge local optimum.",
        ),
    )


if __name__ == "__main__":
    main()
