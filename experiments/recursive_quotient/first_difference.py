"""Exact first-difference recursion for rational step quotients."""
from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
import math
from pathlib import Path
import shutil
import subprocess
import time

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


HERE = Path(__file__).resolve().parent


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def generic_fixed_point(matrix, q, maximum=4):
    """Literal equality-partition recurrence, only for tiny controls."""
    b = len(matrix)
    result = {"red": [Fraction(0), Fraction(1)],
              "blue": [Fraction(0), Fraction(1)]}
    for color in ("red", "blue"):
        a = [[Fraction(0) if i == j else
              Fraction(matrix[i][j] if color == "red" else q - matrix[i][j], q)
              for j in range(b)] for i in range(b)]
        for t in range(2, maximum + 1):
            numerator = Fraction(0)
            for labels in product(range(b), repeat=t):
                if len(set(labels)) == 1:
                    continue
                term = Fraction(1)
                fibers = {}
                for position, label in enumerate(labels):
                    fibers.setdefault(label, []).append(position)
                for i, j in combinations(range(t), 2):
                    if labels[i] != labels[j]:
                        term *= a[labels[i]][labels[j]]
                for positions in fibers.values():
                    if len(positions) >= 2:
                        term *= result[color][len(positions)]
                numerator += term
            result[color].append(numerator / (b**t - b))
    return result


def formula_recurrence(terms, b, q):
    s1, s2, s3, s4, triangle, paired, clique4 = terms
    t2 = Fraction(s1, q * (b**2 - b))
    triangle_term = Fraction(triangle, q**3)
    pair21_term = 3 * t2 * Fraction(s2, q**2)
    t3 = (triangle_term + pair21_term) / (b**3 - b)
    distinct4 = Fraction(clique4, q**6)
    pair211 = 6 * t2 * Fraction(paired, q**5)
    pair22 = 3 * t2**2 * Fraction(s4, q**4)
    triple31 = 4 * t3 * Fraction(s3, q**3)
    t4 = (distinct4 + pair211 + pair22 + triple31) / (b**4 - b)
    return {
        "T2": t2, "T3": t3, "T4": t4,
        "T3_terms": {"111": triangle_term, "21": pair21_term},
        "T4_terms": {"1111": distinct4, "211": pair211,
                     "22": pair22, "31": triple31},
    }


def brute_terms(matrix, q, color):
    b = len(matrix)
    a = [[0 if i == j else (matrix[i][j] if color == "red" else q - matrix[i][j])
          for j in range(b)] for i in range(b)]
    s = [sum(a[i][j]**degree for i in range(b) for j in range(b) if i != j)
         for degree in range(1, 5)]
    triangle = sum(a[i][j]*a[i][k]*a[j][k]
                   for i, j, k in product(range(b), repeat=3)
                   if len({i, j, k}) == 3)
    paired = sum(a[i][j]**2*a[i][k]**2*a[j][k]
                 for i, j, k in product(range(b), repeat=3)
                 if len({i, j, k}) == 3)
    clique4 = sum(a[i][j]*a[i][k]*a[i][l]*a[j][k]*a[j][l]*a[k][l]
                  for i, j, k, l in product(range(b), repeat=4)
                  if len({i, j, k, l}) == 4)
    return [*s, triangle, paired, clique4]


def materialize_depth(matrix, q, depth, terminal_red):
    b = len(matrix)
    words = list(product(range(b), repeat=depth))
    result = [[0] * len(words) for _ in words]
    for i, left in enumerate(words):
        for j in range(i + 1):
            right = words[j]
            value = terminal_red * q
            for x, y in zip(left, right):
                if x != y:
                    value = matrix[x][y]
                    break
            result[i][j] = result[j][i] = value
    return result


def literal_profile(matrix, q, maximum=4):
    n = len(matrix)
    answer = {"red": [Fraction(0), Fraction(1)],
              "blue": [Fraction(0), Fraction(1)]}
    for color in ("red", "blue"):
        a = matrix if color == "red" else [[q - x for x in row] for row in matrix]
        for t in range(2, maximum + 1):
            total = 0
            for vertices in product(range(n), repeat=t):
                term = 1
                for i, j in combinations(range(t), 2):
                    term *= a[vertices[i]][vertices[j]]
                total += term
            answer[color].append(Fraction(total, n**t * q**math.comb(t, 2)))
    return answer


def one_depth_update(matrix, q, previous, maximum=4):
    b = len(matrix)
    result = {"red": [Fraction(0), Fraction(1)],
              "blue": [Fraction(0), Fraction(1)]}
    for color in ("red", "blue"):
        a = [[Fraction(0) if i == j else
              Fraction(matrix[i][j] if color == "red" else q - matrix[i][j], q)
              for j in range(b)] for i in range(b)]
        for t in range(2, maximum + 1):
            total = Fraction(0)
            for labels in product(range(b), repeat=t):
                term = Fraction(1)
                fibers = {}
                for position, label in enumerate(labels):
                    fibers.setdefault(label, []).append(position)
                for i, j in combinations(range(t), 2):
                    if labels[i] != labels[j]:
                        term *= a[labels[i]][labels[j]]
                for positions in fibers.values():
                    if len(positions) >= 2:
                        term *= previous[color][len(positions)]
                total += term
            result[color].append(total / b**t)
    return result


def tiny_controls(binary):
    fixtures = [([[0, 2], [2, 0]], 5),
                ([[0, 2, 5], [2, 0, 3], [5, 3, 0]], 7)]
    records = []
    for matrix, q in fixtures:
        b = len(matrix)
        payload = f"{b} {q}\n" + "\n".join(" ".join(map(str, row)) for row in matrix) + "\n"
        lines = subprocess.check_output([str(binary)], input=payload, text=True, timeout=10).splitlines()
        native = {color: list(map(int, line.split()))
                  for color, line in zip(("red", "blue"), lines)}
        for color in ("red", "blue"):
            expected = brute_terms(matrix, q, color)
            if native[color] != expected:
                raise RuntimeError("native equality term mismatch")
        fixed_generic = generic_fixed_point(matrix, q)
        fixed_formula = {color: formula_recurrence(native[color], b, q)
                         for color in ("red", "blue")}
        for color in ("red", "blue"):
            for t in range(2, 5):
                if fixed_formula[color][f"T{t}"] != fixed_generic[color][t]:
                    raise RuntimeError("closed recurrence disagrees with generic recurrence")
        for terminal_red in (0, 1):
            previous = {
                "red": [Fraction(0), Fraction(1)] + [Fraction(terminal_red)] * 3,
                "blue": [Fraction(0), Fraction(1)] + [Fraction(1-terminal_red)] * 3,
            }
            for depth in range(1, 4):
                previous = one_depth_update(matrix, q, previous)
                literal = literal_profile(materialize_depth(matrix, q, depth, terminal_red), q)
                if previous != literal:
                    raise RuntimeError("finite-depth materialization disagrees with recurrence")
            records.append({
                "B": b, "Q": q, "terminal_red": terminal_red, "depth": 3,
                "T4_red": str(previous["red"][4]),
                "T4_blue": str(previous["blue"][4]),
                "fixed_T4_red": str(fixed_generic["red"][4]),
                "fixed_T4_blue": str(fixed_generic["blue"][4]),
                "union_bound_depth3": str(Fraction(math.comb(4, 2), b**3)),
            })
    return records


def evaluate_parent(directory, binary):
    candidate_path = directory / "graphon-candidate.json"
    report_path = directory / "report.json"
    candidate = json.loads(candidate_path.read_text())
    report = json.loads(report_path.read_text())
    matrix = candidate["red_probability_numerators"]
    q = candidate["edge_probability_denominator"]
    b = len(matrix)
    payload = f"{b} {q}\n" + "\n".join(" ".join(map(str, row)) for row in matrix) + "\n"
    lines = subprocess.check_output([str(binary)], input=payload, text=True, timeout=120).splitlines()
    terms = {color: list(map(int, line.split()))
             for color, line in zip(("red", "blue"), lines)}
    solved = {color: formula_recurrence(terms[color], b, q)
              for color in ("red", "blue")}
    nested = solved["red"]["T4"] + solved["blue"]["T4"]
    ordinary = Fraction(report["density"])
    return {
        "directory": str(directory), "candidate_sha256": sha256(candidate_path),
        "B": b, "Q": q, "ordinary_density": str(ordinary),
        "ordinary_decimal": float(ordinary), "nested_density": str(nested),
        "nested_decimal": float(nested), "delta_nested_minus_ordinary": str(nested - ordinary),
        "improves_parent": nested < ordinary,
        "improves_global_checked_reference": nested < Fraction("0.03013890356539909"),
        "colors": {
            color: {
                "terms": terms[color],
                "T2": str(solved[color]["T2"]),
                "T3": str(solved[color]["T3"]),
                "T4": str(solved[color]["T4"]),
                "T3_terms": {k: str(v) for k, v in solved[color]["T3_terms"].items()},
                "T4_terms": {k: str(v) for k, v in solved[color]["T4_terms"].items()},
            } for color in ("red", "blue")
        },
    }


def main():
    started = time.monotonic()
    out = ROOT / "reports/recursive-quotient-first-difference-001"
    out.mkdir(parents=True, exist_ok=False)
    source = HERE / "first_difference_terms.cpp"
    shutil.copy2(__file__, out / "driver_snapshot.py")
    shutil.copy2(source, out / "counter_snapshot.cpp")
    shutil.copy2(ROOT / "research/theory-directions-round3.md", out / "formal_derivation_snapshot.md")
    binary = out / "terms"
    subprocess.run(["/usr/bin/clang++", "-O3", "-std=c++17", str(source), "-o", str(binary)],
                   check=True, timeout=60)
    controls = tiny_controls(binary)
    parents = [
        ROOT / "reports/literature-simple-graphon-001",
        ROOT / "reports/literature-two-parameter-001",
    ]
    results = [evaluate_parent(parent, binary) for parent in parents]
    report = {
        "hypothesis": "H-TR3-1 homogeneous first-difference recursion",
        "prediction": "Nested density is below the ordinary step density of the same quotient",
        "formula": {
            "T2": "S1/(B^2-B)",
            "T3": "(S111+3*T2*S2)/(B^3-B)",
            "T4": "(S1111+6*T2*S211+3*T2^2*S4+4*T3*S3)/(B^4-B)",
        },
        "tiny_controls": controls,
        "results": results,
        "global_checked_reference": "0.03013890356539909",
        "counter_sha256": sha256(binary), "counter_source_sha256": sha256(source),
        "driver_source_sha256": sha256(Path(__file__)),
        "seconds": time.monotonic() - started,
        "evidence": "Exact U128 ordered equality-term enumeration; Fraction recurrence; native terms checked against literal tiny enumeration; finite-depth recurrence checked against literal depth1-3 materializations",
        "scope": "Homogeneous first-difference recursion for the two tested rational192 quotients; not typed or alternating recursion",
    }
    write_json(out / "report.json", report)
    print(json.dumps({"seconds": report["seconds"], "results": [{
        k: result[k] for k in ("directory", "ordinary_decimal", "nested_decimal",
                               "improves_parent", "improves_global_checked_reference")}
        for result in results]}, indent=2))


if __name__ == "__main__":
    main()
