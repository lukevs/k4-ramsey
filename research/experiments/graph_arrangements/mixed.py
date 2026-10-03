import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import sys,json,time,subprocess,signal
from collections import defaultdict
import numpy as np
from scipy.optimize import minimize
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
sys.path.insert(0,str(Path('research/experiments/round5_C1').resolve()))
from base import base,Fval
start=time.monotonic();out=Path('reports/graph-arrangements-001');p=.779180833031354;h=.5342651880306992;W,typ,cls=base(p,h);n=len(W);Q=1-W;fr=(W>0)&(W<1);nb=[list(np.flatnonzero(row)) for row in fr];hc=(typ=='H').astype(int);coef=defaultdict(float)
def key(r,edges):return (r,tuple(int(hc[x,y]) for x,y in edges))
for x in range(n):
 for y in nb[x]:
  for z in nb[y]:
   if fr[z,x]:coef[key(3,[(x,y),(y,z),(z,x)])]+=4*np.sum(W[x]*W[y]*W[z]-Q[x]*Q[y]*Q[z])/n**4
   for t in nb[z]:
    if fr[t,x]:coef[key(4,[(x,y),(y,z),(z,t),(t,x)])]+=3*(W[x,z]*W[y,t]+Q[x,z]*Q[y,t])/n**4
  cn=[z for z in nb[x] if fr[z,y]]
  for z in cn:
   for t in cn:
    es=[(x,y),(x,z),(y,z),(x,t),(y,t)];coef[key(5,es)]+=6*(2*W[z,t]-1)/n**4
    if fr[z,t]:coef[key(6,es+[(z,t)])]+=2/n**4
positions={3:[0,3,1],4:[0,3,5,2],5:[0,1,3,2,4],6:[0,1,3,2,4,5]};F0=Fval(W)
data=json.loads((out/'graphs.json').read_text());data['clebsch_control']={'adjacency':[[int((i^j) in (1,2,4,8,15)) for j in range(16)] for i in range(16)]};common={r['graph']:r for r in json.loads((out/'latent-summary.json').read_text())['runs']};runs=[]
for name,g in data.items():
 A=g['adjacency'];m=len(A);k=sum(A[0]);file=out/(name+'-adjacency.txt');file.write_text(str(m)+'\n'+'\n'.join(' '.join(map(str,row)) for row in A))
 res=subprocess.run(['/private/tmp/graph-arrangements-patterns',str(file)],capture_output=True,text=True,check=True,timeout=30);(out/(name+'-patterns.txt')).write_text(res.stdout)
 rows=np.array([list(map(int,s.split())) for s in res.stdout.splitlines()]);assert int(rows[:,1].sum())==m**4;codes=rows[:,0];freq=rows[:,1]/m**4;rel=np.array([codes//3**i%3 for i in range(6)]).T
 # Variables Pdiag,Pedge,Hdiag,Hedge; nonedge values fixed by row mean.
 def values(x):return np.array([[(m*p-x[0]-k*x[1])/(m-1-k),x[1],x[0]],[(m*h-x[2]-k*x[3])/(m-1-k),x[3],x[2]]])
 def terms(x):
  D=values(x)-np.array([[p],[h]]);result=np.zeros(4)
  for (r,word),c in coef.items():result[r-3]+=c*(freq@np.prod(D[np.array(word)[None,:],rel[:,positions[r]]],axis=1))
  return result
 def constraints(x):
  v=values(x)[:,0];return np.r_[v,1-v]
 v=common[name]['amplitudes_PH'];rho=k/m;commonx=np.array([p-v[0]*rho,p+v[0]*(1-rho),h-v[1]*rho,h+v[1]*(1-rho)])
 assert abs(sum(terms(commonx))-common[name]['delta'])<2e-15
 rng=np.random.default_rng(930);starts=[commonx,np.array([p,p,h,h])]+[np.clip(np.array([p,p,h,h])+rng.uniform(-.12,.12,4),0,1) for _ in range(5)]
 best=None
 for j,x in enumerate(starts):
  opt=minimize(lambda v:sum(terms(v))*1e8,x,method='SLSQP',bounds=[(0,1)]*4,constraints=[{'type':'ineq','fun':constraints}],options={'maxiter':350,'ftol':1e-10})
  if constraints(opt.x).min()<-1e-8:continue
  r={'graph':name,'seed':j,'probabilities_PH_nonedge_edge_diag':values(opt.x).tolist(),'delta':float(sum(terms(opt.x))),'F':float(F0+sum(terms(opt.x))),'terms':terms(opt.x).tolist(),'success':bool(opt.success),'iterations':int(opt.nit),'message':str(opt.message)};runs.append(r)
  if best is None or r['F']<best['F']:best=r
 print('BEST',json.dumps(best),flush=True)
 (out/'mixed-summary.json').write_text(json.dumps({'base_F':F0,'runs':runs,'seconds':time.monotonic()-start,'coarse_words':[{'degree':r,'word':word,'coefficient':c} for (r,word),c in coef.items()],'scope':'Numerical mixed-kernel moment expansion; no promoted candidate'},indent=2)+'\n')
