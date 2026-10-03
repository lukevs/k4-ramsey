"""Symmetry-guided affine insertion screen; no global optimality claim."""
import signal,time,os
signal.signal(signal.SIGALRM,signal.SIG_DFL); signal.alarm(175)
START=time.time()
import sys,json,hashlib,platform,itertools
from pathlib import Path
import numpy as np
import scipy
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[2]; sys.path.insert(0,str(ROOT))
from experiments.clebsch_bowl.audit_weighted import density,literal
OUT=ROOT/'reports/assumption-symmetry_insertion-001'
SOURCE=ROOT/'reports/clebsch-size-coarse-002/weighted-k12.json'
D=json.loads(SOURCE.read_text()); W=np.array(D['red_probability_numerators'],float)/D['edge_probability_denominator']; n=len(W); m=np.ones(n)/n

def dump(name,obj):
 p=OUT/name; t=p.with_suffix('.tmp'); t.write_text(json.dumps(obj,indent=2)+'\n'); t.replace(p)
def rooted(q,V=W,w=m):
 f=0.; g=np.zeros(len(q))
 for A,z,s in [(V,q,1),(1-V,1-q,-1)]:
  v=w*z; B=(A*v)@A; h=np.sum(B*A*v[None,:],axis=1); f+=v@h; g+=3*s*w*h
 return float(f),g
def coeff(q,d,F,V=W,w=m):
 v=w*q*q; u=w*(1-q)**2
 return np.array([F,rooted(q,V,w)[0],d*(v@V@v)+(1-d)*(u@(1-V)@u),d**3*(w@q**3)+(1-d)**3*(w@(1-q)**3),d**6+(1-d)**6])
def poly(e,c): return float(sum(k*e**i*(1-e)**(4-i)*c[i] for i,k in enumerate([1,4,6,4,1])))
def materialize(q,d,e):
 V=np.empty((n+1,n+1)); V[:-1,:-1]=W; V[-1,:-1]=V[:-1,-1]=q; V[-1,-1]=d
 return V,np.r_[m*(1-e),e]
class Budget(Exception):pass

def fit(B,q0,label,seed,budget=100,release=False):
 count=0; best=[float('inf'),q0.copy()]; t=time.time()
 def fun(z):
  nonlocal count
  if count>=budget: raise Budget()
  q=z if release else .5+B@z
  f,g=rooted(q); count+=1
  if q.min()>=-1e-10 and q.max()<=1+1e-10 and f<best[0]:best[:]=[f,np.clip(q,0,1)]
  return f*1e4,(g if release else B.T@g)*1e4
 z0=q0 if release else B.T@(q0-.5)
 try:
  if release:r=minimize(fun,z0,jac=True,method='L-BFGS-B',bounds=[(0,1)]*n,options={'maxiter':1000,'ftol':1e-14,'gtol':1e-8,'maxls':20})
  else:r=minimize(fun,z0,jac=True,method='SLSQP',constraints={'type':'ineq','fun':lambda z:np.r_[.5+B@z,.5-B@z],'jac':lambda z:np.vstack([B,-B])},options={'maxiter':1000,'ftol':1e-12})
  status=str(r.message)
 except Budget:status='evaluation budget'
 # Pad converged runs with evaluations of the best profile to match total oracle calls exactly.
 used=count
 while count<budget:rooted(best[1]);count+=1
 q=best[1]; rr=rooted(q)[0]; dist=np.sqrt(np.mean((W-q)**2,axis=1))
 row={'label':label,'seed':seed,'dimension':n if release else B.shape[1],'budget':budget,'optimization_evaluations':used,'total_evaluations':count,'status':status,'R':rr,'R_minus_F':rr-F,'slope':4*(rr-F),'nearest_row_rms':float(dist.min()),'q':q.tolist(),'seconds':time.time()-t}
 print(json.dumps({k:v for k,v in row.items() if k!='q'}),flush=True);return row

if __name__=='__main__':
 dump('active.json',{'pid':os.getpid(),'start':START,'deadline':START+175,'stage':'matched symmetry/random affine screens'})
 F=density(W,m); print('BASE',F,flush=True)
 chars=np.array([[(-1)**((x&s).bit_count()) for s in range(16)] for x in range(16)],float)/4
 A=np.array([[int((x^y) in [1,2,4,8,15]) for y in range(16)] for x in range(16)])
 ev=np.diag(chars.T@A@chars).round().astype(int)
 checks={'F_equal_mass':F,'char_orthogonality':float(abs(chars.T@chars-np.eye(16)).max()),'char_eigen_error':float(abs(A@chars-chars*ev).max()),'character_eigenvalues':ev.tolist()}
 # Translation covariance and coarse-character Hessian blocks; each character is a real 1D F2^4 irrep.
 H=np.zeros((n,n))
 for V in [W,1-W]: H+=3*V*((V*m)@V)*m[:,None]*m[None,:]
 full=np.kron(np.eye(12),chars); HH=full.T@H@full
 checks['hessian_character_offblock_error']=float(max(abs(HH[i,j]) for i in range(n) for j in range(n) if i%16!=j%16))
 checks['hessian_coarse_eigenvalues_by_character']={str(s):np.linalg.eigvalsh(HH[np.ix_(np.arange(s,n,16),np.arange(s,n,16))]).tolist() for s in range(16)}
 roots=np.array([rooted(r)[0] for r in W]);checks['existing_root_range']=[float(roots.min()),float(roots.max())]
 ids=list(range(n))+[0]; mw=np.r_[m,m[0]*.37];mw[0]*=.63
 checks['split_null_error']=abs(density(W[np.ix_(ids,ids)],mw)-F)
 rng=np.random.default_rng(930501); q=rng.uniform(size=n); _,g=rooted(q);h=1e-5
 checks['gradient_error']=max(abs((rooted(q+np.eye(n)[i]*h)[0]-rooted(q-np.eye(n)[i]*h)[0])/(2*h)-g[i]) for i in [0,13,80,191])
 checks['tiny_oracle_errors']=[]
 for nn in [2,3,4]:
  N=rng.integers(0,14,(nn,nn));N=np.triu(N)+np.triu(N,1).T; weights=rng.integers(1,6,nn)
  checks['tiny_oracle_errors'].append(abs(density(N/13,weights)-float(literal(N,13,weights))))
 checks['polynomial_error']=abs(poly(.07,coeff(q,.31,F))-density(*materialize(q,.31,.07)))
 assert max(checks['char_orthogonality'],checks['char_eigen_error'],checks['split_null_error'],checks['gradient_error'],checks['polynomial_error'],*checks['tiny_oracle_errors'])<1e-9
 dump('checks.json',checks)
 rows=[];constant=np.kron(np.eye(12),chars[:,[0]])
 for eig in [1,-3]:
  latent=chars[:,np.r_[0,np.where(ev==eig)[0]]]; guided=np.kron(np.eye(12),latent); dim=guided.shape[1]
  for seed in [501,502,503]:
   rr=np.random.default_rng(seed); raw=rr.normal(size=(n,dim-12));raw-=constant@(constant.T@raw);Q=np.linalg.qr(raw)[0];random=np.column_stack([constant,Q])
   z=rr.normal(size=dim)
   for label,B in [('guided',guided),('random',random)]:
    delta=B@z; q0=.5+.4*delta/max(abs(delta));row=fit(B,q0,f'{label}_eig{eig}',seed);rows.append(row);dump('runs.json',rows)
   if time.time()-START>125:break
 # Equal-budget unrestricted release of each family's best seed, not a separate unrestricted multistart campaign.
 for label in sorted(set(r['label'] for r in rows)):
  if time.time()-START>145:break
  best=min((r for r in rows if r['label']==label),key=lambda r:r['R'])
  rows.append(fit(None,np.array(best['q']),label+'_release',best['seed'],budget=80,release=True));dump('runs.json',rows)
 dump('receipt.json',{'start':START,'end':time.time(),'seconds':time.time()-START,'pid':os.getpid(),'termination':'completed','F':F,'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256((ROOT/'experiments/clebsch_bowl/audit_weighted.py').read_bytes()).hexdigest(),'numpy':np.__version__,'scipy':scipy.__version__,'python':sys.version,'platform':platform.platform(),'thread_env':{k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']},'scope':'B192 exact equal masses; affine eigenspace versus same-dimension random subspaces, then release; numerical only'})
 dump('active.json',{'pid':None,'stage':'completed','end':time.time()});print('DONE',time.time()-START,flush=True)
