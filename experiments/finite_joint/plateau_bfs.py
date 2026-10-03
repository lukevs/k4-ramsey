"""Bounded exact neutral-component search in the C4 parity model."""
import argparse
from collections import deque
import json
from pathlib import Path
import time

from k4_ramsey.engine import Graph, certificate, load
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


def analyze(state, terms, width):
    parities = []
    gains = [0] * width
    variable = 0
    for term in terms:
        parity = sum((state >> e) & 1 for e in term["edges"]) & 1
        parities.append(parity)
        variable += term["delta"] * parity
        contribution = term["delta"] * (1 - 2 * parity)
        for e in term["edges"]:
            gains[e] += contribution
    return variable, gains


def strict_descent(state, value, terms, width):
    moves = 0
    while True:
        _, gains = analyze(state, terms, width)
        delta = min(gains)
        if delta >= 0:
            return state, value, moves, gains
        e = gains.index(delta)
        state ^= 1 << e
        value += delta
        moves += 1


def main():
    p = argparse.ArgumentParser()
    for name in ("input", "output", "config"):
        p.add_argument("--" + name, type=Path, required=True)
    p.add_argument("--seed", type=int, required=True)
    p.add_argument("--seconds", type=float, required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    model = json.loads(Path(config["model_path"]).read_text())
    max_states = config.get("max_states", 20000)
    max_escapes = config.get("max_escapes", 20)
    rows = load(args.input)["red_rows"]
    fibers, blocks, terms = model["fibers"], model["blocks"], model["terms"]
    shifts = [infer_shift(rows, fibers[i], fibers[j]) for i, j, *_ in blocks]
    state = sum((s & 1) << e for e, s in enumerate(shifts))
    graph = Graph(certificate(rows))
    initial = value = graph.counts()["numerator"]
    graph.close()
    # The parent should already be a strict local minimum; retain this as the
    # matched strict-descent control rather than silently doing extra work.
    variable, initial_gains = analyze(state, terms, len(blocks))
    if min(initial_gains) < 0:
        raise RuntimeError("input is not the preregistered strict local minimum")
    constant = value - variable
    if constant + variable != value:
        raise RuntimeError("model baseline arithmetic failed")

    start = time.monotonic()
    deadline = start + args.seconds
    history = []
    examined_total = 0
    termination = "escape_limit"
    for escape in range(max_escapes):
        frontier = deque([state])
        visited = {state}
        exposed = None
        while frontier and len(visited) <= max_states and time.monotonic() < deadline:
            current = frontier.popleft()
            variable, gains = analyze(current, terms, len(blocks))
            examined_total += 1
            negative = min(gains)
            if negative < 0:
                exposed = (current, constant + variable, gains)
                break
            for e, gain in enumerate(gains):
                if gain == 0:
                    child = current ^ (1 << e)
                    if child not in visited:
                        visited.add(child)
                        frontier.append(child)
        if exposed is None:
            termination = ("time_limit" if time.monotonic() >= deadline else
                           "state_limit" if len(visited) > max_states else
                           "neutral_component_exhausted")
            history.append({"escape": escape, "states": len(visited),
                            "frontier": len(frontier), "result": termination,
                            "numerator": value, "seconds": time.monotonic() - start})
            break
        plateau_state, plateau_value, gains = exposed
        depth_delta = (plateau_state ^ state).bit_count()
        e = gains.index(min(gains))
        next_state = plateau_state ^ (1 << e)
        next_value = plateau_value + gains[e]
        next_state, next_value, strict_moves, final_gains = strict_descent(
            next_state, next_value, terms, len(blocks))
        if next_value >= value:
            raise RuntimeError("neutral escape failed to lower objective")
        history.append({"escape": escape, "states": len(visited),
                        "hamming_from_local_minimum": depth_delta,
                        "exposing_coordinate": e, "exposing_delta": gains[e],
                        "strict_moves": strict_moves + 1,
                        "old_numerator": value, "numerator": next_value,
                        "seconds": time.monotonic() - start})
        state, value = next_state, next_value
    else:
        termination = "escape_limit"

    bits = [(state >> e) & 1 for e in range(len(blocks))]
    result = [list(row) for row in rows]
    for e, (i, j, *_) in enumerate(blocks):
        shift = (shifts[e] & 2) | bits[e]
        for a, u in enumerate(fibers[i]):
            for b, v in enumerate(fibers[j]):
                result[u][v] = result[v][u] = str(int((a ^ shift) != b))
    data = certificate(["".join(row) for row in result])
    graph = Graph(data)
    actual = graph.counts()["numerator"]
    graph.close()
    if actual != value:
        raise RuntimeError(f"C4 model/full recount mismatch: {value} != {actual}")
    write_json(args.output, data)
    write_json(args.output.parent / "search.json", {
        "hypothesis": "H-ROOT-005", "numerator": value,
        "initial_numerator": initial, "delta": value - initial,
        "initial_minimum_gain": min(initial_gains),
        "initial_zero_coordinates": sum(g == 0 for g in initial_gains),
        "escapes": sum("exposing_delta" in h for h in history),
        "examined_states": examined_total, "history": history,
        "termination": termination, "seconds": time.monotonic() - start,
        "note": "Exact bounded breadth-first neutral-component exploration in the fixed-first-bit C4 parity model."
    })


if __name__ == "__main__":
    main()
