import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import numpy as np,json,time,signal
from pathlib import Path
from scipy.optimize import minimize
signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
start=time.monotonic();out=Path('reports/flexible-mechanisms-001');old=json.loads(Path('reports/graph-arrangements-001/mixed-summary.json').read_text());words=old['coarse_words'];F0=old['base_F'];p=.779180833031354;h=.5342651880306992;rho=5/16
A=np.array([[int((i^j) in (1,2,4,8,15)) for j in range(16)] for i in range(16)]);R=A+2*np.eye(16,dtype=int)
# x=Pdiag,Pedge,Hdiag,Hedge; six deviations affine in x.
J=np.array([[-.1,-.5,0,0],[0,1,0,0],[1,0,0,0],[0,0,-.1,-.5],[0,0,0,1],[0,0,1,0]])
const=np.array([1.6*p,0,0,1.6*h,0,0]);means=np.array([p]*3+[h]*3)
verts=np.indices((16,)*4).reshape(4,-1);edges={3:[(0,1),(1,2),(2,0)],4:[(0,1),(1,2),(2,3),(3,0)],5:[(0,1),(0,2),(1,2),(0,3),(1,3)],6:[(0,1),(0,2),(1,2),(0,3),(1,3),(2,3)]}
def build(perm):
 RH=R[np.ix_(perm,perm)];acc={}
 for w in words:
  r=w['degree'];code=np.zeros(16**4,dtype=np.int64)
  for (i,j),typ in zip(edges[r],w['word']):
   rel=(R if typ==0 else RH)[verts[i],verts[j]];code+=7**(rel+3*typ)
  hist=np.bincount(code,minlength=7**6)
  for z in np.flatnonzero(hist):acc[(r,int(z))]=acc.get((r,int(z)),0)+w['coefficient']*hist[z]/16**4
 keys=list(acc);ex=np.array([[z//7**j%7 for j in range(6)] for r,z in keys]);cs=np.array([acc[k] for k in keys]);degrees=np.array([r for r,z in keys])
 def evaluate(x,grad=False):
  D=const+J@x-means;mon=np.prod(D[None,:]**ex,axis=1);terms=np.array([cs[degrees==r]@mon[degrees==r] for r in (3,4,5,6)])
  if not grad:return terms
  gd=np.zeros(6)
  for j in range(6):
   ee=ex.copy();ee[:,j]=np.maximum(0,ee[:,j]-1);gd[j]=np.sum(cs*ex[:,j]*np.prod(D[None,:]**ee,axis=1))
  return terms,gd@J
 return evaluate
center=np.array([p,p,h,h]);Ma=np.array([-rho,1-rho,0,0]);Mb=np.array([0,0,-rho,1-rho]);Dp=np.array([1,0,0,0]);Dh=np.array([0,0,1,0])
maps={'opposite':np.column_stack([-Ma+Mb]),'independent':np.column_stack([Ma,Mb]),'P_diagonal':np.column_stack([Ma,Mb,Dp]),'H_diagonal':np.column_stack([Ma,Mb,Dh]),'both_diagonals':np.eye(4)}
bestold=min((r for r in old['runs'] if r['graph']=='clebsch_control'),key=lambda r:r['F']);v=np.array(bestold['probabilities_PH_nonedge_edge_diag']);oldx=v[:,[2,1]].ravel()
rng=np.random.default_rng(93001);eval0=build(np.arange(16));assert abs(sum(eval0(oldx))-bestold['delta'])<1e-17
# Central differences guard gradient implementation.
test=center+np.array([-.03,.02,.04,-.05]);t,g=eval0(test,True)
fd=np.array([(sum(eval0(test+np.eye(4)[i]*1e-5))-sum(eval0(test-np.eye(4)[i]*1e-5)))/2e-5 for i in range(4)])
assert max(abs(g-fd))<1e-12
runs=[]
def fit(ev,label,M,extra=[]):
 starts=[np.linalg.lstsq(M,oldx-center,rcond=None)[0],np.zeros(M.shape[1])]+[rng.uniform(-.2,.2,M.shape[1]) for _ in range(5)]+extra
 best=None
 for y0 in starts:
  fun=lambda y:(sum(ev(center+M@y,True)[0])*1e8,ev(center+M@y,True)[1]@M*1e8)
  def con(y):
   z=const+J@(center+M@y);return np.r_[z,1-z]
  opt=minimize(fun,y0,jac=True,method='SLSQP',constraints=[{'type':'ineq','fun':con,'jac':lambda y:np.r_[J@M,-J@M]}],options={'maxiter':180,'ftol':1e-10})
  if min(con(opt.x)) < -1e-8:continue
  x=center+M@opt.x;val=sum(ev(x))
  if best is None or val<best['delta']:best=dict(label=label,x=x.tolist(),probabilities=(const+J@x).reshape(2,3).tolist(),terms=ev(x).tolist(),delta=float(val),F=F0+float(val),success=bool(opt.success),iterations=int(opt.nit))
 return best
for name,M in maps.items():
 r=fit(eval0,name,M);runs.append(r);print(json.dumps(r),flush=True)
(out/'ablation.json').write_text(json.dumps(dict(base_F=F0,runs=runs,gradient_error=float(max(abs(g-fd)))),indent=2)+'\n')
# Relative permutations change eigenvector alignment but preserve spectra of H.
align=[]
for seed in range(8):
 perm=np.arange(16)
 if seed==1:perm[[0,1]]=perm[[1,0]]
 elif seed>1:perm=rng.permutation(16)
 ev=build(perm);r=fit(ev,'alignment_'+str(seed),np.eye(4));r['permutation']=perm.tolist();r['at_aligned_optimum_delta']=float(sum(ev(np.array(runs[-1]['x']))))
 P=(const+J@np.array(r['x'])-means)[:3][R];H=(const+J@np.array(r['x'])-means)[3:][R[np.ix_(perm,perm)]]
 r['commutator_norm']=float(np.linalg.norm(P@H-H@P)/16**2);r['cubic_trace_PPH']=float(np.trace(P@P@H)/16**3)
 align.append(r);print('ALIGN',seed,r['F'],flush=True)
 (out/'alignment.json').write_text(json.dumps(dict(runs=align,seconds=time.monotonic()-start),indent=2)+'\n')
# Active face Hessian for aligned four-variable optimum.
x=np.array(runs[-1]['x']);_,g=eval0(x,True);eps=1e-4
H=np.column_stack([(eval0(x+np.eye(4)[i]*eps,True)[1]-eval0(x-np.eye(4)[i]*eps,True)[1])/(2*eps) for i in range(4)])
free=np.flatnonzero((x>1e-7)&(x<1-1e-7));info=dict(x=x.tolist(),gradient=g.tolist(),hessian_eigenvalues=np.linalg.eigvalsh((H+H.T)/2).tolist(),active_face_indices=free.tolist(),active_face_eigenvalues=np.linalg.eigvalsh(H[np.ix_(free,free)]).tolist(),seconds=time.monotonic()-start)
(out/'curvature.json').write_text(json.dumps(info,indent=2)+'\n')
