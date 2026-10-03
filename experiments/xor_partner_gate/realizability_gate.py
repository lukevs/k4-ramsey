"""Continuous 11-profile outer gate with exact disjoint-edge realizability."""
import argparse
import hashlib
import json
import math
from fractions import Fraction
from itertools import combinations
from pathlib import Path

from experiments.structural.profiles import CLASSES
from experiments.xor_partner_gate.run import solve_square

ROOT = Path(__file__).resolve().parents[2]
PROFILE_REPORT = ROOT / "reports/xor-partner-e26-gate-005/report.json"
DISJOINT = ((0, 5), (1, 4), (2, 3))
TRIANGLES = ((0, 1, 3), (0, 2, 4), (1, 2, 5), (3, 4, 5))


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def add(p, q):
    return tuple(a + b for a, b in zip(p, q))


def scale(a, p):
    return tuple(a * x for x in p)


def polysum(items):
    result = (Fraction(0), Fraction(0), Fraction(0))
    for item in items:
        result = add(result, item)
    return result


def value(p, x):
    return float(p[0]) + float(p[1]) * x + float(p[2]) * x * x


def roots(p):
    a, b, c = map(float, p)
    if abs(c) < 1e-14:
        return [] if abs(b) < 1e-14 else [-a / b]
    disc = b*b - 4*a*c
    if disc < -1e-12:
        return []
    disc = max(0.0, disc)
    return [(-b-math.sqrt(disc))/(2*c), (-b+math.sqrt(disc))/(2*c)]


def metrics(mask):
    edge = Fraction(mask.bit_count(), 6)
    disjoint = Fraction(sum((mask >> a & 1) and (mask >> b & 1)
                            for a, b in DISJOINT), 3)
    adjacent_pairs = math.comb(mask.bit_count(), 2) - sum(
        (mask >> a & 1) and (mask >> b & 1) for a, b in DISJOINT)
    adjacent = Fraction(adjacent_pairs, 12)
    degree = [0] * 4
    edges = ((0,1), (0,2), (0,3), (1,2), (1,3), (2,3))
    for bit, (u, v) in enumerate(edges):
        if mask >> bit & 1:
            degree[u] += 1; degree[v] += 1
    star = Fraction(sum(d == 3 for d in degree), 4)
    mono_tri = Fraction(sum(all(((mask >> e) & 1) == color for e in tri)
                                 for tri in TRIANGLES for color in (0, 1)), 4)
    return edge, disjoint, adjacent, star, mono_tri


def reconstruct(report):
    denominator = report["profile_denominator"]
    g = [None] * 64
    for item, orbit in zip(report["unlabeled_profile"], CLASSES):
        assert item["representative"] == orbit[0] and item["orbit_size"] == len(orbit)
        per_mask = item["numerator_total"] // len(orbit)
        assert per_mask * len(orbit) == item["numerator_total"]
        for mask in orbit:
            g[mask] = per_mask
    return g, denominator


def flag_psd_cut(color, vector):
    """Coefficient of v^T M_color v for each unlabeled orbit mass."""
    result = []
    for orbit in CLASSES:
        total = Fraction(0)
        for mask in orbit:
            if ((mask >> 0) & 1) != color:
                continue
            alpha = ((mask >> 1) & 1) + 2 * ((mask >> 3) & 1)
            beta = ((mask >> 2) & 1) + 2 * ((mask >> 4) & 1)
            total += vector[alpha] * vector[beta]
        result.append(total / len(orbit))
    return result


def poly_solution(rows, rhs_poly):
    columns = []
    for degree in range(3):
        solved = solve_square(rows, [p[degree] for p in rhs_poly])
        if solved is None:
            return None
        columns.append(solved)
    return [tuple(columns[d][i] for d in range(3)) for i in range(len(rows))]


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    report = json.loads(PROFILE_REPORT.read_text())
    g, denominator = reconstruct(report)
    coeff = []
    edge = []
    disjoint = []
    adjacent = []
    star = []
    goodman = []
    for orbit in CLASSES:
        rep = orbit[0]
        coeff.append(Fraction(g[rep] + g[63 ^ rep], denominator))
        e, d, a, s, t = metrics(rep)
        edge.append(e); disjoint.append(d); adjacent.append(a); star.append(s); goodman.append(t)

    # Equalities: sum h=1, edge density=mu, disjoint-red probability=mu^2.
    base_rows = [[Fraction(1)] * len(CLASSES), edge, disjoint]
    base_rhs = [(Fraction(1), Fraction(0), Fraction(0)),
                (Fraction(0), Fraction(1), Fraction(0)),
                (Fraction(0), Fraction(0), Fraction(1))]
    # Optional active inequalities: Goodman, and the 2-flag degree-variance PSD
    # E[W(X,Y)W(X,Z)] >= mu^2.
    optional = [
        (goodman, (Fraction(1, 4), Fraction(0), Fraction(0)), "goodman"),
        (adjacent, (Fraction(0), Fraction(0), Fraction(1)), "degree_variance_psd"),
        ([edge[i] - 4*adjacent[i] + 4*star[i] for i in range(len(CLASSES))],
         (Fraction(0), Fraction(0), Fraction(0)), "red_flag_psd_vector_1_minus_2"),
        ([1 - 5*edge[i] + 8*adjacent[i] - 4*star[i] for i in range(len(CLASSES))],
         (Fraction(0), Fraction(0), Fraction(0)), "blue_flag_psd_vector_1_minus_2"),
        (flag_psd_cut(0, (0, -3, 1, 2)),
         (Fraction(0), Fraction(0), Fraction(0)), "full_2flag_blue_cut_0_-3_1_2"),
        (flag_psd_cut(1, (-1, -1, -1, 3)),
         (Fraction(0), Fraction(0), Fraction(0)), "full_2flag_red_cut_-1_-1_-1_3"),
    ]
    best = None
    bases = 0
    for active_count in range(len(optional) + 1):
        for active_ids in combinations(range(len(optional)), active_count):
            support_size = 3 + active_count
            for support in combinations(range(len(CLASSES)), support_size):
                rows = [[row[i] for i in support] for row in base_rows]
                rhs = list(base_rhs)
                for active_id in active_ids:
                    vector, polynomial, _ = optional[active_id]
                    rows.append([vector[i] for i in support])
                    rhs.append(polynomial)
                solution = poly_solution(rows, rhs)
                if solution is None:
                    continue
                bases += 1
                constraints = list(solution)  # masses >= 0
                for optional_id, (vector, rhs_poly, _) in enumerate(optional):
                    if optional_id not in active_ids:
                        constraints.append(add(
                            polysum(scale(vector[i], solution[j])
                                    for j, i in enumerate(support)),
                            scale(-1, rhs_poly)))
                objective = polysum(scale(coeff[i], solution[j])
                                    for j, i in enumerate(support))
                cuts = [0.0, 1.0]
                for constraint in constraints:
                    cuts.extend(x for x in roots(constraint) if -1e-10 <= x <= 1+1e-10)
                cuts = sorted(set(max(0.0, min(1.0, x)) for x in cuts))
                candidates = list(cuts)
                for lo, hi in zip(cuts, cuts[1:]):
                    mid = (lo + hi) / 2
                    if all(value(p, mid) >= -1e-9 for p in constraints):
                        a, b, c = map(float, objective)
                        if abs(c) > 1e-14:
                            stationary = -b / (2*c)
                            if lo <= stationary <= hi:
                                candidates.append(stationary)
                for mu in candidates:
                    if not all(value(p, mu) >= -2e-8 for p in constraints):
                        continue
                    score = value(objective, mu)
                    if best is None or score < best[0]:
                        masses = [(CLASSES[i][0], value(solution[j], mu))
                                  for j, i in enumerate(support) if value(solution[j], mu) > 1e-9]
                        best = (score, mu, support, active_ids, objective, masses,
                                min(value(p, mu) for p in constraints))
    if best is None:
        raise AssertionError("outer relaxation unexpectedly infeasible")
    score, mu, support, active_ids, objective, masses, residual = best
    answer = {
        "schema": "xor-partner-profile-realizability-gate-v1",
        "parent_profile_report": str(PROFILE_REPORT.relative_to(ROOT)),
        "parent_profile_report_sha256": sha(PROFILE_REPORT),
        "objective": "actual e26 XOR partner score; no standalone partner-c4 restriction",
        "constraints": [
            "h_i>=0 and sum h_i=1",
            "edge density mu=sum_i (#red_edges/6)h_i",
            "exact disjoint-edge identity sum_i (#disjoint_red_pairs/3)h_i=mu^2",
            "Goodman monochromatic triangle density >=1/4",
            "2-flag degree variance: adjacent-red-pair probability>=mu^2",
            "red and blue 1-flag PSD cuts at rational vector (1,-2)",
            "two exact full 2-flag PSD rational-vector cuts selected from the preceding outer optimizer",
        ],
        "basis_count": bases,
        "continuous_outer_minimum": score,
        "edge_density_at_minimum": mu,
        "active_inequalities": [optional[i][2] for i in active_ids],
        "support": [{"representative": r, "mass": m} for r, m in masses],
        "objective_polynomial_low_to_high_exact": [str(x) for x in objective],
        "minimum_constraint_residual": residual,
        "incumbent": 0.03013890356539909,
        "interpretation": "Numerical minimization of finitely many exact quadratic basis families. It is an outer relaxation, not a realizable graphon or a rigorous floating-point bound.",
        "source_sha256": sha(Path(__file__)),
    }
    args.out.mkdir(parents=True)
    (args.out / "report.json").write_text(json.dumps(answer, indent=2) + "\n")
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    main()
