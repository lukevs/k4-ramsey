"""Materialize and generically recount the admitted r=5 cyclic candidate."""

from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARENT = ROOT / "reports/literature-two-parameter-001"
COEFFICIENTS = ROOT / "reports/association-scheme-coefficients-001"
OUT = ROOT / "reports/association-scheme-r5-001"
CPP = HERE / "ordered_graphon_u256.cpp"
R = 5
EDGES = tuple(combinations(range(4), 2))


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kernel(difference):
    return 3 if difference % 5 in (1, 4) else -2


def edge_phase(i, j):
    if i == j:
        raise ValueError("fractional support has no loops")
    return 1 if i < j else -1


def materialize(base, denominator, q):
    n = len(base)
    matrix = []
    for ia in range(R * n):
        row = []
        i, a = divmod(ia, R)
        for jb in range(R * n):
            j, b = divmod(jb, R)
            value = base[i][j]
            if i != j and 0 < value < denominator:
                value += q * kernel(a - b - edge_phase(i, j))
            row.append(value)
        matrix.append(row)
    return matrix


def literal_counts(matrix, denominator):
    red_answer = blue_answer = 0
    for vertices in product(range(len(matrix)), repeat=4):
        red = blue = 1
        for u, v in EDGES:
            value = matrix[vertices[u]][vertices[v]]
            red *= value
            blue *= denominator - value
        red_answer += red
        blue_answer += blue
    return red_answer, blue_answer, red_answer + blue_answer


def payload(matrix, denominator):
    return f"{len(matrix)} {denominator}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix
    ) + "\n"


def main():
    start = time.monotonic()
    prereg = json.loads((HERE / "preregistration.json").read_text())
    expansion = json.loads((COEFFICIENTS / "report.json").read_text())
    assert expansion["supported"] is True
    assert expansion["admission_decision"] == "admit_generic_recount"
    q = expansion["selected_q"]
    assert q == -2611

    parent_bytes = (PARENT / "graphon-candidate.json").read_bytes()
    parent = json.loads(parent_bytes)
    assert hashlib.sha256(parent_bytes).hexdigest() == prereg["parent_sha256"]
    base = parent["red_probability_numerators"]
    denominator = parent["edge_probability_denominator"]
    n = len(base)
    matrix = materialize(base, denominator, q)
    order = len(matrix)
    assert order == 960
    assert all(0 <= value <= denominator for row in matrix for value in row)
    assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))

    # Exact preservation of every coarse marginal, including diagonal blocks.
    for i in range(n):
        for j in range(n):
            block_sum = sum(
                matrix[R * i + a][R * j + b]
                for a in range(R)
                for b in range(R)
            )
            assert block_sum == R * R * base[i][j]

    pair_product_bound = denominator**2
    inner_sum_bound = order**2 * denominator**5
    contribution_bound = order**2 * denominator**6
    normalization = order**4 * denominator**6
    assert pair_product_bound <= 2**64
    assert inner_sum_bound < 2**128
    assert contribution_bound < 2**128
    assert normalization < 2**256

    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(CPP, OUT / "checker_snapshot.cpp")
    shutil.copy2(HERE / "preregistration.json", OUT / "preregistration.json")
    write_json(
        OUT / "graphon-candidate.json",
        {
            "schema": "rational-step-graphon-v1",
            "block_weights": [1] * order,
            "edge_probability_denominator": denominator,
            "red_probability_numerators": matrix,
        },
    )

    binary = OUT / "ordered_graphon_u256"
    compile_command = ["c++", "-O3", "-std=c++17", str(CPP), "-o", str(binary)]
    subprocess.run(compile_command, check=True, timeout=60)

    # Generic checker tests: an arbitrary rational matrix, then a structured
    # r=5 fixture. Literal ordered tuples independently include all repetitions.
    arbitrary = [[0, 1, 4, 2], [1, 0, 3, 4], [4, 3, 0, 1], [2, 4, 1, 0]]
    tiny_base = [[0, 4, 5], [4, 0, 6], [5, 6, 0]]
    structured = materialize(tiny_base, 10, -1)
    tiny_results = []
    for fixture, fixture_denominator, label in (
        (arbitrary, 5, "arbitrary"),
        (structured, 10, "structured_r5_with_repeated_coarse_indices"),
    ):
        expected = literal_counts(fixture, fixture_denominator)
        actual = tuple(
            map(
                int,
                subprocess.check_output(
                    [str(binary)],
                    input=payload(fixture, fixture_denominator),
                    text=True,
                    timeout=30,
                ).split(),
            )
        )
        assert actual == expected
        tiny_results.append({"fixture": label, "order": len(fixture), "expected": expected, "actual": actual})

    run_start = time.monotonic()
    red, blue, total = map(
        int,
        subprocess.check_output(
            [str(binary)], input=payload(matrix, denominator), text=True, timeout=600
        ).split(),
    )
    run_seconds = time.monotonic() - run_start
    actual_density = Fraction(total, normalization)
    predicted_density = Fraction(expansion["predicted_density"])
    assert actual_density == predicted_density
    parent_density = Fraction(expansion["parent_density"])

    report = {
        "schema": "association-scheme-r5-recount-v1",
        "status": "independent_generic_ordered_recount_passed",
        "hypothesis": "H-F2-01 cyclic r=5 difference-set coherent refinement",
        "parent": str(PARENT.relative_to(ROOT)),
        "parent_candidate_sha256": hashlib.sha256(parent_bytes).hexdigest(),
        "coefficient_report": str((COEFFICIENTS / "report.json").relative_to(ROOT)),
        "coefficient_report_sha256": sha256(COEFFICIENTS / "report.json"),
        "base_order": n,
        "refined_order": order,
        "denominator": denominator,
        "selected_q": q,
        "selected_epsilon": str(Fraction(q, denominator)),
        "coarse_marginals_exactly_preserved": True,
        "red": red,
        "blue": blue,
        "numerator": total,
        "normalization": normalization,
        "actual_density": str(actual_density),
        "actual_decimal": float(actual_density),
        "parent_density": str(parent_density),
        "improvement": str(parent_density - actual_density),
        "candidate_sha256": sha256(OUT / "graphon-candidate.json"),
        "source_sha256": sha256(Path(__file__)),
        "checker_source_sha256": sha256(CPP),
        "checker_binary_sha256": sha256(binary),
        "compile_command": compile_command,
        "run_command": [str(binary)],
        "run_seconds": run_seconds,
        "total_seconds": time.monotonic() - start,
        "tiny_checker_tests": tiny_results,
        "overflow_bounds": {
            "pair_product_le": str(pair_product_bound),
            "inner_sum_lt": str(inner_sum_bound),
            "per_ij_contribution_lt": str(contribution_bound),
            "normalization": str(normalization),
            "outer_accumulator": "four-limb unsigned 256-bit integer",
        },
        "machine": platform.platform(),
        "evidence": "Exact sparse motif polynomial followed by a separately organized generic direct ordered-index C++ recount; two literal checker fixtures include a structured repeated-coarse-index case.",
        "realization": "An ordinary deterministic 960-step graphon. Equal fine-class blow-ups and conditionally independent distinct vertex edges give the standard first-moment asymptotic construction.",
        "scope": "One preregistered cyclic r=5 direction on the precision parent; no novelty, record, or family-optimality claim.",
    }
    write_json(OUT / "report.json", report)
    print(json.dumps({k: report[k] for k in ("status", "actual_density", "actual_decimal", "improvement", "run_seconds", "total_seconds")}, indent=2))


if __name__ == "__main__":
    main()
