"""One-job exact screen of a three-state Potts latent graphon refinement."""

from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import time

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


HERE = ROOT / "experiments/correlated_graphon"
OUT = ROOT / "reports/correlated-graphon-potts-001"
PARENT = ROOT / "reports/literature-simple-graphon-001"


def expand(base, den, q):
    n = len(base)
    return [[
        base[ia // 3][jb // 3]
        + (q * (2 if ia % 3 == jb % 3 else -1)
           if ia // 3 != jb // 3 and 0 < base[ia // 3][jb // 3] < den else 0)
        for jb in range(3*n)
    ] for ia in range(3*n)]


def literal(matrix, den):
    total = 0
    for vertices in product(range(len(matrix)), repeat=4):
        red = blue = 1
        for u, v in combinations(range(4), 2):
            value = matrix[vertices[u]][vertices[v]]
            red *= value
            blue *= den - value
        total += red + blue
    return Fraction(total, len(matrix)**4 * den**6)


def feasible_interval(base, den):
    lo, hi = -den, den
    for i, row in enumerate(base):
        for j, p in enumerate(row[:i]):
            if not 0 < p < den:
                continue
            valid = [q for q in range(-den, den + 1)
                     if 0 <= p + 2*q <= den and 0 <= p - q <= den]
            lo, hi = max(lo, min(valid)), min(hi, max(valid))
    return lo, hi


def candidate_data(base, den, q):
    matrix = expand(base, den, q)
    return {
        "schema": "rational-step-graphon-v1",
        "block_weights": [1] * len(matrix),
        "edge_probability_denominator": den,
        "red_probability_numerators": matrix,
    }


def main():
    start = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(HERE / "potts_counter.cpp", OUT / "counter_snapshot.cpp")

    parent_bytes = (PARENT / "graphon-candidate.json").read_bytes()
    parent = json.loads(parent_bytes)
    parent_report = json.loads((PARENT / "report.json").read_text())
    base = parent["red_probability_numerators"]
    den = parent["edge_probability_denominator"]
    n = len(base)
    assert parent["block_weights"] == [1] * n
    assert all(base[i][j] == base[j][i] for i in range(n) for j in range(n))
    assert all(base[i][i] == 0 for i in range(n))

    # Semantics/correctness tests happen before the sole large counter job.
    # Every refined coarse block has the same average numerator as its parent.
    for q in (-1, 1):
        tiny = [[0, 2, 3], [2, 0, 2], [3, 2, 0]]
        refined = expand(tiny, 5, q)
        assert all(0 <= x <= 5 for row in refined for x in row)
        for i in range(3):
            for j in range(3):
                assert sum(refined[3*i+a][3*j+b] for a in range(3) for b in range(3)) == 9*tiny[i][j]
        # This literal test includes repeated coarse indices and independently
        # sampled latent indices in all four ordered positions.
        assert literal(refined, 5) >= 0

    lo, hi = feasible_interval(base, den)
    assert (lo, hi) == (-9, 4), (lo, hi)
    maximum = 2 * (3*n)**4 * den**6
    assert maximum < 2**127

    binary = OUT / "potts_counter"
    compile_command = ["clang++", "-O3", "-std=c++17", str(HERE / "potts_counter.cpp"), "-o", str(binary)]
    subprocess.run(compile_command, check=True, timeout=60)
    payload = f"{n} {den}\n" + "\n".join(" ".join(map(str, row)) for row in base) + "\n"
    run_start = time.monotonic()
    proc = subprocess.run([str(binary)], input=payload, text=True, capture_output=True, check=True, timeout=900)
    run_seconds = time.monotonic() - run_start
    rows = []
    normalization = (3*n)**4 * den**6
    for line in proc.stdout.splitlines():
        q, red, blue, total = map(int, line.split())
        rows.append({"q": q, "epsilon": str(Fraction(q, den)), "red": red,
                     "blue": blue, "numerator": total,
                     "density": str(Fraction(total, normalization))})
    assert [row["q"] for row in rows] == list(range(lo, hi + 1))
    baseline = Fraction(parent_report["density"])
    zero = next(row for row in rows if row["q"] == 0)
    assert Fraction(zero["density"]) == baseline
    best = min(rows, key=lambda row: Fraction(row["density"]))

    candidate = candidate_data(base, den, best["q"])
    write_json(OUT / "graphon-candidate.json", candidate)
    report = {
        "schema": "correlated-graphon-screen-v1",
        "status": "completed",
        "hypothesis": "H-CG-1: a centered three-state Potts latent type improves the simple two-parameter graphon",
        "mechanism": "Each coarse class is split into three equal latent types; fractional blocks use p+q*(2 if latent types agree else -1)",
        "prediction": "Some feasible nonzero q has lower exact ordered K4 density than q=0",
        "cheapest_falsifier": "Exact evaluation of the complete integer feasibility interval q=-9..4 on the readable denominator-41 parent",
        "parent": str(PARENT.relative_to(ROOT)),
        "parent_candidate_sha256": hashlib.sha256(parent_bytes).hexdigest(),
        "base_order": n,
        "refined_order": 3*n,
        "probability_denominator": den,
        "kernel": [[2, -1, -1], [-1, 2, -1], [-1, -1, 2]],
        "kernel_rank": 2,
        "kernel_row_sums": [0, 0, 0],
        "feasible_q": [lo, hi],
        "baseline_density": str(baseline),
        "best": best,
        "improvement": str(baseline - Fraction(best["density"])),
        "supported": Fraction(best["density"]) < baseline and best["q"] != 0,
        "all_results": rows,
        "normalization": normalization,
        "candidate_sha256": hashlib.sha256((OUT / "graphon-candidate.json").read_bytes()).hexdigest(),
        "counter_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256((HERE / "potts_counter.cpp").read_bytes()).hexdigest(),
        "overflow_bound": str(maximum),
        "overflow_limit": str(2**127),
        "compile_command": compile_command,
        "run_command": [str(binary)],
        "machine": platform.platform(),
        "run_seconds": run_seconds,
        "total_seconds": time.monotonic() - start,
        "evidence": "Exact direct ordered-index C++128 screen by the search implementation; no independent recount or Lean certificate",
        "realization": "A deterministic 576-step graphon. In finite blow-ups, use equal fine classes and independently color every distinct vertex edge with its fine-block probability. Distinct edges remain independent conditional on vertex fine classes.",
        "repeated_class_semantics": "Four ordered graphon samples choose latent fine classes independently even when coarse indices coincide; the direct 576-index sum includes all such terms.",
        "scope": "A mechanism screen on the simple denominator-41 parent, not a record, novelty, or optimality claim.",
    }
    write_json(OUT / "report.json", report)
    print(json.dumps({key: report[key] for key in ("status", "supported", "baseline_density", "best", "improvement", "run_seconds")}, indent=2))


if __name__ == "__main__":
    main()
