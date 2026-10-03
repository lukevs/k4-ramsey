"""Discriminating refinement: can a pointwise transport even match N6?"""
import os
for k in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import numpy as np
from scipy.optimize import minimize
import json,time,hashlib
from pathlib import Path
START=time.monotonic();rng=np.random.default_rng(93003)
OUT=Path('reports/lower-frontier-B-005');OUT.mkdir(exist_ok=True)
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

parent=Path('reports/lower-frontier-B-004/screen.json')
r=json.loads(parent.read_text())['runs'][-1];n=r['n'];iu=np.triu_indices(n)
v=np.r_[np.array(r['W'])[iu],r['a'],r['w'],r['score']]
def constraints(z):
 q=fun(z[:-1],n,True)
 return np.array([z[-1]-q[k]for k in ['cross','same','local']])
sol=minimize(lambda z:z[-1],v,method='SLSQP',constraints=[{'type':'ineq','fun':constraints}],bounds=[(0,1)]*(len(v)-n-1)+[(.005,1)]*n+[(0,1)],options={'maxiter':350,'ftol':1e-12})
rec=fun(sol.x[:-1],n,True);rec.update(n=n,nit=int(sol.nit),success=bool(sol.success),message=str(sol.message),seconds=time.monotonic()-START)
report={'result':rec,'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seed':93003,'scope':'Numerical epigraph continuation after nonsmooth L-BFGS termination.'}
(OUT/'screen.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:v for k,v in rec.items()if k not in ['W','a','w']})
