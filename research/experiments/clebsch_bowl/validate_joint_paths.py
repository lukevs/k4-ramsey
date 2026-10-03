"""Actual constant-margin kernels test joint Gram and centered K4 bounds."""
import itertools
import json
from pathlib import Path
import sys
import numpy as np

rng=np.random.default_rng(668144)
min_eig=1.; worst_excess=-1.; max_mean=0.; cases=0
for m in (3,4,5,8):
    for trial in range(12):
        D={}; p={}; v={}
        for a,b in itertools.combinations(range(4),2):
            deg=int(rng.integers(1,m)); lev=deg/m
            U=np.zeros((m,m))
            for k in range(deg): U[np.arange(m),(np.arange(m)+k)%m]=1
            U=U[np.ix_(rng.permutation(m),rng.permutation(m))]
            if trial%2: U=.3*U+.7*U[np.ix_(rng.permutation(m),rng.permutation(m))]
            D[a,b]=U-lev; D[b,a]=D[a,b].T
            p[a,b]=p[b,a]=lev; v[a,b]=v[b,a]=lev*(1-lev)
        for x,y in itertools.combinations(range(4),2):
            z,w=[a for a in range(4) if a not in (x,y)]
            S=np.stack([(D[x,c]@D[c,y]/m).ravel() for c in (z,w)],axis=1)
            d=D[x,y].ravel(); F=np.column_stack([np.ones(m*m),S])
            A=F.T@F/m**2; B=F.T@(d[:,None]*F)/m**2; C=F.T@(d[:,None]**2*F)/m**2
            lev=p[x,y]
            for M in (lev*A+B,(1-lev)*A-B,lev*(1-lev)*A+(1-2*lev)*B-C):
                min_eig=min(min_eig,float(np.linalg.eigvalsh(M).min()))
            max_mean=max(max_mean,float(np.max(np.abs(S.mean(axis=0)))))
            q=(S*S).mean(axis=0)
            rz=v[x,z]*v[y,z]-q[0]; rw=v[x,w]*v[y,w]-q[1]
            assert min(rz,rw)>-1e-14
            bound=max(lev,1-lev)*min(p[z,w],1-p[z,w])*np.sqrt(max(0,rz*rw))
            exact=np.einsum('ij,ik,jk,il,jl,kl->',D[x,y],D[x,z],D[y,z],D[x,w],D[y,w],D[z,w],optimize=True)/m**4
            worst_excess=max(worst_excess,abs(float(exact))-bound)
            cases+=1
assert min_eig > -1e-14 and worst_excess < 1e-14 and max_mean < 1e-14
report=dict(cases=cases,min_localizer_eigenvalue=min_eig,max_path_mean_error=max_mean,
            max_K4_bound_violation=worst_excess,seed=668144,
            scope='actual finite kernels, all six spine choices, full six-edge K4 contraction and centered localizers')
Path(sys.argv[1]).write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
