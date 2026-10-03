import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import sys,json,time,signal,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
import cvxpy as cp
sys.path.insert(0,str(Path('experiments/clebsch_bowl').resolve()))
from coupled_flag_followup import exact_positive_definite
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s limit')));signal.alarm(175)
t0=time.monotonic();out=Path('reports/energy-bootstrap-001'); z=np.load('reports/global-coupled-pilot-001/coefficients.npz');obs=np.load(out/'observables.npz'); c=z['c6']; n=len(c)
C=[np.einsum('hg,hij->gij',z['P'],z[k]) for k in sorted(z.files) if k.startswith('N5_')]+[z[k] for k in sorted(z.files) if k.startswith('N6_')]
# Preserve identification of the inherited independently audited tensors.
reference=json.loads(Path('reports/global-coupled-pilot-003/full-certificate.json').read_text())
refs={np.array(b['C_integer'],dtype=np.int64).tobytes():i for i,b in enumerate(reference['blocks'])}
indices=[refs[np.rint(B*720).astype(np.int64).tobytes()] for B in C]
x=obs['X'][1];zz=obs['Z'][1];SCALE=10**10;D=720*256
intervals=[(0,4),(4,5),(5,6),(6,7),(7,8),(8,16)];results=[]
for ia,ib in intervals:
 a=F(ia,16);b=F(ib,16); y=cp.Variable(n)
 # Only the secant: no U restriction, no uncertified endpoints.
 linear=(float(a+b)*x-zz);const=-a*b
 cons=[y>=0,cp.sum(y)==1,linear@y+float(const)>=0]
 for B in C:
  d=B.shape[1];cons.append(cp.reshape(B.reshape(n,d*d).T@y,(d,d),order='C')>>0)
 prob=cp.Problem(cp.Minimize(c@y),cons);prob.solve(solver='CLARABEL',tol_gap_abs=1e-10,tol_gap_rel=1e-10,tol_feas=1e-10,max_iter=150,time_limit=15)
 assert y.value is not None,(ia,ib,prob.status)
 lam=max(0,round(float(cons[2].dual_value)*SCALE)); blocks=[];pen=[0]*n
 for B,con,idx in zip(C,cons[3:],indices):
  Q=con.dual_value; R=np.rint((Q+Q.T)/2*SCALE).astype(np.int64); shift=max(1,int(np.ceil(-np.linalg.eigvalsh(R.astype(float))[0]))+2)
  while not exact_positive_definite(R+shift*np.eye(len(R),dtype=np.int64)):shift*=2
  R=R+shift*np.eye(len(R),dtype=np.int64);Ci=np.rint(B*720).astype(np.int64)
  for g in range(n):pen[g]+=sum(int(R[i,j])*int(Ci[g,i,j])*256 for i in range(len(R)) for j in range(len(R)))
  blocks.append({'reference_block':idx,'Q_integer':R.tolist()})
 li=np.rint(linear*D).astype(np.int64);ci=np.rint(c*D).astype(np.int64)
 slacks=[int(ci[g])*SCALE-pen[g]-lam*int(li[g]) for g in range(n)]
 bound=F(min(slacks),D*SCALE)-F(lam,SCALE)*const
 r={'interval':[str(a),str(b)],'numerical':float(prob.value),'status':prob.status,'bound':str(bound),'bound_decimal':float(bound),'lambda_integer':lam,'blocks':blocks}
 results.append(r);print(json.dumps({k:v for k,v in r.items() if k!='blocks'}),flush=True)
(out/'certificate.json').write_text(json.dumps({'scale':SCALE,'branches':results,'bound':str(min(F(r['bound']) for r in results)),'seconds':time.monotonic()-t0,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}))
