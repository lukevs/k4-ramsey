import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,subprocess,time,signal
import numpy as np
from scipy.optimize import minimize
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s limit')));signal.alarm(175)
start=time.monotonic();out=Path('reports/graph-arrangements-001');runs=[]
for name in ('gewirtz','M22','higman_sims'):
 for mode in ('plain','ambient','anchor'):
  folder=out/f'{name}-{mode}-0';cfg=json.loads((folder/'config.json').read_text());r=cfg['relation_count'];n=cfg['n']
  subprocess.run(['/private/tmp/graph-arrangements-export',str(folder/'fixture.txt'),str(folder/'polynomial.txt')],check=True,timeout=20)
  lines=(folder/'polynomial.txt').read_text().splitlines();mass,k=map(int,lines[0].split());assert mass==n**4
  table=np.array([list(map(int,s.split())) for s in lines[1:]],dtype=np.int64);counts=table[:,0];ids=table[:,1:];weights=counts/mass
  def fun(p):
   x=p[ids];y=1-x;v=float(weights@(np.prod(x,axis=1)+np.prod(y,axis=1)));g=np.zeros(r)
   for j in range(6):
    keep=[i for i in range(6) if i!=j];vals=weights*(np.prod(x[:,keep],axis=1)-np.prod(y[:,keep],axis=1));g+=np.bincount(ids[:,j],weights=vals,minlength=r)
   return v,g
  p0=np.array(cfg['probability_numerators'])/cfg['q'];native=json.loads((folder/'native.json').read_text());assert abs(fun(p0)[0]-native['parent_decimal'])<1e-14
  rng=np.random.default_rng(930);starts=[np.array(native['continuous_probabilities'])]+[rng.uniform(.01,.99,r) for _ in range(4)]
  best=None
  for j,p in enumerate(starts):
   opt=minimize(fun,p,jac=True,method='L-BFGS-B',bounds=[(0,1)]*r,options={'maxiter':450,'ftol':1e-14,'gtol':1e-9,'maxls':30})
   row={'graph':name,'partition':mode,'seed':j,'F':float(opt.fun),'probabilities':opt.x.tolist(),'iterations':int(opt.nit),'success':bool(opt.success),'message':str(opt.message)};runs.append(row)
   if best is None or opt.fun<best['F']:best=row
  (folder/'polished.json').write_text(json.dumps(best,indent=2)+'\n');print(json.dumps({k:v for k,v in best.items() if k!='probabilities'}),flush=True)
  (out/'polish-summary.json').write_text(json.dumps({'runs':runs,'seconds':time.monotonic()-start},indent=2)+'\n')
