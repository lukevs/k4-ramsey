"""Exact coordinate descent over both bits of four-sheet V4 voltages.

Each quotient variable replaces one missing perfect matching in a 4x4 block.
Changing a voltage toggles the symmetric difference of two matchings (eight
binary graph edges).  Trial deltas are exact sums of cached one-edge deltas,
with an exact rollback before the next alternative is inspected.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json


def infer_shift(rows, left, right):
    missing = []
    for a, u in enumerate(left):
        zeros = [b for b, v in enumerate(right) if rows[u][v] == "0"]
        if len(zeros) != 1:
            raise ValueError("defect block is not the complement of a matching")
        missing.append(zeros[0])
    shifts = [missing[a] ^ a for a in range(4)]
    if len(set(shifts)) != 1:
        raise ValueError("defect block is not a V4 translation")
    return shifts[0]


def transition_edges(fibers, block, old, new):
    if old == new:
        return []
    i, j = block[:2]
    return [(fibers[i][a], fibers[j][a ^ shift])
            for a in range(4) for shift in (old, new)]


def apply_transition(graph, fibers, block, old, new):
    delta = 0
    for u, v in transition_edges(fibers, block, old, new):
        delta += graph.cached_delta(u, v)
        graph.flip(u, v)
    return delta


def trial_transition(graph, fibers, block, old, new):
    delta = apply_transition(graph, fibers, block, old, new)
    rollback = apply_transition(graph, fibers, block, new, old)
    if rollback != -delta:
        raise RuntimeError("group rollback failed")
    return delta


def main():
    parser = argparse.ArgumentParser()
    for name in ("input", "output", "config"):
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--seed", type=int, required=True)
    parser.add_argument("--seconds", type=float, required=True)
    args = parser.parse_args()
    config = json.loads(args.config.read_text())
    allowed = {"fibers", "blocks", "model_path", "mode", "max_sweeps", "checkpoint_moves"}
    if set(config) - allowed:
        raise ValueError("unknown config keys")
    mode = config.get("mode", "joint")
    if mode not in {"joint", "second_only"}:
        raise ValueError("mode must be joint or second_only")
    max_sweeps = config.get("max_sweeps", 8)
    checkpoint = config.get("checkpoint_moves", 25)
    if type(max_sweeps) is not int or max_sweeps < 1:
        raise ValueError("max_sweeps must be positive")
    if type(checkpoint) is not int or checkpoint < 1:
        raise ValueError("checkpoint_moves must be positive")

    data = load(args.input)
    rows = data["red_rows"]
    if "model_path" in config:
        model = json.loads(Path(config["model_path"]).read_text())
        fibers, blocks = model["fibers"], model["blocks"]
    else:
        fibers, blocks = config["fibers"], config["blocks"]
    if sorted(v for cell in fibers for v in cell) != list(range(len(rows))):
        raise ValueError("fibers do not partition the graph")
    shifts = [infer_shift(rows, fibers[i], fibers[j]) for i, j, *_ in blocks]
    graph = Graph(data)
    graph.enable_cache()
    initial = value = graph.counts()["numerator"]
    write_json(args.output, graph.export())
    start = time.monotonic()
    deadline = start + args.seconds
    rng = random.Random(args.seed)
    history = []
    evaluations = moves = 0
    termination = "sweep_limit"
    for sweep in range(max_sweeps):
        accepted = 0
        order = list(range(len(blocks)))
        rng.shuffle(order)
        for e in order:
            if time.monotonic() >= deadline:
                termination = "time_limit"
                break
            old = shifts[e]
            targets = [old ^ 1] if mode == "second_only" else [q for q in range(4) if q != old]
            best_delta, best = 0, old
            for target in targets:
                delta = trial_transition(graph, fibers, blocks[e], old, target)
                evaluations += 1
                if delta < best_delta or (delta == best_delta and target < best):
                    best_delta, best = delta, target
            if best != old:
                actual = apply_transition(graph, fibers, blocks[e], old, best)
                if actual != best_delta:
                    raise RuntimeError("accepted delta changed after rollback")
                shifts[e] = best
                value += actual
                moves += 1
                accepted += 1
                if moves % checkpoint == 0:
                    if graph.counts()["numerator"] != value:
                        raise RuntimeError("checkpoint count drift")
                    write_json(args.output, graph.export())
        history.append({"sweep": sweep, "accepted": accepted, "numerator": value,
                        "evaluations": evaluations, "seconds": time.monotonic() - start})
        if termination == "time_limit":
            break
        if accepted == 0:
            termination = "restricted_local_minimum"
            break
    actual = graph.counts()["numerator"]
    if actual != value:
        raise RuntimeError("final count drift")
    write_json(args.output, graph.export())
    graph.close()
    write_json(args.output.parent / "search.json", {
        "hypothesis": "H-FJ-001",
        "mode": mode,
        "numerator": value,
        "initial_numerator": initial,
        "delta": value - initial,
        "moves": moves,
        "evaluations": evaluations,
        "history": history,
        "termination": termination,
        "seconds": time.monotonic() - start,
        "input_sha256": hashlib.sha256(args.input.read_bytes()).hexdigest(),
        "note": "Exact two-bit V4 quotient-block coordinate moves; restricted neighborhood only."
    })


if __name__ == "__main__":
    main()
