"""Validate certified orbitals and emit the five-orbit relation-engine input."""
import hashlib
import json
from pathlib import Path

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


CONFIG = ROOT / "experiments/collective_mean_engine/config.json"
OUT = ROOT / "reports/collective-mean-engine-input-001"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    config = json.loads(CONFIG.read_text())
    parent_path = ROOT / config["parent"]
    orbit_report_path = ROOT / config["orbital_report"]
    orbit_map_path = ROOT / config["fractional_orbit_map"]
    for path, expected in (
        (parent_path, config["parent_sha256"]),
        (orbit_report_path, config["orbital_report_sha256"]),
        (orbit_map_path, config["fractional_orbit_map_sha256"]),
    ):
        if sha256(path) != expected:
            raise RuntimeError(f"immutable input hash mismatch: {path}")
    parent = json.loads(parent_path.read_text())
    p = parent["red_probability_numerators"]
    q = parent["edge_probability_denominator"]
    n = len(p)
    if n != 192 or q != 65536:
        raise RuntimeError("unexpected parent dimensions")
    if any(len(row) != n for row in p):
        raise RuntimeError("parent is not square")
    if any(p[i][j] != p[j][i] for i in range(n) for j in range(n)):
        raise RuntimeError("parent is not symmetric")
    if any(not 0 <= x <= q for row in p for x in row):
        raise RuntimeError("parent probability out of bounds")

    orbit_data = json.loads(orbit_map_path.read_text())
    edge_to_orbit = orbit_data["edge_to_orbit"]
    expected_fractional = {
        f"{i},{j}" for i in range(n) for j in range(i)
        if 0 < p[i][j] < q
    }
    if set(edge_to_orbit) != expected_fractional:
        raise RuntimeError("certified orbit map does not exactly cover fractional pairs")
    sizes = [0] * 5
    relation_ids = [[-1] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            if i == j:
                relation = 5
            elif 0 < p[i][j] < q:
                relation = int(edge_to_orbit[f"{i},{j}"])
                sizes[relation] += 1
            elif p[i][j] == 0:
                relation = 5
            elif p[i][j] == q:
                relation = 6
            else:
                raise RuntimeError("unclassified parent entry")
            relation_ids[i][j] = relation_ids[j][i] = relation
    if sizes != [480, 96, 480, 96, 96]:
        raise RuntimeError(f"fractional orbit sizes mismatch: {sizes}")
    parameters = [51064, 51064, 51064, 35015, 51064, 0, q]
    if any(parameters[relation_ids[i][j]] != p[i][j]
           for i in range(n) for j in range(n)):
        raise RuntimeError("relation input does not reconstruct parent")
    relation_cell_counts = [sum(relation_ids[i][j] == relation
                                for i in range(n) for j in range(n))
                            for relation in range(7)]
    engine_input = {
        "schema": "relation-engine-input-v1",
        "order": n,
        "denominator": q,
        "relation_count": 7,
        "relation_ids": relation_ids,
        "parent_probability_numerators": parameters,
        "variable_relations": [0, 1, 2, 3, 4],
        "frozen_relations": [5, 6],
        "unordered_variable_counts": sizes,
        "oriented_relation_cell_counts": relation_cell_counts,
        "neutral_constraint_rows": [
            [480, 96, 480, 0, 96],
            [0, 0, 0, 96, 0]
        ],
        "neutral_constraint_meaning": [
            "weighted sum of four p-orbit mean changes is zero",
            "singleton h-orbit mean change is zero"
        ],
        "interpretation": "Five certified orbit-constant fractional means only; not the full1248-coordinate space",
    }
    OUT.mkdir(parents=True, exist_ok=False)
    write_json(OUT / "input.json", engine_input)
    report = {
        "status": "validated_relation_input_emitted",
        "config": str(CONFIG), "config_sha256": sha256(CONFIG),
        "parent_sha256": sha256(parent_path),
        "orbit_report_sha256": sha256(orbit_report_path),
        "orbit_map_sha256": sha256(orbit_map_path),
        "input_sha256": sha256(OUT / "input.json"),
        "order": n, "denominator": q,
        "fractional_unordered_edges": len(expected_fractional),
        "fractional_orbit_sizes": sizes,
        "relation_cell_counts": relation_cell_counts,
        "parent_reconstruction": "exact",
        "scope": engine_input["interpretation"],
    }
    write_json(OUT / "report.json", report)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
