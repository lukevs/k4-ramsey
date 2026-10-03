"""Canonical 384-class size-two refinement of the retained 192 parent."""
from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import time

from research.experiments.algebraic.lift import discover_fibers, half_blocks
from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


SCALE = 256


def literal_numerator(matrix, denominator):
    red_answer = blue_answer = 0
    for vertices in product(range(len(matrix)), repeat=4):
        red = blue = 1
        for a, b in combinations(range(4), 2):
            value = matrix[vertices[a]][vertices[b]]
            red *= value
            blue *= denominator - value
        red_answer += red
        blue_answer += blue
    return red_answer + blue_answer


def differences(values):
    rows = [list(values)]
    while len(rows[-1]) > 1:
        rows.append([b - a for a, b in zip(rows[-1], rows[-1][1:])])
    return [row[0] for row in rows]


def polynomial_value(forward_differences, x):
    # Generalized integer binomial supports held-out negative coordinates.
    coefficient = 1
    total = 0
    for degree, delta in enumerate(forward_differences):
        if degree:
            coefficient = coefficient * (x - degree + 1) // degree
        total += delta * coefficient
    return total


def tiny_oracle():
    # A nontrivial centered two-by-two cross-block refinement.  Values at
    # t=0..6 interpolate a degree-six polynomial and independent held-out
    # negative/positive integer points test the interpolation.
    denominator = 20
    base = [[0, 10], [10, 0]]
    unit = [[0, 0, 0, 0] for _ in range(4)]
    for a in range(2):
        for b in range(2):
            sign = 1 if a == b else -1
            unit[a][2 + b] = unit[2 + b][a] = sign

    def matrix(t):
        return [[base[i // 2][j // 2] + unit[i][j] * t
                 for j in range(4)] for i in range(4)]

    samples = [literal_numerator(matrix(t), denominator) for t in range(7)]
    ds = differences(samples)
    held_out = {}
    for t in (-5, -2, 7, 10):
        actual = literal_numerator(matrix(t), denominator)
        predicted = polynomial_value(ds, t)
        if actual != predicted:
            raise RuntimeError("tiny polynomial interpolation failed")
        held_out[str(t)] = actual
    return {"samples_0_to_6": samples, "forward_differences": ds,
            "held_out": held_out}


def canonical_pairs(rows, fibers):
    pairs = [None] * len(fibers)
    halves = half_blocks(rows, fibers)
    if len(halves) * 2 != len(fibers):
        raise RuntimeError("degree-two relation is not a perfect matching")
    for i, j, pattern in halves:
        left_groups = {}
        for a, mask in enumerate(pattern):
            left_groups.setdefault(mask, []).append(fibers[i][a])
        column_masks = []
        for b in range(4):
            column_masks.append(sum(((pattern[a] >> b) & 1) << a for a in range(4)))
        right_groups = {}
        for b, mask in enumerate(column_masks):
            right_groups.setdefault(mask, []).append(fibers[j][b])
        if sorted(map(len, left_groups.values())) != [2, 2]:
            raise RuntimeError("left K2,2 endpoint did not induce two pairs")
        if sorted(map(len, right_groups.values())) != [2, 2]:
            raise RuntimeError("right K2,2 endpoint did not induce two pairs")
        if pairs[i] is not None or pairs[j] is not None:
            raise RuntimeError("degree-two endpoint repeated")
        pairs[i] = sorted((sorted(group) for group in left_groups.values()))
        pairs[j] = sorted((sorted(group) for group in right_groups.values()))
    if any(value is None for value in pairs):
        raise RuntimeError("unpaired old fiber")
    flat = [cell for fiber_pairs in pairs for cell in fiber_pairs]
    if sorted(v for cell in flat for v in cell) != list(range(len(rows))):
        raise RuntimeError("canonical pairs do not partition vertices")
    return pairs, flat, halves


def build_direction(rows, fibers, pairs, parent, denominator):
    order = 2 * len(fibers)
    base = [[0] * order for _ in range(order)]
    direction = [[0] * order for _ in range(order)]
    old_counts = [[0] * len(fibers) for _ in fibers]
    for i, left in enumerate(fibers):
        for j in range(i + 1):
            count = sum(rows[u][v] == "1" for u in left for v in fibers[j])
            old_counts[i][j] = old_counts[j][i] = count
    for a in range(order):
        i, ia = divmod(a, 2)
        for b in range(a + 1):
            j, jb = divmod(b, 2)
            base[a][b] = base[b][a] = parent[i][j]
            subcount = sum(rows[u][v] == "1" for u in pairs[i][ia]
                           for v in pairs[j][jb])
            # subdensity - olddensity = subcount/4 - oldcount/16.
            numerator = (4 * subcount - old_counts[i][j]) * (denominator // 16)
            if numerator % SCALE:
                raise RuntimeError("direction is not integral on amplitude grid")
            direction[a][b] = direction[b][a] = numerator // SCALE
    # Each old 2x2 block of fine cells must have zero total direction.
    for i in range(len(fibers)):
        for j in range(len(fibers)):
            if sum(direction[2 * i + a][2 * j + b]
                   for a in range(2) for b in range(2)) != 0:
                raise RuntimeError("old block mean changed")
    return base, direction, old_counts


def feasible_interval(base, direction, denominator):
    def ceil_div(a, b):
        return -((-a) // b)

    low, high = -10**18, 10**18
    for i, row in enumerate(base):
        for j, value in enumerate(row):
            d = direction[i][j]
            if d > 0:
                low = max(low, ceil_div(-value, d))
                high = min(high, (denominator - value) // d)
            elif d < 0:
                low = max(low, ceil_div(denominator - value, d))
                high = min(high, (-value) // d)
    if not low <= 0 <= high:
        raise RuntimeError("zero amplitude is not feasible")
    return low, high


def materialize(base, direction, amplitude):
    matrix = [[x + amplitude * direction[i][j] for j, x in enumerate(row)]
              for i, row in enumerate(base)]
    return matrix


def recount(binary, matrix, denominator):
    payload = f"{len(matrix)} {denominator}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix) + "\n"
    return tuple(map(int, subprocess.check_output(
        [str(binary)], input=payload, text=True, timeout=120).split()))


def main():
    started = time.monotonic()
    out = ROOT / "reports/quotient-refinement-canonical-pairs-003"
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, out / "source_snapshot.py")
    shutil.copy2(ROOT / "research/experiments/quotient_refinement/preregistration.json",
                 out / "preregistration.json")
    tiny = tiny_oracle()

    seed_path = ROOT / "data/published_cayley_768.json"
    seed = json.loads(seed_path.read_text())
    rows = seed["red_rows"]
    fibers = discover_fibers(rows)
    stored_quotient_path = ROOT / "reports/pilot-algebraic-lift-001/quotient.json"
    stored_fibers = json.loads(stored_quotient_path.read_text())["fibers"]
    if fibers != stored_fibers:
        raise RuntimeError("discovered fibers are not aligned with the retained parent quotient")
    pairs, flat, halves = canonical_pairs(rows, fibers)
    parent_path = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
    parent_report_path = ROOT / "reports/literature-two-parameter-001/report.json"
    parent_data = json.loads(parent_path.read_text())
    parent = parent_data["red_probability_numerators"]
    denominator = parent_data["edge_probability_denominator"]
    if denominator != 65536 or len(parent) != 192:
        raise RuntimeError("unexpected parent")
    base, direction, old_counts = build_direction(
        rows, fibers, pairs, parent, denominator)
    low, high = feasible_interval(base, direction, denominator)

    checker = ROOT / "reports/association-scheme-phase-001/ordered_graphon_u256"
    sample_counts = []
    sample_color_counts = []
    for amplitude in range(7):
        matrix = materialize(base, direction, amplitude)
        if any(not 0 <= x <= denominator for row in matrix for x in row):
            raise RuntimeError("interpolation sample outside box")
        red, blue, total = recount(checker, matrix, denominator)
        sample_counts.append(total)
        sample_color_counts.append({"amplitude": amplitude, "red": red,
                                    "blue": blue, "total": total})
    ds = differences(sample_counts)
    # Six graph edges make degree<=6 a mathematical bound.  The selected
    # point's direct recount below is the independent interpolation gate.
    normalization = 384 ** 4 * denominator ** 6
    parent_density = Fraction(json.loads(parent_report_path.read_text())["density"])
    if Fraction(sample_counts[0], normalization) != parent_density:
        raise RuntimeError("zero-amplitude duplicated parent mismatch")

    values = [(polynomial_value(ds, amplitude), amplitude)
              for amplitude in range(low, high + 1)]
    best_total, best_amplitude = min(values)
    best_matrix = materialize(base, direction, best_amplitude)
    red, blue, direct_total = recount(checker, best_matrix, denominator)
    if direct_total != best_total:
        raise RuntimeError("selected amplitude direct recount mismatch")
    # Pair-label reversal in every old fiber is a simultaneous row/column
    # permutation.  Verify it materializes the corresponding permuted matrix.
    permutation = [2 * i + (1 - s) for i in range(192) for s in range(2)]
    permuted = [[best_matrix[permutation[i]][permutation[j]]
                 for j in range(384)] for i in range(384)]
    reversed_pairs = [list(reversed(fiber_pairs)) for fiber_pairs in pairs]
    reverse_base, reverse_direction, _ = build_direction(
        rows, fibers, reversed_pairs, parent, denominator)
    if materialize(reverse_base, reverse_direction, best_amplitude) != permuted:
        raise RuntimeError("pair-label relabeling control failed")

    candidate = {
        "schema": "rational-step-graphon-v1",
        "block_weights": [1] * 384,
        "edge_probability_denominator": denominator,
        "red_probability_numerators": best_matrix,
    }
    write_json(out / "canonical-pairs.json", pairs)
    write_json(out / "graphon-candidate.json", candidate)
    best_density = Fraction(best_total, normalization)
    report = {
        "hypothesis": "H-QR-001 canonical pair refinement",
        "seed": str(seed_path), "seed_sha256": hashlib.sha256(seed_path.read_bytes()).hexdigest(),
        "parent": str(parent_path), "parent_sha256": hashlib.sha256(parent_path.read_bytes()).hexdigest(),
        "stored_quotient": str(stored_quotient_path),
        "stored_quotient_sha256": hashlib.sha256(stored_quotient_path.read_bytes()).hexdigest(),
        "fiber_alignment_gate": "exact ordered equality passed",
        "parent_density": str(parent_density), "global_checked_reference": "0.03013890356539909",
        "base_order": 192, "refined_order": 384, "denominator": denominator,
        "degree_two_blocks": len(halves), "canonical_pair_cells": len(flat),
        "direction_nonzero_coordinates": sum(direction[i][j] != 0 for i in range(384) for j in range(i + 1)),
        "direction_values": sorted({x for row in direction for x in row}),
        "amplitude_grid_scale": SCALE, "feasible_amplitudes": [low, high],
        "feasible_epsilon": [str(Fraction(low, SCALE)), str(Fraction(high, SCALE))],
        "interpolation_samples": sample_color_counts,
        "forward_differences": ds,
        "selected_amplitude": best_amplitude,
        "selected_epsilon": str(Fraction(best_amplitude, SCALE)),
        "numerator": best_total, "normalization": normalization,
        "density": str(best_density), "decimal": float(best_density),
        "delta_numerator_from_parent_lift": best_total - sample_counts[0],
        "red": red, "blue": blue, "direct_total": direct_total,
        "tiny_oracle": tiny,
        "candidate_sha256": hashlib.sha256((out / "graphon-candidate.json").read_bytes()).hexdigest(),
        "checker_sha256": hashlib.sha256(checker.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "seconds": time.monotonic() - started,
        "evidence": "Tiny literal polynomial oracle; exact U256 counts at seven interpolation points; exact zero-amplitude parent reproduction; exact direct U256 recount of selected candidate",
        "scope": "Common amplitude on the actual canonical pair-density direction only; precision-lane independent recount required before promotion",
    }
    write_json(out / "report.json", report)
    print(json.dumps({k: report[k] for k in (
        "feasible_amplitudes", "selected_amplitude", "selected_epsilon",
        "density", "decimal", "delta_numerator_from_parent_lift", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
