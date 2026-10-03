"""Independent Lean native recount; never trusts the search's incremental score."""

from __future__ import annotations

import subprocess
import tempfile
import time
from fractions import Fraction
from pathlib import Path

from .artifacts import hash_file
from .engine import ROOT
from .schemas.certificates import UnitCertificate
from .schemas.verification import Verification


def verify(
    data: dict,
    expected: int | None = None,
    timeout: float = 30,
    *,
    checker: Path | None = None,
) -> dict:
    """JSON-compatible API retained for existing research strategies."""
    return recount(data, expected, timeout, checker=checker).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )


def recount(
    data: dict | UnitCertificate,
    expected: int | None = None,
    timeout: float = 30,
    *,
    checker: Path | None = None,
) -> Verification:
    """Validate a graph, run the independent checker, and check its exact contract."""
    certificate = UnitCertificate.model_validate(data)
    checker = checker or ROOT / "lean/.lake/build/bin/check_candidate"
    if not checker.is_file():
        raise RuntimeError("Build checker first: just runner-build")
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="k4-verify-") as directory:
        matrix = Path(directory) / "rows.txt"
        matrix.write_text("\n".join(certificate.red_rows) + "\n")
        command = [str(checker), str(matrix)]
        if expected is not None:
            command.append(str(expected))
        result = subprocess.run(
            command, text=True, capture_output=True, check=True, timeout=timeout
        )
    return parse_recount(
        result.stdout,
        len(certificate.red_rows),
        expected,
        time.monotonic() - started,
        hash_file(checker),
    )


def parse_recount(
    stdout: str, order: int, expected: int | None, seconds: float, checker_hash: str
) -> Verification:
    """Interpret seven checker integers; reject shape, order, or score disagreement."""
    values = list(map(int, stdout.split()))
    if len(values) != 7:
        raise ValueError("malformed checker output")
    n, numerator, denominator, edges, triangles, red4, blue4 = values
    if n != order or (expected is not None and numerator != expected):
        raise ValueError("checker disagrees with search")
    if denominator <= 0:
        raise ValueError("invalid checker denominator")
    return Verification(
        n=n,
        numerator=numerator,
        denominator=denominator,
        density=str(Fraction(numerator, denominator)),
        red_edges=edges,
        blue_triangles=triangles,
        red_k4=red4,
        blue_k4=blue4,
        seconds=seconds,
        checker_binary_sha256=checker_hash,
    )


def hash_verifier_sources() -> dict[str, str]:
    """Hashes of the source contract used for a unit recount."""
    paths = [
        "lean/Executables/CheckCandidate.lean",
        "lean/K4Ramsey/Counting/Multiplicity.lean",
        "lean/K4Ramsey/Counting/WeightedMultiplicity.lean",
        "lean/K4Ramsey/Counting/ValidatedTemplate.lean",
        "lean/K4Ramsey/IO/TemplateInput.lean",
        "lean/lean-toolchain",
        "lean/lakefile.toml",
        "src/k4_ramsey/verify.py",
        "src/k4_ramsey/engine.py",
        "src/k4_ramsey/artifacts.py",
    ]
    paths.extend(
        str(p.relative_to(ROOT)) for p in (ROOT / "src/k4_ramsey/schemas").glob("*.py")
    )
    return {p: hash_file(ROOT / p) for p in paths}
