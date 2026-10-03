"""Bounded numerical screen of cross-colour rooted K4 transport."""
import os
for v in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']: os.environ[v]='1'
import numpy as np
from scipy.optimize import minimize
from pathlib import Path
import json,time,hashlib,sys,scipy
START=time.monotonic(); rng=np.random.default_rng(93002)
OUT=Path('reports/lower-frontier-B-002');OUT.mkdir(exist_ok=True)
best=None; runs=[]
def evaluate(v,n,details=False):
 iu=np.triu_indices(n); W=np.zeros((n,n));W[iu]=v[:len(iu[0])];W[(iu[1],iu[0])]=W[iu]
 a=v[len(iu[0]):len(iu[0])+n]; w=v[-n:];w=w/w.sum()
 vals=[];roots=[]
 for U,b in [(W,a),(1-W,1-a)]:
  T=np.einsum('i,j,k,ij,ik,jk->ijk',w,w,w,U,U,U,optimize=True)
  vals.append(float(np.einsum('ijk,i,j,k',T,b,b,b)))
  roots.append(np.einsum('ijk,li,lj,lk->l',T,U,U,U,optimize=True))
 d=w@a; g=d*vals[0]+(1-d)*vals[1]+w@(a*roots[1]+(1-a)*roots[0])
 if details:return dict(g=float(g),W=W.tolist(),w=w.tolist(),a=a.tolist(),d=float(d),root_R=vals[0],root_B=vals[1],base_c4=float(w@(roots[0]+roots[1])))
 return g
for n in [2,3,4,5]:
 for seed in range(4):
  if time.monotonic()-START>105:break
  k=n*(n+1)//2+n+n
  v=rng.uniform(.05,.95,k)
  if seed==0:v[:n*(n+1)//2]=.5;v[n*(n+1)//2:-n]=.5
  sol=minimize(evaluate,v,args=(n,),method='L-BFGS-B',bounds=[(0,1)]*(k-n)+[(.01,1)]*n,options={'maxiter':110,'ftol':1e-12,'maxfun':7500})
  rec=evaluate(sol.x,n,True);rec.update(n=n,seed=seed,success=bool(sol.success),nit=int(sol.nit),seconds=time.monotonic()-START)
  runs.append(rec)
  if best is None or rec['g']<best['g']:best=rec;print(json.dumps(best),flush=True)
report={'hypothesis':'B2-cross','runs':runs,'best':best,'seconds':time.monotonic()-START,'numpy':np.__version__,'scipy':scipy.__version__,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seed':93002,'scope':'Numerical anomalous-root screen. Root has zero mass in this limit; exact positive-mass check required.'}
(OUT/'screen.json').write_text(json.dumps(report,indent=2)+'\n')
