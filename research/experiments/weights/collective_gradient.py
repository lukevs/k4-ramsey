"""Collective fixed-mass directions with exact quartic interpolation and recount."""
import argparse
from datetime import datetime, timezone
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from research.experiments.weights.pair_transfer import features
from k4_ramsey.engine import Graph, load
from k4_ramsey.lab import write_json
from k4_ramsey.weighted_verify import verify


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def gradient_direction(gradient, amplitude=32):
    """Round a centered negative gradient, then enforce exactly zero total mass."""
    n = len(gradient)
    centered = [n*g-sum(gradient) for g in gradient]
    scale = max(map(abs, centered), default=0)
    if not scale:
        return [0]*n
    direction = [int(Fraction(-amplitude*g, scale)) for g in centered]
    remainder = sum(direction)
    order = sorted(range(n), key=lambda i: gradient[i], reverse=remainder > 0)
    for i in order[:abs(remainder)]:
        direction[i] -= 1 if remainder > 0 else -1
    if sum(direction):
        raise RuntimeError('direction does not preserve total mass')
    return direction


def differences(values):
    if len(values) != 5:
        raise ValueError('five values required for quartic interpolation')
    result = []
    row = list(values)
    while row:
        result.append(row[0])
        row = [b-a for a,b in zip(row,row[1:])]
    return result


def evaluate(coefficients, step):
    """Newton forward polynomial, exact for every integer step."""
    choose = Fraction(1)
    result = Fraction(0)
    for k,c in enumerate(coefficients):
        if k:
            choose *= Fraction(step-k+1,k)
        result += c*choose
    return result


def screen(input_path, out, *, base=1024, amplitude=32, seconds=90, direction_builder=None):
    started = time.monotonic()
    deadline = started+seconds
    out = Path(out).resolve()
    out.mkdir(parents=True, exist_ok=False)
    input_path = Path(input_path).resolve()
    source = Path(__file__).resolve()
    shutil.copy2(source,out/'source_snapshot.py')
    shutil.copy2(input_path,out/'input.json')
    report = dict(schema='k4-collective-weight-v1', status='preparing',
                  hypothesis='H-CW1: a collective gradient mass direction improves the graph',
                  prediction='A positive fixed-total-weight point on the gradient line has lower exact density',
                  started_at=datetime.now(timezone.utc).isoformat(), input=str(input_path),
                  input_sha256=digest(input_path), source_sha256=digest(source),
                  feature_source_sha256=digest(Path(__file__).with_name('pair_transfer.py')),
                  evidence='unverified', base=base, amplitude=amplitude, seconds_limit=seconds)
    write_json(out/'status.json',report)
    try:
        data = load(input_path)
        graph = Graph(data)
        try:
            f = features(graph)
        finally:
            graph.close()
        gradient = [28*d+48*t+24*k for d,t,k in zip(f['db'],f['tb'],f['k4'])]
        if direction_builder is None:
            direction = gradient_direction(gradient,amplitude)
        else:
            direction,diagnostics = direction_builder(f,gradient,amplitude)
            report.update(hypothesis='H-CW2: collective curvature-informed mass optimization improves the graph',
                          direction_diagnostics=diagnostics)
            write_json(out/'direction-diagnostics.json',diagnostics)
        if len(direction)!=len(gradient) or sum(direction) or any(type(d)is not int for d in direction):
            raise RuntimeError('invalid fixed-mass direction')
        write_json(out/'direction.json',dict(gradient=gradient,direction=direction))
        if not any(direction):
            report.update(status='completed', decision='No first-order direction: all gradients equal')
            return report
        max_step = min((base-1)//-d if d<0 else (65535-base)//d for d in direction if d)
        if max_step<5:
            raise ValueError('base too small for five positive-weight interpolation points and holdout')
        total = len(direction)*base
        def checked(step, expected=None):
            remaining = deadline-time.monotonic()
            if remaining<=0:
                raise TimeoutError('collective screen deadline')
            candidate = dict(data,weights=[base+step*d for d in direction])
            result = verify(candidate,expected_density=expected,timeout=min(30,remaining))
            if result['total_weight'] != total:
                raise RuntimeError('fixed mass changed')
            return candidate,result
        samples=[]
        report['status']='searching'
        write_json(out/'status.json',report)
        for step in range(5):
            _,recount=checked(step)
            samples.append(recount)
            write_json(out/'interpolation-counts.json',samples)
        if samples[0]['numerator'] != f['numerator']*base**4:
            raise RuntimeError('unit baseline differs from weighted recount')
        polynomial=differences([sample['numerator'] for sample in samples])
        step=min(range(max_step+1),key=lambda s:evaluate(polynomial,s))
        expected=evaluate(polynomial,step)/total**4
        candidate,recount=checked(step,expected)
        # Extrapolated sixth point protects the interpolation beyond fitted samples.
        _,holdout=checked(5,evaluate(polynomial,5)/total**4)
        write_json(out/'holdout-verification.json',holdout)
        candidate_path=out/'candidate-weighted.json'
        write_json(candidate_path,candidate)
        recount.update(candidate=str(candidate_path),candidate_sha256=digest(candidate_path))
        write_json(out/'weighted-verification-v1.json',recount)
        improvement=Fraction(f['numerator'])-expected*len(direction)**4
        report.update(status='completed',evidence='lean_native_checked_weighted_v1',
                      baseline_numerator=f['numerator'],n=len(direction),
                      direction_nonzero=sum(d!=0 for d in direction),
                      directional_derivative=sum(g*d for g,d in zip(gradient,direction)),
                      max_step=max_step,selected_step=step,forward_coefficients=polynomial,
                      best_density=str(expected),improvement_fixed_n4=str(improvement),
                      decision='Supported on this parent' if improvement>0 else 'No positive gain on this direction grid',
                      limitation='Exact integer line grid only; not full weight-space optimization. Interpolation uses Lean as the objective oracle; final recount is separate from interpolation, not a second Lean implementation.')
    except Exception as error:
        report.update(status='failed',error=f'{type(error).__name__}: {error}')
    finally:
        report.update(total_seconds=time.monotonic()-started,
                      finished_at=datetime.now(timezone.utc).isoformat())
        write_json(out/'status.json',report)
        with (out/'report.json').open('x') as handle:
            json.dump(report,handle,indent=2)
            handle.write('\n')
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    parser.add_argument('--base',type=int,default=1024)
    parser.add_argument('--amplitude',type=int,default=32)
    parser.add_argument('--seconds',type=float,default=90)
    args=parser.parse_args()
    if not 1<=args.base<=65535 or args.amplitude<1 or args.seconds<=0:
        raise ValueError('invalid positive-weight search configuration')
    result=screen(args.input,args.out,base=args.base,amplitude=args.amplitude,seconds=args.seconds)
    print(json.dumps(result,indent=2))
    raise SystemExit(result['status']!='completed')


if __name__=='__main__':
    main()
