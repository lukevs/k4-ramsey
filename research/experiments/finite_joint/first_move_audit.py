"""Isolate the first exact-improving low-bit move and compare the C4 model."""
import argparse
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
            raise ValueError("not a complement-matching block")
        missing.append(zeros[0])
    shifts = [missing[a] ^ a for a in range(4)]
    if len(set(shifts)) != 1:
        raise ValueError("not a V4 translation")
    return shifts[0]


def apply(graph, fibers, block, old, new):
    delta = 0
    i, j = block[:2]
    for a in range(4):
        for shift in (old, new):
            u, v = fibers[i][a], fibers[j][a ^ shift]
            delta += graph.cached_delta(u, v)
            graph.flip(u, v)
    return delta


def main():
    p = argparse.ArgumentParser()
    for name in ("input", "output", "config"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    model = json.loads(Path(config["model_path"]).read_text())
    data = load(args.input)
    rows = data["red_rows"]
    fibers, blocks, terms = model["fibers"], model["blocks"], model["terms"]
    shifts = [infer_shift(rows, fibers[i], fibers[j]) for i, j, *_ in blocks]
    bits = [s & 1 for s in shifts]
    parities = [sum(bits[e] for e in term["edges"]) % 2 for term in terms]
    incidence = [[] for _ in blocks]
    for k, term in enumerate(terms):
        for e in term["edges"]:
            incidence[e].append(k)
    graph = Graph(data)
    graph.enable_cache()
    before = graph.counts()["numerator"]
    order = list(range(len(blocks)))
    random.Random(args.seed).shuffle(order)
    chosen = None
    plateau_moves = []
    for rank, e in enumerate(order):
        old, new = shifts[e], shifts[e] ^ 1
        delta = apply(graph, fibers, blocks[e], old, new)
        rollback = apply(graph, fibers, blocks[e], new, old)
        if rollback != -delta:
            raise RuntimeError("audit rollback mismatch")
        predicted = sum(terms[k]["delta"] * (1 - 2 * parities[k])
                        for k in incidence[e])
        if predicted != delta:
            raise RuntimeError(f"model/exact delta mismatch at {e}: {predicted} != {delta}")
        if delta < 0:
            chosen = {"coordinate": e, "order_rank": rank, "old_shift": old,
                      "new_shift": new, "exact_sequential_delta": delta,
                      "model_predicted_delta": predicted,
                      "incidence_count": len(incidence[e]),
                      "incident_terms": [terms[k] for k in incidence[e]]}
            actual = apply(graph, fibers, blocks[e], old, new)
            if actual != delta:
                raise RuntimeError("accepted audit delta mismatch")
            break
        # Reproduce the control's deterministic zero-delta tie rule.  These
        # plateau moves are why strict cycle descent and this run differ.
        if delta == 0 and new < old:
            actual = apply(graph, fibers, blocks[e], old, new)
            if actual != 0:
                raise RuntimeError("plateau move changed after rollback")
            shifts[e] = new
            bits[e] ^= 1
            for k in incidence[e]:
                parities[k] ^= 1
            plateau_moves.append({"coordinate": e, "order_rank": rank,
                                  "old_shift": old, "new_shift": new,
                                  "exact_delta": delta, "model_delta": predicted})
    if chosen is None:
        raise RuntimeError("no improving low-bit coordinate found")
    after = graph.counts()["numerator"]
    if after - before != chosen["exact_sequential_delta"]:
        raise RuntimeError("full native recount disagrees with sequential delta")
    write_json(args.output, graph.export())
    graph.close()
    write_json(args.output.parent / "search.json", {
        "hypothesis": "H-FJ-001-integrity-audit",
        "input_numerator": before,
        "numerator": after,
        "chosen": chosen,
        "preceding_plateau_moves": plateau_moves,
        "model_source_baseline": model["baseline_numerator"],
        "model_path": config["model_path"],
        "note": "Single isolated low-bit move; exact cached sequence plus full native recount."
    })


if __name__ == "__main__":
    main()
