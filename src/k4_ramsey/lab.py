"""One isolated experiment: validate → freeze → search → recount → record.

The justfile owns builds; this module owns runtime supervision, never scheduling.
Public orchestration appears before the helpers it calls.
"""

from __future__ import annotations

import json
import os
import platform
import shutil
import signal
import subprocess
import sys
import time
from datetime import datetime, timezone
from fractions import Fraction
from pathlib import Path
from typing import Annotated

import typer

from .artifacts import hash_file, read_json, write_json
from .engine import ROOT, SEED, TARGET, locate_native_library, read_certificate
from .schemas.experiments import (
    ExperimentReport,
    ExperimentRequest,
    ProcessResult,
    SearchMetrics,
)
from .verify import recount

app = typer.Typer(help=__doc__, no_args_is_help=True, pretty_exceptions_enable=False)


def main() -> None:
    app()


@app.command("run")
def run_command(
    out: Annotated[Path, typer.Option()],
    hypothesis: Annotated[str, typer.Option()],
    prediction: Annotated[str, typer.Option()],
    input_path: Annotated[Path, typer.Option("--input")] = SEED,
    strategy: Annotated[Path, typer.Option()] = ROOT
    / "src/k4_ramsey/strategies/edge_descent.py",
    seed: Annotated[int, typer.Option()] = 0,
    seconds: Annotated[float, typer.Option()] = 10.0,
    timeout: Annotated[float, typer.Option()] = 40.0,
    config: Annotated[Path | None, typer.Option()] = None,
) -> None:
    """Run one experiment without scheduling other jobs."""
    request = ExperimentRequest(
        out=out,
        input_path=input_path,
        strategy=strategy,
        hypothesis=hypothesis,
        prediction=prediction,
        seed=seed,
        seconds=seconds,
        timeout=timeout,
        config=read_json(config) if config else {},
    )
    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        report = run_experiment(request).model_dump(
            mode="json", by_alias=True, exclude_none=True
        )
        typer.echo(
            json.dumps(
                {
                    k: report[k]
                    for k in ("status", "evidence", "improvement", "gap_to_mckay")
                    if k in report
                }
            )
        )
        typer.echo(out.resolve() / "report.json")
        if report["status"] != "completed":
            raise typer.Exit(1)
    finally:
        signal.signal(signal.SIGTERM, previous)


@app.command("record-build")
def record_build_command() -> None:
    """Record prebuilt artifact hashes (called by just runner-build)."""
    record_build()
    typer.echo("Native engine and Lean checker build identities recorded.")


@app.command("dashboard")
def dashboard_command(
    reports: Annotated[Path, typer.Option()] = ROOT / "reports",
    out: Annotated[Path, typer.Option()] = ROOT / "journal.html",
) -> None:
    """Render a self-contained snapshot of experiment states."""
    from .dashboard import render

    typer.echo(render(reports, out))


def run_legacy_experiment(
    *,
    out,
    input_path,
    strategy,
    hypothesis,
    prediction,
    seed=0,
    seconds=10.0,
    timeout=40.0,
    config=None,
) -> dict:
    """Compatibility boundary for research callers; use run_experiment internally."""
    request = ExperimentRequest(
        out=Path(out),
        input_path=Path(input_path),
        strategy=Path(strategy),
        hypothesis=hypothesis,
        prediction=prediction,
        seed=seed,
        seconds=seconds,
        timeout=timeout,
        config={} if config is None else config,
    )
    return run_experiment(request).model_dump(
        mode="json", by_alias=True, exclude_none=True
    )


def run_experiment(request: ExperimentRequest) -> ExperimentReport:
    """Run one validated request, preserving failure evidence and reaping children."""
    data = read_certificate(request.input_path)
    strategy = request.strategy.resolve(strict=True)
    out = request.out.resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    deadline = start + request.timeout
    report = ExperimentReport(
        hypothesis=request.hypothesis,
        prediction=request.prediction,
        seed=request.seed,
        search_seconds=request.seconds,
        timeout_seconds=request.timeout,
        started_at=datetime.now(timezone.utc).isoformat(),
        source_input=str(request.input_path.resolve()),
        strategy=str(strategy),
        python=sys.version,
        platform=platform.platform(),
    )
    write_json(out / "status.json", report)
    try:
        source = out / "snapshot"
        report.source_hashes = freeze_sources(source)
        strategy_copy = source / "src/strategy.py"
        shutil.copy2(strategy, strategy_copy)
        report.strategy_sha256 = hash_file(strategy_copy)
        write_json(out / "input.json", data)
        write_json(out / "config.json", request.config)
        report.input_sha256 = hash_file(out / "input.json")
        checker = source / "lean/.lake/build/bin/check_candidate"
        report.baseline = recount(
            data, timeout=remaining_budget(deadline), checker=checker
        )
        report.setup_seconds = time.monotonic() - start
        report.command = strategy_command(request, out, strategy_copy)
        report.status = "searching"
        write_json(out / "status.json", report)
        report.process = supervise(
            report.command,
            cwd=out,
            env=strategy_environment(),
            timeout=search_budget(request, deadline),
            stdout=out / "stdout.log",
            stderr=out / "stderr.log",
        )
        if report.process.status != "completed":
            report.status = report.process.status
            return report
        report.status = "verifying"
        write_json(out / "status.json", report)
        verify_candidate(report, out, source, checker, len(data["red_rows"]), deadline)
    except KeyboardInterrupt:
        report.status = "interrupted"
        report.error = "Interrupted by user or termination signal"
    except subprocess.TimeoutExpired as exc:
        report.status, report.error = "timeout", str(exc)
    except Exception as exc:
        report.status, report.error = "failed", f"{type(exc).__name__}: {exc}"
    finally:
        report.total_seconds = time.monotonic() - start
        ExperimentReport.model_validate(
            report.model_dump(mode="json", by_alias=True, exclude_none=True)
        )
        write_json(out / "status.json", report)
        with (out / "report.json").open("x") as handle:
            json.dump(
                report.model_dump(mode="json", by_alias=True, exclude_none=True),
                handle,
                indent=2,
                allow_nan=False,
            )
            handle.write("\n")
    return report


def verify_candidate(
    report: ExperimentReport,
    out: Path,
    source: Path,
    checker: Path,
    order: int,
    deadline: float,
) -> None:
    """Promote only an unchanged-order candidate recounted against frozen sources."""
    candidate = read_certificate(out / "candidate.json")
    if len(candidate["red_rows"]) != order:
        raise ValueError(
            "this runner requires unchanged order; extend verification contract first"
        )
    metrics_path = out / "search.json"
    raw_metrics = read_json(metrics_path) if metrics_path.exists() else {}
    metrics = SearchMetrics.model_validate(raw_metrics)
    report.search_reported = raw_metrics
    check_snapshot(source, report.source_hashes, report.strategy_sha256)
    checked = recount(
        candidate,
        metrics.numerator,
        timeout=remaining_budget(deadline),
        checker=checker,
    )
    write_json(out / "verification.json", checked)
    candidate_hash = hash_file(out / "candidate.json")
    gap = Fraction(checked.numerator, checked.denominator) - Fraction(TARGET, 768**4)
    assert report.baseline is not None
    report.verification = checked
    report.candidate_sha256 = candidate_hash
    report.improvement = report.baseline.numerator - checked.numerator
    report.gap_to_mckay, report.beats_mckay = str(gap), gap < 0
    report.interpretation = (
        "Verified candidate value; hypothesis interpretation remains for coordinator."
    )
    report.status, report.evidence = "completed", "lean_native_checked"


def record_build() -> dict[str, str]:
    """Record existing build artifacts; just owns all compiler invocations."""
    native = locate_native_library()
    paths = [
        "native/search.cpp",
        "native/search.h",
        "lean/Executables/CheckCandidate.lean",
        "lean/K4Ramsey/Counting/Multiplicity.lean",
        "lean/K4Ramsey/Counting/WeightedMultiplicity.lean",
        "lean/K4Ramsey/Counting/ValidatedTemplate.lean",
        "lean/K4Ramsey/IO/TemplateInput.lean",
        "lean/lean-toolchain",
        "lean/lakefile.toml",
        str(native.relative_to(ROOT)),
        "lean/.lake/build/bin/check_candidate",
        "justfile",
        "scripts/lean.sh",
        "pyproject.toml",
        "uv.lock",
    ]
    manifest = {p: hash_file(ROOT / p) for p in paths}
    write_json(ROOT / "build/experiment-build.json", manifest)
    return manifest


def freeze_sources(destination: Path) -> dict[str, str]:
    """Refuse stale builds and copy a private source/binary/dependency identity."""
    manifest_path = ROOT / "build/experiment-build.json"
    if not manifest_path.exists():
        raise ValueError("Run just runner-build before experiments")
    manifest = read_json(manifest_path)
    for path, expected in manifest.items():
        if hash_file(ROOT / path) != expected:
            raise ValueError(
                f"Stale build: {path}; run just runner-build before dispatch"
            )
    paths = set(manifest)
    paths.update(
        str(p.relative_to(ROOT)) for p in (ROOT / "src/k4_ramsey").rglob("*.py")
    )
    identities = {}
    for path in sorted(paths):
        target = destination / path
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / path, target)
        identities[path] = hash_file(target)
        if path in manifest and identities[path] != manifest[path]:
            raise ValueError(f"Build changed during snapshot: {path}")
    return identities


def check_snapshot(
    source: Path, hashes: dict[str, str], strategy_hash: str | None
) -> None:
    """Detect accidental mutation before accepting a candidate."""
    for path, expected in hashes.items():
        if hash_file(source / path) != expected:
            raise ValueError(f"experiment snapshot was modified: {path}")
    if hash_file(source / "src/strategy.py") != strategy_hash:
        raise ValueError("strategy snapshot was modified")


def strategy_command(request: ExperimentRequest, out: Path, script: Path) -> list[str]:
    """Encode the standalone strategy protocol using the current uv interpreter."""
    return [
        sys.executable,
        str(script),
        "--input",
        str(out / "input.json"),
        "--output",
        str(out / "candidate.json"),
        "--seed",
        str(request.seed),
        "--seconds",
        str(request.seconds),
        "--config",
        str(out / "config.json"),
    ]


def strategy_environment() -> dict[str, str]:
    """Use snapshot imports and keep each native numeric runtime single-threaded."""
    env = os.environ.copy()
    env.pop("PYTHONPATH", None)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    for name in [
        "OMP_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "MKL_NUM_THREADS",
        "VECLIB_MAXIMUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ]:
        env[name] = "1"
    return env


def search_budget(request: ExperimentRequest, deadline: float) -> float:
    """Reserve recount time while allowing two seconds for strategy startup."""
    remaining = remaining_budget(deadline)
    reserve = min(10.0, max(0.0, remaining - request.seconds - 2.0))
    return min(request.seconds + 2.0, remaining - reserve)


def remaining_budget(deadline: float) -> float:
    """Fail before starting another operation when the total budget is spent."""
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise subprocess.TimeoutExpired("experiment", 0)
    return remaining


def run_process(command, *, cwd, env, timeout, stdout, stderr) -> dict:
    """Dictionary adapter for older research callers of the process supervisor."""
    return supervise(
        command, cwd=cwd, env=env, timeout=timeout, stdout=stdout, stderr=stderr
    ).model_dump(exclude={"pid"} if timeout <= 0 else set())


def supervise(
    command: list[str],
    *,
    cwd: Path,
    env: dict[str, str],
    timeout: float,
    stdout: Path,
    stderr: Path,
) -> ProcessResult:
    """Bound one process tree; reap descendants on exit, timeout or interruption."""
    if timeout <= 0:
        return ProcessResult(status="timeout", returncode=None, seconds=0.0)
    started = time.monotonic()
    with Path(stdout).open("w") as out, Path(stderr).open("w") as err:
        proc = subprocess.Popen(
            command, cwd=cwd, env=env, stdout=out, stderr=err, start_new_session=True
        )
        try:
            try:
                code = proc.wait(timeout=timeout)
                status = "completed" if code == 0 else "failed"
            except subprocess.TimeoutExpired:
                status, code = "timeout", None
        finally:
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
    return ProcessResult(
        status=status, returncode=code, pid=proc.pid, seconds=time.monotonic() - started
    )


def interrupt(signum, frame) -> None:
    raise KeyboardInterrupt


# Compatibility names used by older research scripts.
experiment = run_legacy_experiment
prepare = record_build
snapshot = freeze_sources
digest = hash_file


if __name__ == "__main__":
    main()
