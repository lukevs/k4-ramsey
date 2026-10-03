"""Fresh direct ordered-index U256 recount of a rational graphon candidate."""

from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import itertools
import json
import os
from pathlib import Path
import random
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT / "research/experiments/association_scheme/ordered_graphon_u256.cpp"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object, *, exclusive: bool = False) -> None:
    with path.open("x" if exclusive else "w") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def payload(matrix: list[list[int]], q: int) -> str:
    return f"{len(matrix)} {q}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix
    ) + "\n"


def literal(matrix: list[list[int]], q: int) -> tuple[int, int]:
    red_total = 0
    blue_total = 0
    for vertices in itertools.product(range(len(matrix)), repeat=4):
        red = 1
        blue = 1
        for a, b in itertools.combinations(range(4), 2):
            p = matrix[vertices[a]][vertices[b]]
            red *= p
            blue *= q - p
        red_total += red
        blue_total += blue
    return red_total, blue_total


def validate(path: Path):
    candidate = json.loads(path.read_text())
    if candidate.get("schema") != "rational-step-graphon-v1":
        raise ValueError("unknown schema")
    matrix = candidate["red_probability_numerators"]
    q = candidate["edge_probability_denominator"]
    n = len(matrix)
    if type(q) is not int or q <= 0 or n <= 0:
        raise ValueError("invalid n/q")
    if candidate.get("block_weights") != [1] * n:
        raise ValueError("unit class weights required")
    for i, row in enumerate(matrix):
        if len(row) != n or any(type(p) is not int or not 0 <= p <= q for p in row):
            raise ValueError("invalid probability matrix")
        if any(row[j] != matrix[j][i] for j in range(n)):
            raise ValueError("asymmetric matrix")
    return matrix, q


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--timeout", type=float, default=300)
    args = parser.parse_args()
    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report: dict = {
        "schema": "direct-ordered-u256-audit-v1",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "A generic direct ordered-index recount matches the frozen candidate",
        "construction_input": "Candidate matrix only; no supplied score, typed decomposition, histogram, or search report",
        "normalization": "equal unit masses; all ordered class quadruples including repeats; N^4*Q^6",
        "trust": "Native U256 exact execution; not compiled Lean, a kernel proof, formal realization theorem, or novelty claim",
    }
    write_json(out / "status.json", report)
    shutil.copy2(SOURCE, out / "ordered_graphon_u256_snapshot.cpp")
    shutil.copy2(Path(__file__), out / "driver_snapshot.py")
    candidate_path = args.candidate.resolve()
    shutil.copy2(candidate_path, out / "candidate_snapshot.json")
    binary = out / "ordered_graphon_u256"
    try:
        candidate_hash = digest(candidate_path)
        if candidate_hash != args.expected_sha256:
            raise RuntimeError("candidate SHA-256 mismatch")
        matrix, q = validate(candidate_path)
        n = len(matrix)
        # Bounds mirror the checker's intermediates: q^2 in U64; an inner
        # contraction and edge-times-inner in U128; the complete sum in U256.
        bounds = {
            "pair_product": q**2,
            "inner_contraction": n**2 * q**5,
            "outer_addend": n**2 * q**6,
            "global_total": n**4 * q**6,
            "u64_limit": 2**64,
            "u128_limit": 2**128,
            "u256_limit": 2**256,
        }
        if not (
            bounds["pair_product"] < bounds["u64_limit"]
            and bounds["inner_contraction"] < bounds["u128_limit"]
            and bounds["outer_addend"] < bounds["u128_limit"]
            and bounds["global_total"] < bounds["u256_limit"]
        ):
            raise RuntimeError("arithmetic bound failed")
        report["candidate"] = {
            "path": str(candidate_path), "sha256": candidate_hash,
            "order": n, "probability_denominator": q,
            "unit_masses": True, "symmetric": True, "probabilities_in_range": True,
        }
        report["overflow_bounds"] = bounds
        compile_started = time.monotonic()
        subprocess.run(
            ["/usr/bin/clang++", "-O3", "-std=c++17", str(out / "ordered_graphon_u256_snapshot.cpp"), "-o", str(binary)],
            check=True, capture_output=True, text=True, timeout=45,
        )
        report["compile_seconds"] = time.monotonic() - compile_started

        def run(matrix_arg, q_arg, timeout):
            run_started = time.monotonic()
            raw = subprocess.check_output(
                [str(binary)], input=payload(matrix_arg, q_arg), text=True, timeout=timeout
            )
            values = tuple(map(int, raw.split()))
            if len(values) != 3:
                raise RuntimeError("checker output arity mismatch")
            return values, time.monotonic() - run_started

        rng = random.Random(960256)
        tiny = []
        for order in range(1, 5):
            for case in range(3):
                q_small = 7
                fixture = [[0] * order for _ in range(order)]
                for i in range(order):
                    for j in range(i + 1):
                        fixture[i][j] = fixture[j][i] = rng.randrange(q_small + 1)
                expected = literal(fixture, q_small)
                actual, seconds = run(fixture, q_small, 10)
                if actual[0:2] != expected or actual[2] != sum(expected):
                    raise RuntimeError(f"tiny direct mismatch order={order} case={case}")
                tiny.append({"order": order, "case": case, "red": actual[0], "blue": actual[1], "total": actual[2], "seconds": seconds})
        report["tiny_literal_oracle"] = {
            "status": "passed", "fixtures": len(tiny), "cases": tiny,
            "semantics": "arbitrary symmetric matrices and diagonals; direct Python big-int ordered quadruples",
        }
        write_json(out / "status.json", report)

        full, full_seconds = run(matrix, q, args.timeout)
        red, blue, total = full
        denominator = n**4 * q**6
        if total != red + blue:
            raise RuntimeError("full red+blue mismatch")
        report["direct_recount"] = {
            "red": red, "blue": blue, "total": total, "denominator": denominator,
            "density": str(Fraction(total, denominator)),
            "decimal": float(Fraction(total, denominator)), "seconds": full_seconds,
        }
        report.update(
            status="completed",
            evidence="independent_generic_direct_ordered_index_u256_recount",
            source_snapshot_sha256=digest(out / "ordered_graphon_u256_snapshot.cpp"),
            driver_snapshot_sha256=digest(out / "driver_snapshot.py"),
            binary_sha256=digest(binary),
        )
    except Exception as error:
        report.update(status="failed", error=f"{type(error).__name__}: {error}")
        if isinstance(error, subprocess.CalledProcessError):
            report["subprocess_stdout"] = error.stdout
            report["subprocess_stderr"] = error.stderr
    finally:
        report["finished_at"] = datetime.now(timezone.utc).isoformat()
        report["seconds"] = time.monotonic() - started
        write_json(out / "status.json", report)
        write_json(out / "report.json", report, exclusive=True)
    print(json.dumps(report, indent=2, sort_keys=True))
    raise SystemExit(report["status"] != "completed")


if __name__ == "__main__":
    main()
