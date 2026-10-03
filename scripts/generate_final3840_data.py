"""Freeze the fixed witness in small Lean source modules; never import its score.

All emitted data is generated from the hashed full matrix. The canonical
coordinate rule is independently checked against every coarse block mean.
"""
from __future__ import annotations

import hashlib
import itertools
import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
SHA = "05302cbc635e939cc41f4ba019cdcba80199b0b83563100bac0b1a0d9fff1a29"


def block_type(u, v):
    a, e, s = ((u[i] - v[i]) % (3 if i == 0 else 2) for i in range(3))
    return ("P" if a == 0 else "Z") if s else (
        ("H" if e else "Z") if a == 0 else ("Z" if e else "X"))


def main():
    raw = (ROOT / "reports/round4-E5-depth2-001/graphon-candidate.json").read_bytes()
    assert hashlib.sha256(raw).hexdigest() == SHA
    obj = json.loads(raw)
    n = np.array(obj["red_probability_numerators"], dtype=np.int64)
    assert n.shape == (3840, 3840) and obj["block_weights"] == [1] * 3840
    assert obj["edge_probability_denominator"] == 65536
    rule = json.loads((ROOT / "experiments/round4_E11/rule.json").read_text())["types"]
    vertex = json.loads((ROOT / "experiments/round4_E11/perm.json").read_text())["vertex_of"]
    families = list(itertools.product(range(3), range(2), range(2)))

    def search(p=()):
        if len(p) == 12:
            return p
        for c in range(12):
            if c not in p and all(rule[len(p)][j] == block_type(families[c], families[v])
                                 for j, v in enumerate(p)):
                found = search((*p, c))
                if found:
                    return found
        return None

    iso = search()
    assert iso is not None
    coarse_order = [vertex[f"{iso.index(f)},{x}"] for f in range(12) for x in range(16)]
    assert sorted(coarse_order) == list(range(192))
    fine_order = [20 * u + x for u in coarse_order for x in range(20)]
    reordered = n[np.ix_(fine_order, fine_order)]
    assert np.array_equal(reordered, reordered.T)
    offsets = np.full((192, 192), -1, dtype=np.int64)
    blocks = []
    base = np.zeros((192, 192), dtype=np.int64)
    for u in range(192):
        for v in range(192):
            z = (u % 16) ^ (v % 16)
            inside = z in (0, 1, 2, 4, 8, 15)
            t = block_type(families[u // 16], families[v // 16])
            b = ((0 if inside else 65536) if t == "Z" else
                 (65536 if inside else 0) if t == "X" else
                 (51064 if inside else 0) if t == "P" else
                 (35139 if z == 0 else 65536 if inside else 0))
            base[u, v] = b
            block = reordered[20*u:20*u+20, 20*v:20*v+20]
            assert np.all(block.sum(axis=0) == 20*b)
            assert np.all(block.sum(axis=1) == 20*b)
            if b in (0, 65536):
                assert np.all(block == b)
            elif u < v:
                offsets[u, v] = len(blocks)
                blocks.append(block.copy())
    assert len(blocks) == 1248
    dest = ROOT / "lean/K4Ramsey/Constructions/Final3840/Data"
    dest.mkdir(parents=True, exist_ok=True)
    names = []
    # Literal decimal strings keep elaboration small. Their parser is Lean code.
    for chunk_no, first in enumerate(range(0, len(blocks), 128)):
        name = f"Part{chunk_no:02d}"
        names.append(name)
        block_strings = [",".join(map(str, b.reshape(-1).tolist()))
                         for b in blocks[first:first+128]]
        body = "\n".join(f'  "{s}",' for s in block_strings)
        source = ("import Std\n\nnamespace K4Ramsey.Final3840Data\n\n"
                  f"-- Generated from candidate SHA-256 {SHA}.\n"
                  f"def part{chunk_no:02d} : Array String := #[\n{body}\n]\n\n"
                  "end K4Ramsey.Final3840Data\n")
        (dest / f"{name}.lean").write_text(source)
    index = ",".join(map(str, (offsets + 1).reshape(-1).tolist()))
    chunks = ", ".join(f"part{i:02d}" for i in range(len(names)))
    imports = "\n".join(f"import K4Ramsey.Constructions.Final3840.Data.{name}" for name in names)
    (ROOT / "lean/K4Ramsey/Constructions/Final3840/Data.lean").write_text(
        f"{imports}\n\nnamespace K4Ramsey.Final3840Data\n\n"
        "-- Zero denotes a hard block. Other entries are one-based block IDs.\n"
        f'def blockIndexText : String := "{index}"\n\n'
        "def parseNaturals (s : String) : Array Nat :=\n"
        '  (s.splitOn ",").toArray.map (fun x => x.toNat!)\n\n'
        "def blockIndex : Array Nat := parseNaturals blockIndexText\n\n"
        f"def blocks : Array (Array Nat) := (#[{chunks}].foldl (· ++ ·) #[]).map parseNaturals\n\n"
        "end K4Ramsey.Final3840Data\n")
    print(json.dumps({"source_sha256": SHA, "canonical_coarse_order": coarse_order,
                      "fractional_blocks": len(blocks), "chunk_files": len(names),
                      "stored_entries": len(blocks)*400,
                      "every_block_mean_checked": True,
                      "source_revision": "working-tree generator; retain source hash",
                      "generator_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
