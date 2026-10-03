"""Exact historical k=10 shell control and one motivated continuous descent."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from research.experiments.hamming_scheme.screen import (
    FRANEK, census, exact_numerator, objective_gradient, write_json,
)


ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/"reports/hamming-scheme-k10-002"
K=10
DEN=65536


def main():
    start=time.monotonic();OUT.mkdir(parents=True,exist_ok=False);shutil.copy2(__file__,OUT/"source_snapshot.py")
    build=time.monotonic();hist=census(K);build_seconds=time.monotonic()-build
    # Franek--Rodl's asymptotic construction blows every core vertex up to a
    # red clique.  Thus distance zero is red even though the finite core graph
    # itself has no loops.  Both Z3 rows are identical, so the three copies of
    # each binary label merge into one red macroclass.
    binary=[DEN if d == 0 or d in FRANEK else 0 for row in range(2) for d in range(K+1)]
    binary_numerator=exact_numerator(hist,binary,DEN);normalization=(3*2**K)**3*DEN**6
    binary_density=Fraction(binary_numerator,normalization)
    x=[value/DEN for value in binary];m=[0.0]*len(x);v=[0.0]*len(x);best=(float(binary_density),list(x));history=[]
    opt=time.monotonic()
    for iteration in range(1,701):
        value,gradient=objective_gradient(x,hist,3*2**K)
        if value<best[0]:best=(value,list(x))
        rate=.035*(.2+.8*(1-iteration/700))
        for i,g in enumerate(gradient):
            m[i]=.9*m[i]+.1*g;v[i]=.999*v[i]+.001*g*g
            mh=m[i]/(1-.9**iteration);vh=v[i]/(1-.999**iteration)
            x[i]=max(0.0,min(1.0,x[i]-rate*mh/(vh**.5+1e-10)))
        if iteration in (1,50,100,200,400,700):history.append(dict(iteration=iteration,density=value,gradient_inf=max(abs(g) for g in gradient)))
    opt_seconds=time.monotonic()-opt
    best_value,best_parameters=best
    report=dict(schema="hamming-k10-historical-control-v1",status="completed",
        rule="red iff Hamming distance is 0 or in {1,3,4,7,8,10}; both Z3 rows identical; distance 0 implements the red-clique blow-up",
        complement_invariance="Reversing the paper edge convention complements every q and leaves red-K4 plus blue-K4 unchanged",
        k=K,group_order=3*2**K,census_states=27*19448,histogram_bins=len(hist),histogram_mass=sum(hist.values()),
        build_seconds=build_seconds,binary_numerator=binary_numerator,normalization=normalization,
        binary_density=str(binary_density),binary_decimal=float(binary_density),
        optimization="one dependency-free projected-Adam trajectory initialized at the exact historical binary rule",
        optimized_numerical_density=best_value,optimized_parameters=best_parameters,
        history=history,optimization_seconds=opt_seconds,total_seconds=time.monotonic()-start,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        evidence="Exact coordinate-count census for historical binary control; numerical continuous follow-up only",
        scope="Corrected historical red-clique blow-up sanity check, not exhaustive Hamming-shell optimization")
    write_json(OUT/"report.json",report)
    print(json.dumps({k:report[k] for k in ("binary_density","binary_decimal","optimized_numerical_density","histogram_bins","build_seconds","optimization_seconds")},indent=2))


if __name__=="__main__":main()
