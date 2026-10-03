"""Diagonal-inclusive exact boundary-face lines on the 192-class graphon.

This is the scope-corrected companion to coarse_face.py.  It treats the 192
positive-measure diagonal blocks as graphon coordinates rather than fixing
them to zero.
"""
import collections
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import time

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


class Counter:
    def __init__(self, binary, classes, k):
        self.p = subprocess.Popen([str(binary)], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True)
        self.p.stdin.write(f"{len(classes)} {k}\n" +
                           "\n".join(" ".join(map(str, row)) for row in classes) + "\n")
        self.p.stdin.flush()

    def __call__(self, denominator, parameters):
        self.p.stdin.write(" ".join(map(str, [denominator, *parameters])) + "\n")
        self.p.stdin.flush()
        return int(self.p.stdout.readline())

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


def main():
    start = time.monotonic()
    out = ROOT / "reports/finite-joint-coarse-face-diagonal-001"
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, out / "source_snapshot.py")
    parent_path = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
    parent = json.loads(parent_path.read_text())
    matrix = parent["red_probability_numerators"]
    q = parent["edge_probability_denominator"]
    n = len(matrix)

    # Recompute the analytic derivative so diagonal coordinates are retained.
    gradient_binary = ROOT / "reports/literature-graphon-gradient-001/gradient"
    payload = str(n) + "\n" + "\n".join(
        " ".join(str(x / q) for x in row) for row in matrix) + "\n"
    gradient_text = subprocess.check_output(
        [str(gradient_binary)], input=payload, text=True, timeout=30)
    lookup = {}
    for line in gradient_text.splitlines():
        i, j, gradient = line.split()
        i, j = int(i), int(j)
        lookup[(i, j)] = {
            "i": i, "j": j, "numerator": matrix[i][j],
            "probability": matrix[i][j] / q, "gradient": float(gradient),
        }

    keys = {}
    initial = []
    classes = [[-1] * n for _ in range(n)]
    cells_by_class = collections.defaultdict(list)
    for i in range(n):
        for j in range(i + 1):
            record = lookup[(i, j)]
            key = (record["numerator"], round(record["gradient"], 8))
            if key not in keys:
                keys[key] = len(keys)
                initial.append(record["numerator"])
            c = keys[key]
            classes[i][j] = classes[j][i] = c
            cells_by_class[c].append((i, j))
    k = len(keys)
    class_counter = ROOT / "reports/literature-class-graphon-001/counter"
    counter = Counter(class_counter, classes, k)
    denominator = q ** 6 * n ** 4
    baseline = counter(q, initial)
    expected = Fraction(json.loads(
        (ROOT / "reports/literature-two-parameter-001/report.json").read_text())["density"])
    if Fraction(baseline, denominator) != expected:
        raise RuntimeError("diagonal-inclusive class counter does not reproduce parent")

    # Degree is the number of cells of this class in each matrix row.  A
    # diagonal cell contributes once; an off-diagonal cell contributes once
    # at each endpoint.  Uniform degree makes the paired lines exactly
    # row-sum preserving.
    degrees = {}
    for c, cells in cells_by_class.items():
        ds = [0] * n
        for i, j in cells:
            ds[i] += 1
            if i != j:
                ds[j] += 1
        if len(set(ds)) != 1:
            raise RuntimeError(f"gradient class {c} is not regular")
        degrees[c] = ds[0]

    zeros = [c for c, x in enumerate(initial) if x == 0]
    ones = [c for c, x in enumerate(initial) if x == q]
    proposals = []
    for c in zeros + ones:
        direction = [0] * k
        direction[c] = 1 if c in zeros else -1
        proposals.append(("single_boundary_orbit", [c], direction, q))
    for z in zeros:
        for o in ones:
            g = math.gcd(degrees[z], degrees[o])
            az, ao = degrees[o] // g, degrees[z] // g
            direction = [0] * k
            direction[z], direction[o] = az, -ao
            maximum = min(q // az, q // ao)
            proposals.append(("row_sum_preserving_pair", [z, o], direction, maximum))

    trials = []
    best = (baseline, list(initial), {"family": "parent", "step": 0})
    for family, selected, direction, maximum in proposals:
        points = sorted(set(round(maximum * i / 16) for i in range(17)))
        local = []
        for step in points:
            parameters = [x + step * d for x, d in zip(initial, direction)]
            if any(x < 0 or x > q for x in parameters):
                raise RuntimeError("line left box")
            value = counter(q, parameters)
            record = {"family": family, "classes": selected, "step": step,
                      "maximum": maximum, "numerator": value,
                      "delta": value - baseline}
            trials.append(record)
            local.append((value, step, parameters))
            if value < best[0]:
                best = (value, parameters, record)
        _, step, parameters = min(local)
        stride = max(1, maximum // 32)
        while stride:
            candidates = []
            for s in sorted(set((max(0, step - stride), step,
                                 min(maximum, step + stride)))):
                ps = [x + s * d for x, d in zip(initial, direction)]
                value = counter(q, ps)
                candidates.append((value, s, ps))
                record = {"family": family, "classes": selected, "step": s,
                          "maximum": maximum, "numerator": value,
                          "delta": value - baseline, "refinement": True}
                trials.append(record)
                if value < best[0]:
                    best = (value, ps, record)
            _, step, parameters = min(candidates)
            stride //= 2
    counter.close()

    best_value, best_parameters, descriptor = best
    best_matrix = [[best_parameters[classes[i][j]] for j in range(n)]
                   for i in range(n)]
    candidate = dict(parent, red_probability_numerators=best_matrix)
    write_json(out / "graphon-candidate.json", candidate)
    ordered = ROOT / "reports/literature-two-parameter-001/ordered_counter"
    payload = f"{n} {q}\n" + "\n".join(
        " ".join(map(str, row)) for row in best_matrix) + "\n"
    red, blue, ordered_total = map(int, subprocess.check_output(
        [str(ordered)], input=payload, text=True, timeout=40).split())
    if ordered_total != best_value:
        raise RuntimeError("independent ordered recount mismatch")

    diagonal_classes = sorted({classes[i][i] for i in range(n)})
    violations = []
    for (i, j), record in lookup.items():
        value, gradient = record["numerator"], record["gradient"]
        if ((value == 0 and gradient < -1e-8) or
                (value == q and gradient > 1e-8)):
            violations.append(record)
    candidate_hash = hashlib.sha256(
        (out / "graphon-candidate.json").read_bytes()).hexdigest()
    report = {
        "hypothesis": "H-FJ-006-diagonal-inclusive-boundary-face",
        "parent": str(parent_path),
        "parent_sha256": hashlib.sha256(parent_path.read_bytes()).hexdigest(),
        "baseline_numerator": baseline,
        "numerator": best_value,
        "denominator": denominator,
        "density": str(Fraction(best_value, denominator)),
        "decimal": float(Fraction(best_value, denominator)),
        "delta": best_value - baseline,
        "best_descriptor": descriptor,
        "best_parameters": best_parameters,
        "symmetric_coordinates": n * (n + 1) // 2,
        "diagonal_coordinates": n,
        "diagonal_classes": diagonal_classes,
        "box_kkt_violations": len(violations),
        "strongest_box_kkt_violations": sorted(
            violations, key=lambda r: -abs(r["gradient"]))[:50],
        "class_keys": [{"numerator": key[0], "gradient": key[1],
                        "class": c, "degree": degrees[c],
                        "cell_count": len(cells_by_class[c]),
                        "diagonal_cells": sum(i == j for i, j in cells_by_class[c])}
                       for key, c in keys.items()],
        "proposal_count": len(proposals),
        "trial_count": len(trials),
        "candidate_sha256": candidate_hash,
        "gradient_binary_sha256": hashlib.sha256(gradient_binary.read_bytes()).hexdigest(),
        "partition_counter_sha256": hashlib.sha256(class_counter.read_bytes()).hexdigest(),
        "ordered_counter_sha256": hashlib.sha256(ordered.read_bytes()).hexdigest(),
        "ordered_red": red,
        "ordered_blue": blue,
        "seconds": time.monotonic() - start,
        "evidence": "Double analytic KKT guide; exact C++128 partition search; retained matrix independently recounted by direct ordered-index C++128 counter",
        "scope": "All18528 symmetric means receive a KKT-sign check; exact line search covers every regular gradient orbit singly and every zero/one regular-orbit row-sum-preserving pair, including the192 diagonal means as one symmetry orbit",
    }
    write_json(out / "gradients.json", list(lookup.values()))
    write_json(out / "trials.json", trials)
    write_json(out / "report.json", report)
    print(json.dumps({k: report[k] for k in (
        "numerator", "density", "decimal", "delta", "best_descriptor",
        "box_kkt_violations", "proposal_count", "trial_count", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
