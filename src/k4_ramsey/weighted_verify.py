"""Versioned independent weighted recount; never accepted by the unit runner."""

import json
import subprocess
import tempfile
import time
from fractions import Fraction
from pathlib import Path
from typing import Annotated

import typer

from .artifacts import hash_file, read_json
from .engine import ROOT
from .schemas.certificates import WeightedCertificate
from .schemas.verification import WeightedVerification

app = typer.Typer(pretty_exceptions_enable=False)


def main() -> None:
    app()


@app.command()
def check_command(
    input_path: Annotated[Path, typer.Option("--input")],
    out: Annotated[Path, typer.Option()],
    expected_density: Annotated[str | None, typer.Option()] = None,
) -> None:
    """Recount a weighted certificate and write new, separately scoped evidence."""
    result = recount(read_json(input_path), expected_density)
    result.candidate_sha256 = hash_file(input_path)
    result.candidate = str(input_path.resolve())
    payload = result.model_dump(mode="json", by_alias=True, exclude_none=True)
    with out.open("x") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    typer.echo(json.dumps(payload, indent=2))


def verify(data: dict, expected_density=None, timeout: float = 120) -> dict:
    """JSON-compatible wrapper for existing research callers."""
    return recount(data, expected_density, timeout).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )


def recount(
    data: dict | WeightedCertificate, expected_density=None, timeout: float = 120
) -> WeightedVerification:
    """Validate weights and graph, execute Lean, then check exact normalization."""
    certificate = WeightedCertificate.model_validate(data)
    checker = ROOT / "lean/.lake/build/bin/check_weighted_candidate"
    if not checker.is_file():
        raise RuntimeError("Build checker first: just runner-build")
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="k4-weighted-v1-") as directory:
        matrix = Path(directory) / "weighted.txt"
        matrix.write_text(
            " ".join(map(str, certificate.weights))
            + "\n"
            + "\n".join(certificate.red_rows)
            + "\n"
        )
        result = subprocess.run(
            [str(checker), str(matrix)],
            text=True,
            capture_output=True,
            check=True,
            timeout=timeout,
        )
    return parse_recount(
        result.stdout,
        certificate,
        expected_density,
        time.monotonic() - started,
        hash_file(checker),
    )


def parse_recount(
    stdout: str,
    certificate: WeightedCertificate,
    expected_density,
    seconds: float,
    checker_hash: str,
) -> WeightedVerification:
    """Interpret the weighted checker's four integers, rejecting inconsistent data."""
    values = list(map(int, stdout.split()))
    if len(values) != 4:
        raise ValueError("invalid weighted checker output")
    n, total, numerator, denominator = values
    if (
        n != len(certificate.red_rows)
        or total != sum(certificate.weights)
        or denominator <= 0
    ):
        raise ValueError("weighted checker normalization mismatch")
    density = Fraction(numerator, denominator)
    if expected_density is not None and density != Fraction(expected_density):
        raise ValueError("weighted checker disagrees with expected density")
    return WeightedVerification(
        n=n,
        total_weight=total,
        numerator=numerator,
        denominator=denominator,
        density=str(density),
        seconds=seconds,
        checker_binary_sha256=checker_hash,
        source_hashes=hash_verifier_sources(),
    )


def validate_weighted(data: dict) -> tuple[list[str], list[int]]:
    """Compatibility adapter for strategies that consume row/weight arrays."""
    certificate = WeightedCertificate.model_validate(data)
    return certificate.red_rows, certificate.weights


def hash_verifier_sources() -> dict[str, str]:
    """Identify the source contract independently of the candidate's report."""
    sources = [
        "lean/Executables/WeightedCandidate.lean",
        "lean/K4Ramsey/Counting/WeightedMultiplicity.lean",
        "lean/Tests/WeightedMultiplicity.lean",
        "lean/K4Ramsey/Counting/Multiplicity.lean",
        "lean/K4Ramsey/Counting/ValidatedTemplate.lean",
        "lean/K4Ramsey/IO/TemplateInput.lean",
        "lean/lean-toolchain",
        "src/k4_ramsey/weighted_verify.py",
        "src/k4_ramsey/artifacts.py",
    ]
    sources.extend(
        str(p.relative_to(ROOT)) for p in (ROOT / "src/k4_ramsey/schemas").glob("*.py")
    )
    return {p: hash_file(ROOT / p) for p in sources}


if __name__ == "__main__":
    main()
