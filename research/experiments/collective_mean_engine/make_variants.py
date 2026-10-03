"""Emit the two preregistered five-orbit relation-engine configurations.

The weighted-neutral constraint is activated only after the exact run-002
gradient gate: G_j / oriented_mass_j is identical for j in {0,1,2,4}.
Relation 3 (the h orbit) and deterministic relations remain frozen there.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED_PARENT = (
    "515776850799050572477656236153/"
    "17113283103081096920205493272576"
)


def write(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    source = json.loads(args.input.read_text())
    base = {
        "schema": "relation-engine-config-v1",
        "mode": "matrix",
        "n": source["order"],
        "q": source["denominator"],
        "relation_count": source["relation_count"],
        "relation_ids": source["relation_ids"],
        "probability_numerators": source["parent_probability_numerators"],
        "integer_direction": [0] * source["relation_count"],
        "materialize_candidate": False,
        "expected_parent_fraction": EXPECTED_PARENT,
    }
    args.out.mkdir(parents=True, exist_ok=False)

    weighted = dict(base)
    weighted["constraint_group_ids"] = [0, 0, 0, -1, 0, -1, -1]
    weighted["consumer_scope"] = (
        "Exact-gradient-neutral 3D subspace of the five certified fractional "
        "orbit constants; not the full 1248-dimensional fractional space."
    )
    write(args.out / "weighted-neutral.json", weighted)

    free = dict(base)
    free["constraint_group_ids"] = [-2, -2, -2, -2, -2, -1, -1]
    free["consumer_scope"] = (
        "All five certified fractional orbit constants free; a 5D invariant "
        "subspace only, not the full 1248-dimensional fractional space."
    )
    write(args.out / "free-five.json", free)


if __name__ == "__main__":
    main()
