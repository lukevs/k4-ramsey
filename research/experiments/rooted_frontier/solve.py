import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,signal,struct
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import cvxpy as cp
from scipy import sparse
sys.path.insert(0,str(Path('research/experiments/energy_bootstrap_auto').resolve()))
from common import blocks
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s N8 solve')));signal.alarm(175);t0=time.monotonic();src=Path('reports/energy-bootstrap-n8-001');out=Path('reports/rooted-frontier-001');roundno=int(sys.argv[1]);mode='cut'
f=open(src/'coefficients.bin','rb');n7,n8=struct.unpack('ii',f.read(8));idx=np.fromfile(f,dtype=np.uint16,count=n8*8).reshape(n8,8);X=np.fromfile(f,dtype=np.uint16,count=n8*11).reshape(n8,11);J=np.fromfile(f,dtype=np.uint16,count=n8*121).reshape(n8,11,11);assert not f.read()
P=sparse.csc_matrix((np.full(n8*8,1/8),(idx.ravel(),np.repeat(np.arange(n8),8))),shape=(n7,n8));Cs,c7=blocks();c8=(X[:,0]+X[:,-1])/70;assert np.max(abs(c7/5040@P-c8))<1e-14
mono=(J[:,0,0]+J[:,0,-1]+J[:,-1,0]+J[:,-1,-1])/70
L=F(57520950383,1966080000000);U=F(30139,1000000);y=cp.Variable(n7);z=cp.Variable(n8);scalar=[c8-float(L),float(U)-c8]
if mode=='cut':scalar.append(float(L+U)*c8-mono-float(L*U))

for j in range(roundno+1):
 data=np.load(out/f'cuts-{j}.npz');scalar.extend(data['coefficients']/float(data['denominator']))
A=np.array(scalar);cons=[z>=0,cp.sum(z)==1,y==P@z,A@z>=0]
for C in Cs:
 d=C.shape[1];cons.append(cp.reshape(sparse.csc_matrix(C.reshape(n7,d*d).T,dtype=float)@y/5040,(d,d),order='C')>>0)
cons.append(cp.reshape(sparse.csc_matrix(J.reshape(n8,121).T,dtype=float)@z/70,(11,11),order='C')>>0)
p=cp.Problem(cp.Minimize(c8@z),cons);print('PREPARED',n8,n7,'variables',len(Cs)+1,'PSD blocks',flush=True)
p.solve(solver='CLARABEL',tol_gap_abs=2e-8,tol_feas=2e-8,tol_gap_rel=2e-8,max_iter=90,time_limit=125)
r={'mode':'rooted-cuts','round':roundno,'scalar_count':len(scalar),'status':p.status,'objective':float(p.value),'seconds':time.monotonic()-t0,'L':str(L),'U':str(U),'numerical_only':True}
if z.value is not None:
 q=z.value;r.update(primal8=q.tolist(),primal7=y.value.tolist(),min_probability=float(q.min()),marginal_residual=float(np.max(abs(y.value-P@q))),objective_variance=float(mono@q-(c8@q)**2),min_scalar_slack=float(np.min(A@q)),mass_residual=float(abs(q.sum()-1)),min_gram_eigenvalue=float(min(np.linalg.eigvalsh(np.einsum('g,gij->ij',y.value,C)/5040)[0] for C in Cs)),min_unrooted_eigenvalue=float(np.linalg.eigvalsh(np.einsum('g,gij->ij',q,J)/70)[0]))
 np.savez_compressed(out/(f'solve-{roundno}-dual.npz'),lam=cons[3].dual_value,**{f'Q{i}':co.dual_value for i,co in enumerate(cons[4:])})
(out/(f'solve-{roundno}.json')).write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if not k.startswith('primal')}),flush=True)
