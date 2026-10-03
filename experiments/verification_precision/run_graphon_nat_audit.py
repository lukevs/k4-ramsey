"""Build and run the standalone exact-Nat Lean graphon recount."""

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


ROOT = Path(__file__).resolve().parents[2]
SOURCE = Path(__file__).with_name("graphon_nat_audit.lean")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object, *, exclusive: bool = False) -> None:
    mode = "x" if exclusive else "w"
    with path.open(mode) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def payload(matrix: list[list[int]], q: int) -> str:
    return (
        f"{len(matrix)} {q}\n"
        + "\n".join(" ".join(map(str, row)) for row in matrix)
        + "\n"
    )


def literal(matrix: list[list[int]], q: int) -> tuple[int, int]:
    """Deliberately direct ordered-quadruple oracle, including repeats."""
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


def validate_candidate(path: Path) -> tuple[dict, list[list[int]], int]:
    candidate = json.loads(path.read_text())
    if candidate.get("schema") != "rational-step-graphon-v1":
        raise ValueError("unknown candidate schema")
    matrix = candidate["red_probability_numerators"]
    q = candidate["edge_probability_denominator"]
    n = len(matrix)
    if type(q) is not int or not (1 <= q <= 65536) or not (1 <= n <= 192):
        raise ValueError("invalid n or q")
    if candidate.get("block_weights") != [1] * n:
        raise ValueError("equal unit class masses required")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError("non-square matrix")
        if any(type(p) is not int or not 0 <= p <= q for p in row):
            raise ValueError("probability numerator outside [0,q]")
        if row[i] != 0:
            raise ValueError("expected blue block diagonal")
        if any(row[j] != matrix[j][i] for j in range(n)):
            raise ValueError("asymmetric matrix")
    return candidate, matrix, q


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full-timeout", type=float, default=300.0)
    args = parser.parse_args()

    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report: dict = {
        "schema": "standalone-lean-graphon-nat-audit-v1",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "hypothesis": (
            "Exact compiled Lean Nat execution matches the strongest Q=65536 "
            "two-parameter graphon numerator and denominator"
        ),
        "disconfirmation": "Any tiny-oracle mismatch, full mismatch, or timeout",
        "arithmetic": "Lean Nat (unbounded); n<=192 and q<=65536 are resource limits",
        "normalization": "ordered equal-mass class quadruples divided by n^4*q^6",
        "repeated_index_semantics": (
            "Repeated class indices are included and represent distinct vertices "
            "with independently randomized finite edges"
        ),
    }
    write_json(out / "status.json", report)
    shutil.copy2(SOURCE, out / "source_snapshot.lean")
    shutil.copy2(Path(__file__), out / "driver_snapshot.py")
    candidate_path = args.candidate.resolve()
    shutil.copy2(candidate_path, out / "candidate_snapshot.json")
    env = dict(os.environ, ELAN_HOME=str(ROOT / ".elan"))
    lake = ROOT / ".elan/bin/lake"
    binary = out / "graphon_nat_audit"
    try:
        candidate, matrix, q = validate_candidate(candidate_path)
        candidate_hash = digest(candidate_path)
        parent_report = json.loads((candidate_path.parent / "report.json").read_text())
        independent = json.loads(
            (candidate_path.parent / "independent-audit.json").read_text()
        )
        if independent.get("candidate_sha256") != candidate_hash:
            raise RuntimeError("independent audit candidate hash mismatch")
        expected_numerator = independent["total"]
        expected_denominator = len(matrix) ** 4 * q**6
        if independent["denominator"] != expected_denominator:
            raise RuntimeError("independent audit denominator mismatch")
        if parent_report["numerator"] != expected_numerator:
            raise RuntimeError("parent and independent numerator mismatch")
        expected_density = Fraction(expected_numerator, expected_denominator)
        if expected_density != Fraction(parent_report["density"]):
            raise RuntimeError("parent reduced density mismatch")
        report["candidate"] = {
            "path": str(candidate_path),
            "sha256": candidate_hash,
            "n": len(matrix),
            "q": q,
            "unique_probability_numerators": sorted({p for row in matrix for p in row}),
            "diagonal_blue": True,
            "symmetric": True,
            "unit_class_weights": True,
            "expected_numerator": expected_numerator,
            "expected_denominator": expected_denominator,
            "expected_density": str(expected_density),
        }

        compile_started = time.monotonic()
        subprocess.run(
            [str(lake), "env", "lean", "-c", str(out / "audit.c"), str(SOURCE)],
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=45,
        )
        subprocess.run(
            [str(lake), "env", "leanc", "-O3", str(out / "audit.c"), "-o", str(binary)],
            env=env,
            check=True,
            capture_output=True,
            text=True,
            timeout=45,
        )
        report["compile_seconds"] = time.monotonic() - compile_started

        def run(matrix_arg: list[list[int]], q_arg: int, name: str, timeout: float):
            input_path = out / f"{name}.txt"
            input_path.write_text(payload(matrix_arg, q_arg))
            run_started = time.monotonic()
            raw = subprocess.check_output(
                [str(binary), str(input_path)], text=True, timeout=timeout
            )
            values = tuple(map(int, raw.split()))
            if len(values) != 4:
                raise RuntimeError("Lean output arity mismatch")
            return values, time.monotonic() - run_started

        # Tiny, arbitrary symmetric probability matrices come first.  Their
        # diagonals are intentionally unrestricted to exercise repeated indices.
        rng = random.Random(20260927)
        tiny = []
        for n in range(1, 5):
            for case in range(5):
                q_small = 5
                fixture = [[0] * n for _ in range(n)]
                for i in range(n):
                    for j in range(i + 1):
                        fixture[i][j] = fixture[j][i] = rng.randrange(q_small + 1)
                expected_red, expected_blue = literal(fixture, q_small)
                actual, seconds = run(fixture, q_small, f"tiny-{n}-{case}", 10)
                red, blue, total, denominator = actual
                if (red, blue) != (expected_red, expected_blue):
                    raise RuntimeError(f"tiny oracle mismatch n={n} case={case}")
                if total != red + blue or denominator != n**4 * q_small**6:
                    raise RuntimeError(f"tiny normalization mismatch n={n} case={case}")
                tiny.append(
                    {
                        "n": n,
                        "case": case,
                        "q": q_small,
                        "red": red,
                        "blue": blue,
                        "total": total,
                        "denominator": denominator,
                        "seconds": seconds,
                        "diagonal": [fixture[i][i] for i in range(n)],
                    }
                )
        report["tiny_oracle"] = {
            "status": "passed",
            "fixtures": len(tiny),
            "cases": tiny,
            "oracle": "direct Python arbitrary-integer six-edge products over all ordered quadruples",
        }
        write_json(out / "status.json", report)

        full, full_seconds = run(matrix, q, "precision-candidate", args.full_timeout)
        red, blue, total, denominator = full
        report["lean_recount"] = {
            "red": red,
            "blue": blue,
            "total": total,
            "denominator": denominator,
            "density": str(Fraction(total, denominator)),
            "seconds": full_seconds,
        }
        if red + blue != total:
            raise RuntimeError("Lean red+blue total mismatch")
        if total != expected_numerator or denominator != expected_denominator:
            raise RuntimeError("full precision Lean recount mismatch")
        report.update(
            status="completed",
            evidence="independent_standalone_compiled_lean_exact_nat_recount",
            source_sha256=digest(SOURCE),
            source_snapshot_sha256=digest(out / "source_snapshot.lean"),
            binary_sha256=digest(binary),
            trust=(
                "Compiled Lean execution using exact Nat arithmetic and an independent "
                "ordered-class implementation; not a kernel proof of the count formula "
                "or the probabilistic realization theorem"
            ),
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
