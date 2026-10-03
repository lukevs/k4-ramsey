"""Persistent parameterized SDP worker; one JSON request/response per line."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,signal,time,hashlib
import numpy as np
import cvxpy as cp
from scipy import sparse
from common import *
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s job limit')))
Cs,c=blocks();obs=json.loads((OUT/'observables.json').read_text());X=np.array([r['X'] for r in obs['rows']],float).T/5040;J=np.array([r['J'] for r in obs['rows']],float).transpose(1,2,0)/5040
n=len(c);y=cp.Variable(n);Lp=cp.Parameter((37,n));cons=[y>=0,cp.sum(y)==1,Lp@y>=0]
for C in Cs:
 d=C.shape[1];cons.append(cp.reshape(sparse.csc_matrix(C.reshape(n,d*d).T,dtype=float)@y/5040,(d,d),order='C')>>0)
problem=cp.Problem(cp.Minimize(c@y/5040),cons);count=0
print(json.dumps({'ready':True,'DPP':problem.is_dpp(),'blocks':len(Cs)}),flush=True)
for line in sys.stdin:
 request=json.loads(line);t0=time.monotonic();signal.alarm(175)
 try:
  if request['kind']=='diagnostic':
   p=np.array([1/8,3/8,3/8,1/8]);dc=[y>=0,cp.sum(y)==1,X@y==p,cp.reshape(J.reshape(16,n)@y,(4,4),order='C')==np.outer(p,p)]+cons[3:]
   dp=cp.Problem(cp.Minimize(c@y/5040),dc);dp.solve(solver='CLARABEL',tol_gap_abs=2e-8,tol_feas=2e-8,tol_gap_rel=2e-8,max_iter=100,time_limit=110)
   q=y.value;result={'name':'diagnostic','status':dp.status,'objective':float(dp.value),'seconds':time.monotonic()-t0,'numerical_only':True,'fixed_profile':p.tolist()}
   if q is not None:result.update(primal=q.tolist(),min_probability=float(q.min()),moment_residual=float(np.max(np.abs(X@q-p))),joint_residual=float(np.max(np.abs(np.einsum('ijg,g->ij',J,q)-np.outer(p,p)))),min_gram_eigenvalue=min(float(np.linalg.eigvalsh(np.einsum('g,gij->ij',q,C)/5040)[0]) for C in Cs))
   (OUT/'diagnostic.json').write_text(json.dumps(result,indent=2))
  else:
   cfg=request['config'];name=cfg['name'];L,labels,_,_=inequalities(cfg);Lp.value=L/D;problem.solve(solver='CLARABEL',warm_start=True,tol_gap_abs=2e-8,tol_feas=2e-8,tol_gap_rel=2e-8,max_iter=100,time_limit=110)
   q=y.value;result={'name':name,'config':cfg,'status':problem.status,'objective':float(problem.value),'seconds':time.monotonic()-t0,'solve_index':count,'DPP':problem.is_dpp(),'compiled_problem_reused':count>0,'warm_start_requested':True};count+=1
   if q is not None:
    means=X@q;result.update(primal=q.tolist(),means=means.tolist(),covariance=(np.einsum('ijg,g->ij',J,q)-np.outer(means,means)).tolist(),min_probability=float(q.min()))
    np.savez_compressed(OUT/(name+'-dual.npz'),lam=cons[2].dual_value,**{f'Q{i}':co.dual_value for i,co in enumerate(cons[3:])})
   (OUT/(name+'-result.json')).write_text(json.dumps(result,indent=2))
  print(json.dumps({k:v for k,v in result.items() if k not in ('primal','covariance')}),flush=True)
 except Exception as e:
  print(json.dumps({'error':repr(e),'request':request,'seconds':time.monotonic()-t0}),flush=True)
 finally:signal.alarm(0)
