"""Full-edge screening with fresh deltas before every accepted flip."""

import time
from pathlib import Path

from k4_ramsey.artifacts import read_json, write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import ScanConfig, StrategyRequest
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    """Run the search using a validated ScanConfig configuration."""
    config = ScanConfig.model_validate(read_json(args.config))
    max_passes = config.max_passes
    start = time.monotonic()
    graph = Graph(read_certificate(Path(args.input)))
    initial = value = graph.count_subgraphs()["numerator"]
    pairs = [(u, v) for u in range(graph.n) for v in range(u + 1, graph.n)]
    history = []
    scans = []
    local = False
    write_json(Path(args.output), graph.export_certificate())
    for step in range(max_passes):
        if time.monotonic() - start >= args.seconds:
            break
        deltas = graph.calculate_deltas(pairs)
        candidates = sorted((d, u, v) for (u, v), d in zip(pairs, deltas) if d < 0)
        scans.append(
            dict(
                pass_index=step,
                minimum=min(deltas, default=0),
                improving=len(candidates),
                numerator=value,
            )
        )
        if not candidates:
            local = True
            break
        # A full scan's deltas become stale after the first flip. Recheck each
        # shortlisted edge against the current graph; rescan on the next pass.
        for _, u, v in candidates:
            if time.monotonic() - start >= args.seconds:
                break
            change = graph.calculate_delta(u, v)
            if change < 0:
                graph.flip(u, v)
                value += change
                history.append(
                    dict(u=u, v=v, numerator=value, seconds=time.monotonic() - start)
                )
        write_json(Path(args.output), graph.export_certificate())
    if graph.count_subgraphs()["numerator"] != value:
        raise RuntimeError("incremental drift")
    write_json(Path(args.output), graph.export_certificate())
    write_json(
        Path(args.output).parent / "search.json",
        dict(
            numerator=value,
            initial_numerator=initial,
            accepted=len(history),
            history=history,
            scans=scans,
            single_edge_local_minimum=local,
            seconds=time.monotonic() - start,
            termination="full_scan_no_improvement" if local else "budget",
            note="Local-minimum statement uses native exhaustive delta scan, not a formal Lean theorem.",
        ),
    )


if __name__ == "__main__":
    main()
