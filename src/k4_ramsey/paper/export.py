"""Freeze the paper data from explicit source tables and existing audit records.

This is a mechanical export, not a new search or an exact density recount.
Run from any directory with the repository's Python environment.
"""

from __future__ import annotations

import gzip
import hashlib
import itertools
import json
import re
from pathlib import Path

from ..artifacts import read_json, reject_constant, reject_duplicate_keys
from ..schemas.paper import SupplementManifest
from .witness import base_numerator, numerator, require, validate

ROOT = Path(__file__).resolve().parents[3]
HERE = ROOT / "paper"
SOURCE_SHA = "05302cbc635e939cc41f4ba019cdcba80199b0b83563100bac0b1a0d9fff1a29"


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def block_type(u, v):
    a = (u[0] - v[0]) % 3
    e = (u[1] - v[1]) % 2
    s = (u[2] - v[2]) % 2
    if s:
        return "P" if a == 0 else "Z"
    if a == 0:
        return "H" if e else "Z"
    return "Z" if e else "X"


def canonical_order():
    families = list(itertools.product(range(3), range(2), range(2)))
    rule = read_json(ROOT / "research/experiments/round4_E11/rule.json")["types"]
    vertices = read_json(ROOT / "research/experiments/round4_E11/perm.json")[
        "vertex_of"
    ]

    def search(partial=()):
        if len(partial) == 12:
            return partial
        for c in range(12):
            if c not in partial and all(
                rule[len(partial)][j] == block_type(families[c], families[v])
                for j, v in enumerate(partial)
            ):
                result = search((*partial, c))
                if result is not None:
                    return result
        return None

    iso = search()
    require(iso is not None, "no class bijection matches the group rule")
    order = [vertices[f"{iso.index(f)},{x}"] for f in range(12) for x in range(16)]
    require(sorted(order) == list(range(192)), "class order is not a permutation")
    return order


def export(workflow: Path | None = None):
    dest = HERE / "data"
    dest.mkdir(exist_ok=True)
    files = {}
    sources = {}

    def write(name, payload):
        if isinstance(payload, (dict, list)):
            raw = (
                json.dumps(payload, separators=(",", ":"), ensure_ascii=True) + "\n"
            ).encode()
        else:
            raw = payload
        if name.endswith(".gz"):
            raw = gzip.compress(raw, mtime=0)
        (dest / name).write_bytes(raw)
        files[name] = {"sha256": sha(raw), "bytes": len(raw)}

    def copy_json(source, name):
        raw = (ROOT / source).read_bytes()
        sources[source] = sha(raw)
        write(name, raw)

    data_dir = ROOT / "lean/K4Ramsey/Constructions/Final3840"
    index_source = (data_dir / "Data.lean").read_text()
    match = re.search(r'def blockIndexText : String := "([0-9,]+)"', index_source)
    require(match is not None, "Lean block index not found")
    index = [int(v) for v in match.group(1).split(",")]
    blocks = []
    for path in sorted((data_dir / "Data").glob("Part*.lean")):
        raw = path.read_bytes()
        sources[str(path.relative_to(ROOT))] = sha(raw)
        blocks.extend(
            [
                [int(v) for v in s.split(",")]
                for s in re.findall(r'"([0-9,]+)"', raw.decode())
            ]
        )
    require(len(index) == 192**2 and len(blocks) == 1248, "wrong Lean table dimensions")
    require(
        all(len(b) == 400 for b in blocks), "wrong Lean refinement block dimensions"
    )
    order = canonical_order()
    compact = {
        "schema": "clebsch192-refinement20-v1",
        "denominator": 65536,
        "coarse_classes": 192,
        "fine_labels": 20,
        "base_parameters": {"p_numerator": 51064, "h_numerator": 35139},
        "original_candidate_sha256": SOURCE_SHA,
        "canonical_to_original_coarse": order,
        "block_index": index,
        "blocks": blocks,
    }
    # Verify the compact definition against every original matrix entry.
    validate(compact)
    original_path = ROOT / "reports/round4-E5-depth2-001/graphon-candidate.json"
    original_raw = original_path.read_bytes()
    require(sha(original_raw) == SOURCE_SHA, "original candidate hash mismatch")
    original = json.loads(
        original_raw,
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    del original_raw
    require(
        original["edge_probability_denominator"] == 65536, "wrong original denominator"
    )
    require(original["block_weights"] == [1] * 3840, "wrong original class weights")
    matrix = original["red_probability_numerators"]
    require(
        len(matrix) == 3840 and all(len(r) == 3840 for r in matrix),
        "wrong original matrix dimensions",
    )
    checked = 0
    for i in range(192):
        for j in range(192):
            b = base_numerator(i, j)
            for x in range(20):
                row = matrix[20 * order[i] + x]
                for y in range(20):
                    require(
                        numerator(compact, i, j, x, y, b) == row[20 * order[j] + y],
                        "export differs from original matrix",
                    )
                    checked += 1
    write("final3840.json.gz", compact)
    sources[str(original_path.relative_to(ROOT))] = SOURCE_SHA
    del original, matrix

    for source, name in [
        ("reports/round5-F5-audit-E5-depth2-001/report.json", "final3840-audit.json"),
        (
            "reports/round5-F5-audit-E5-depth1-001/report.json",
            "sign1920-character-audit.json",
        ),
        (
            "reports/round4-P-audit-E5-depth1-001/report.json",
            "sign1920-direct-audit.json",
        ),
        ("research/experiments/round5_F4/Fpoly.json", "base-polynomial.json"),
        ("research/experiments/round5_F4/crit.json", "base-minimum.json"),
        (
            "reports/round4-P-package/candidates/C-pentagon-Q9.json",
            "pentagon-q9.json.gz",
        ),
        (
            "reports/round4-P-package/structure/phase-assignment.json",
            "pentagon-phases.json",
        ),
        (
            "reports/round4-P-package/structure/e11-vertex-map.json",
            "base-class-map.json",
        ),
        (
            "reports/round4-P-package/structure/b192-base.json",
            "base-original-order.json",
        ),
        (
            "reports/round4-P-package/structure/per-edge-amplitudes.json",
            "parent-amplitudes.json",
        ),
        (
            "reports/round4-P-package/receipts/C-u256.json",
            "pentagon-q9-direct-audit.json",
        ),
        ("reports/round4-P-package/receipts/C-crt.json", "pentagon-q9-crt-audit.json"),
    ]:
        copy_json(source, name)
    if workflow:
        for path, name in [
            (workflow, "research-workflow.md"),
            (
                workflow.parent / "references/source-principles.md",
                "workflow-source-principles.md",
            ),
        ]:
            write(name, path.read_bytes())
    else:
        for name in ("research-workflow.md", "workflow-source-principles.md"):
            if (dest / name).exists():
                write(name, (dest / name).read_bytes())
    manifest = {
        "schema": "k4-paper-supplement-v1",
        "files": files,
        "source_sha256": sources,
        "export": {
            "original_matrix_entries_checked": checked,
            "mismatches": 0,
            "exporter_sha256": sha(Path(__file__).read_bytes()),
            "witness_checker_sha256": sha(
                Path(__file__).with_name("witness.py").read_bytes()
            ),
            "note": "Source and witness checks, not a new density recount.",
        },
    }
    SupplementManifest.model_validate(manifest)
    (dest / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(f"Exported {len(files)} files; checked {checked:,} original matrix entries.")
