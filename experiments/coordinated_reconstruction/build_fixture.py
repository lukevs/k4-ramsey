"""Build the H-CR-001 structured and matched-random six-class fixtures."""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    parent_path = Path("reports/literature-two-parameter-001/graphon-candidate.json")
    orbit_path = Path("reports/group-recovery-orbitals-001/orbital-matrix.json")
    parent = json.loads(parent_path.read_text())
    orbit = json.loads(orbit_path.read_text())
    p = parent["red_probability_numerators"]
    n = len(p)
    q = parent["edge_probability_denominator"]
    fractional_relations = [10, 11, 12, 13, 16]
    representatives = [next(j for j in range(n) if orbit[0][j] == relation)
                       for relation in fractional_relations]
    structured = [0] + representatives
    rng = random.Random(20260927)
    random_control = sorted(rng.sample(range(n), 6))
    if len(set(structured)) != 6 or len(set(random_control)) != 6:
        raise RuntimeError("six-class fixture collision")
    rows = [f"COORD_RECON_V1 {n} {q} 2"]
    rows.extend(" ".join(map(str, row)) for row in p)
    rows.append("structured " + " ".join(map(str, structured)))
    rows.append("random_control " + " ".join(map(str, random_control)))
    args.out.mkdir(parents=True, exist_ok=False)
    (args.out / "fixture.txt").write_text("\n".join(rows) + "\n")
    audit = {
        "schema": "coordinated-reconstruction-input-v1",
        "parent_path": str(parent_path),
        "parent_sha256": sha(parent_path),
        "orbital_matrix_path": str(orbit_path),
        "orbital_matrix_sha256": sha(orbit_path),
        "n": n,
        "q": q,
        "structured_vertices": structured,
        "structured_rule": "root 0 plus first representative in each fractional root orbital 10,11,12,13,16",
        "random_control_vertices": random_control,
        "random_seed": 20260927,
        "variables_per_set": 15,
        "search": "exhaustive 2^15 binary assignments of all internal offdiagonal block probabilities",
        "parent_total_numerator": "3244987362620791518517985192882208768",
    }
    (args.out / "input-audit.json").write_text(json.dumps(audit, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
