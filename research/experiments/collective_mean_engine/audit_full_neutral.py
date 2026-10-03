"""Exact Sylvester certificate on the five-orbit global-gradient-neutral slice."""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
import shutil


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def determinant(matrix: list[list[int]]) -> int:
    """Fraction-free Bareiss determinant."""
    work = [row[:] for row in matrix]
    if not work:
        return 1
    previous = 1
    sign = 1
    for k in range(len(work) - 1):
        if work[k][k] == 0:
            swap = next((i for i in range(k + 1, len(work)) if work[i][k]), None)
            if swap is None:
                return 0
            work[k], work[swap] = work[swap], work[k]
            sign *= -1
        pivot = work[k][k]
        for i in range(k + 1, len(work)):
            for j in range(k + 1, len(work)):
                numerator = work[i][j] * pivot - work[i][k] * work[k][j]
                if numerator % previous:
                    raise RuntimeError("Bareiss division was not exact")
                work[i][j] = numerator // previous
        previous = pivot
    return sign * work[-1][-1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--weighted-report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)

    report = json.loads(args.weighted_report.read_text())
    gradient = [int(value) for value in report["exact_gradient"]]
    hessian = [
        [int(value) for value in row]
        for row in report["exact_hessian_second_derivative"]
    ]
    if len(gradient) != 7 or len(hessian) != 7 or any(len(row) != 7 for row in hessian):
        raise RuntimeError("unexpected relation derivative dimensions")
    if any(hessian[i][j] != hessian[j][i] for i in range(7) for j in range(7)):
        raise RuntimeError("exact Hessian is not symmetric")

    # First three columns span the p-orbit redistribution slice.  The fourth
    # transfers aggregate probability between p and h in the primitive exact
    # ratio forced by their two distinct gradient values.
    divisor = math.gcd(abs(gradient[1]), abs(gradient[3]))
    basis = [
        [1, -5, 0, 0, 0, 0, 0],
        [0, -5, 1, 0, 0, 0, 0],
        [0, -1, 0, 0, 1, 0, 0],
        [0, gradient[3] // divisor, 0, -gradient[1] // divisor, 0, 0, 0],
    ]
    linear = [sum(gradient[j] * column[j] for j in range(7)) for column in basis]
    if linear != [0, 0, 0, 0]:
        raise RuntimeError("basis is not exactly gradient-neutral")
    restricted = [
        [
            sum(
                basis[i][a] * hessian[a][b] * basis[j][b]
                for a in range(7)
                for b in range(7)
            )
            for j in range(4)
        ]
        for i in range(4)
    ]
    minors = [determinant([row[:k] for row in restricted[:k]]) for k in range(1, 5)]
    if not all(value > 0 for value in minors):
        raise RuntimeError("Sylvester positivity failed")

    source_snapshot = args.out / "source_snapshot.py"
    shutil.copy2(Path(__file__), source_snapshot)
    artifact = {
        "schema": "collective-mean-five-orbit-global-neutral-exact-v1",
        "status": "exact_positive_definite",
        "weighted_report": str(args.weighted_report),
        "weighted_report_sha256": sha256(args.weighted_report),
        "source_snapshot": str(source_snapshot),
        "source_snapshot_sha256": sha256(source_snapshot),
        "gradient_values": gradient[:5],
        "compensated_pair_gcd": divisor,
        "basis_columns": basis,
        "exact_neutral_linear_coefficients": linear,
        "restricted_hessian_second_derivative": restricted,
        "leading_principal_minors": minors,
        "leading_principal_minor_bit_lengths": [value.bit_length() for value in minors],
        "restricted_pd_by_sylvester": True,
        "scope": (
            "The complete four-dimensional first-order-neutral tangent space "
            "inside the five certified fractional-edge orbit constants; not the "
            "nonconstant 1248-coordinate space and not a global line optimum."
        ),
    }
    output = args.out / "audit.json"
    output.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "audit": str(output),
        "minor_bit_lengths": artifact["leading_principal_minor_bit_lengths"],
        "status": artifact["status"],
    }, sort_keys=True))


if __name__ == "__main__":
    main()
