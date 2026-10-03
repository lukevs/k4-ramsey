"""One advisory exact-factorization solve at the weakest node's rounded profile."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,signal
import numpy as np
import cvxpy as cp
from scipy import sparse
from fractions import Fraction as F
from common import *
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s diagnostic')));signal.alarm(175);t0=time.monotonic()
queue=json.loads((OUT/'queue.json').read_text());node=min(queue['leaves'],key=lambda n:F(n['bound']));folder=Path(node['folder']);path=folder/(node['name']+'-result.json');mu=json.loads(path.read_text())['means'];den=2**20;nums=np.rint(np.array(mu)*den).astype(np.int64);nums[3]+=den-int(nums.sum());target=nums/den;assert min(nums)>=0
Cs,c=blocks();obs=json.loads((OUT/'observables.json').read_text());X=np.array([r['X'] for r in obs['rows']],float).T/5040;J=np.array([r['J'] for r in obs['rows']],float).transpose(1,2,0)/5040;y=cp.Variable(len(c));cons=[y>=0,cp.sum(y)==1,X@y==target,cp.reshape(J.reshape(16,len(c))@y,(4,4),order='C')==np.outer(target,target)]
for C in Cs:
 d=C.shape[1];cons.append(cp.reshape(sparse.csc_matrix(C.reshape(len(c),d*d).T,dtype=float)@y/5040,(d,d),order='C')>>0)
p=cp.Problem(cp.Minimize(c@y/5040),cons);p.solve(solver='CLARABEL',tol_gap_abs=2e-8,tol_feas=2e-8,tol_gap_rel=2e-8,max_iter=100,time_limit=110)
r={'name':'weakest_profile_diagnostic','source_node':node['name'],'profile_numerators':nums.tolist(),'profile_denominator':den,'profile':target.tolist(),'status':p.status,'objective':float(p.value),'seconds':time.monotonic()-t0,'numerical_only':True,'scope':'Approximate point of exact-factorization moment relaxation; not a graphon or certified ceiling.'}
if y.value is not None:
 q=y.value;r.update(primal=q.tolist(),min_probability=float(q.min()),moment_residual=float(np.max(abs(X@q-target))),joint_residual=float(np.max(abs(np.einsum('ijg,g->ij',J,q)-np.outer(target,target)))),min_gram_eigenvalue=min(float(np.linalg.eigvalsh(np.einsum('g,gij->ij',q,C)/5040)[0]) for C in Cs))
(OUT/'weakest-profile-diagnostic.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='primal'}),flush=True)
