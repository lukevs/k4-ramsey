"""Versioned independent weighted recount; never accepted by the unit runner."""
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile
import time

from .engine import ROOT,validate


def validate_weighted(data):
    if not isinstance(data,dict) or set(data)!={'schema','weights','red_rows'}:
        raise ValueError('invalid certificate keys')
    weights=data['weights']
    rows=data['red_rows']
    if not isinstance(rows,list) or not isinstance(weights,list) or len(weights)!=len(rows):
        raise ValueError('weights and rows must be equal-length arrays')
    if any(type(w)is not int or not 1<=w<=65535 for w in weights):
        raise ValueError('weights must be positive integers <=65535')
    # Reuse only schema/adjacency validation, not the unit-weight objective.
    validate(dict(data,weights=[1]*len(rows)))
    return rows,weights


def verify(data,expected_density=None,timeout=120):
    rows,weights=validate_weighted(data)
    checker=ROOT/'lean/.lake/build/bin/check_weighted_candidate'
    if not checker.is_file(): raise RuntimeError('build check_weighted_candidate first')
    started=time.monotonic()
    with tempfile.TemporaryDirectory(prefix='k4-weighted-v1-') as directory:
        matrix=Path(directory)/'weighted.txt'
        matrix.write_text(' '.join(map(str,weights))+'\n'+'\n'.join(rows)+'\n')
        result=subprocess.run([str(checker),str(matrix)],text=True,capture_output=True,check=True,timeout=timeout)
    values=list(map(int,result.stdout.split()))
    if len(values)!=4: raise ValueError('invalid weighted checker output')
    n,total,numerator,denominator=values
    if n!=len(rows) or total!=sum(weights) or denominator!=total**4:
        raise ValueError('weighted checker normalization mismatch')
    density=Fraction(numerator,denominator)
    if expected_density is not None and density!=Fraction(expected_density):
        raise ValueError('weighted checker disagrees with expected density')
    sources=['lean/Executables/WeightedCandidate.lean','lean/K4Ramsey/Counting/WeightedMultiplicity.lean','lean/Tests/WeightedMultiplicity.lean',
             'lean/K4Ramsey/Counting/Multiplicity.lean','lean/lean-toolchain','src/k4_ramsey/weighted_verify.py']
    return dict(schema='k4-weighted-verification-v1',status='lean_native_checked_weighted_v1',
        n=n,total_weight=total,numerator=numerator,denominator=denominator,density=str(density),
        seconds=time.monotonic()-started,checker_binary_sha256=hashlib.sha256(checker.read_bytes()).hexdigest(),
        source_hashes={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in sources},
        scope='Positive integer weights <=65535; order<=1024; symmetric binary graph; blue diagonals.',
        trust='Independent compiled Lean full weighted recount; not a kernel-only proof of the general counting identity or asymptotic bound.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--expected-density')
    args=parser.parse_args()
    data=json.loads(args.input.read_text())
    result=verify(data,args.expected_density)
    result['candidate_sha256']=hashlib.sha256(args.input.read_bytes()).hexdigest()
    result['candidate']=str(args.input.resolve())
    with args.out.open('x') as handle: json.dump(result,handle,indent=2);handle.write('\n')
    print(json.dumps(result,indent=2))


if __name__=='__main__': main()
