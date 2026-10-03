"""Exact full-neighborhood tabu walk retaining the best checked-native state.

Bit-attribute tabu is adapted from Parczyk et al. (2024), section 3.2.
Tie breaking is lexicographic; the seed randomizes tenure, not equal-cost ties.
"""

import ctypes as C
import json
import random
import time

from k4_ramsey.artifacts import write_json
from k4_ramsey.engine import Graph, read_certificate
from k4_ramsey.schemas.strategies import StrategyRequest, TabuConfig
from k4_ramsey.strategy_cli import run_strategy


def main() -> None:
    run_strategy(run_search)


def run_search(args: StrategyRequest) -> None:
    data = read_certificate(args.input)
    # Preserve a valid checkpoint even if initial cache construction exhausts time.
    write_json(args.output, data)
    _, report = run_tabu_walk(
        data,
        seed=args.seed,
        seconds=args.seconds,
        config=json.loads(args.config.read_text()),
        checkpoint=lambda candidate: write_json(args.output, candidate),
    )
    write_json(args.output.parent / "search.json", report)


def run_tabu_walk(data, *, seed, seconds, config, checkpoint=None):
    config = TabuConfig.model_validate(config)
    maximum, tenure, jitter = config.max_moves, config.tenure, config.tenure_jitter
    checkpoint_seconds = config.checkpoint_seconds
    rng = random.Random(seed)
    started = time.monotonic()
    graph = Graph(data)
    initial = current = best = graph.count_subgraphs()["numerator"]
    graph.enable_cache()
    setup_seconds = time.monotonic() - started
    expiry = (C.c_int * (graph.n * graph.n))()
    rows = [bytearray(row, "ascii") for row in data["red_rows"]]
    best_rows = tuple(bytes(row) for row in rows)
    best_data = data
    last_checkpoint = time.monotonic()
    if checkpoint is not None:
        checkpoint(best_data)
    moves = uphill = sideways = aspiration = improvements = 0
    history, trace = [], []
    termination = "move_limit"
    while moves < maximum:
        if time.monotonic() - started >= seconds:
            termination = "time_limit"
            break
        step = moves
        move = graph.find_best_cached_allowed(expiry, step, best - current)
        if move is None:
            termination = "no_allowed_move"
            break
        u, v, delta = move
        was_tabu = expiry[u * graph.n + v] > step
        if was_tabu and current + delta >= best:
            raise RuntimeError("native scan violated aspiration")
        if graph.calculate_delta(u, v) != delta:
            raise RuntimeError("cached move delta mismatch")
        graph.flip(u, v)
        rows[u][v] = rows[v][u] = ord("1") if rows[u][v] == ord("0") else ord("0")
        current += delta
        duration = tenure + rng.randrange(jitter + 1)
        expires = calculate_expiry_step(step, duration)
        expiry[u * graph.n + v] = expiry[v * graph.n + u] = expires
        moves += 1
        uphill += delta > 0
        sideways += delta == 0
        aspiration += was_tabu
        if len(trace) < 100:
            trace.append(
                dict(
                    step=step,
                    u=u,
                    v=v,
                    delta=delta,
                    expiry=expires,
                    aspirational=was_tabu,
                    numerator=current,
                )
            )
        if current < best:
            best = current
            improvements += 1
            best_rows = tuple(bytes(row) for row in rows)
            history.append(
                dict(move=moves, numerator=best, seconds=time.monotonic() - started)
            )
        if (
            checkpoint is not None
            and time.monotonic() - last_checkpoint >= checkpoint_seconds
        ):
            best_data = dict(data, red_rows=[row.decode("ascii") for row in best_rows])
            checkpoint(best_data)
            last_checkpoint = time.monotonic()
    if graph.count_subgraphs()["numerator"] != current:
        raise RuntimeError("final walk count drift")
    if graph.export_certificate()["red_rows"] != [row.decode("ascii") for row in rows]:
        raise RuntimeError("Python adjacency mirror drift")
    best_data = dict(data, red_rows=[row.decode("ascii") for row in best_rows])
    if Graph(best_data).count_subgraphs()["numerator"] != best:
        raise RuntimeError("retained best count drift")
    if checkpoint is not None:
        checkpoint(best_data)
    return best_data, dict(
        numerator=best,
        initial_numerator=initial,
        final_walk_numerator=current,
        attempted=moves,
        accepted=moves,
        uphill=uphill,
        sideways=sideways,
        aspiration_moves=aspiration,
        improvements=improvements,
        tenure=tenure,
        tenure_jitter=jitter,
        history=history,
        trace=trace,
        setup_seconds=setup_seconds,
        seconds=time.monotonic() - started,
        termination=termination,
        rng_state=rng.getstate(),
        note="Exact best allowed single-edge move; bit-attribute tabu with strict global-best aspiration; lexicographic ties. No optimality claim.",
    )


def calculate_expiry_step(step, tenure):
    """Block the following `tenure` decisions; permit reuse immediately afterward."""
    return step + tenure + 1


# Compatibility aliases for historical research imports.
expiry_step = calculate_expiry_step
tabu_walk = run_tabu_walk


if __name__ == "__main__":
    main()
