import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sys,json,time,itertools as it,signal
import numpy as np
from scipy.optimize import minimize
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
sys.path.insert(0,str(Path('experiments/round5_C1').resolve()))
from base import base,Fval
start=time.monotonic();out=Path('reports/graph-arrangements-001');p=.779180833031354;h=.5342651880306992;W,typ,cls=base(p,h);n=len(W);Q=1-W;fr=(W>0)&(W<1);nb=[list(np.flatnonzero(row)) for row in fr];hc=(typ=='H').astype(int);coef={r:np.zeros(r+1) for r in (3,4,5,6)}
# Combinatorial expansion coefficients, retaining H/P amplitude separately.
for x in range(n):
 for y in nb[x]:
  for z in nb[y]:
   if fr[z,x]:coef[3][hc[x,y]+hc[y,z]+hc[z,x]]+=4*np.sum(W[x]*W[y]*W[z]-Q[x]*Q[y]*Q[z])/n**4
   for t in nb[z]:
    if fr[t,x]:coef[4][hc[x,y]+hc[y,z]+hc[z,t]+hc[t,x]]+=3*(W[x,z]*W[y,t]+Q[x,z]*Q[y,t])/n**4
  cn=[z for z in nb[x] if fr[z,y]]
  for z in cn:
   for t in cn:
    k=hc[x,y]+hc[x,z]+hc[y,z]+hc[x,t]+hc[y,t];coef[5][k]+=6*(2*W[z,t]-1)/n**4
    if fr[z,t]:coef[6][k+hc[z,t]]+=2/n**4
F0=Fval(W)
def moments(S):
 m=len(S);S2=S@S;t3=np.trace(S2@S)/m**3;t4=np.sum(S2*S2)/m**4;t5=np.sum(S*S2*S2)/m**4;t6=0
 for a in range(m):
  X=S[a][None,:]*S;Y=X@S;t6+=S[a]@np.einsum('bc,bc->b',X,Y)
 return np.array([t3,t4,t5,t6/m**4])
def delta(v,mu):
 a,b=v;return sum(mu[r-3]*sum(coef[r][k]*a**(r-k)*b**k for k in range(r+1)) for r in (3,4,5,6))
# Separate direct576-class recount for a random3-class zero-row-sum kernel.
rng=np.random.default_rng(930);S=rng.uniform(-.2,.2,(3,3));S=(S+S.T)/2;S=S-S.mean(0)[None,:]-S.mean(1)[:,None]+S.mean();v=(.1,-.1);X=np.where(fr,np.where(typ=='H',v[1],v[0]),0);full=np.kron(W,np.ones((3,3)))+np.kron(X,S)
# B192 translations remain automorphisms; enumerate all12 block positions and3 latent roots.
from family import F
reps=[(16*s)*3+a for s in range(12) for a in range(3)];direct=F(full,reps,[16]*len(reps));pred=F0+delta(v,moments(S));assert abs(direct-pred)<2e-14,(direct,pred)
data=json.loads((out/'graphs.json').read_text());data['clebsch_control']={'adjacency':[[int((i^j) in (1,2,4,8,15)) for j in range(16)] for i in range(16)]}
runs=[]
for name,d in data.items():
 A=np.array(d['adjacency'],dtype=float);m=len(A);S=A-A.mean();assert np.max(abs(S.sum(1)))<1e-12;mu=moments(S);lo,hi=S.min(),S.max()
 def bounds(w):return (max(-w/hi,(1-w)/lo),min((1-w)/hi,-w/lo))
 bs=[bounds(p),bounds(h)];starts=[(a,b) for a in [bs[0][0],0,bs[0][1]] for b in [bs[1][0],0,bs[1][1]]]
 opts=[minimize(lambda v:delta(v,mu),v,method='Nelder-Mead',bounds=bs,options={'maxiter':500,'xatol':1e-10,'fatol':1e-17}) for v in starts];best=min(opts,key=lambda r:r.fun);terms=[float(mu[r-3]*sum(coef[r][k]*best.x[0]**(r-k)*best.x[1]**k for k in range(r+1))) for r in (3,4,5,6)]
 r={'graph':name,'latent_order':m,'lift_order':n*m,'moments':mu.tolist(),'amplitudes_PH':best.x.tolist(),'bounds':bs,'terms_T3_T4_T5_T6':terms,'delta':float(best.fun),'predicted_F':float(F0+best.fun),'success':bool(best.success)};runs.append(r);print(json.dumps(r),flush=True)
(out/'latent-summary.json').write_text(json.dumps({'base_F':F0,'coefficients':{r:a.tolist() for r,a in coef.items()},'validation':{'direct576':direct,'expanded':pred,'error':abs(direct-pred)},'runs':runs,'seconds':time.monotonic()-start,'scope':'Floating moment expansion; no exact promotion, common centered SRG kernel on P/H pairs only.'},indent=2)+'\n')
