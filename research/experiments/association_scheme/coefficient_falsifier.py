"""Exact sparse motif coefficients for one preregistered cyclic r=5 refinement."""

from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import shutil
import time


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
PARENT = ROOT / "reports/literature-two-parameter-001"
OUT = ROOT / "reports/association-scheme-coefficients-001"
R = 5
EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
TRIANGLE = ((0, 1), (0, 2), (1, 2))
CYCLE = ((0, 1), (1, 2), (2, 3), (0, 3))
DIAMOND = tuple(edge for edge in EDGES if edge != (0, 1))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kappa(x):
    return 3 if x % R in (1, 4) else -2


def phase(i, j):
    assert i != j
    return 1 if i < j else -1


def micro_sum(vertices, selected):
    """Raw sum over all r^4 microtype assignments for selected fine edges."""
    answer = 0
    for types in product(range(R), repeat=4):
        term = 1
        for u, v in selected:
            i, j = vertices[u], vertices[v]
            term *= kappa(types[u] - types[v] - phase(i, j))
        answer += term
    return answer


def support_data(p, denominator):
    n = len(p)
    neighbors = [set() for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if 0 < p[i][j] < denominator:
                neighbors[i].add(j)
                neighbors[j].add(i)
    return neighbors


def sparse_coefficients(p, denominator):
    """Return raw expanded-numerator coefficients for q^3 through q^6.

    Each selected perturbation subgraph must have minimum degree at least two,
    because every cyclic kernel row sum is zero.  On four positions the only
    possibilities are a triangle, C4, diamond, and K4.
    """
    n = len(p)
    neighbors = support_data(p, denominator)
    coefficients = {3: 0, 4: 0, 5: 0, 6: 0}
    embeddings = {3: 0, 4: 0, 5: 0, 6: 0}
    moment_cache = {}

    def moment(vertices, selected):
        key = (tuple(phase(vertices[u], vertices[v]) for u, v in selected), selected)
        if key not in moment_cache:
            moment_cache[key] = micro_sum(vertices, selected)
        return moment_cache[key]

    # Canonical triangle on positions 0,1,2, with position 3 free.  The factor
    # 24 chooses the free position and orders the three selected vertices.
    for i in range(n):
        for j in neighbors[i]:
            if j <= i:
                continue
            for k in neighbors[i] & neighbors[j]:
                if k <= j:
                    continue
                for l in range(n):
                    vertices = (i, j, k, l)
                    weight = (
                        p[i][l] * p[j][l] * p[k][l]
                        - (denominator - p[i][l])
                        * (denominator - p[j][l])
                        * (denominator - p[k][l])
                    )
                    coefficients[3] += 24 * moment(vertices, TRIANGLE) * weight
                    embeddings[3] += 24

    # One canonical labeled C4; the three possible C4 edge subsets contribute
    # equally after summing every ordered base quadruple.
    for i in range(n):
        for j in neighbors[i]:
            for k in neighbors[j]:
                for l in neighbors[k] & neighbors[i]:
                    vertices = (i, j, k, l)
                    weight = (
                        p[i][k] * p[j][l]
                        + (denominator - p[i][k]) * (denominator - p[j][l])
                    )
                    coefficients[4] += 3 * moment(vertices, CYCLE) * weight
                    embeddings[4] += 3

    # Canonical diamond missing edge 0-1; six choices of the missing edge.
    for i in range(n):
        for j in range(n):
            common = neighbors[i] & neighbors[j]
            for k in common:
                for l in common & neighbors[k]:
                    vertices = (i, j, k, l)
                    coefficients[5] += (
                        6 * moment(vertices, DIAMOND) * (2 * p[i][j] - denominator)
                    )
                    embeddings[5] += 6

    # All six edges selected.  Red and blue give the same even-degree term.
    for i in range(n):
        for j in neighbors[i]:
            common = neighbors[i] & neighbors[j]
            for k in common:
                for l in common & neighbors[k]:
                    vertices = (i, j, k, l)
                    coefficients[6] += 2 * moment(vertices, EDGES)
                    embeddings[6] += 1

    return coefficients, embeddings, neighbors, moment_cache


def baseline_raw(p, denominator):
    answer = 0
    for vertices in product(range(len(p)), repeat=4):
        red = blue = 1
        for u, v in EDGES:
            value = p[vertices[u]][vertices[v]]
            red *= value
            blue *= denominator - value
        answer += red + blue
    return answer


def refined_matrix(p, denominator, q):
    n = len(p)
    return [
        [
            p[ia // R][jb // R]
            + (
                q
                * kappa(ia % R - jb % R - phase(ia // R, jb // R))
                if ia // R != jb // R
                and 0 < p[ia // R][jb // R] < denominator
                else 0
            )
            for jb in range(R * n)
        ]
        for ia in range(R * n)
    ]


def tiny_tests():
    fixtures = [
        ([[0, 2], [2, 0]], 5),
        ([[0, 2, 3], [2, 0, 2], [3, 2, 0]], 5),
        ([[0, 1, 4], [1, 0, 3], [4, 3, 0]], 5),
    ]
    results = []
    for p, denominator in fixtures:
        coefficients, _, _, _ = sparse_coefficients(p, denominator)
        base = baseline_raw(p, denominator)
        for q in (-1, 1):
            refined = refined_matrix(p, denominator, q)
            if not all(0 <= x <= denominator for row in refined for x in row):
                continue
            actual = baseline_raw(refined, denominator)
            predicted = base * R**4 + sum(
                coefficients[degree] * q**degree for degree in range(3, 7)
            )
            assert actual == predicted, (p, q, actual, predicted, coefficients)
            # Explicitly check every coarse pair average, including i=j.
            for i in range(len(p)):
                for j in range(len(p)):
                    total = sum(
                        refined[R * i + a][R * j + b]
                        for a in range(R)
                        for b in range(R)
                    )
                    assert total == R * R * p[i][j]
            results.append(
                {
                    "base_order": len(p),
                    "refined_order": R * len(p),
                    "q": q,
                    "coefficients": {str(k): v for k, v in coefficients.items()},
                    "predicted_raw": predicted,
                    "actual_raw": actual,
                    "includes_repeated_coarse_indices": True,
                }
            )
    return results


def feasible_interval(p, denominator):
    lo, hi = -denominator, denominator
    for i in range(len(p)):
        for j in range(i + 1, len(p)):
            value = p[i][j]
            if not 0 < value < denominator:
                continue
            valid = [
                q
                for q in range(-denominator, denominator + 1)
                if 0 <= value - 2 * q <= denominator
                and 0 <= value + 3 * q <= denominator
            ]
            lo, hi = max(lo, min(valid)), min(hi, max(valid))
    return lo, hi


def main():
    start = time.monotonic()
    tests = tiny_tests()
    parent_bytes = (PARENT / "graphon-candidate.json").read_bytes()
    candidate = json.loads(parent_bytes)
    parent_report = json.loads((PARENT / "report.json").read_text())
    p = candidate["red_probability_numerators"]
    denominator = candidate["edge_probability_denominator"]
    n = len(p)
    assert n == 192 and denominator == 65536
    assert sha256(PARENT / "graphon-candidate.json") == "e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450"
    assert all(p[i][j] == p[j][i] for i in range(n) for j in range(n))
    assert all(p[i][i] == 0 for i in range(n))
    assert sum(kappa(x) for x in range(R)) == 0

    coefficients, embeddings, neighbors, cache = sparse_coefficients(p, denominator)
    lo, hi = feasible_interval(p, denominator)
    assert (lo, hi) == (-7236, 4824), (lo, hi)
    delta_by_q = {
        q: sum(coefficients[d] * q**d for d in range(3, 7))
        for q in range(lo, hi + 1)
    }
    selected_q = min(delta_by_q, key=lambda q: (delta_by_q[q], q))
    selected_delta = delta_by_q[selected_q]
    parent_density = Fraction(parent_report["density"])
    normalization = (R * n) ** 4 * denominator**6
    predicted = parent_density + Fraction(selected_delta, normalization)
    supported = selected_q != 0 and selected_delta < 0

    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(HERE / "preregistration.json", OUT / "preregistration.json")
    report = {
        "schema": "association-scheme-motif-falsifier-v1",
        "status": "completed",
        "hypothesis": "H-F2-01 cyclic r=5 difference-set coherent refinement",
        "parent": str(PARENT.relative_to(ROOT)),
        "parent_candidate_sha256": hashlib.sha256(parent_bytes).hexdigest(),
        "parent_density": str(parent_density),
        "microtypes": R,
        "difference_set": [1, 4],
        "kernel_values_by_difference": [kappa(x) for x in range(R)],
        "kernel_row_sum": sum(kappa(x) for x in range(R)),
        "phase_rule": "g(i,j)=1 for i<j and -1 for i>j",
        "support": "all fractional coarse pairs",
        "support_edges": sum(len(row) for row in neighbors) // 2,
        "support_degree_min": min(map(len, neighbors)),
        "support_degree_max": max(map(len, neighbors)),
        "raw_polynomial_coefficients": {str(k): v for k, v in coefficients.items()},
        "embedding_terms": {str(k): v for k, v in embeddings.items()},
        "micro_moment_cache_entries": len(cache),
        "feasible_q": [lo, hi],
        "selected_q": selected_q,
        "selected_epsilon": str(Fraction(selected_q, denominator)),
        "selected_delta_raw": selected_delta,
        "predicted_density": str(predicted),
        "predicted_decimal": float(predicted),
        "supported": supported,
        "admission_decision": "admit_generic_recount" if supported else "retire_preregistered_direction",
        "tiny_tests": tests,
        "normalization": normalization,
        "seconds": time.monotonic() - start,
        "source_sha256": sha256(Path(__file__)),
        "evidence": "Exact sparse motif/intersection polynomial, validated against literal refined ordered quadruples on tiny cases; not yet a full generic recount.",
        "scope": "One preregistered r=5 kernel, phase rule, support, and scalar interval; not all cyclic or association-scheme refinements.",
    }
    write_json(OUT / "report.json", report)
    print(json.dumps({k: report[k] for k in ("supported", "feasible_q", "selected_q", "selected_delta_raw", "predicted_density", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
