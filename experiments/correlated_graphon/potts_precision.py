"""One bounded two-phase job for Potts refinement of the strongest graphon."""

from fractions import Fraction
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
OUT = ROOT / "reports/correlated-graphon-potts-precision-003"
PARENT = ROOT / "reports/literature-two-parameter-001"


def expand(base, den, q):
    n = len(base)
    return [[base[ia//3][jb//3] + (
        q*(2 if ia%3 == jb%3 else -1)
        if ia//3 != jb//3 and 0 < base[ia//3][jb//3] < den else 0)
        for jb in range(3*n)] for ia in range(3*n)]


def interpolate(points):
    """Power-basis polynomial through exact integer points, low degree first."""
    xs = [Fraction(x) for x, _ in points]
    dd = [Fraction(y) for _, y in points]
    newton = []
    for k in range(len(points)):
        newton.append(dd[0])
        dd = [(dd[i+1]-dd[i])/(xs[i+k+1]-xs[i]) for i in range(len(dd)-1)]
    power = [Fraction(0)]
    basis = [Fraction(1)]
    for k, coefficient in enumerate(newton):
        if len(power) < len(basis):
            power += [Fraction(0)]*(len(basis)-len(power))
        for i, value in enumerate(basis):
            power[i] += coefficient*value
        if k+1 < len(newton):
            nxt = [Fraction(0)]*(len(basis)+1)
            for i, value in enumerate(basis):
                nxt[i] -= xs[k]*value
                nxt[i+1] += value
            basis = nxt
    return power


def evaluate(coefficients, q):
    answer = Fraction(0)
    for coefficient in reversed(coefficients):
        answer = answer*q + coefficient
    return answer


def derivative_sign(coefficients, q):
    return evaluate([k*coefficients[k] for k in range(1, len(coefficients))], q)


def feasible_interval(base, den):
    valid = []
    for q in range(-den, den+1):
        if all(not (0 < base[i][j] < den) or
               (0 <= base[i][j]+2*q <= den and 0 <= base[i][j]-q <= den)
               for i in range(len(base)) for j in range(i)):
            valid.append(q)
    return min(valid), max(valid)


def run_counter(binary, base, den, qs, timeout):
    payload = f"{len(base)} {den} {len(qs)}\n" + " ".join(map(str, qs)) + "\n"
    payload += "\n".join(" ".join(map(str, row)) for row in base) + "\n"
    proc = subprocess.run([str(binary)], input=payload, text=True,
                          capture_output=True, check=True, timeout=timeout)
    rows = []
    for line in proc.stdout.splitlines():
        q, red, blue, total = map(int, line.split())
        rows.append({"q": q, "red": red, "blue": blue, "numerator": total})
    assert [row["q"] for row in rows] == qs
    return rows


def main():
    start = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(HERE / "potts_precision_counter.cpp", OUT / "counter_snapshot.cpp")
    parent_bytes = (PARENT / "graphon-candidate.json").read_bytes()
    parent = json.loads(parent_bytes)
    parent_report = json.loads((PARENT / "report.json").read_text())
    base = parent["red_probability_numerators"]
    den = parent["edge_probability_denominator"]
    n = len(base)
    assert parent["block_weights"] == [1]*n
    assert all(base[i][j] == base[j][i] for i in range(n) for j in range(n))
    assert all(base[i][i] == 0 for i in range(n))
    lo, hi = feasible_interval(base, den)
    assert (lo, hi) == (-14472, 7236), (lo, hi)
    m = 3*n
    inner_bound = m*m*den**5
    assert inner_bound < 2**128
    global_bound = 2*m**4*den**6
    assert global_bound < 2**134 < 2**192

    binary = OUT / "potts_precision_counter"
    compile_command = ["clang++", "-O3", "-std=c++17", str(HERE/"potts_precision_counter.cpp"), "-o", str(binary)]
    subprocess.run(compile_command, check=True, timeout=60)

    calibration_q = [-6144, -4096, -2048, 0, 2048, 4096, 6144]
    phase1_start = time.monotonic()
    calibration = run_counter(binary, base, den, calibration_q, 600)
    phase1_seconds = time.monotonic()-phase1_start
    coefficients = interpolate([(row["q"], row["numerator"]) for row in calibration])
    assert all(value.denominator == 1 for value in coefficients)
    coefficients = [int(value) for value in coefficients]
    assert calibration[3]["numerator"] * den**0 == int(Fraction(parent_report["density"])*m**4*den**6)

    # Exact exhaustive polynomial scan is negligible and launches no counter.
    # Bracket derivative roots by exact signs, then preregister only root
    # neighbors, the exact discrete polynomial minimum, zero, and boundaries.
    stationary_brackets = []
    last_q, last_s = lo, derivative_sign(coefficients, lo)
    for q in range(lo+1, hi+1):
        s = derivative_sign(coefficients, q)
        if s == 0 or last_s == 0 or (s < 0 < last_s) or (last_s < 0 < s):
            stationary_brackets.append([last_q, q])
        last_q, last_s = q, s
    discrete_best = min(range(lo, hi+1), key=lambda q: evaluate(coefficients, q))
    candidates = {lo, hi, 0, discrete_best-1, discrete_best, discrete_best+1}
    for a, b in stationary_brackets:
        candidates.update((a-1, a, b, b+1))
    candidates = sorted(q for q in candidates if lo <= q <= hi)
    preregistration = {
        "schema": "potts-precision-preregistration-v1",
        "created_after_calibration_before_candidate_recounts": True,
        "calibration_q": calibration_q,
        "numerator_coefficients_low_to_high": [str(x) for x in coefficients],
        "stationary_integer_brackets": stationary_brackets,
        "polynomial_discrete_best": discrete_best,
        "candidate_q": candidates,
        "selection_rule": "all exact derivative sign-change/equality bracket neighbors, exact discrete minimum neighbors, q=0, and feasibility boundaries",
    }
    write_json(OUT/"preregistration.json", preregistration)

    phase2_start = time.monotonic()
    checks = run_counter(binary, base, den, candidates, 600)
    phase2_seconds = time.monotonic()-phase2_start
    for row in checks:
        assert row["numerator"] == evaluate(coefficients, row["q"])
    normalization = m**4*den**6
    best = min(checks, key=lambda row: row["numerator"])
    for row in calibration + checks:
        row["density"] = str(Fraction(row["numerator"], normalization))
    baseline = Fraction(parent_report["density"])
    best_density = Fraction(best["numerator"], normalization)

    candidate = {
        "schema": "rational-step-graphon-v1",
        "block_weights": [1]*m,
        "edge_probability_denominator": den,
        "red_probability_numerators": expand(base, den, best["q"]),
    }
    write_json(OUT/"graphon-candidate.json", candidate)
    report = {
        "schema": "correlated-graphon-screen-v1",
        "status": "completed",
        "hypothesis": "H-CG-2: validated rank-two Potts interaction transfers to the strongest precision parent",
        "parent": str(PARENT.relative_to(ROOT)),
        "parent_candidate_sha256": hashlib.sha256(parent_bytes).hexdigest(),
        "base_order": n,
        "refined_order": m,
        "probability_denominator": den,
        "feasible_q": [lo, hi],
        "calibration": calibration,
        "numerator_coefficients_low_to_high": [str(x) for x in coefficients],
        "stationary_integer_brackets": stationary_brackets,
        "preregistered_candidate_q": candidates,
        "candidate_recounts": checks,
        "baseline_density": str(baseline),
        "best": {**best, "epsilon": str(Fraction(best["q"], den)), "density": str(best_density)},
        "improvement": str(baseline-best_density),
        "supported": best_density < baseline and best["q"] != 0,
        "normalization": normalization,
        "candidate_sha256": hashlib.sha256((OUT/"graphon-candidate.json").read_bytes()).hexdigest(),
        "counter_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256((HERE/"potts_precision_counter.cpp").read_bytes()).hexdigest(),
        "inner_contraction_bound": str(inner_bound),
        "inner_contraction_limit": str(2**128),
        "global_total_bound": str(global_bound),
        "global_total_limit": str(2**192),
        "outer_accumulator": "checked 192-bit three-limb unsigned integer; global bound below 2^134",
        "tiny_falsifier": "Three embedded matrices compare optimized contraction with literal ordered quadruples before each phase",
        "compile_command": compile_command,
        "phase1_seconds": phase1_seconds,
        "phase2_seconds": phase2_seconds,
        "total_seconds": time.monotonic()-start,
        "machine": platform.platform(),
        "evidence": "Exact arbitrary-precision search counter with preregistered candidate recounts; not an independent audit or Lean certificate",
        "scope": "Transfer test on strongest known local precision parent; no recursion, record, novelty, or optimality claim",
    }
    write_json(OUT/"report.json", report)
    print(json.dumps({key: report[key] for key in ("status", "supported", "baseline_density", "best", "improvement", "phase1_seconds", "phase2_seconds")}, indent=2))


if __name__ == "__main__":
    main()
