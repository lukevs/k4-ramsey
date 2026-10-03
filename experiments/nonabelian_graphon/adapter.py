"""Emit relation-engine matrix configs for semidirect Cayley candidates.

This is intentionally only a group-to-relation adapter.  Optimization and
counting belong to experiments.relation_engine.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def apply_once(value: int, acted_blocks: int) -> int:
    answer = value
    for block in range(acted_blocks):
        x = (value >> (2 * block)) & 1
        y = (value >> (2 * block + 1)) & 1
        answer &= ~(3 << (2 * block))
        answer |= y << (2 * block)
        answer |= (x ^ y) << (2 * block + 1)
    return answer


def apply(value: int, exponent: int, acted_blocks: int) -> int:
    for _ in range(exponent % 3):
        value = apply_once(value, acted_blocks)
    return value


def code(vector: int, exponent: int) -> int:
    return 3 * vector + exponent


def decode(element: int) -> tuple[int, int]:
    return divmod(element, 3)


def multiply(left: int, right: int, acted_blocks: int) -> int:
    v, t = decode(left)
    w, s = decode(right)
    return code(v ^ apply(w, t, acted_blocks), (t + s) % 3)


def inverse(element: int, acted_blocks: int) -> int:
    v, t = decode(element)
    return code(apply(v, -t, acted_blocks), (-t) % 3)


def inverse_orbits(acted_blocks: int) -> tuple[list[int], list[list[int]]]:
    relation = [-1] * 192
    members: list[list[int]] = []
    for element in range(192):
        if relation[element] >= 0:
            continue
        partner = inverse(element, acted_blocks)
        orbit = [element] if partner == element else [element, partner]
        relation_id = len(members)
        members.append(orbit)
        for item in orbit:
            relation[item] = relation_id
    assert len(members) == 128
    return relation, members


def relation_matrix(acted_blocks: int) -> list[list[int]]:
    relation, _ = inverse_orbits(acted_blocks)
    inverses = [inverse(element, acted_blocks) for element in range(192)]
    matrix = []
    for left in range(192):
        row = []
        for right in range(192):
            difference = multiply(inverses[left], right, acted_blocks)
            row.append(relation[difference])
        matrix.append(row)
    assert all(matrix[i][j] == matrix[j][i] for i in range(192) for j in range(192))
    return matrix


def config(candidate_path: Path, acted_blocks: int, expected_fraction: str) -> dict:
    candidate = json.loads(candidate_path.read_text())
    assert candidate["schema"] == "rational-step-graphon-v1"
    assert candidate["block_weights"] == [1] * 192
    q = candidate["edge_probability_denominator"]
    probabilities = candidate["red_probability_numerators"]
    assert len(probabilities) == 192
    relations = relation_matrix(acted_blocks)
    relation_values: list[int | None] = [None] * 128
    for i in range(192):
        assert len(probabilities[i]) == 192
        for j in range(192):
            value = probabilities[i][j]
            assert type(value) is int and 0 <= value <= q
            relation_id = relations[i][j]
            previous = relation_values[relation_id]
            if previous is None:
                relation_values[relation_id] = value
            else:
                assert previous == value, (i, j, relation_id, previous, value)
    assert all(value is not None for value in relation_values)
    return {
        "schema": "relation-engine-config-v1",
        "mode": "matrix",
        "n": 192,
        "q": q,
        "relation_count": 128,
        "relation_ids": relations,
        "probability_numerators": relation_values,
        "constraint_group_ids": [-1] * 128,
        "expected_parent_fraction": expected_fraction,
        "materialize_candidate": True,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--acted-blocks", type=int, choices=(1, 2, 3), required=True)
    parser.add_argument("--expected-fraction", required=True)
    args = parser.parse_args()
    output = config(args.candidate, args.acted_blocks, args.expected_fraction)
    # Compact output keeps the explicit N x N relation matrix practical as a
    # versioned config while remaining ordinary JSON.
    print(json.dumps(output, sort_keys=True, separators=(",", ":")))


if __name__ == "__main__":
    main()
