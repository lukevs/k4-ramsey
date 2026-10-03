"""Validate localizing matrices against direct weighted feature enumeration."""
import json
from pathlib import Path
import sys
import numpy as np

rng = np.random.default_rng(668192)
errors = []
eigenvalues = []
for p in (.01,.2,.5,.8,.99):
    for trial in range(12):
        m, k = 7, 4
        d = rng.uniform(-p,1-p,size=m*m)
        d[0],d[-1] = -p,1-p
        features = rng.standard_normal((m*m,k))
        weight = rng.dirichlet(np.ones(m*m))
        A = features.T @ ((weight)[:,None]*features)
        B = features.T @ ((weight*d)[:,None]*features)
        C = features.T @ ((weight*d*d)[:,None]*features)
        matrices = [p*A+B,(1-p)*A-B,p*(1-p)*A+(1-2*p)*B-C]
        factors = [p+d,1-p-d,(p+d)*(1-p-d)]
        for matrix,factor in zip(matrices,factors):
            direct = sum(weight[i]*factor[i]*np.outer(features[i],features[i]) for i in range(m*m))
            errors.append(float(np.max(np.abs(matrix-direct))))
            eigenvalues.append(float(np.linalg.eigvalsh(matrix).min()))
assert max(errors)<1e-14 and min(eigenvalues)>-1e-14
report=dict(seed=668192,cases=60,matrices=180,max_identity_error=max(errors),
            minimum_eigenvalue=min(eigenvalues),
            scope='new localizing inequalities only; not a verification of the entire existing relaxation')
print(json.dumps(report,indent=2))
Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n')
