import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']: os.environ[key]='1'
import sys, time, json, signal, hashlib, itertools, math
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'research/experiments/clebsch_size_coarse'))
import pilot as oracle
signal.signal(signal.SIGALRM,signal.SIG_DFL); signal.alarm(175)
OUT=ROOT/'reports/assumption-block_arrangement-001'; start=time.time()
def save(name,obj):
 p=OUT/(name+'.tmp'); p.write_text(json.dumps(obj,indent=2)); p.replace(OUT/name)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
co=np.load(ROOT/'reports/clebsch-size-coarse-001/coefficients.npy').reshape(4096,-1)
ix=np.array(list(itertools.combinations_with_replacement(range(12),4)))
mult=np.array([24/math.prod(math.factorial(list(x).count(a)) for a in set(x)) for x in ix])/12**4
pairs=list(itertools.combinations(range(4),2)); edges=list(itertools.combinations_with_replacement(range(12),2))
powers=4**np.arange(5,-1,-1)
def signature(t):return sum(p*t[ix[:,i],ix[:,j]] for p,(i,j) in zip(powers,pairs))
effects=[]
for a,b in edges:
 effects.append(sum(p*(((ix[:,i]==a)&(ix[:,j]==b))|((ix[:,i]==b)&(ix[:,j]==a))) for p,(i,j) in zip(powers,pairs)))
effects=np.array(effects)
def polish(t,ph):
 c=mult@co[signature(t)]
 def fg(v):
  b,dp,dh=oracle.basis(*v);return (float(c@b)*1e5,np.array([c@dp,c@dh])*1e5)
 r=minimize(fg,ph,jac=True,bounds=[(0,1)]*2,method='L-BFGS-B',options={'ftol':1e-14,'gtol':1e-8,'maxiter':80})
 return float(r.fun/1e5),r.x
T=oracle.T.copy(); base,ph=polish(T,np.array([.77918,.534265])); K=co@oracle.basis(*ph)[0]
def score(t):return float(mult@K[signature(t)])
def descend(t,limit,deadline):
 t=t.copy(); sig=signature(t); f=float(mult@K[sig]); moves=0
 for _ in range(limit):
  if time.time()>deadline:break
  best=(f,None,None,None)
  for ei,(a,b) in enumerate(edges):
   old=t[a,b]; cand=sig[None,:]+(np.arange(4)-old)[:,None]*effects[ei]
   vals=K[cand]@mult; typ=int(np.argmin(vals))
   if vals[typ]<best[0]-1e-14:best=(float(vals[typ]),ei,typ,cand[typ])
  if best[1] is None:break
  f,ei,typ,sig=best; a,b=edges[ei];t[a,b]=t[b,a]=typ;moves+=1
 return t,f,moves
# Every coarse root is retained; compare to separate full-root contraction.
checks={'baseline':base,'baseline_direct':oracle.direct(oracle.matrix(T,*ph),np.ones(192)/192)}
rng=np.random.default_rng(120012)
for n in range(2):
 t=T.copy()
 for a,b in [edges[j] for j in rng.choice(len(edges),8,replace=False)]:t[a,b]=t[b,a]=int(rng.integers(4))
 checks['asymmetric_'+str(n)]=[score(t),oracle.direct(oracle.matrix(t,*ph),np.ones(192)/192)]
assert abs(checks['baseline_direct']-base)<1e-12
assert all(abs(checks['asymmetric_'+str(n)][0]-checks['asymmetric_'+str(n)][1])<1e-12 for n in range(2))
save('initial-checks.json',checks)
print('PID',os.getpid(),'baseline',base,'checks',checks,flush=True)
rows=[]; witnesses={}; budgets=45
for mode in ['local','destroy_rebuild']:
 deadline=time.time()+budgets; rng=np.random.default_rng(120012); best=T.copy(); bestf=base; steps=0; evals=0; returns=0; seen=set(); accepted=0; strongest_changed=None
 while time.time()<deadline-.15:
  t=T.copy()
  if mode=='destroy_rebuild':
   # Rebuild all incident assignments of 3-5 rows, not a vertex permutation.
   rowsel=rng.choice(12,size=int(rng.integers(3,6)),replace=False)
   for a,b in edges:
    if a in rowsel or b in rowsel:
     if rng.random()<.45:t[a,b]=t[b,a]=int(rng.integers(4))
  else:
   # Local-only control receives the same wall budget and parent.
   pass
  raw=score(t); t,f,n=descend(t,100,deadline); steps+=n;evals+=1
  key=t.tobytes();seen.add(key);dist=int(np.count_nonzero(np.triu(t!=T)))
  if dist==0:returns+=1
  if dist and (strongest_changed is None or f<strongest_changed['F']):strongest_changed={'F':f,'types':t.tolist(),'ph':ph.tolist(),'distance':dist}
  if f<bestf-1e-13:best,bestf=t.copy(),f;accepted+=1
  rows.append({'mode':mode,'trial':evals,'raw':raw,'F':f,'moves':n,'hamming':dist})
  if evals%10==0: print(mode,'trial',evals,'best',bestf,'last',f,'moves',steps,flush=True)
 polished,pp=polish(best,ph)
 witnesses[mode]={'F':polished,'types':best.tolist(),'ph':pp.tolist(),'budget_seconds':budgets,'trials':evals,'moves':steps,'unique_labelled_endpoints':len(seen),'exact_parent_returns':returns,'improvements':accepted,'strongest_changed':strongest_changed}
 save(mode+'.json',witnesses[mode]);save('basins.json',rows)
 print('COMPLETE',mode,json.dumps(witnesses[mode]),flush=True)
save('receipt.json',{'seconds':time.time()-start,'pid':os.getpid(),'seed':120012,'termination':'completed','scope':'uniform 192 classes, shared p/h, arbitrary symmetric 12x12 types including diagonal; all repeats retained','command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python research/experiments/assumption_block_arrangement/search.py','hashes':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),ROOT/'research/experiments/clebsch_size_coarse/pilot.py',ROOT/'reports/clebsch-size-coarse-001/coefficients.npy',ROOT/'research/experiments/round4_E11/rule.json']},'python':sys.version,'numpy':np.__version__})
