import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,signal,time,hashlib
from pathlib import Path
import numpy as np
import cvxpy as cp
from scipy import sparse
from common import *
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175);t0=time.monotonic();name=sys.argv[1];cfg=json.loads((OUT/(name+'-config.json')).read_text());Cs,c=blocks();L,labels,X,J=inequalities(cfg);y=cp.Variable(len(c));cons=[y>=0,cp.sum(y)==1,L@y/D>=0]
for C in Cs:
 d=C.shape[1];cons.append(cp.reshape(sparse.csc_matrix(C.reshape(len(c),d*d).T,dtype=float)@y/5040,(d,d),order='C')>>0)
p=cp.Problem(cp.Minimize(c@y/5040),cons);p.solve(solver='CLARABEL',tol_gap_abs=2e-8,tol_feas=2e-8,tol_gap_rel=2e-8,max_iter=100,time_limit=115)
r={'name':name,'config':cfg,'status':p.status,'objective':float(p.value),'seconds':time.monotonic()-t0}
if y.value is not None:
 q=y.value;means=X@q/5040;joint=np.einsum('ijg,g->ij',J,q)/5040;r.update(primal=q.tolist(),means=means.tolist(),covariance=(joint-np.outer(means,means)).tolist(),min_probability=float(q.min()))
 np.savez_compressed(OUT/(name+'-dual.npz'),lam=cons[2].dual_value,**{f'Q{i}':con.dual_value for i,con in enumerate(cons[3:])})
(OUT/(name+'-result.json')).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='primal'}),flush=True)
