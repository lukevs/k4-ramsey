import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import json,struct,time,signal
from pathlib import Path
import numpy as np
from scipy import sparse
from scipy.optimize import linprog
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('30s extension screen')));signal.alarm(30);t0=time.monotonic();out=Path('reports/energy-bootstrap-n8-001');f=open(out/'coefficients.bin','rb');n7,n8=struct.unpack('ii',f.read(8));idx=np.fromfile(f,dtype=np.uint16,count=n8*8).reshape(n8,8);P=sparse.csc_matrix((np.full(n8*8,1/8),(idx.ravel(),np.repeat(np.arange(n8),8))),shape=(n7,n8));q=np.array(json.loads(Path('reports/energy-bootstrap-auto-001/diagnostic.json').read_text())['primal']);q=q/q.sum();sol=linprog(np.zeros(n8),A_eq=P,b_eq=q,bounds=(0,None),method='highs',options={'threads':1,'time_limit':15});r={'success':sol.success,'status':sol.status,'message':sol.message,'seconds':time.monotonic()-t0,'scope':'Numerical nonnegative N8 extension test for one normalized N7 point; no universal bound or exact infeasibility certificate.'}
if sol.x is not None:r.update(max_marginal_residual=float(np.max(abs(P@sol.x-q))),min_probability=float(sol.x.min()))
(out/'extension-screen.json').write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
