"""Independent Lean native recount; never trusts the search's incremental score."""
from __future__ import annotations

import hashlib
import os
import subprocess
import tempfile
import time
from pathlib import Path

from .engine import ROOT, validate


def verifier_identity():
    paths = ['CheckCandidate.lean', 'K4Ramsey/Multiplicity.lean', 'lean-toolchain',
             'lakefile.toml', 'src/k4_ramsey/verify.py', 'src/k4_ramsey/engine.py']
    return {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths}


def build_checker():
    env = os.environ.copy()
    local = ROOT / '.elan'
    if local.exists():
        env['ELAN_HOME'] = str(local)
        env['PATH'] = str(local/'bin') + os.pathsep + env['PATH']
    subprocess.run(['lake','build','check_candidate'], cwd=ROOT, env=env,
                   check=True, timeout=180)


def verify(data: dict, expected: int | None = None, timeout: float = 30,
           *, checker: Path | None = None) -> dict:
    rows = validate(data)
    checker = checker or ROOT / '.lake/build/bin/check_candidate'
    if not checker.exists():
        raise RuntimeError('build checker first: python -m k4_ramsey.lab build')
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='k4-verify-') as directory:
        matrix = Path(directory) / 'rows.txt'
        matrix.write_text('\n'.join(rows)+'\n')
        command = [str(checker),str(matrix)]
        if expected is not None:
            command.append(str(expected))
        result = subprocess.run(command, text=True, capture_output=True,
                                check=True, timeout=timeout)
    values = list(map(int,result.stdout.strip().split()))
    if len(values) != 7:
        raise ValueError('malformed checker output')
    n, numerator, denominator, edges, triangles, red4, blue4 = values
    if n != len(rows) or denominator != n**4 or (expected is not None and numerator != expected):
        raise ValueError('checker disagrees with search')
    from fractions import Fraction
    density = Fraction(numerator,denominator)
    return dict(status='lean_native_checked', n=n, numerator=numerator,
                denominator=denominator, density=str(density), red_edges=edges,
                blue_triangles=triangles, red_k4=red4, blue_k4=blue4,
                seconds=time.monotonic()-started,
                checker_binary_sha256=hashlib.sha256(checker.read_bytes()).hexdigest(),
                trust='Compiled Lean execution; not a kernel-only proof of c4 bound')
