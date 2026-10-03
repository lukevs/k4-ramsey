"""Exact certificate and one explicit free-mean line for H-TR3-2."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def determinant(a: list[list[int]]) -> int:
    """Fraction-free Bareiss determinant."""
    x = [row[:] for row in a]
    n = len(x)
    if n == 0:
        return 1
    sign = 1
    previous = 1
    for k in range(n - 1):
        if x[k][k] == 0:
            swap = next((i for i in range(k + 1, n) if x[i][k]), None)
            if swap is None:
                return 0
            x[k], x[swap] = x[swap], x[k]
            sign *= -1
        pivot = x[k][k]
        for i in range(k + 1, n):
            for j in range(k + 1, n):
                x[i][j] = (x[i][j] * pivot - x[i][k] * x[k][j]) // previous
        previous = pivot
    return sign * x[-1][-1]


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weighted-report", type=Path, required=True)
    parser.add_argument("--base-config", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)

    report = json.loads(args.weighted_report.read_text())
    gradient = [int(x) for x in report["exact_gradient"]]
    hessian = [[int(x) for x in row] for row in report["exact_hessian_second_derivative"]]

    # Integer basis for 5*d0+d1+5*d2+d4=0, with d3=d5=d6=0.
    basis = [
        [1, -5, 0, 0, 0, 0, 0],
        [0, -5, 1, 0, 0, 0, 0],
        [0, -1, 0, 0, 1, 0, 0],
    ]
    restricted = [
        [sum(basis[i][a] * hessian[a][b] * basis[j][b] for a in range(7) for b in range(7))
         for j in range(3)]
        for i in range(3)
    ]
    linear = [sum(gradient[j] * b[j] for j in range(7)) for b in basis]
    minors = [determinant([row[:k] for row in restricted[:k]]) for k in range(1, 4)]
    if linear != [0, 0, 0] or not all(x > 0 for x in minors):
        raise RuntimeError("neutrality or positive-definiteness certificate failed")

    # The exact total-gradient ratios suggest this small integral free-mean
    # direction. It is intentionally outside the neutral subspace and is a
    # line probe, not a claim of a five-dimensional optimum.
    direction = [5, 1, 5, 0, 1, 0, 0]
    c1 = sum(gradient[j] * direction[j] for j in range(7))
    twice_c2 = sum(direction[i] * hessian[i][j] * direction[j] for i in range(7) for j in range(7))
    if c1 >= 0 or twice_c2 <= 0 or twice_c2 % 2:
        raise RuntimeError("unexpected free-line derivatives")

    audit = {
        "schema": "collective-mean-five-orbit-exact-audit-v1",
        "weighted_report": str(args.weighted_report),
        "weighted_report_sha256": sha(args.weighted_report),
        "basis_columns": basis,
        "restricted_hessian_second_derivative": restricted,
        "leading_principal_minors": minors,
        "exact_neutral_linear_coefficients": linear,
        "restricted_pd_by_sylvester": True,
        "scope": "Only the 3D p-orbit-constant mean-neutral subspace; not all 1248 fractional coordinates.",
        "free_line_direction": direction,
        "free_line_c1": str(c1),
        "free_line_c2": str(twice_c2 // 2),
    }
    write(args.out / "audit.json", audit)

    config = json.loads(args.base_config.read_text())
    config["constraint_group_ids"] = [-2, -2, -2, -2, -2, -1, -1]
    config["integer_direction"] = direction
    config["materialize_candidate"] = False
    config["consumer_scope"] = "Exact nonneutral five-orbit line; q=0..6 values requested."
    write(args.out / "free-line.json", config)


if __name__ == "__main__":
    main()
