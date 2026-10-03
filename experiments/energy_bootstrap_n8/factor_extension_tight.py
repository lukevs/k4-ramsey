import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import json,struct,time,signal
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('35s factor-extension screen')));signal.alarm(35);t0=time.monotonic();out=Path('reports/energy-bootstrap-n8-001');f=open(out/'coefficients.bin','rb');n7,n8=struct.unpack('ii',f.read(8));idx=np.fromfile(f,dtype=np.uint16,count=n8*8).reshape(n8,8);X=np.fromfile(f,dtype=np.uint16,count=n8*11).reshape(n8,11);J=np.fromfile(f,dtype=np.uint16,count=n8*121).reshape(n8,121);P=sparse.csc_matrix((np.full(n8*8,1/8),(idx.ravel(),np.repeat(np.arange(n8),8))),shape=(n7,n8));q=np.array(json.loads(Path('reports/energy-bootstrap-auto-001/diagnostic.json').read_text())['primal']);q=q/q.sum();four=json.loads(Path('reports/mixed-motif-screen-001/coefficients.json').read_text());p4=q@np.array([r['x4'] for r in four['rows']])/5040;A=sparse.vstack([P,sparse.csc_matrix(J.T,dtype=float)/70],format='csc');b=np.r_[q,np.outer(p4,p4).ravel()];sol=linprog(np.zeros(n8),A_eq=A,b_eq=b,bounds=(0,None),method='highs',options={'threads':1,'time_limit':10,'primal_feasibility_tolerance':1e-9,'dual_feasibility_tolerance':1e-9});r={'success':sol.success,'status':sol.status,'message':sol.message,'seconds':time.monotonic()-t0,'scope':'Numerical N8 extension of one near-feasible N7 point, imposing ALL disjoint-four factorization identities. No rigorous primal or universal bound.'}
if sol.x is not None:
 r.update(max_residual=float(np.max(abs(A@sol.x-b))),min_probability=float(sol.x.min()),objective=float((X[:,0]+X[:,-1])@sol.x/70),profile4=p4.tolist());np.savez_compressed(out/'factor-extension-tight-primal.npz',q8=sol.x,q7=q,p4=p4)
(out/'factor-extension-tight-screen.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
