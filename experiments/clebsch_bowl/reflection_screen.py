"""Exact admissibility screen for proper-subset latent reflections on Z5 parent.

At one coarse class, Q_S=2J/|S|-I on subset S fixes constants and is
orthogonal. Transforming incident centered kernels on that endpoint preserves
all closed-walk traces. Test the probability box exactly before any recount.
"""
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time
import numpy as np

root=Path(__file__).resolve().parents[2]
source=root/'reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json'
out=Path(sys.argv[1]); out.mkdir(exist_ok=False)
t0=time.time(); d=json.loads(source.read_text())
N=np.array(d['red_probability_numerators'],dtype=np.int64); Q=int(d['edge_probability_denominator'])
assert len(N)==960 and len(set(d['block_weights']))==1
counts={}; best_violation=None; nontrivial=[]
for size in (3,4,5):
    row=dict(tested=0,admissible=0,row_permutation_only=0,nontrivial=0)
    for u in range(192):
        assert not N[5*u:5*u+5,5*u:5*u+5].any()
        for subset in itertools.combinations(range(5),size):
            ids=5*u+np.array(subset)
            block=N[ids]
            transformed=2*block.sum(axis=0)[None,:]-size*block
            row['tested']+=1
            violation=int(max(0,-int(transformed.min()),int(transformed.max())-size*Q))
            if violation:
                if best_violation is None or violation/size < best_violation['excess_in_numerator_units']:
                    best_violation=dict(coarse=u,subset=list(subset),excess_in_numerator_units=violation/size)
                continue
            row['admissible']+=1
            # Sorting the complete incident rows detects a pure label change.
            before=sorted(map(tuple,(size*block).tolist()))
            after=sorted(map(tuple,transformed.tolist()))
            if before==after:
                row['row_permutation_only']+=1
            else:
                row['nontrivial']+=1
                nontrivial.append(dict(coarse=u,subset=list(subset)))
    counts[str(size)]=row
result=dict(source=str(source.relative_to(root)),sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
            counts=counts,nontrivial=nontrivial,best_rejected=best_violation,
            elapsed_seconds=time.time()-t0,evidence='exact integer box test and exact row-permutation test; no objective improvement claimed')
(out/'report.json').write_text(json.dumps(result,indent=2)+'\n')
(out/'source_snapshot.py').write_text(Path(__file__).read_text())
print(json.dumps(result,indent=2))
