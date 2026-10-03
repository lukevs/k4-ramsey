"""Discriminating refinement: can a pointwise transport even match N6?"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import numpy as np
from scipy.optimize import minimize
import json,time,hashlib
from pathlib import Path
START=time.monotonic();rng=np.random.default_rng(93003)
OUT=Path('reports/lower-frontier-B-004');OUT.mkdir(exist_ok=True)
base=np.array([[.54,.68,.16,.24],[.68,.43,.09,.77],[.16,.09,1,1],[.24,.77,1,.30]])
w0=np.array([.34,.31,.16,.19]);a0=np.array([1,0,1,0]);runs=[]
def fun(v,n,detail=False):
 iu=np.triu_indices(n);m=len(iu[0]);W=np.zeros((n,n));W[iu]=v[:m];W[(iu[1],iu[0])]=W[iu];a=v[m:m+n];w=v[-n:]/sum(v[-n:]);d=w@a;f=[];r=[]
 for U,b in [(W,a),(1-W,1-a)]:
  T=np.einsum('i,j,k,ij,ik,jk->ijk',w,w,w,U,U,U,optimize=True)
  f.append(np.einsum('ijk,i,j,k',T,b,b,b));r.append(np.einsum('ijk,li,lj,lk->l',T,U,U,U,optimize=True))
 cross=d*f[0]+(1-d)*f[1]+w@(a*r[1]+(1-a)*r[0])
 same=(1-d)*f[0]+d*f[1]+w@(a*r[0]+(1-a)*r[1])
 # Shared counterexample to the whole convex family, rather than a single coefficient.
 score=max(cross,same,f[0]+f[1])
 if detail:return dict(score=float(score),cross=float(cross),same=float(same),local=float(f[0]+f[1]),W=W.tolist(),w=w.tolist(),a=a.tolist(),base_c4=float(w@(r[0]+r[1])))
 return score
for n in [4,8]:
 W=base if n==4 else np.kron(base,np.ones((2,2)));w=w0 if n==4 else np.repeat(w0/2,2);a=a0 if n==4 else np.repeat(a0,2)
 iu=np.triu_indices(n);v=np.r_[W[iu],a,w]
 if n==8:v[:len(iu[0])]=np.clip(v[:len(iu[0])]+rng.normal(0,.05,len(iu[0])),0,1)
 sol=minimize(fun,v,args=(n,),method='L-BFGS-B',bounds=[(0,1)]*(len(v)-n)+[(.005,1)]*n,options={'maxiter':500,'ftol':1e-14,'maxfun':30000,'gtol':1e-7})
 rec=fun(sol.x,n,True);rec.update(n=n,nit=int(sol.nit),success=bool(sol.success),seconds=time.monotonic()-START);runs.append(rec);print(json.dumps(rec),flush=True)
(OUT/'screen.json').write_text(json.dumps({'runs':runs,'seconds':time.monotonic()-START,'seed':93003,'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Numerical exceptional-root minimax; not a c4 bound.'},indent=2)+'\n')
