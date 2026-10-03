"""Build the preregistered delta=1/8 full symmetric-orbital engine control."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


Q = 65536


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--orbit-report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=False)

    report = json.loads(args.orbit_report.read_text())
    matrix_path = Path(report["orbital_matrix"])
    matrix = json.loads(matrix_path.read_text())
    n = len(matrix)
    if n != 192 or any(len(row) != n for row in matrix):
        raise RuntimeError("orbital matrix shape")
    if sha(matrix_path) != report["orbital_matrix_sha256"]:
        raise RuntimeError("orbital matrix hash")
    if report["inputs"]["parent_sha256"] != "e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450":
        raise RuntimeError("unexpected parent")

    directed = report["directed_orbitals"]
    transpose = [-1] * directed
    for i in range(n):
        for j in range(n):
            a, b = matrix[i][j], matrix[j][i]
            if transpose[a] not in (-1, b):
                raise RuntimeError("orbital transpose not well-defined")
            transpose[a] = b
    if any(x < 0 or transpose[transpose[r]] != r for r, x in enumerate(transpose)):
        raise RuntimeError("transpose is not an involution")

    original = [int(report["orbital_probability_numerators"][str(r)]) for r in range(directed)]
    if any(original[r] != original[transpose[r]] for r in range(directed)):
        raise RuntimeError("transpose-paired parent probabilities differ")

    pairs = sorted({tuple(sorted((r, transpose[r]))) for r in range(directed)})
    pair_id = {pair: k for k, pair in enumerate(pairs)}
    directed_to_symmetric = [pair_id[tuple(sorted((r, transpose[r])))] for r in range(directed)]
    symmetric = [[directed_to_symmetric[matrix[i][j]] for j in range(n)] for i in range(n)]
    if any(symmetric[i][j] != symmetric[j][i] for i in range(n) for j in range(n)):
        raise RuntimeError("symmetric merge failed")

    parent = [original[pair[0]] for pair in pairs]
    # nearest integer to ((3/4)p + Q/8) = (6p+Q)/8, ties upward
    softened = [(6 * p + Q + 4) // 8 for p in parent]
    if any(not 0 < p < Q for p in softened):
        raise RuntimeError("softening did not enter the box interior")
    reconstructed = [[parent[symmetric[i][j]] for j in range(n)] for i in range(n)]
    parent_path = Path("reports/literature-two-parameter-001/graphon-candidate.json")
    parent_artifact = json.loads(parent_path.read_text())
    if sha(parent_path) != report["inputs"]["parent_sha256"]:
        raise RuntimeError("parent artifact hash")
    if reconstructed != parent_artifact["red_probability_numerators"]:
        raise RuntimeError("merged orbitals do not reconstruct parent")

    diagonal_ids = sorted({symmetric[i][i] for i in range(n)})
    if any(parent[r] != 0 for r in diagonal_ids):
        raise RuntimeError("original diagonal relation not zero")

    base = {
        "schema": "relation-engine-config-v1",
        "mode": "matrix",
        "n": n,
        "q": Q,
        "relation_count": len(pairs),
        "relation_ids": symmetric,
        "probability_numerators": softened,
        "integer_direction": [0] * len(pairs),
        "materialize_candidate": False,
    }
    frozen = dict(base)
    frozen["constraint_group_ids"] = [-1] * len(pairs)
    write(args.out / "frozen-control.json", frozen)

    write(args.out / "audit.json", {
        "schema": "softened-symmetric-orbitals-audit-v1",
        "orbit_report": str(args.orbit_report),
        "orbit_report_sha256": sha(args.orbit_report),
        "orbital_matrix_sha256": sha(matrix_path),
        "source_parent_sha256": sha(parent_path),
        "directed_orbitals": directed,
        "transpose_involution": transpose,
        "symmetric_orbit_pairs": pairs,
        "symmetric_relations": len(pairs),
        "diagonal_symmetric_relation_ids": diagonal_ids,
        "parent_probability_numerators": parent,
        "softened_probability_numerators": softened,
        "rounding_rule": "nearest integer, ties upward, to (6*p+65536)/8 at Q=65536",
        "rounding_errors_eighths": [8*x-(6*p+Q) for p,x in zip(parent,softened)],
        "controls": ["transpose involution", "symmetric merged matrix", "exact source-parent reconstruction", "original diagonal relation zero", "all softened entries strictly interior"],
    })


if __name__ == "__main__":
    main()
