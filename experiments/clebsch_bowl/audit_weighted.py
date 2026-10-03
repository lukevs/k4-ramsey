"""Independent all-root weighted K4 evaluator for size/weight pilot checks."""
import os
for key in ('VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):
    os.environ[key]='1'
import argparse
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import signal
import time
import numpy as np


def density(W, weights):
    W=np.asarray(W,dtype=float)
    w=np.asarray(weights,dtype=float); w=w/w.sum()
    assert np.all(w>=0) and np.all((W>=0)&(W<=1)) and np.array_equal(W,W.T)
    total=0.
    for U in (W,1-W):
        for a in range(len(W)):
            if w[a]==0: continue
            V=U*U[a][None,:]
            Y=(V*w[None,:])@U
            rooted=np.einsum('bd,bd,d->b',V,Y,w)
            total+=w[a]*np.dot(w*U[a],rooted)
    return float(total)


def literal(N,Q,weights):
    total=0
    for ids in itertools.product(range(len(N)),repeat=4):
        red=blue=1; weight=1
        for a in ids: weight*=int(weights[a])
        for i,j in itertools.combinations(range(4),2):
            v=int(N[ids[i],ids[j]]); red*=v; blue*=Q-v
        total+=weight*(red+blue)
    return Fraction(total,sum(map(int,weights))**4*Q**6)


def selfcheck():
    rng=np.random.default_rng(768192)
    errs=[]; split=[]; deleted=[]
    for n in range(1,7):
        for _ in range(4):
            Q=13; N=rng.integers(Q+1,size=(n,n)); N=np.triu(N)+np.triu(N,1).T
            w=rng.integers(1,8,size=n)
            f=density(N/Q,w); errs.append(abs(f-float(literal(N,Q,w))))
            # Unequal subdivision, retaining ALL within-parent entries.
            mapping=np.repeat(np.arange(n),2)
            splitw=np.column_stack([w,2*w]).ravel()
            split.append(abs(f-density((N/Q)[np.ix_(mapping,mapping)],splitw)))
            if n>1:
                wz=w.copy(); wz[0]=0
                deleted.append(abs(density(N/Q,wz)-density(N[1:,1:]/Q,w[1:])))
    assert max(errs+split+deleted)<2e-14
    return dict(fixtures=len(errs),max_literal_error=max(errs),max_duplication_error=max(split),max_zero_weight_deletion_error=max(deleted))


if __name__=='__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--candidate'); parser.add_argument('--out',required=True)
    args=parser.parse_args(); signal.alarm(180); t0=time.time()
    result={'validation':selfcheck()}
    if args.candidate:
        path=Path(args.candidate); d=json.loads(path.read_text()); Q=int(d['edge_probability_denominator'])
        N=np.asarray(d['red_probability_numerators'],dtype=float)
        w=[float(Fraction(str(v))) for v in d['block_weights']]
        result.update(candidate=str(path),candidate_sha256=hashlib.sha256(path.read_bytes()).hexdigest(),
                      classes=len(N),density=density(N/Q,w),evidence='independent all-root weighted float64 recount')
    result.update(elapsed_seconds=time.time()-t0,source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    dest=Path(args.out); dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(result,indent=2)+'\n'); print(json.dumps(result,indent=2))
