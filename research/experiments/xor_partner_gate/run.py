"""Exact profile and small-bank gate for heterogeneous XOR partners of e26."""
import argparse
import hashlib
import json
import subprocess
import time
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from research.experiments.structural.profiles import CLASSES, graph_from_mask, nested_limit, profile

ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
GENERATORS = ROOT / "reports/group-recovery-orbitals-001/generators.json"
SOURCE = Path(__file__).with_name("profile.cpp")


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_transitivity(matrix):
    data = json.loads(GENERATORS.read_text())
    generators = data["point_stabilizer_generators"] + data["transitive_movers"]
    n = len(matrix)
    for perm in generators:
        if sorted(perm) != list(range(n)):
            raise ValueError("stored action is not a permutation")
        if any(matrix[perm[i]][perm[j]] != matrix[i][j]
               for i in range(n) for j in range(n)):
            raise ValueError("stored action does not preserve parent")
    # The three root movers together with the point stabilizer generate the
    # transitive group; they are not a 192-element transversal themselves.
    orbit = {0}
    frontier = [0]
    while frontier:
        x = frontier.pop()
        for perm in generators:
            y = perm[x]
            if y not in orbit:
                orbit.add(y)
                frontier.append(y)
    if orbit != set(range(n)):
        raise ValueError("stored generators do not act transitively")
    return len(generators)


def exact_parent_profile(binary, matrix, q):
    n = len(matrix)
    payload = f"{n} {q}\n" + "\n".join(" ".join(map(str, row)) for row in matrix) + "\n"
    lines = subprocess.check_output([str(binary)], input=payload, text=True).splitlines()
    denominator = int(lines[0].split()[1])
    numerators = [0] * 64
    for line in lines[1:]:
        _, mask, value = line.split()
        numerators[int(mask)] = int(value)
    if sum(numerators) != denominator:
        raise AssertionError("profile does not normalize")
    # Exchangeability: all labeled masks in an isomorphism orbit must agree.
    for orbit in CLASSES:
        if len({numerators[m] for m in orbit}) != 1:
            raise AssertionError("profile is not exchangeable")
    return numerators, denominator


def xor_value(g_num, g_den, h_num):
    h_den = sum(h_num)
    num = sum(g_num[s] * (h_num[s] + h_num[63 ^ s]) for s in range(64))
    return Fraction(num, g_den * h_den)


def unique_finite_profiles(n):
    found = {}
    for mask in range(1 << (n * (n - 1) // 2)):
        raw = profile(graph_from_mask(n, mask))
        p = tuple(Fraction(x, sum(raw)) for x in raw)
        found.setdefault(p, {"kind": "finite", "order": n, "mask": mask})
    return found


def bank_gate(g_num, g_den, competitive_bound):
    bank = {}
    for n in range(2, 6):
        bank.update(unique_finite_profiles(n))
    # Existing exact recursive bank, represented once per distinct profile.
    for mask in range(1 << 10):
        rows = graph_from_mask(5, mask)
        p = nested_limit(rows)
        bank.setdefault(p, {"kind": "nested_limit", "order": 5, "mask": mask})
    records = []
    for p, descriptor in bank.items():
        value = xor_value(g_num, g_den, p)
        records.append((value, descriptor, Fraction(p[0] + p[63], sum(p))))
    records.sort(key=lambda x: x[0])
    competitive = [r for r in records if r[2] <= competitive_bound]
    near = [r for r in records if r[2] <= Fraction(31, 1000)]
    return len(bank), records[:10], competitive[:10], near[:10]


def solve_square(a, b):
    n = len(b)
    rows = [[Fraction(x) for x in a[i]] + [Fraction(b[i])] for i in range(n)]
    for col in range(n):
        pivot = next((r for r in range(col, n) if rows[r][col]), None)
        if pivot is None:
            return None
        rows[col], rows[pivot] = rows[pivot], rows[col]
        scale = rows[col][col]
        rows[col] = [x / scale for x in rows[col]]
        for r in range(n):
            if r == col:
                continue
            scale = rows[r][col]
            rows[r] = [x - scale * y for x, y in zip(rows[r], rows[col])]
    return [row[-1] for row in rows]


def weak_outer_lp(g_num, g_den, competitive_bound):
    """Weak outer relaxation of the requested two-competitive-factor subclass."""
    coeff = []
    mono_tri = []
    mono4 = []
    for orbit in CLASSES:
        rep = orbit[0]
        comp = 63 ^ rep
        coeff.append(Fraction(g_num[rep] + g_num[comp], g_den))
        triangles = [(0,1,3), (0,2,4), (1,2,5), (3,4,5)]
        count = sum(all(((rep >> e) & 1) == color for e in tri)
                    for tri in triangles for color in (0, 1))
        mono_tri.append(Fraction(count, 4))
        mono4.append(int(rep in (0, 63)))
    best = None
    # With normalization plus two optional inequalities, every vertex has at
    # most three positive coordinates. Enumerate exact rational basic solutions.
    optional = [(mono_tri, Fraction(1, 4)), (mono4, competitive_bound)]
    for support_size in range(1, 4):
        for support in combinations(range(len(CLASSES)), support_size):
            for active in combinations(range(2), support_size - 1):
                rows = [[Fraction(1)] * support_size]
                rhs = [Fraction(1)]
                for constraint in active:
                    vector, value = optional[constraint]
                    rows.append([vector[i] for i in support])
                    rhs.append(value)
                x = solve_square(rows, rhs)
                if x is None or any(v < 0 for v in x):
                    continue
                full = [Fraction(0)] * len(CLASSES)
                for i, v in zip(support, x):
                    full[i] = v
                if sum(a*b for a, b in zip(mono_tri, full)) < Fraction(1, 4):
                    continue
                if sum(a*b for a, b in zip(mono4, full)) > competitive_bound:
                    continue
                objective = sum(a*b for a, b in zip(coeff, full))
                if best is None or objective < best[0]:
                    best = (objective, full)
    assert best is not None
    return {"status": "exact_vertex_enumeration", "success": True,
            "lower_bound": str(best[0]), "lower_bound_float": float(best[0]),
            "nonzero_orbits": [{"representative": CLASSES[i][0], "mass": str(v)}
                               for i, v in enumerate(best[1]) if v],
            "constraints": ["nonnegative", "sum=1", "Goodman mono-triangle>=1/4",
                            "voluntary scope: partner standalone monochromatic K4<=current incumbent"],
            "warning": "This is an outer relaxation only of the requested two-competitive-factor subclass, not of every possible XOR partner; its constraints are far from a characterization of graphon 4-profiles."}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    started = time.monotonic()
    parent = json.loads(PARENT.read_text())
    matrix = parent["red_probability_numerators"]
    q = parent["edge_probability_denominator"]
    generator_count = validate_transitivity(matrix)
    args.out.mkdir(parents=True)
    binary = args.out / "profile"
    subprocess.run(["c++", "-O3", "-std=c++17", str(SOURCE), "-o", str(binary)], check=True)
    compiled = time.monotonic()
    g_num, g_den = exact_parent_profile(binary, matrix, q)
    profiled = time.monotonic()
    orbit_profile = []
    for orbit in CLASSES:
        orbit_profile.append({"representative": orbit[0], "orbit_size": len(orbit),
                              "numerator_total": sum(g_num[m] for m in orbit),
                              "denominator": g_den})
    incumbent = Fraction(16900934504649027287619486865996291,
                         560768060721761383881293603555770368)
    bank_count, best, competitive, near = bank_gate(g_num, g_den, incumbent)
    banked = time.monotonic()
    answer = {
        "schema": "heterogeneous-xor-partner-gate-v1",
        "scope": "exact e26 induced-4 profile, archived small feasible partner bank, weak LP outer gate",
        "coverage": "reviewed prior repo XOR screens used only small factors or fixed K4xM4; no e26-optimized partner appears in those screens",
        "parent": str(PARENT.relative_to(ROOT)), "parent_sha256": sha(PARENT),
        "probability_denominator": q, "parent_order": len(matrix),
        "transitivity_generators_checked": generator_count,
        "profile_denominator": g_den, "unlabeled_profile": orbit_profile,
        "parent_monochromatic_density": str(Fraction(g_num[0] + g_num[63], g_den)),
        "self_xor_density": str(xor_value(g_num, g_den, g_num)),
        "self_xor_cauchy_floor": "1/32",
        "small_bank_profiles": bank_count,
        "small_bank_best": [{"xor_density": str(v), "partner": d,
                             "partner_monochromatic_density": str(m)} for v, d, m in best],
        "small_bank_partner_standalone_at_most_incumbent_count": len(competitive),
        "small_bank_best_with_partner_standalone_at_most_0.031": [
            {"xor_density": str(v), "partner": d,
             "partner_monochromatic_density": str(m)} for v, d, m in near],
        "weak_outer_lp": weak_outer_lp(g_num, g_den, incumbent),
        "decision_rule": "Ask before a continuous partner optimizer only if the feasible bank or outer gate is plausibly competitive.",
        "timing_seconds": {"compile": compiled-started, "profile": profiled-compiled,
                           "bank": banked-profiled, "total": time.monotonic()-started},
        "source_hashes": {str(SOURCE.relative_to(ROOT)): sha(SOURCE),
                          str(Path(__file__).relative_to(ROOT)): sha(Path(__file__)),
                          str(GENERATORS.relative_to(ROOT)): sha(GENERATORS)},
        "evidence_limit": "Development exact arithmetic, not independent verification; LP is only a weak outer relaxation of the stated two-competitive-factor subclass.",
    }
    (args.out / "report.json").write_text(json.dumps(answer, indent=2) + "\n")
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    main()
