"""Candidate-bound typed-kernel histogram plus independent Lean Nat evaluation."""

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
CPP_SOURCE = Path(__file__).with_name("typed_kernel_histogram.cpp")
LEAN_SOURCE = Path(__file__).with_name("typed_kernel_histogram.lean")


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path: Path, value: object, *, exclusive: bool = False) -> None:
    with path.open("x" if exclusive else "w") as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")


def matrix_payload(matrix: list[list[int]], q: int) -> str:
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


def validate_candidate(path: Path, types: int) -> tuple[list[list[int]], int]:
    candidate = json.loads(path.read_text())
    if candidate.get("schema") != "rational-step-graphon-v1":
        raise ValueError("unknown candidate schema")
    matrix = candidate["red_probability_numerators"]
    q = candidate["edge_probability_denominator"]
    n = len(matrix)
    if type(q) is not int or q <= 0 or not (1 <= types <= 16) or n % types:
        raise ValueError("invalid q/order/types")
    if candidate.get("block_weights") != [1] * n:
        raise ValueError("unit equal class masses required")
    for i, row in enumerate(matrix):
        if len(row) != n:
            raise ValueError("non-square matrix")
        if any(type(p) is not int or not 0 <= p <= q for p in row):
            raise ValueError("probability outside [0,q]")
        if any(row[j] != matrix[j][i] for j in range(n)):
            raise ValueError("asymmetric matrix")
    return matrix, q


def random_typed_matrix(base: int, types: int, q: int, rng: random.Random):
    blocks: list[list[list[int] | None]] = [[None] * base for _ in range(base)]
    for a in range(base):
        for b in range(a, base):
            if a == b:
                kernel = [[0] * types for _ in range(types)]
                for s in range(types):
                    for t in range(s + 1):
                        kernel[s][t] = kernel[t][s] = rng.randrange(q + 1)
                blocks[a][b] = kernel
            else:
                kernel = [[rng.randrange(q + 1) for _ in range(types)] for _ in range(types)]
                blocks[a][b] = kernel
                blocks[b][a] = [list(row) for row in zip(*kernel)]
    n = base * types
    matrix = [[0] * n for _ in range(n)]
    for a in range(base):
        for b in range(base):
            kernel = blocks[a][b]
            assert kernel is not None
            for s in range(types):
                for t in range(types):
                    matrix[a * types + s][b * types + t] = kernel[s][t]
    return matrix


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--types", type=int, required=True)
    parser.add_argument("--expected-sha256", required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--generator-timeout", type=float, default=300)
    args = parser.parse_args()

    started = time.monotonic()
    out = args.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    report: dict = {
        "schema": "typed-kernel-histogram-audit-v1",
        "status": "running",
        "started_at": datetime.now(timezone.utc).isoformat(),
        "hypothesis": "Compressed typed-kernel recount exactly matches the supplied candidate",
        "disconfirmation": "Candidate integrity failure, tiny literal mismatch, generator failure, or arithmetic inconsistency",
        "construction_input": "Only the candidate matrix and declared latent type count; no supplied score or expansion metadata",
        "indexing": "base-major, type-minor",
        "kernel_scope": (
            "Arbitrary oriented T-by-T kernels; full candidate symmetry is required. "
            "The native generator rejects instances whose K^6 signature encoding does not fit UInt64."
        ),
        "normalization": "equal unit masses, ordered fine-class quadruples, denominator N^4*Q^6",
        "evidence_scope": (
            "Native generator binds the sparse histogram to every candidate matrix entry; "
            "standalone compiled Lean checks certificate structure/mass and exact Nat arithmetic. "
            "Lean does not independently reconstruct the full-candidate histogram."
        ),
    }
    write_json(out / "status.json", report)
    for source in (CPP_SOURCE, LEAN_SOURCE, Path(__file__)):
        shutil.copy2(source, out / f"{source.stem}_snapshot{source.suffix}")
    candidate_path = args.candidate.resolve()
    shutil.copy2(candidate_path, out / "candidate_snapshot.json")
    generator = out / "typed_kernel_histogram_generator"
    lean_binary = out / "typed_kernel_histogram_lean"
    env = dict(os.environ, ELAN_HOME=str(ROOT / ".elan"))
    lake = ROOT / ".elan/bin/lake"
    try:
        setup_started = time.monotonic()
        candidate_hash = digest(candidate_path)
        if candidate_hash != args.expected_sha256:
            raise RuntimeError("candidate SHA-256 mismatch")
        matrix, q = validate_candidate(candidate_path, args.types)
        report["candidate"] = {
            "path": str(candidate_path), "sha256": candidate_hash,
            "order": len(matrix), "base_order": len(matrix) // args.types,
            "latent_types": args.types, "probability_denominator": q,
            "unit_masses": True, "symmetric": True, "probabilities_in_range": True,
        }
        report["setup_seconds"] = time.monotonic() - setup_started

        compile_started = time.monotonic()
        subprocess.run(
            ["/usr/bin/clang++", "-O3", "-std=c++17", str(CPP_SOURCE), "-o", str(generator)],
            check=True, capture_output=True, text=True, timeout=45,
        )
        subprocess.run(
            [str(lake), "env", "lean", "-c", str(out / "audit.c"), str(LEAN_SOURCE)],
            env=env, check=True, capture_output=True, text=True, timeout=45,
        )
        subprocess.run(
            [str(lake), "env", "leanc", "-O3", str(out / "audit.c"), "-o", str(lean_binary)],
            env=env, check=True, capture_output=True, text=True, timeout=45,
        )
        report["compile_seconds"] = time.monotonic() - compile_started

        def compressed_count(matrix_arg, q_arg, types_arg, name, timeout):
            matrix_file = out / f"{name}-matrix.txt"
            certificate = out / f"{name}-certificate.txt"
            matrix_file.write_text(matrix_payload(matrix_arg, q_arg))
            generated_at = time.monotonic()
            generator_raw = subprocess.check_output(
                [str(generator), str(matrix_file), str(types_arg), str(certificate)],
                text=True, timeout=timeout,
            )
            generator_seconds = time.monotonic() - generated_at
            generator_fields = tuple(map(int, generator_raw.split()))
            if len(generator_fields) != 7:
                raise RuntimeError("native generator output arity mismatch")
            evaluated_at = time.monotonic()
            lean_raw = subprocess.check_output(
                [str(lean_binary), str(certificate)], text=True, timeout=60,
            )
            lean_seconds = time.monotonic() - evaluated_at
            lean_fields = tuple(map(int, lean_raw.split()))
            if len(lean_fields) != 7:
                raise RuntimeError("Lean evaluator output arity mismatch")
            return generator_fields, lean_fields, generator_seconds, lean_seconds, certificate

        rng = random.Random(57665536)
        tiny = []
        for types in (2, 3):
            for base in range(1, 5):
                fixture = random_typed_matrix(base, types, 5, rng)
                expected_red, expected_blue = literal(fixture, 5)
                native, lean, native_s, lean_s, cert = compressed_count(
                    fixture, 5, types, f"tiny-b{base}-t{types}", 15
                )
                red, blue, total, denominator, mass, kernel_count, histogram_count = lean
                if (red, blue) != (expected_red, expected_blue):
                    raise RuntimeError(f"tiny literal mismatch base={base} types={types}")
                if total != red + blue or denominator != (base * types) ** 4 * 5**6:
                    raise RuntimeError(f"tiny normalization mismatch base={base} types={types}")
                if mass != base**4 or tuple(native[0:4]) != (base * types, 5, base, types):
                    raise RuntimeError(f"tiny histogram metadata mismatch base={base} types={types}")
                tiny.append({
                    "base_order": base, "types": types, "red": red, "blue": blue,
                    "total": total, "denominator": denominator, "coarse_mass": mass,
                    "kernel_count": kernel_count, "histogram_count": histogram_count,
                    "generator_seconds": native_s, "lean_seconds": lean_s,
                    "certificate_sha256": digest(cert),
                })
        report["tiny_literal_oracle"] = {
            "status": "passed", "fixtures": len(tiny), "cases": tiny,
            "coverage": "base orders 1..4 cover coarse partitions 4,31,22,211,1111; arbitrary oriented T=2,3 kernels",
        }
        write_json(out / "status.json", report)

        native, lean, generator_seconds, lean_seconds, certificate = compressed_count(
            matrix, q, args.types, "full", args.generator_timeout
        )
        red, blue, total, denominator, mass, kernel_count, histogram_count = lean
        expected_denominator = len(matrix) ** 4 * q**6
        if total != red + blue or denominator != expected_denominator:
            raise RuntimeError("full arithmetic/normalization mismatch")
        if mass != (len(matrix) // args.types) ** 4:
            raise RuntimeError("full coarse mass mismatch")
        if tuple(native[0:4]) != (len(matrix), q, len(matrix) // args.types, args.types):
            raise RuntimeError("full generator metadata mismatch")
        report["compressed_recount"] = {
            "red": red, "blue": blue, "total": total, "denominator": denominator,
            "density": str(Fraction(total, denominator)),
            "decimal": float(Fraction(total, denominator)),
            "coarse_histogram_mass": mass, "kernel_count": kernel_count,
            "histogram_count": histogram_count,
            "generator_seconds": generator_seconds, "lean_evaluation_seconds": lean_seconds,
            "certificate_path": str(certificate), "certificate_sha256": digest(certificate),
        }
        report.update(
            status="completed",
            evidence="independent_native_candidate_bound_histogram_plus_compiled_lean_exact_nat_arithmetic",
            generator_source_sha256=digest(out / "typed_kernel_histogram_snapshot.cpp"),
            lean_source_sha256=digest(out / "typed_kernel_histogram_snapshot.lean"),
            driver_source_sha256=digest(out / "run_typed_kernel_audit_snapshot.py"),
            generator_binary_sha256=digest(generator),
            lean_binary_sha256=digest(lean_binary),
            trust=(
                "Fresh native code scans the full matrix and reconstructs the typed-kernel histogram; "
                "compiled Lean independently evaluates the resulting exact certificate. Not a kernel "
                "proof, a second Lean reconstruction, a formal graphon realization, or a novelty claim."
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
