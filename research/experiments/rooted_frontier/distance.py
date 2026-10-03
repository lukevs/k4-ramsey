import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import json,struct,time,signal
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
signal.alarm(175)
t=time.monotonic();src=Path('reports/energy-bootstrap-n8-001');out=Path('reports/rooted-frontier-001')
with open(src/'coefficients.bin','rb') as f:
 n7,n8=struct.unpack('ii',f.read(8));idx=np.fromfile(f,dtype=np.uint16,count=n8*8).reshape(n8,8);X=np.fromfile(f,dtype=np.uint16,count=n8*11).reshape(n8,11);J=np.fromfile(f,dtype=np.uint16,count=n8*121).reshape(n8,121)
P=sparse.csc_matrix((np.full(n8*8,1/8),(idx.ravel(),np.repeat(np.arange(n8),8))),shape=(n7,n8))
q=np.array(json.loads(Path('reports/energy-bootstrap-auto-001/diagnostic.json').read_text())['primal']);q/=q.sum()
four=json.loads(Path('reports/mixed-motif-screen-001/coefficients.json').read_text());p4=q@np.array([r['x4'] for r in four['rows']])/5040
A=sparse.vstack([P,sparse.csc_matrix(J.T,dtype=float)/70],format='csc');b=np.r_[q,np.outer(p4,p4).ravel()]
# Minimize uniform error, requiring an exactly normalized nonnegative N8 distribution.
m=len(b);col=sparse.csc_matrix(-np.ones((m,1)))
U=sparse.vstack([sparse.hstack([A,col]),sparse.hstack([-A,col])],format='csc');v=np.r_[b,-b]
sol=linprog(np.r_[np.zeros(n8),1.],A_ub=U,b_ub=v,A_eq=sparse.csc_matrix(np.r_[np.ones(n8),0.][None,:]),b_eq=[1.],bounds=(0,None),method='highs',options={'time_limit':120,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9,'threads':1})
r={'status':sol.status,'success':sol.success,'message':sol.message,'seconds':time.monotonic()-t,'scope':'Numerical distance to extension of a fixed approximate N7 point, not a universal bound.'}
if sol.x is not None:
 z=sol.x[:-1];r.update(distance=float(sol.fun),measured_error=float(np.max(abs(A@z-b))),mass_error=float(abs(z.sum()-1)),min_probability=float(z.min()))
 np.savez_compressed(out/'distance-witness.npz',z=z,q=q,p4=p4,dual=sol.ineqlin.marginals)
(out/'distance.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
