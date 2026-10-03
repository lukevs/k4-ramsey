"""Independently recount a 384-class rational graphon with compiled Lean Nat."""

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
SOURCE = Path(__file__).with_name("latent_graphon_nat_audit.lean")


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


def validate_candidate(path: Path) -> tuple[list[list[int]], int]:
    candidate = json.loads(path.read_text())
    if candidate.get("schema") != "rational-step-graphon-v1":
        raise ValueError("unknown candidate schema")
    matrix = candidate["red_probability_numerators"]
    q = candidate["edge_probability_denominator"]
    n = len(matrix)
    if type(q) is not int or not (1 <= q <= 65536) or not (1 <= n <= 384):
        raise ValueError("invalid n or q")
    if candidate.get("block_weights") != [1] * n:
        raise ValueError("equal unit class masses required")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError("non-square matrix")
        if any(type(p) is not int or not 0 <= p <= q for p in row):
            raise ValueError("probability numerator outside [0,q]")
        if any(row[j] != matrix[j][i] for j in range(n)):
            raise ValueError("asymmetric matrix")
    return matrix, q


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--full-timeout", type=float, default=1800.0)
    args = parser.parse_args()

    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report: dict = {
        "schema": "standalone-lean-latent-graphon-nat-audit-v1",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "A fresh exact-Nat Lean recount confirms the 384-class Q=65536 candidate",
        "disconfirmation": "Candidate-integrity failure, tiny split-oracle mismatch, timeout, or arithmetic inconsistency",
        "arithmetic": "Lean Nat (unbounded); n<=384 and q<=65536 are resource limits",
        "normalization": "equal class masses; ordered class quadruples divided by n^4*q^6",
        "repeated_index_semantics": "All ordered class quadruples are retained, including repeated class indices",
        "independence": "The candidate matrix is the only construction input; no expansion metadata or prior score is read",
    }
    write_json(out / "status.json", report)
    shutil.copy2(SOURCE, out / "source_snapshot.lean")
    shutil.copy2(Path(__file__), out / "driver_snapshot.py")
    candidate_path = args.candidate.resolve()
    shutil.copy2(candidate_path, out / "candidate_snapshot.json")
    env = dict(os.environ, ELAN_HOME=str(ROOT / ".elan"))
    lake = ROOT / ".elan/bin/lake"
    binary = out / "latent_graphon_nat_audit"
    try:
        candidate_hash = digest(candidate_path)
        if candidate_hash != args.expected_sha256:
            raise RuntimeError("candidate SHA-256 mismatch")
        matrix, q = validate_candidate(candidate_path)
        report["candidate"] = {
            "path": str(candidate_path),
            "sha256": candidate_hash,
            "n": len(matrix),
            "q": q,
            "unit_class_weights": True,
            "symmetric": True,
            "probabilities_in_range": True,
            "unique_probability_numerators": sorted({p for row in matrix for p in row}),
        }

        compile_started = time.monotonic()
        subprocess.run(
            [str(lake), "env", "lean", "-c", str(out / "audit.c"), str(SOURCE)],
            env=env, check=True, capture_output=True, text=True, timeout=45,
        )
        subprocess.run(
            [str(lake), "env", "leanc", "-O3", str(out / "audit.c"), "-o", str(binary)],
            env=env, check=True, capture_output=True, text=True, timeout=45,
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

        # Tiny matrices are explicitly indexed as (base class, latent sign).
        # Their probabilities are independently random and need not arise from
        # the candidate's unpublished expansion mechanism.
        rng = random.Random(38465536)
        tiny = []
        for base_n in range(1, 4):
            n = 2 * base_n
            for case in range(4):
                q_small = 7
                fixture = [[0] * n for _ in range(n)]
                for i in range(n):
                    for j in range(i + 1):
                        fixture[i][j] = fixture[j][i] = rng.randrange(q_small + 1)
                expected_red, expected_blue = literal(fixture, q_small)
                actual, seconds = run(fixture, q_small, f"tiny-split-{base_n}-{case}", 10)
                red, blue, total, denominator = actual
                if (red, blue) != (expected_red, expected_blue):
                    raise RuntimeError(f"tiny split oracle mismatch base_n={base_n} case={case}")
                if total != red + blue or denominator != n**4 * q_small**6:
                    raise RuntimeError(f"tiny split normalization mismatch base_n={base_n} case={case}")
                tiny.append({
                    "base_classes": base_n,
                    "latent_types_per_base": 2,
                    "n": n,
                    "case": case,
                    "q": q_small,
                    "red": red,
                    "blue": blue,
                    "total": total,
                    "denominator": denominator,
                    "diagonal": [fixture[i][i] for i in range(n)],
                    "seconds": seconds,
                })
        report["tiny_split_oracle"] = {
            "status": "passed",
            "fixtures": len(tiny),
            "cases": tiny,
            "oracle": "direct Python arbitrary-integer six-edge products over all ordered quadruples",
        }
        write_json(out / "status.json", report)

        full, full_seconds = run(matrix, q, "candidate-384", args.full_timeout)
        red, blue, total, denominator = full
        expected_denominator = len(matrix) ** 4 * q**6
        if red + blue != total:
            raise RuntimeError("Lean red+blue total mismatch")
        if denominator != expected_denominator:
            raise RuntimeError("Lean normalization denominator mismatch")
        report["lean_recount"] = {
            "red": red,
            "blue": blue,
            "total": total,
            "denominator": denominator,
            "density": str(Fraction(total, denominator)),
            "decimal": float(Fraction(total, denominator)),
            "seconds": full_seconds,
        }
        report.update(
            status="completed",
            evidence="independent_standalone_compiled_lean_exact_nat_recount",
            source_sha256=digest(SOURCE),
            source_snapshot_sha256=digest(out / "source_snapshot.lean"),
            binary_sha256=digest(binary),
            trust=(
                "Compiled Lean exact-Nat execution of a direct ordered-class formula; "
                "not a kernel proof, formal realization theorem, or novelty claim"
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
