import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'): os.environ[k]='1'
import json,time,signal,hashlib,itertools as it
from pathlib import Path
import numpy as np
import cvxpy as cp
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s limit')))
signal.alarm(175)
start=time.monotonic(); out=Path('reports/energy-bootstrap-001')
z=np.load('reports/global-coupled-pilot-001/coefficients.npz'); G=z['graphs6']; c=z['c6']; P=z['P']; n=len(c)
C=[np.einsum('hg,hij->gij',P,z[k]) for k in sorted(z.files) if k.startswith('N5_')]+[z[k] for k in sorted(z.files) if k.startswith('N6_')]
# Induced three-vertex types are uniquely determined by their number of edges.
X=np.zeros((4,n)); Z=np.zeros((4,n)); E=np.zeros(n); E2=np.zeros(n)
for gi,A in enumerate(G):
 for vs in it.combinations(range(6),3):
  k=sum(int(A[i,j]) for i,j in it.combinations(vs,2)); ws=tuple(set(range(6))-set(vs)); l=sum(int(A[i,j]) for i,j in it.combinations(ws,2))
  X[k,gi]+=1/20; Z[k,gi]+=int(k==l)/20
 E[gi]=A.sum()/30
 E2[gi]=sum(int(A[a,b])*int(A[d,e]) for a,b,d,e in it.permutations(range(6),4))/360
X=np.vstack([X,E]); Z=np.vstack([Z,E2]); names=['empty_triple','one_edge','two_edges','triangle','edge']
np.savez_compressed(out/'observables.npz',X=X,Z=Z,graphs=G)
y=cp.Variable(n); base=[y>=0,cp.sum(y)==1]
for B in C:
 d=B.shape[1]; base.append(cp.reshape(B.reshape(n,d*d).T@y,(d,d),order='C')>>0)
U=0.030138887566497220; records=[]
def solve(label,obj,extra=()):
 p=cp.Problem(cp.Minimize(obj@y),base+list(extra)); t=time.monotonic()
 p.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9,max_iter=120,time_limit=8)
 r={'label':label,'status':p.status,'value':float(p.value),'seconds':time.monotonic()-t}
 if y.value is not None:
  q=y.value.copy(); r.update(primal=q.tolist(),means=(X@q).tolist(),variances=(Z@q-(X@q)**2).tolist(),min_probability=float(q.min()),min_eigenvalue=min(float(np.linalg.eigvalsh(np.einsum('g,gij->ij',q,B))[0]) for B in C))
 records.append(r); (out/'runs.json').write_text(json.dumps(records,indent=2)); print(json.dumps({k:v for k,v in r.items() if k!='primal'}),flush=True); return r
control=solve('control',c); conditioned=solve('conditioned',c,[c@y<=U])
ranges={}
for k,name in enumerate(names):
 lo=solve(name+'_min',X[k],[c@y<=U]); hi=solve(name+'_max',-X[k],[c@y<=U]); ranges[name]=[lo['value'],-hi['value']]
# Exhaustive [0,1] cells, no reliance on uncertified observable endpoints.
k=int(np.argmax(control['variances'])); leaves=[]
for i in range(16):
 a=i/16; b=(i+1)/16
 extra=[c@y<=U,X[k]@y>=a,X[k]@y<=b,Z[k]@y<=(a+b)*(X[k]@y)-a*b]
 r=solve('branch_'+str(i),c,extra); r['interval']=[a,b]; leaves.append(r)
result={'observable':names[k],'ranges_numerical':ranges,'control':control['value'],'conditioned':conditioned['value'],'branch_min_numerical':min(r['value'] for r in leaves),'branch_intervals':[r['interval'] for r in leaves],'seconds':time.monotonic()-start,'certified':False,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(out/'result.json').write_text(json.dumps(result,indent=2)); print(json.dumps(result),flush=True)
