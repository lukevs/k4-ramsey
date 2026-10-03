"""Exact Hamming census plus numerical shell-probability optimization."""

from collections import Counter
from fractions import Fraction
from itertools import product
from math import comb, factorial
import hashlib
import json
from pathlib import Path
import shutil
import time
import random


ROOT=Path(__file__).resolve().parents[3]
HERE=Path(__file__).resolve().parent
OUT=ROOT/"reports/hamming-scheme-002"
CURRENT=Fraction(66019395791930410328084302012171,2190500237194380405786303138889728)
EDGES=((0,1),(0,2),(0,3),(1,2),(1,3),(2,3))
FRANEK={1,3,4,7,8,10}


def write_json(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")
def sha256(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def compositions(total,parts,prefix=()):
    if parts==1:
        yield prefix+(total,);return
    for value in range(total+1):yield from compositions(total-value,parts-1,prefix+(value,))


COLUMN_DIST=[]
for mask in range(8):
    bits=(0,(mask>>2)&1,(mask>>1)&1,mask&1)
    COLUMN_DIST.append(tuple(bits[i]^bits[j] for i,j in EDGES))


def census(k):
    """Sorted six-relation histogram after fixing the first group element."""
    answer=Counter();fact=factorial(k)
    for counts in compositions(k,8):
        multiplicity=fact
        for count in counts:multiplicity//=factorial(count)
        distances=tuple(sum(counts[b]*COLUMN_DIST[b][e] for b in range(8)) for e in range(6))
        for a,b,c in product(range(3),repeat=3):
            z=(0,a,b,c)
            ids=tuple(sorted((int(z[u]!=z[v])*(k+1)+distances[e]) for e,(u,v) in enumerate(EDGES)))
            answer[ids]+=multiplicity
    assert sum(answer.values())==(3*(2**k))**3
    return answer


def literal_census(k):
    answer=Counter();vectors=range(2**k)
    for u,v,w in product(vectors,repeat=3):
        binary=(0,u,v,w)
        distances=tuple((binary[i]^binary[j]).bit_count() for i,j in EDGES)
        for a,b,c in product(range(3),repeat=3):
            z=(0,a,b,c)
            ids=tuple(sorted(int(z[i]!=z[j])*(k+1)+distances[e] for e,(i,j) in enumerate(EDGES)))
            answer[ids]+=1
    return answer


def objective_gradient(parameters,histogram,group_order):
    objective=0.0;gradient=[0.0]*len(parameters)
    for ids,count in histogram.items():
        values=[parameters[i] for i in ids]
        red=blue=1.0
        for value in values:red*=value;blue*=1-value
        objective+=count*(red+blue)
        for edge,relation in enumerate(ids):
            red_other=blue_other=1.0
            for other,value in enumerate(values):
                if other!=edge:red_other*=value;blue_other*=1-value
            gradient[relation]+=count*(red_other-blue_other)
    scale=1/(group_order**3)
    return objective*scale,[x*scale for x in gradient]


def exact_numerator(histogram,numerators,denominator):
    total=0
    for ids,count in histogram.items():
        red=blue=1
        for relation in ids:
            value=numerators[relation];red*=value;blue*=denominator-value
        total+=count*(red+blue)
    return total


def tiny_tests():
    results=[]
    for k in range(4):
        compact=census(k);literal=literal_census(k);assert compact==literal
        denominator=7;numerators=[(3*i+2)%8 for i in range(2*(k+1))]
        numerators=[min(denominator,x) for x in numerators]
        exact=exact_numerator(compact,numerators,denominator)
        numeric,_=objective_gradient([x/denominator for x in numerators],compact,3*2**k)
        rational=Fraction(exact,(3*2**k)**3*denominator**6)
        assert abs(numeric-float(rational))<1e-14
        results.append(dict(k=k,histogram_bins=len(compact),mass=sum(compact.values()),density=str(rational)))
    return results


def seeds(k):
    binary=[1.0 if d in FRANEK else 0.0 for row in range(2) for d in range(k+1)]
    rng=random.Random(20260927+k)
    alternating=[0.8 if (d+row)%2 else 0.2 for row in range(2) for d in range(k+1)]
    return [("franek_binary",binary),("franek_soft",[.05+.9*x for x in binary]),
            ("random_a",[rng.uniform(.15,.85) for _ in range(2*(k+1))]),
            ("random_b",[rng.uniform(.15,.85) for _ in range(2*(k+1))]),
            ("alternating",alternating)]


def optimize_dimension(k,histogram):
    order=3*2**k;records=[]
    for name,initial in seeds(k):
        started=time.monotonic();x=list(initial);m=[0.0]*len(x);v=[0.0]*len(x);best=(float("inf"),list(x));stale=0
        for iteration in range(1,601):
            value,gradient=objective_gradient(x,histogram,order)
            if value<best[0]-1e-16:best=(value,list(x));stale=0
            else:stale+=1
            rate=.035*(.2+.8*(1-iteration/600))
            for i,g in enumerate(gradient):
                m[i]=.9*m[i]+.1*g;v[i]=.999*v[i]+.001*g*g
                mh=m[i]/(1-.9**iteration);vh=v[i]/(1-.999**iteration)
                x[i]=max(0.0,min(1.0,x[i]-rate*mh/(vh**.5+1e-10)))
            if stale>=80:break
        x=best[1];value,gradient=objective_gradient(x,histogram,order)
        records.append(dict(seed=name,density=value,parameters=x,success=True,message="projected_adam",
                            iterations=iteration,seconds=time.monotonic()-started,
                            gradient_inf=max(abs(g) for g in gradient)))
    return min(records,key=lambda r:r["density"]),records


def rational_polish(histogram,parameters,k,denominator=65536):
    numerators=[max(0,min(denominator,round(x*denominator))) for x in parameters]
    current=exact_numerator(histogram,numerators,denominator);passes=[]
    for sweep in range(20):
        moves=0
        for i in range(len(numerators)):
            best_value=current;best=numerators[i]
            for trial in (best-1,best+1):
                if not 0<=trial<=denominator:continue
                proposal=list(numerators);proposal[i]=trial
                value=exact_numerator(histogram,proposal,denominator)
                if value<best_value:best_value,best=value,trial
            if best!=numerators[i]:numerators[i]=best;current=best_value;moves+=1
        passes.append(dict(sweep=sweep+1,moves=moves,numerator=current))
        if moves==0:break
    density=Fraction(current,(3*2**k)**3*denominator**6)
    return numerators,current,density,passes


def main():
    start=time.monotonic();OUT.mkdir(parents=True,exist_ok=False)
    shutil.copy2(__file__,OUT/"source_snapshot.py");shutil.copy2(HERE/"preregistration.json",OUT/"preregistration.json")
    tiny=tiny_tests();dimensions=[];histograms={}
    for k in (6,7,8):
        build=time.monotonic();hist=census(k);build_seconds=time.monotonic()-build;histograms[k]=hist
        best,runs=optimize_dimension(k,hist)
        dimensions.append(dict(k=k,group_order=3*2**k,census_states=27*comb(k+7,7),
            histogram_bins=len(hist),histogram_mass=sum(hist.values()),build_seconds=build_seconds,best=best,runs=runs))
    best_dimension=min(dimensions,key=lambda x:x["best"]["density"]);promising=best_dimension["best"]["density"]<float(CURRENT)
    exact=None
    if promising:
        k=best_dimension["k"]
        numerators,numerator,density,passes=rational_polish(histograms[k],best_dimension["best"]["parameters"],k)
        exact=dict(k=k,probability_denominator=65536,red_probability_numerators_by_z3row_distance=[numerators[:k+1],numerators[k+1:]],
            numerator=numerator,normalization=(3*2**k)**3*65536**6,density=str(density),decimal=float(density),
            polish=passes,beats_current=density<CURRENT)
        write_json(OUT/"construction.json",dict(schema="z3-f2-hamming-graphon-v1",k=k,
            probability_denominator=65536,red_probability_numerators_by_z3row_distance=exact["red_probability_numerators_by_z3row_distance"]))
        exact["construction_sha256"]=sha256(OUT/"construction.json")
        # A fresh exact pass through the immutable histogram checks the retained
        # rational point; independent implementation remains checker-lane work.
        assert exact_numerator(histograms[k],numerators,65536)==numerator
    report=dict(schema="hamming-scheme-screen-v1",status="rational_candidate" if exact and exact["beats_current"] else "completed_no_admission",
        hypothesis="Fractional Z3 x F2^k Hamming-shell relations improve structured Ramsey graphons",
        tiny_tests=tiny,dimensions=dimensions,current_comparison=str(CURRENT),retained_exact=exact,
        total_seconds=time.monotonic()-start,source_sha256=sha256(Path(__file__)),
        evidence="Exact census validated literally at k<=3; numerical L-BFGS-B exploration; retained point exact rational census if admitted",
        scope="2(k+1)-parameter uniform Hamming shells only; no quadratic-form or syndrome refinement")
    write_json(OUT/"report.json",report)
    print(json.dumps({"status":report["status"],"best_by_dimension":[(x["k"],x["best"]["density"],x["best"]["seed"]) for x in dimensions],"retained_exact":exact},indent=2))


if __name__=="__main__":main()
