"""Check or expand the paper's explicit compact 3840-class witness.

Default checks do not recount its K4 density. --matrix writes a full candidate
for a separate counter. All checks use Python standard-library integers.
"""

from __future__ import annotations

import gzip
import hashlib
import json
from fractions import Fraction
from pathlib import Path

from ..artifacts import read_json, reject_constant, reject_duplicate_keys
from ..schemas.paper import CompactWitness, SupplementManifest

HERE = Path(__file__).resolve().parents[3] / "paper"
Q = 65536
VALUE = Fraction(
    8450462766487926638466333426306607129, 280384030360880691940646801777885184000
)


def require(condition: bool, message: str) -> None:
    """Evidence checks must also run when Python assertion removal is enabled."""
    if not condition:
        raise ValueError(message)


def read_witness() -> dict:
    data = json.loads(
        gzip.decompress((HERE / "data/final3840.json.gz").read_bytes()),
        object_pairs_hook=reject_duplicate_keys,
        parse_constant=reject_constant,
    )
    CompactWitness.model_validate(data)
    return data


def base_numerator(i, j):
    same_a = i // 64 == j // 64
    same_e = i // 32 % 2 == j // 32 % 2
    same_s = i // 16 % 2 == j // 16 % 2
    z = (i % 16) ^ (j % 16)
    inside = z in {0, 1, 2, 4, 8, 15}
    zero_type = 0 if inside else Q
    if not same_s:
        return (51064 if inside else 0) if same_a else zero_type
    if same_a:
        if same_e:
            return zero_type
        return 35139 if z == 0 else Q if inside else 0
    return (Q if inside else 0) if same_e else zero_type


def numerator(data, i, j, x, y, base=None):
    block_id = data["block_index"][min(i, j) * 192 + max(i, j)]
    if block_id == 0:
        return base_numerator(i, j) if base is None else base
    position = 20 * x + y if i <= j else 20 * y + x
    return data["blocks"][block_id - 1][position]


def validate(data):
    CompactWitness.model_validate(data)
    index, blocks = data["block_index"], data["blocks"]
    used = []
    for i in range(192):
        require(base_numerator(i, i) == 0, "nonzero coarse diagonal")
        for j in range(192):
            b = base_numerator(i, j)
            require(b == base_numerator(j, i), "asymmetric coarse table")
            block_id = index[i * 192 + j]
            if i >= j or b in (0, Q):
                require(block_id == 0, "unexpected fractional block")
            else:
                require(block_id > 0, "missing fractional block")
                used.append(block_id)
                block = blocks[block_id - 1]
                for x in range(20):
                    require(
                        sum(block[20 * x : 20 * x + 20]) == 20 * b, "incorrect row mean"
                    )
                    require(
                        sum(block[20 * y + x] for y in range(20)) == 20 * b,
                        "incorrect column mean",
                    )
                    for y in range(20):
                        for mask in (1, 2):
                            require(
                                block[20 * x + y]
                                == block[20 * (x ^ mask) + (y ^ mask)],
                                "invalid simultaneous sign action",
                            )
    require(
        sorted(used) == list(range(1, len(blocks) + 1)),
        "fractional block IDs are not a bijection",
    )


def check_manifest():
    manifest = read_json(HERE / "data/manifest.json")
    SupplementManifest.model_validate(manifest)
    for name, metadata in manifest["files"].items():
        raw = (HERE / "data" / name).read_bytes()
        require(len(raw) == metadata["bytes"], f"wrong byte length: {name}")
        require(
            hashlib.sha256(raw).hexdigest() == metadata["sha256"], f"wrong hash: {name}"
        )
    return manifest


def check_receipt(data):
    audit = read_json(HERE / "data/final3840-audit.json")
    require(audit["status"] == "completed", "audit is not complete")
    require(
        audit["candidate"]["sha256"] == data["original_candidate_sha256"],
        "audit identifies another candidate",
    )
    require(
        audit["candidate"]["N"] == 3840 and audit["candidate"]["Q"] == Q,
        "wrong audit dimensions",
    )
    exact = audit["exact"]
    red, blue = int(exact["red"]), int(exact["blue"])
    require(red + blue == int(exact["total"]), "inconsistent red and blue totals")
    require(int(exact["denominator"]) == 3840**4 * Q**6, "wrong density denominator")
    require(
        Fraction(red + blue, int(exact["denominator"])) == VALUE,
        "totals do not give the stated bound",
    )
    require(Fraction(exact["density_fraction"]) == VALUE, "wrong recorded fraction")
    # Recombine the independently recorded character-orbit contractions.
    for color, total in (("red", red), ("blue", blue)):
        assignments = audit["method"][color]["assignments"]
        require(
            sum(a["orbit_size"] for a in assignments) == 64,
            "wrong character orbit multiplicity",
        )
        contraction_sum = sum(a["orbit_size"] * int(a["S"]) for a in assignments)
        require(
            contraction_sum == 16 * total,
            "character sums do not recombine to the total",
        )


def write_matrix(data, path, original_order=False):
    order = data["canonical_to_original_coarse"]
    inverse = [order.index(i) for i in range(192)]
    coarse = inverse if original_order else list(range(192))
    # Exclusive creation prevents accidental replacement of a large candidate.
    with path.open("x") as out:
        out.write('{"schema":"rational-step-graphon-v1","block_weights":')
        json.dump([1] * 3840, out)
        out.write(
            ',"edge_probability_denominator":65536,"red_probability_numerators":['
        )
        first = True
        for i in coarse:
            for x in range(20):
                if not first:
                    out.write(",")
                first = False
                row = [numerator(data, i, j, x, y) for j in coarse for y in range(20)]
                json.dump(row, out, separators=(",", ":"))
        out.write("]}\n")


def check(matrix: Path | None = None, original_order: bool = False):
    manifest = check_manifest()
    data = read_witness()
    validate(data)
    check_receipt(data)
    print("Supplement hashes, all 1248 block means, bounds, and sign actions: passed.")
    print("Recorded red/blue character sums and reduced fraction: passed.")
    print(
        f"Export checked {manifest['export']['original_matrix_entries_checked']:,} original entries."
    )
    print(
        "These checks validate the witness and receipt; they do not perform a new density recount."
    )
    if matrix:
        write_matrix(data, matrix, original_order)
        print(
            f"Wrote {matrix} (3840 classes; same table up to the stated permutation)."
        )
