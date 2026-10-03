"""Check operator contraction on explicit constant-margin probability kernels."""
import json
from pathlib import Path
import sys
import numpy as np

rng = np.random.default_rng(192668)
results = []
for m in (4,5,8,13):
    for degree in range(1,m):
        p = degree/m
        W = np.zeros((m,m))
        for offset in range(degree):
            W[np.arange(m),(np.arange(m)+offset)%m] = 1
        # Regular binary kernels, and convex combinations of independently
        # permuted regular kernels, all have exact constant margins.
        for mixed in (False,True):
            U = W.copy()
            if mixed:
                U = .3*U + .7*W[np.ix_(rng.permutation(m),rng.permutation(m))]
            D = U-p
            assert np.max(np.abs(D.mean(axis=0)))<1e-14
            assert np.max(np.abs(D.mean(axis=1)))<1e-14
            op = float(np.linalg.svd(D/m,compute_uv=False)[0])
            assert op <= min(p,1-p)+1e-14
            results.append(dict(m=m,p=p,mixed=mixed,op=op,bound=min(p,1-p)))
report=dict(cases=len(results),max_excess=max(x['op']-x['bound'] for x in results),
            maximum_ratio=max(x['op']/x['bound'] for x in results),
            cases_at_bound=sum(abs(x['op']-x['bound'])<1e-14 for x in results),results=results)
Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='results'},indent=2))
