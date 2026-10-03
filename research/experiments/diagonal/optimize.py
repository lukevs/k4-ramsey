"""Exact all-diagonal optimization for fixed unit-weight off-diagonal graphs."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import time
import shutil

from k4_ramsey.engine import Graph,load
from k4_ramsey.lab import write_json
from k4_ramsey.verify import verify
from k4_ramsey.engine import ROOT


def triangle_incidence(neighbors):
    result=[]
    for mask in neighbors:
        remaining=mask
        twice=0
        while remaining:
            bit=remaining & -remaining
            v=bit.bit_length()-1
            twice+=(neighbors[v]&mask).bit_count()
            remaining-=bit
        result.append(twice//2)
    return result


def coefficients(rows):
    n=len(rows)
    full=(1<<n)-1
    red=[sum(1<<j for j,c in enumerate(row) if j!=i and c=='1') for i,row in enumerate(rows)]
    blue=[full^mask^(1<<i) for i,mask in enumerate(red)]
    tr,tb=triangle_incidence(red),triangle_incidence(blue)
    dr,db=[mask.bit_count() for mask in red],[mask.bit_count() for mask in blue]
    linear=[4*dr[i]-10*db[i]+12*(tr[i]-tb[i]) for i in range(n)]
    return linear,dict(red_degrees=dr,blue_degrees=db,red_triangles_at=tr,blue_triangles_at=tb)


def optimize(rows):
    """Return exact minimum relative to the all-blue-diagonal baseline."""
    linear,counts=coefficients(rows)
    ranked=sorted(range(len(rows)),key=lambda i:(linear[i],i))
    prefix=0
    best=0
    best_k=0
    by_count=[0]
    for k,i in enumerate(ranked,1):
        prefix+=linear[i]
        value=prefix+3*k*(k-1)
        by_count.append(value)
        if value<best: best,best_k=value,k
    return dict(delta=best,red_loop_vertices=ranked[:best_k],red_loop_count=best_k,
                all_blue_is_optimal=best==0,linear=linear,minimum_delta_by_red_count=by_count,
                counts=counts)


def screen(inputs,out):
    started_at=datetime.now(timezone.utc).isoformat()
    out=Path(out).resolve()
    out.mkdir(parents=True,exist_ok=False)
    shutil.copy2(Path(__file__),out/'source_snapshot.py')
    records=[]
    for index,input_path in enumerate(inputs):
        start=time.monotonic()
        data=load(Path(input_path))
        graph=Graph(data)
        baseline=graph.counts()['numerator']
        baseline_check=verify(data,baseline)
        result=optimize(data['red_rows'])
        rows=[list(row) for row in data['red_rows']]
        for i in result['red_loop_vertices']: rows[i][i]='1'
        candidate=dict(data,red_rows=[''.join(row) for row in rows])
        candidate_path=out/f'candidate-{index:03d}.json'
        write_json(candidate_path,candidate)
        records.append(dict(input=str(Path(input_path).resolve()),
            input_sha256=hashlib.sha256(Path(input_path).read_bytes()).hexdigest(),
            baseline_numerator=baseline,minimum_numerator=baseline+result['delta'],denominator=graph.n**4,
            baseline_check=baseline_check,
            **result,seconds=time.monotonic()-start,candidate=str(candidate_path),
            candidate_sha256=hashlib.sha256(candidate_path.read_bytes()).hexdigest()))
        graph.close()
    report=dict(schema='k4-diagonal-screen-v1',status='completed',started_at=started_at,
        hypothesis='H10: exact optimization of all loop colors can improve the fixed off-diagonal incumbent',
        evidence='algebraic_exact_search_with_tiny_oracle_tests_not_independent_mixed_diagonal_check',
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),records=records,
        source_hashes={name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest() for name in ['native/search.cpp','src/k4_ramsey/engine.py','src/k4_ramsey/verify.py']},
        scope='Unit weights; arbitrary fixed off-diagonal symmetric coloring; all diagonal assignments. No global graph optimum.',
        promotion='Any changed-diagonal candidate requires a separately versioned independent checker before promotion.')
    write_json(out/'report.json',report)
    return report


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input',nargs='+',type=Path,required=True)
    parser.add_argument('--out',type=Path,required=True)
    args=parser.parse_args()
    result=screen(args.input,args.out)
    print(json.dumps([{k:r[k] for k in ('input','baseline_numerator','minimum_numerator','delta','red_loop_count','seconds')} for r in result['records']],indent=2))


if __name__=='__main__': main()
