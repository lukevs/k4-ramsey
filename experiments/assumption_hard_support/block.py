import os,signal,time,json,sys,itertools,hashlib,platform
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(170)
import numpy as np
import scipy
from scipy.optimize import minimize
from pathlib import Path
sys.path.insert(0,'experiments/family_mechanism_followup');from local_patch import LocalPatch
sys.path.insert(0,'experiments/round4_E5');from load import load
OUT=Path('reports/assumption-hard_support-001');start=time.monotonic();seed=93042;rng=np.random.default_rng(seed)
deep=len(sys.argv)>1 and sys.argv[1]=='depth2';label='depth2' if deep else 'block';mult=10 if deep else 5
parent_path='reports/round4-E5-depth1-001/graphon-candidate.json' if deep else 'reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json'
amp_path='reports/round4-E5-depth2-001/a_int.npy' if deep else 'reports/round4-E5-depth1-001/a_int.npy'
N,Q,w=load(parent_path);A=np.load(amp_path);n=len(N);W=np.empty((2*n,2*n))
for s,t in itertools.product(range(2),repeat=2):W[s::2,t::2]=(N+(-1)**(s+t)*A)/Q
B=json.load(open('reports/literature-two-parameter-001/graphon-candidate.json'));B=np.array(B['red_probability_numerators'])/B['edge_probability_denominator']
gs=json.load(open('reports/finite-joint-coarse-face-diagonal-001/gradients.json'));cheap=[(r['i'],r['j']) for r in gs if r['i']!=r['j'] and B[r['i'],r['j']]==1 and -r['gradient']<.1]
# Different derivative scales in saved unnormalized gradient: select two weakest solid-one levels.
one=sorted(set(round(-r['gradient'],6) for r in gs if r['i']!=r['j'] and B[r['i'],r['j']]==1))[:2]
cheap=[(r['i'],r['j']) for r in gs if r['i']!=r['j'] and B[r['i'],r['j']]==1 and round(-r['gradient'],6) in one]
neighbor={i:[] for i in range(192)}
for u,v in cheap:neighbor[u].append(v);neighbor[v].append(u)
sets=[]
for attempt in range(4000):
 u=int(rng.integers(192));near=neighbor[u]
 if len(near)<3:continue
 v=int(rng.choice(near));common=np.where((B[u]>0)&(B[u]<1)&(B[v]>0)&(B[v]<1))[0]
 if not len(common):continue
 z=int(rng.choice(common));fourth=int(rng.choice(neighbor[z]));cc=[u,v,z,fourth]
 if len(set(cc))<4:continue
 ss=[mult*c+int(rng.integers(mult)) for c in cc];edges=list(itertools.combinations(range(4),2));hard=[e for e in edges if N[ss[e[0]],ss[e[1]]] in (0,Q)];frac=[e for e in edges if e not in hard]
 if len(hard)>=2 and len(frac)>=2:sets.append(ss)
 if len(sets)==12:break
meta=dict(pid=os.getpid(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),seed=seed,n=2*n,denominator=int(Q),parent=parent_path,amplitudes=amp_path,baseline='.030138887566497220' if deep else '.03013889526362365',scope=('depth2 incumbent' if deep else 'first-layer1920')+';4 parent-node/8 lifted-node internal patches,all repeats/diagonals included,uniform weights',command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/assumption_hard_support/block.py'+(' depth2' if deep else ''),timeout=170,rows=[])
print(json.dumps(meta),flush=True)
for ss in sets:
 if time.monotonic()-start>125:break
 S=[2*s+t for s in ss for t in range(2)];model=LocalPatch(W,np.repeat(w/2,2),S);base=model.base;Ds=[];hard=np.zeros((8,8));fracs=[]
 for i,j in itertools.combinations(range(4),2):
  u,v=ss[i],ss[j];p=N[u,v]/Q
  if p in (0.,1.):
   for s,t in itertools.product(range(2),repeat=2):hard[2*i+s,2*j+t]=hard[2*j+t,2*i+s]=1-2*p
  else:
   D=np.zeros((8,8))
   for s,t in itertools.product(range(2),repeat=2):D[2*i+s,2*j+t]=D[2*j+t,2*i+s]=(-1)**(s+t)
   Ds.append(D);a=A[u,v]/Q;cap=min(p,1-p);fracs.append(dict(edge=[i,j],old_amplitude=a,bounds=[-cap-a,cap-a]))
 dirs=np.array([hard,*Ds]);bounds=[(0,1)]+[tuple(f['bounds']) for f in fracs]
 def ev(x):return model.evaluate(base+np.einsum('i,ijk->jk',x,dirs),dirs)
 controls={}
 for name in ('parent_only','amplitude_only','joint'):
  bb=list(bounds)
  if name=='parent_only':bb=[bb[0]]+[(0,0)]*(len(bb)-1)
  if name=='amplitude_only':bb[0]=(0,0)
  starts=[np.zeros(len(bb))]
  for t in (.2,.6,1.):
   xx=np.array([rng.uniform(lo,hi) for lo,hi in bb]);xx[0]=t if bb[0]!=(0,0) else 0;starts.append(xx)
  best=(0.,np.zeros(len(bb)));runs=[]
  for x0 in starts:
   def f(x):
    val,g=ev(x);return 1e12*val,1e12*g
   opt=minimize(f,x0,jac=True,bounds=bb,method='L-BFGS-B',options={'maxiter':80,'ftol':1e-14,'gtol':1e-8});val=ev(opt.x)[0]
   runs.append(dict(start=x0.tolist(),x=opt.x.tolist(),delta=val,success=bool(opt.success)))
   if val<best[0]:best=val,opt.x.copy()
  controls[name]=dict(delta=best[0],x=best[1].tolist(),runs=runs)
 row=dict(parent_nodes=ss,hard_edges=int(np.count_nonzero(hard)//8),fractional=fracs,controls=controls);meta['rows'].append(row);meta['seconds']=time.monotonic()-start;(OUT/(label+'.json')).write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(row),flush=True)
meta['seconds']=time.monotonic()-start;meta['termination']='completed';(OUT/(label+'.json')).write_text(json.dumps(meta,indent=2)+'\n');print('completed',meta['seconds'],flush=True)
