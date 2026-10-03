"""Exact latent-sign split screen for the strongest Q=65536 graphon."""

from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "reports/literature-two-parameter-001"
OUT = ROOT / "reports/latent-precision-002"
CPP = Path(__file__).with_name("ordered_graphon_cppint.cpp")


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coefficient_data(p, denominator, supported):
    """Return exact cubic/quartic integer coefficients for a 0/1 support C."""
    n = len(p)
    neighbors = [set() for _ in range(n)]
    for i, j in supported:
        neighbors[i].add(j)
        neighbors[j].add(i)

    cubic = 0
    triangles = 0
    for i in range(n):
        for j in neighbors[i]:
            if j <= i:
                continue
            for k in neighbors[i] & neighbors[j]:
                if k <= j:
                    continue
                triangles += 1
                cubic += 24 * sum(
                    p[i][l] * p[j][l] * p[k][l]
                    - (denominator - p[i][l])
                    * (denominator - p[j][l])
                    * (denominator - p[k][l])
                    for l in range(n)
                )

    quartic = 0
    four_cycle_walks = 0
    for i in range(n):
        for k in range(n):
            common = neighbors[i] & neighbors[k]
            count = len(common)
            if count == 0:
                continue
            four_cycle_walks += count * count
            cross_total = sum(p[j][l] for j in common for l in common)
            quartic += 3 * (
                (denominator - p[i][k]) * denominator * count * count
                + (2 * p[i][k] - denominator) * cross_total
            )
    return cubic, quartic, triangles, four_cycle_walks, neighbors


def split_matrix(p, q, neighbors):
    n = len(p)
    return [
        [
            p[i // 2][j // 2]
            + (q if (i + j) % 2 == 0 else -q)
            * int(j // 2 in neighbors[i // 2])
            for j in range(2 * n)
        ]
        for i in range(2 * n)
    ]


def literal_density(p, denominator):
    red_answer = 0
    blue_answer = 0
    for vertices in product(range(len(p)), repeat=4):
        red = 1
        blue = 1
        for a, b in combinations(range(4), 2):
            value = p[vertices[a]][vertices[b]]
            red *= value
            blue *= denominator - value
        red_answer += red
        blue_answer += blue
    return Fraction(red_answer + blue_answer, len(p) ** 4 * denominator**6)


def literal_raw_counts(p, denominator):
    red_answer = 0
    blue_answer = 0
    for vertices in product(range(len(p)), repeat=4):
        red = 1
        blue = 1
        for a, b in combinations(range(4), 2):
            value = p[vertices[a]][vertices[b]]
            red *= value
            blue *= denominator - value
        red_answer += red
        blue_answer += blue
    return red_answer, blue_answer, red_answer + blue_answer


def tiny_falsifiers():
    fixtures = [
        ([[0, 2], [2, 0]], 5, [(0, 1)]),
        ([[0, 2, 3], [2, 0, 2], [3, 2, 0]], 5, [(0, 1), (0, 2), (1, 2)]),
        ([[0, 1, 2], [1, 0, 3], [2, 3, 0]], 4, [(0, 1), (1, 2)]),
        ([[0, 1, 4, 2], [1, 0, 3, 4], [4, 3, 0, 1], [2, 4, 1, 0]], 5,
         [(0, 1), (1, 2), (2, 3), (0, 3)]),
    ]
    results = []
    for p, denominator, edges in fixtures:
        supported = {tuple(sorted(edge)) for edge in edges}
        cubic, quartic, triangles, walks, neighbors = coefficient_data(
            p, denominator, supported
        )
        baseline = literal_density(p, denominator)
        limit = min(
            min(p[i][j], denominator - p[i][j]) for i, j in supported
        )
        for q in {-limit, -1, 1, limit}:
            predicted = baseline + Fraction(
                cubic * q**3 + quartic * q**4,
                len(p) ** 4 * denominator**6,
            )
            actual = literal_density(split_matrix(p, q, neighbors), denominator)
            assert predicted == actual
            results.append(
                {
                    "n": len(p),
                    "q": q,
                    "support_edges": len(supported),
                    "support_triangles": triangles,
                    "closed_four_walks": walks,
                    "predicted": str(predicted),
                    "actual": str(actual),
                }
            )
    return results


def exact_integer_minimum(cubic, quartic, limit):
    candidates = {-limit, 0, limit}
    stationary = None
    if quartic:
        stationary = Fraction(-3 * cubic, 4 * quartic)
        floor = stationary.numerator // stationary.denominator
        for q in (floor - 1, floor, floor + 1, floor + 2):
            candidates.add(max(-limit, min(limit, q)))
    q = min(candidates, key=lambda x: (cubic * x**3 + quartic * x**4, x))
    return q, stationary, sorted(candidates)


def main():
    start = time.monotonic()
    # Literal ordered-tuple falsifiers run before touching the full candidate.
    tests = tiny_falsifiers()

    candidate = json.loads((PARENT / "graphon-candidate.json").read_text())
    parent_report = json.loads((PARENT / "report.json").read_text())
    p = candidate["red_probability_numerators"]
    denominator = candidate["edge_probability_denominator"]
    n = len(p)
    assert n == 192 and denominator == 65536
    assert len(candidate["block_weights"]) == n
    assert all(weight == 1 for weight in candidate["block_weights"])
    assert all(len(row) == n for row in p)
    assert all(p[i][j] == p[j][i] for i in range(n) for j in range(n))
    assert all(p[i][i] == 0 for i in range(n))
    assert all(0 <= value <= denominator for row in p for value in row)

    fractional_values = sorted(
        {p[i][j] for i in range(n) for j in range(i + 1, n) if 0 < p[i][j] < denominator}
    )
    assert fractional_values == [35015, 51064]
    value_edges = {
        value: {
            (i, j)
            for i in range(n)
            for j in range(i + 1, n)
            if p[i][j] == value
        }
        for value in fractional_values
    }
    support_specs = {
        "h_only_35015": value_edges[35015],
        "p_only_51064": value_edges[51064],
        "all_fractional": value_edges[35015] | value_edges[51064],
    }

    baseline = Fraction(parent_report["density"])
    screens = []
    best = None
    best_neighbors = None
    for name, supported in support_specs.items():
        cubic, quartic, triangles, walks, neighbors = coefficient_data(
            p, denominator, supported
        )
        limit = min(
            min(p[i][j], denominator - p[i][j]) for i, j in supported
        )
        q, stationary, integer_candidates = exact_integer_minimum(
            cubic, quartic, limit
        )
        delta_numerator = cubic * q**3 + quartic * q**4
        density = baseline + Fraction(delta_numerator, n**4 * denominator**6)
        row_degrees = [len(row) for row in neighbors]
        screen = {
            "support": name,
            "undirected_edges": len(supported),
            "row_degree_min": min(row_degrees),
            "row_degree_max": max(row_degrees),
            "support_triangles": triangles,
            "closed_four_walks": walks,
            "cubic_integer_coefficient": cubic,
            "quartic_integer_coefficient": quartic,
            "admissible_q": [-limit, limit],
            "admissible_epsilon": [str(Fraction(-limit, denominator)), str(Fraction(limit, denominator))],
            "stationary_q": None if stationary is None else str(stationary),
            "checked_integer_candidates": integer_candidates,
            "selected_q": q,
            "selected_epsilon": str(Fraction(q, denominator)),
            "delta_polynomial_numerator": delta_numerator,
            "predicted_density": str(density),
            "predicted_decimal": float(density),
        }
        screens.append(screen)
        key = (density, name)
        if best is None or key < best[0]:
            best = (key, screen)
            best_neighbors = neighbors

    selected = best[1]
    q = selected["selected_q"]
    matrix = split_matrix(p, q, best_neighbors)
    order = len(matrix)
    assert order == 384
    assert all(0 <= value <= denominator for row in matrix for value in row)
    assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))

    # Exact arithmetic bounds for the checker implementation.
    pair_product_bound = denominator**2
    inner_sum_bound = order**2 * denominator**5
    contribution_bound = order**2 * denominator**6
    normalization_bound = order**4 * denominator**6
    assert pair_product_bound <= 2**64
    assert inner_sum_bound < 2**128
    assert contribution_bound < 2**128
    # The complete sum exceeds signed128's capacity, so the checker deliberately
    # uses cpp_int only for its outer O(n^2) accumulator.
    needs_big_outer = normalization_bound >= 2**127
    assert needs_big_outer

    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__), OUT / "source_snapshot.py")
    shutil.copy2(CPP, OUT / "ordered_checker_snapshot.cpp")
    write_json(
        OUT / "graphon-candidate.json",
        {
            "schema": "rational-step-graphon-v1",
            "block_weights": [1] * order,
            "edge_probability_denominator": denominator,
            "red_probability_numerators": matrix,
        },
    )
    preliminary = {
        "hypothesis": "H-LAT",
        "parent": str(PARENT),
        "parent_candidate_sha256": sha256(PARENT / "graphon-candidate.json"),
        "parent_density": str(baseline),
        "base_order": n,
        "split_order": order,
        "denominator": denominator,
        "fractional_values": fractional_values,
        "support_screens": screens,
        "selected_support": selected["support"],
        "selected_q": q,
        "selected_epsilon": selected["selected_epsilon"],
        "predicted_density": selected["predicted_density"],
        "predicted_decimal": selected["predicted_decimal"],
        "tiny_tests": tests,
        "expansion": "F(q/Q)=F0+(Aint*q^3+Bint*q^4)/(n^4*Q^6)",
        "overflow_bounds": {
            "pair_product_le": str(pair_product_bound),
            "inner_sum_lt": str(inner_sum_bound),
            "per_ij_contribution_lt": str(contribution_bound),
            "normalization": str(normalization_bound),
            "unsigned_128_limit": str(2**128),
            "signed_128_limit": str(2**127),
            "outer_accumulator": "four-limb unsigned 256-bit integer",
        },
        "status": "awaiting_independent_ordered_recount",
    }
    write_json(OUT / "expansion.json", preliminary)

    checker = OUT / "ordered_counter_cppint"
    subprocess.run(
        ["c++", "-O3", "-std=c++17", str(CPP), "-o", str(checker)],
        check=True,
        timeout=60,
    )
    checker_fixture = [
        [0, 1, 4, 2],
        [1, 0, 3, 4],
        [4, 3, 0, 1],
        [2, 4, 1, 0],
    ]
    checker_payload = "4 5\n" + "\n".join(
        " ".join(map(str, row)) for row in checker_fixture
    ) + "\n"
    checker_tiny_actual = tuple(
        map(
            int,
            subprocess.check_output(
                [str(checker)], input=checker_payload, text=True, timeout=10
            ).split(),
        )
    )
    checker_tiny_expected = literal_raw_counts(checker_fixture, 5)
    assert checker_tiny_actual == checker_tiny_expected
    payload = f"{order} {denominator}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix
    ) + "\n"
    red, blue, total = map(
        int,
        subprocess.check_output(
            [str(checker)], input=payload, text=True, timeout=120
        ).split(),
    )
    actual = Fraction(total, normalization_bound)
    predicted = Fraction(selected["predicted_density"])
    assert actual == predicted
    preliminary.update(
        {
            "status": "independent_u256_ordered_recount_passed",
            "red": red,
            "blue": blue,
            "numerator": total,
            "normalization": normalization_bound,
            "actual_density": str(actual),
            "actual_decimal": float(actual),
            "candidate_sha256": sha256(OUT / "graphon-candidate.json"),
            "source_sha256": sha256(Path(__file__)),
            "checker_source_sha256": sha256(CPP),
            "checker_binary_sha256": sha256(checker),
            "checker_tiny_expected": list(checker_tiny_expected),
            "checker_tiny_actual": list(checker_tiny_actual),
            "seconds": time.monotonic() - start,
            "trust": "Exact expansion plus independent ordered-index C++ recount with a four-limb U256 outer accumulator; no Lean certificate, novelty claim, or formal graphon-limit theorem",
        }
    )
    write_json(OUT / "report.json", preliminary)
    print(
        json.dumps(
            {
                key: preliminary[key]
                for key in (
                    "status",
                    "selected_support",
                    "selected_epsilon",
                    "actual_density",
                    "actual_decimal",
                    "seconds",
                )
            },
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
