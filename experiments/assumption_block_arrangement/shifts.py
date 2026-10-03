import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[key]='1'
import sys,time,json,signal,hashlib,itertools
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'experiments/clebsch_size_coarse'))
import pilot as oracle
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
OUT=ROOT/'reports/assumption-block_arrangement-001';start=time.time();T=oracle.T;ph=np.array(json.load(open(OUT/'local.json'))['ph'])
d=np.arange(16)[:,None]^np.arange(16)[None,:];C=oracle.C

def matrix(S,v):
 ds=d[None,None,:,:]^S[:,:,None,None];c=np.isin(ds,list(C));gs=np.array([~c,c,v[0]*c,np.where(ds==0,v[1],c)]).astype(float)
 return np.take_along_axis(gs,T[None,:,:,None,None],axis=0)[0].transpose(0,2,1,3).reshape(192,192)
def rooted(W):
 total=0.
 for U in (W,1-W):
  for a in range(0,192,16):
   X=U[a][None,:]*U;total+=16*(U[a]@np.einsum('bc,bc->b',X,X@U))
 return float(total/192**4)
def score(S,v=ph):return rooted(matrix(S,v))
def save(name,obj):
 p=OUT/(name+'.tmp');p.write_text(json.dumps(obj,indent=2));p.replace(OUT/name)
zero=np.zeros((12,12),int);base=score(zero);rng=np.random.default_rng(121212)
a=rng.integers(0,16,12);gauge=a[:,None]^a[None,:]
changed=zero.copy();changed[0,1]=changed[1,0]=7
checks={'base':base,'gauge':score(gauge),'asymmetric':score(changed),'asymmetric_allroot':oracle.direct(matrix(changed,ph),np.ones(192)/192)}
assert abs(checks['base']-checks['gauge'])<1e-12
assert abs(checks['asymmetric']-checks['asymmetric_allroot'])<1e-12
save('shift-checks.json',checks);print('PID',os.getpid(),'checks',checks,flush=True)
edges=list(itertools.combinations(range(12),2));records=[];best_changed=None
for mode in ['local_shift','cycle_destroy_rebuild']:
 stop=time.time()+55;rng=np.random.default_rng(121212);S=zero.copy();f=base;best=zero.copy();bestf=base;n=0;accept=0;rebuilds=0
 while time.time()<stop-1:
  candidate=S.copy()
  if mode=='cycle_destroy_rebuild' and n%12==0:
   # Cycle holonomy cannot be removed by independent coarse-fiber relabels.
   cycle=rng.choice(12,int(rng.integers(3,7)),replace=False)
   for aa,bb in zip(cycle,np.roll(cycle,-1)):candidate[aa,bb]=candidate[bb,aa]=int(rng.integers(1,16))
   rebuilds+=1
  else:
   aa,bb=edges[int(rng.integers(len(edges)))];candidate[aa,bb]=candidate[bb,aa]=int(rng.integers(16))
  val=score(candidate);n+=1
  # Escape steps accepted only in structural lane, followed by greedy repair.
  accepted=val<f-1e-13 or (mode=='cycle_destroy_rebuild' and n%12==1)
  if accepted:S=candidate;f=val;accept+=1
  if val<bestf-1e-13:best=candidate.copy();bestf=val
  hol=int(sum((candidate[0,a]^candidate[a,b]^candidate[b,0])!=0 for a,b in itertools.combinations(range(1,12),2)))
  if hol and (best_changed is None or val<best_changed['F']):best_changed={'F':val,'shifts':candidate.tolist(),'ph':ph.tolist(),'holonomy_nonzero_triangles':hol,'mode':mode}
  records.append({'mode':mode,'trial':n,'F':val,'accepted':accepted,'holonomy':hol})
  if n%100==0:print(mode,n,bestf,f,flush=True)
 result={'F':bestf,'shifts':best.tolist(),'ph':ph.tolist(),'trials':n,'accepted':accept,'rebuilds':rebuilds,'budget_seconds':55}
 save(mode+'.json',result);print('COMPLETE',mode,result,flush=True)
# Polish strongest genuinely changed shift witness, even if worse.
if best_changed:
 S=np.array(best_changed['shifts']);r=minimize(lambda v:score(S,v)*1e5,ph,method='Nelder-Mead',bounds=[(0,1)]*2,options={'maxiter':80,'xatol':1e-8,'fatol':1e-10})
 best_changed.update(F_polished=score(S,r.x),ph_polished=r.x.tolist(),polish_success=bool(r.success));save('best-shift-changed.json',best_changed)
save('shift-basins.json',records)
save('shift-receipt.json',{'seconds':time.time()-start,'pid':os.getpid(),'seed':121212,'termination':'completed','command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/assumption_block_arrangement/shifts.py','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checker':'root contraction; representatives (s,0) for all twelve s; simultaneous XOR translation is explicitly preserved; separate full-root check','scope':'uniform 192 classes including repeats and shifted diagonal probabilities'})
