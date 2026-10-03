import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,signal,struct,hashlib
from pathlib import Path
import numpy as np
import cvxpy as cp
from scipy import sparse
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
out=Path('reports/energy-bootstrap-n7-001');mode=sys.argv[1];t0=time.monotonic()
f=open(out/'coefficients.bin','rb');nb,ng=struct.unpack('ii',f.read(8));Cs=[]
for i in range(nb):
 d=struct.unpack('i',f.read(4))[0]; B=np.fromfile(f,dtype=np.uint16,count=ng*d*d).reshape(ng,d*d);Cs.append((d,sparse.csc_matrix(B.T,dtype=float)/5040))
x=np.fromfile(f,dtype=np.uint16,count=ng)/5040;z=np.fromfile(f,dtype=np.uint16,count=ng)/5040;c=np.fromfile(f,dtype=np.uint16,count=ng)/5040;P=np.fromfile(f,dtype=np.uint16,count=156*ng).reshape(156,ng)/7;assert not f.read();f.close()
y=cp.Variable(ng);cons=[y>=0,cp.sum(y)==1];extra=None
if mode!='control':
 a,b=map(float,mode.split(','));extra=(a+b)*x-z;cons.append(extra@y-a*b>=0)
for d,C in Cs:cons.append(cp.reshape(C@y,(d,d),order='C')>>0)
# Retain audited N6 constraints, all lifted through deletion marginals.
src=np.load('reports/global-coupled-pilot-001/coefficients.npz');old=[np.einsum('hg,hij->gij',src['P'],src[k]) for k in sorted(src.files) if k.startswith('N5_')]+[src[k] for k in sorted(src.files) if k.startswith('N6_')]
for B in old:
 d=B.shape[1];C=sparse.csc_matrix(B.reshape(156,d*d).T@P);Cs.append((d,C));cons.append(cp.reshape(C@y,(d,d),order='C')>>0)
print('prepared',len(Cs),'blocks',sum(C.nnz for d,C in Cs),'nonzeros',time.monotonic()-t0,flush=True)
p=cp.Problem(cp.Minimize(c@y),cons);p.solve(solver='CLARABEL',tol_gap_abs=2e-8,tol_feas=2e-8,tol_gap_rel=2e-8,max_iter=100,time_limit=110)
q=y.value;assert q is not None,p.status
r={'mode':mode,'status':p.status,'objective':float(p.value),'x':float(x@q),'z_minus_x2':float(z@q-(x@q)**2),'min_probability':float(q.min()),'seconds':time.monotonic()-t0,'primal':q.tolist(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
name=mode.replace(',','_');(out/(name+'.json')).write_text(json.dumps(r,indent=2));offset=3 if extra is not None else 2
np.savez_compressed(out/(name+'-dual.npz'),**{f'Q{i}':con.dual_value for i,con in enumerate(cons[offset:])},lam=np.array(float(cons[2].dual_value) if extra is not None else 0))
print(json.dumps({k:v for k,v in r.items() if k!='primal'}),flush=True)
