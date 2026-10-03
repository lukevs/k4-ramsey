"""Exact full-neighborhood tabu walk retaining the best checked-native state.

Bit-attribute tabu is adapted from Parczyk et al. (2024), section 3.2.
Tie breaking is lexicographic; the seed randomizes tenure, not equal-cost ties.
"""
import argparse
import ctypes as C
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def expiry_step(step, tenure):
    """Block the following `tenure` decisions; permit reuse immediately afterward."""
    return step + tenure + 1


def tabu_walk(data, *, seed, seconds, config, checkpoint=None):
    if set(config) - {"max_moves", "tenure", "tenure_jitter", "checkpoint_seconds"}:
        raise ValueError("unknown configuration key")
    maximum = config.get("max_moves", 1000000000)
    tenure = config.get("tenure", 40)
    jitter = config.get("tenure_jitter", 40)
    checkpoint_seconds = config.get("checkpoint_seconds", 1)
    for name, value in (("max_moves", maximum), ("tenure", tenure), ("tenure_jitter", jitter)):
        if type(value) is not int or value < 0:
            raise ValueError(name + " must be a nonnegative integer")
    if maximum + tenure + jitter + 1 >= 2**31:
        raise ValueError("expiry could overflow native signed int")
    if not isinstance(checkpoint_seconds, (int, float)) or not 0 < checkpoint_seconds <= 60:
        raise ValueError("checkpoint_seconds must be in (0,60]")
    rng = random.Random(seed)
    started = time.monotonic()
    graph = Graph(data)
    initial = current = best = graph.counts()["numerator"]
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
        move = graph.best_cached_allowed(expiry, step, best - current)
        if move is None:
            termination = "no_allowed_move"
            break
        u, v, delta = move
        was_tabu = expiry[u * graph.n + v] > step
        if was_tabu and current + delta >= best:
            raise RuntimeError("native scan violated aspiration")
        if graph.delta(u, v) != delta:
            raise RuntimeError("cached move delta mismatch")
        graph.flip(u, v)
        rows[u][v] = rows[v][u] = ord("1") if rows[u][v] == ord("0") else ord("0")
        current += delta
        duration = tenure + rng.randrange(jitter + 1)
        expires = expiry_step(step, duration)
        expiry[u * graph.n + v] = expiry[v * graph.n + u] = expires
        moves += 1
        uphill += delta > 0
        sideways += delta == 0
        aspiration += was_tabu
        if len(trace) < 100:
            trace.append(dict(step=step, u=u, v=v, delta=delta, expiry=expires,
                              aspirational=was_tabu, numerator=current))
        if current < best:
            best = current
            improvements += 1
            best_rows = tuple(bytes(row) for row in rows)
            history.append(dict(move=moves, numerator=best, seconds=time.monotonic() - started))
        if checkpoint is not None and time.monotonic() - last_checkpoint >= checkpoint_seconds:
            best_data = dict(data, red_rows=[row.decode("ascii") for row in best_rows])
            checkpoint(best_data)
            last_checkpoint = time.monotonic()
    if graph.counts()["numerator"] != current:
        raise RuntimeError("final walk count drift")
    if graph.export()["red_rows"] != [row.decode("ascii") for row in rows]:
        raise RuntimeError("Python adjacency mirror drift")
    best_data = dict(data, red_rows=[row.decode("ascii") for row in best_rows])
    if Graph(best_data).counts()["numerator"] != best:
        raise RuntimeError("retained best count drift")
    if checkpoint is not None:
        checkpoint(best_data)
    return best_data, dict(
        numerator=best, initial_numerator=initial, final_walk_numerator=current,
        attempted=moves, accepted=moves, uphill=uphill, sideways=sideways,
        aspiration_moves=aspiration, improvements=improvements,
        tenure=tenure, tenure_jitter=jitter, history=history, trace=trace,
        setup_seconds=setup_seconds, seconds=time.monotonic() - started,
        termination=termination, rng_state=rng.getstate(),
        note="Exact best allowed single-edge move; bit-attribute tabu with strict global-best aspiration; lexicographic ties. No optimality claim.")


def main():
    p = argparse.ArgumentParser()
    for name in ("input", "output", "config"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)
    args = p.parse_args()
    data = load(args.input)
    # Preserve a valid checkpoint even if initial cache construction exhausts time.
    write_json(args.output, data)
    _, report = tabu_walk(data, seed=args.seed, seconds=args.seconds,
                          config=json.loads(args.config.read_text()),
                          checkpoint=lambda candidate: write_json(args.output, candidate))
    write_json(args.output.parent / "search.json", report)


if __name__ == "__main__":
    main()
