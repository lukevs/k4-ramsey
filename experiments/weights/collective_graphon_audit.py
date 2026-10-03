"""Adversarial artifact audit and standalone bounded Lean recount of simple graphon."""
import argparse
from datetime import datetime,timezone
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

from k4_ramsey.lab import write_json


ROOT=Path(__file__).resolve().parents[2]


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def payload(matrix,q):
    return f'{len(matrix)} {q}\n'+'\n'.join(' '.join(map(str,row))for row in matrix)+'\n'


def literal(matrix,q):
    total=0
    for vertices in itertools.product(range(len(matrix)),repeat=4):
        red=blue=1
        for i,j in itertools.combinations(range(4),2):
            p=matrix[vertices[i]][vertices[j]]
            red*=p;blue*=q-p
        total+=red+blue
    return total


def validate(candidate):
    if candidate.get('schema')!='rational-step-graphon-v1': raise ValueError('unknown schema')
    matrix=candidate['red_probability_numerators'];q=candidate['edge_probability_denominator'];n=len(matrix)
    if type(q)is not int or q<=0 or not 1<=n<=192: raise ValueError('invalid n/q')
    if candidate['block_weights'] != [1]*n: raise ValueError('unit block weights required')
    for i,row in enumerate(matrix):
        if len(row)!=n or any(type(p)is not int or not 0<=p<=q for p in row): raise ValueError('invalid probability')
        if row[i]!=0: raise ValueError('expected blue block diagonals')
        if any(row[j]!=matrix[j][i]for j in range(n)): raise ValueError('asymmetric matrix')
    return matrix,q


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--simple',type=Path,required=True)
    parser.add_argument('--precision',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args();started=time.monotonic()
    args.out=args.out.resolve();args.out.mkdir(parents=True,exist_ok=False)
    report=dict(status='running',started_at=datetime.now(timezone.utc).isoformat(),
                hypothesis='Adversarial graphon artifact, arithmetic, and independent Lean audit')
    write_json(args.out/'status.json',report)
    env=dict(os.environ,ELAN_HOME=str(ROOT/'.elan'))
    lake=ROOT/'.elan/bin/lake'
    source=Path(__file__).with_suffix('.lean')
    shutil.copy2(source,args.out/'source_snapshot.lean')
    shutil.copy2(Path(__file__),args.out/'driver_snapshot.py')
    binary=args.out/'lean_graphon_audit'
    try:
        artifacts=[]
        for path in (args.simple,args.precision):
            candidate=json.loads(path.read_text());matrix,q=validate(candidate);n=len(matrix)
            bound=n**4*q**6
            audit=json.loads((path.parent/'independent-audit.json').read_text())
            original=json.loads((path.parent/'report.json').read_text())
            if audit['candidate_sha256']!=digest(path): raise RuntimeError('candidate SHA mismatch')
            if audit['denominator']!=bound or audit['total']!=original['numerator']:
                raise RuntimeError('exact denominator/numerator mismatch')
            density=Fraction(audit['total'],bound)
            if density!=Fraction(original['density']): raise RuntimeError('reduced density mismatch')
            if bound>=2**127: raise RuntimeError('signed128 total bound unsafe')
            artifacts.append(dict(path=str(path.resolve()),candidate_sha256=digest(path),n=n,q=q,
                                  denominator=bound,density=str(density),
                                  numerator=audit['total'],signed128_bound_passed=True,
                                  diagonal_blue=True,symmetric=True,probabilities_in_range=True))
        report['artifact_audits']=artifacts
        subprocess.run([str(lake),'env','lean','-c',str(args.out/'audit.c'),str(source)],
                       env=env,check=True,capture_output=True,text=True,timeout=45)
        subprocess.run([str(lake),'env','leanc','-O3',str(args.out/'audit.c'),'-o',str(binary)],
                       env=env,check=True,capture_output=True,text=True,timeout=45)
        def run(matrix,q):
            path=args.out/'scratch-matrix.txt';path.write_text(payload(matrix,q))
            output=subprocess.check_output([str(binary),str(path)],text=True,timeout=50)
            return list(map(int,output.split()))
        rng=random.Random(90927);fixtures=0
        for n in range(1,5):
            for _ in range(5):
                q=3;matrix=[[0]*n for _ in range(n)]
                for i in range(n):
                    for j in range(i+1):matrix[i][j]=matrix[j][i]=rng.randrange(q+1)
                red,blue,total,denominator=run(matrix,q)
                if total!=literal(matrix,q) or denominator!=n**4*q**6 or red+blue!=total:
                    raise RuntimeError('tiny ordered-tuple disagreement')
                fixtures+=1
        simple=json.loads(args.simple.read_text());matrix,q=validate(simple)
        red,blue,total,denominator=run(matrix,q)
        if total!=artifacts[0]['numerator'] or denominator!=artifacts[0]['denominator']:
            raise RuntimeError('full simple Lean disagreement')
        report.update(status='completed',evidence='independent_standalone_compiled_lean_simple_graphon_recount',
                      tiny_fixtures_passed=fixtures,lean_simple=dict(red=red,blue=blue,total=total,
                      denominator=denominator,density=str(Fraction(total,denominator))),
                      binary_sha256=digest(binary),source_sha256=digest(source),
                      trust='Compiled Lean exact bounded arithmetic; no kernel proof of count formula or probabilistic realization. Precision candidate has two C++ counters plus artifact/overflow audit, not this Lean recount.')
    except Exception as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}')
        if isinstance(error,subprocess.CalledProcessError):
            report['compiler_stderr']=error.stderr
            report['compiler_stdout']=error.stdout
    finally:
        report['seconds']=time.monotonic()-started
        write_json(args.out/'status.json',report)
        with (args.out/'report.json').open('x')as handle:json.dump(report,handle,indent=2);handle.write('\n')
    print(json.dumps(report,indent=2))
    raise SystemExit(report['status']!='completed')


if __name__=='__main__':main()
