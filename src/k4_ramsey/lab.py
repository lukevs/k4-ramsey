"""One isolated experiment. Scheduling belongs to the coordinating session."""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import signal
import subprocess
import sys
import time

from .engine import ROOT, SEED, TARGET, build, load
from .verify import build_checker, verify


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def read_json(path):
    def reject(value):
        raise ValueError(f'nonfinite JSON constant: {value}')
    value = json.loads(Path(path).read_text(), parse_constant=reject)
    # Valid JSON number syntax can still overflow a Python float (e.g. 1e999).
    # Reject it before attaching the data to the durable failure report.
    json.dumps(value, allow_nan=False)
    return value


def write_json(path, data):
    """Atomic replacement for checkpoints and mutable status, not final evidence."""
    path = Path(path)
    temporary = path.with_name(path.name + '.tmp')
    temporary.write_text(json.dumps(data, indent=2, allow_nan=False) + '\n')
    temporary.replace(path)


def prepare():
    native = build()
    build_checker()
    paths = ['native/search.cpp', 'CheckCandidate.lean', 'K4Ramsey/Multiplicity.lean',
             'lean-toolchain', 'lakefile.toml', str(native.relative_to(ROOT)),
             '.lake/build/bin/check_candidate']
    manifest = {p: digest(ROOT/p) for p in paths}
    write_json(ROOT/'build/experiment-build.json', manifest)
    return manifest


def snapshot(destination):
    """Refuse stale binaries; each experiment runs a private copy of the code."""
    manifest_path = ROOT/'build/experiment-build.json'
    if not manifest_path.exists():
        raise ValueError('Run python -m k4_ramsey.lab build before experiments')
    manifest = json.loads(manifest_path.read_text())
    for p, expected in manifest.items():
        if digest(ROOT/p) != expected:
            raise ValueError(f'Stale build: {p}; run lab build again before dispatch')
    paths = set(manifest)
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'src/k4_ramsey').glob('*.py'))
    paths.update(str(p.relative_to(ROOT)) for p in (ROOT/'build').glob('libk4.sha256'))
    identities = {}
    for p in sorted(paths):
        target = destination/p
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT/p, target)
        identities[p] = digest(target)
        if p in manifest and identities[p] != manifest[p]:
            raise ValueError(f'Build changed during snapshot: {p}')
    return identities


def run_process(command, *, cwd, env, timeout, stdout, stderr):
    """Bound one process tree; clean descendants on exit, timeout or interruption."""
    if timeout <= 0:
        return {'status': 'timeout', 'returncode': None, 'seconds': 0}
    started = time.monotonic()
    with Path(stdout).open('w') as out, Path(stderr).open('w') as err:
        proc = subprocess.Popen(command, cwd=cwd, env=env, stdout=out, stderr=err,
                                start_new_session=True)
        try:
            try:
                code = proc.wait(timeout=timeout)
                status = 'completed' if code == 0 else 'failed'
            except subprocess.TimeoutExpired:
                status, code = 'timeout', None
        finally:
            # Even a successful strategy must not leave background compute behind.
            try:
                os.killpg(proc.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            proc.wait()
    return dict(status=status, returncode=code, pid=proc.pid,
                seconds=time.monotonic()-started)


def experiment(*, out, input_path, strategy, hypothesis, prediction, seed=0,
               seconds=10.0, timeout=40.0, config=None):
    for name, value in [('seconds', seconds), ('timeout', timeout)]:
        if not math.isfinite(value) or value <= 0:
            raise ValueError(f'{name} must be positive and finite')
    if timeout <= seconds:
        raise ValueError('timeout must exceed search seconds to leave verification time')
    if not hypothesis.strip() or not prediction.strip():
        raise ValueError('hypothesis and prediction are required')
    data = load(Path(input_path))
    strategy = Path(strategy).resolve(strict=True)
    config = {} if config is None else config
    if not isinstance(config, dict):
        raise ValueError('config must be a JSON object')
    # Validate serialization before creating a run directory.
    json.dumps(config, allow_nan=False)
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    start = time.monotonic()
    deadline = start + timeout
    report = dict(schema='k4-experiment-v1', status='preparing', hypothesis=hypothesis, prediction=prediction,
                  seed=seed, search_seconds=seconds, timeout_seconds=timeout,
                  started_at=datetime.now(timezone.utc).isoformat(),
                  source_input=str(Path(input_path).resolve()), strategy=str(strategy),
                  python=sys.version, platform=platform.platform(),
                  evidence='unverified', official_autolab_report=False)
    write_json(out/'status.json', report)
    try:
        source = out/'snapshot'
        report['source_hashes'] = snapshot(source)
        shutil.copy2(strategy, source/'strategy.py')
        report['strategy_sha256'] = digest(source/'strategy.py')
        write_json(out/'input.json', data)
        write_json(out/'config.json', config)
        report['input_sha256'] = digest(out/'input.json')
        checker = source/'.lake/build/bin/check_candidate'
        report['baseline'] = verify(data, timeout=max(.001, deadline-time.monotonic()), checker=checker)
        report['setup_seconds'] = time.monotonic()-start
        command = [sys.executable, str(source/'strategy.py'), '--input', str(out/'input.json'),
                   '--output', str(out/'candidate.json'), '--seed', str(seed),
                   '--seconds', str(seconds), '--config', str(out/'config.json')]
        env = os.environ.copy()
        env['PYTHONPATH'] = str(source/'src')
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS',
                     'VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS']:
            env[name] = '1'
        report.update(status='searching', command=command)
        write_json(out/'status.json', report)
        # Reserve up to 10 seconds for checking. A cooperative strategy receives
        # its own search duration; the parent also enforces a hard process limit.
        remaining = deadline-time.monotonic()
        if remaining <= 0:
            raise subprocess.TimeoutExpired(command, timeout)
        # Leave startup/serialization grace in the process budget too. Reserving
        # all non-search time can otherwise kill a short run during Python import.
        reserve = min(10.0, max(0.0, remaining-seconds-2.0))
        report['process'] = run_process(command, cwd=out, env=env,
            timeout=min(seconds+2.0, remaining-reserve),
            stdout=out/'stdout.log', stderr=out/'stderr.log')
        report['status'] = report['process']['status']
        if report['status'] != 'completed':
            # Any surviving checkpoint remains explicitly unverified; restarting
            # it is a new experiment, never an implicit successful completion.
            return report
        candidate = load(out/'candidate.json')
        if len(candidate['red_rows']) != len(data['red_rows']):
            raise ValueError('this runner requires unchanged order; extend verification contract first')
        metrics_path = out/'search.json'
        metrics = read_json(metrics_path) if metrics_path.exists() else {}
        if not isinstance(metrics, dict):
            raise ValueError('search.json must be an object')
        report['search_reported'] = metrics
        expected = metrics.get('numerator')
        if expected is not None and (type(expected) is not int or expected < 0):
            raise ValueError('search numerator must be a nonnegative integer')
        report['status'] = 'verifying'
        write_json(out/'status.json', report)
        # Detect accidental source/binary mutation before promotion.
        for p, expected_hash in report['source_hashes'].items():
            if digest(source/p) != expected_hash:
                raise ValueError(f'experiment snapshot was modified: {p}')
        if digest(source/'strategy.py') != report['strategy_sha256']:
            raise ValueError('strategy snapshot was modified')
        checked = verify(candidate, expected, timeout=max(.001, deadline-time.monotonic()), checker=checker)
        write_json(out/'verification.json', checked)
        numerator, denominator = checked['numerator'], checked['denominator']
        gap = Fraction(numerator,denominator) - Fraction(TARGET,768**4)
        report.update(status='completed', evidence='lean_native_checked',
                      verification=checked, candidate_sha256=digest(out/'candidate.json'),
                      improvement=report['baseline']['numerator']-numerator,
                      gap_to_mckay=str(gap), beats_mckay=gap<0,
                      interpretation='Verified candidate value; hypothesis interpretation remains for coordinator.')
    except KeyboardInterrupt:
        report.update(status='interrupted', error='Interrupted by user or termination signal')
    except subprocess.TimeoutExpired as exc:
        report.update(status='timeout', error=str(exc))
    except Exception as exc:
        report.update(status='failed', error=f'{type(exc).__name__}: {exc}')
    finally:
        report['total_seconds'] = time.monotonic()-start
        write_json(out/'status.json', report)
        # Never overwrite evidence from another attempt: out was exclusively created.
        with (out/'report.json').open('x') as handle:
            json.dump(report, handle, indent=2, allow_nan=False)
            handle.write('\n')
    return report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='action', required=True)
    sub.add_parser('build', help='Build once before parallel dispatch; never during active experiments')
    dash = sub.add_parser('dashboard', help='Render a self-contained HTML snapshot of experiment states')
    dash.add_argument('--reports', type=Path, default=ROOT/'reports')
    dash.add_argument('--out', type=Path, default=ROOT/'journal.html')
    run = sub.add_parser('run', help='Run one experiment, without scheduling other jobs')
    run.add_argument('--out', type=Path, required=True)
    run.add_argument('--input', type=Path, default=SEED)
    run.add_argument('--strategy', type=Path, default=ROOT/'experiments/strategies/edge_descent.py')
    run.add_argument('--hypothesis', required=True)
    run.add_argument('--prediction', required=True)
    run.add_argument('--seed', type=int, default=0)
    run.add_argument('--seconds', type=float, default=10)
    run.add_argument('--timeout', type=float, default=40)
    run.add_argument('--config', type=Path)
    args = parser.parse_args()
    if args.action == 'build':
        prepare()
        print('Native engine and Lean checker prepared.')
        return
    if args.action == 'dashboard':
        from .dashboard import render
        render(args.reports, args.out)
        print(args.out.resolve())
        return
    def interrupt(signum, frame):
        raise KeyboardInterrupt
    previous = signal.signal(signal.SIGTERM, interrupt)
    try:
        report = experiment(out=args.out, input_path=args.input, strategy=args.strategy,
            hypothesis=args.hypothesis, prediction=args.prediction, seed=args.seed,
            seconds=args.seconds, timeout=args.timeout,
            config=read_json(args.config) if args.config else {})
        print(json.dumps({k:report[k] for k in ('status','evidence','improvement','gap_to_mckay') if k in report}))
        print(args.out.resolve()/'report.json')
        if report['status'] != 'completed':
            raise SystemExit(1)
    finally:
        signal.signal(signal.SIGTERM, previous)


if __name__ == '__main__':
    main()
