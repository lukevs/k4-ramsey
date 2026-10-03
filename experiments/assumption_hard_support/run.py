import os,signal,time,json,sys,hashlib,itertools,platform
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(170)
import numpy as np
import scipy
from scipy.optimize import minimize
sys.path.insert(0,'experiments/family_mechanism_followup')
from local_patch import LocalPatch,direct
from pathlib import Path
OUT=Path('reports/assumption-hard_support-001');start=time.monotonic();mode=sys.argv[1]
parent=Path('reports/literature-two-parameter-001/graphon-candidate.json')
d=json.loads(parent.read_text());Q=d['edge_probability_denominator'];P=np.array(d['red_probability_numerators'])/Q
w=np.array(d['block_weights'],float);w/=w.sum()
rng=np.random.default_rng(93041)
meta=dict(mode=mode,pid=os.getpid(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),seed=93041,parent=str(parent),parent_sha256=hashlib.sha256(parent.read_bytes()).hexdigest(),python=sys.version,numpy=np.__version__,scipy=scipy.__version__,machine=platform.platform(),scope='B192 dyadic parent, not incumbent; uniform normalized weights, ordered tuples including repeats and diagonal probabilities',command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/assumption_hard_support/run.py '+mode,timeout_seconds=170)
print(json.dumps(meta),flush=True)
if mode=='tiny':
 tests=[]
 for n in (6,7):
  X=rng.uniform(.1,.9,(n,n));X=(X+X.T)/2;ww=rng.uniform(.1,1,n);ww/=ww.sum();S=list(range(4));m=LocalPatch(X,ww,S);B=m.base.copy();B[0,1]=B[1,0]=.02;B[1,2]=B[2,1]=.96;B[2,3]=B[3,2]=.43
  V=X.copy();V[np.ix_(S,S)]=B;a=m.evaluate(B)[0];b=direct(V,ww)-direct(X,ww);assert abs(a-b)<3e-14
  tests.append(dict(n=n,polynomial=a,direct=b,error=abs(a-b)))
 meta['tests']=tests
else:
 # triangles with one hard bridge and two fractional bridges, sorted by hard-edge inward derivative
 gs=json.load(open('reports/finite-joint-coarse-face-diagonal-001/gradients.json'));gl={(min(r['i'],r['j']),max(r['i'],r['j'])):r['gradient'] for r in gs}
 triangles=[]
 for u in range(192):
  for v in range(u+1,192):
   if P[u,v] not in (0.,1.):continue
   for z in np.where((P[u]>0)&(P[u]<1)&(P[v]>0)&(P[v]<1))[0]:
    triangles.append((gl[(u,v)]*(1-2*P[u,v]),u,v,int(z)))
 rng.shuffle(triangles);triangles.sort(key=lambda x:x[0]);print('triangles',len(triangles),flush=True)
 # preserve diversity in endpoint probability type and hard derivative orbit
 selected=[];seen=set()
 for row in triangles:
  _,u,v,z=row;key=(round(row[0],6),P[u,v],P[u,z],P[v,z])
  if key not in seen:seen.add(key);selected.append(row)
 selected=selected[:12];rows=[]
 W=np.repeat(np.repeat(P,2,0),2,1);weights=np.repeat(w/2,2)
 for _,u,v,z in selected:
  if time.monotonic()-start>135:break
  S=[2*u,2*u+1,2*v,2*v+1,2*z,2*z+1];m=LocalPatch(W,weights,S);base=m.base
  def bridge(a,b,polar=False):
   D=np.zeros((6,6))
   for i,j in itertools.product(range(2),repeat=2):D[2*a+i,2*b+j]=D[2*b+j,2*a+i]=(-1)**(i+j) if polar else 1
   return D
  hard=bridge(0,1)*(1-2*P[u,v])
  if mode=='means':
   dirs=np.array([hard,bridge(0,2),bridge(1,2)]);bounds=[(0,1),(-P[u,z],1-P[u,z]),(-P[v,z],1-P[v,z])];names=['hard_open','fractional_uz_mean','fractional_vz_mean']
  else:
   dirs=np.array([hard,bridge(0,1,True),bridge(0,2,True),bridge(1,2,True)]);bounds=[(0,1),(-.5,.5),(-min(P[u,z],1-P[u,z]),min(P[u,z],1-P[u,z])),(-min(P[v,z],1-P[v,z]),min(P[v,z],1-P[v,z]))];names=['hard_open','new_hard_amplitude','uz_amplitude','vz_amplitude']
  def ev(x):return m.evaluate(base+np.einsum('i,ijk->jk',x,dirs),dirs)
  cons=[]
  if mode!='means':cons=[{'type':'ineq','fun':lambda x:np.array([x[0]-x[1],x[0]+x[1],1-x[0]-x[1],1-x[0]+x[1]])}]
  controls={}
  for name in ('parent_only','amplitude_only','joint'):
   bb=list(bounds)
   if name=='parent_only':bb=[bb[0]]+[(0,0)]*(len(bb)-1)
   if name=='amplitude_only':bb[0]=(0,0)
   starts=[np.zeros(len(bb))]
   for t in (.25,.75,1.):
    xx=np.array([(lo+hi)/2 for lo,hi in bb]);xx[0]=t if bb[0]!=(0,0) else 0
    if mode!='means':xx[1]=0;xx[2:]=[rng.choice([-1,1])*min(abs(lo),abs(hi)) for lo,hi in bb[2:]]
    starts.append(xx)
   best=(0.,np.zeros(len(bb)));runs=[]
   for x0 in starts:
    def f(x):
     val,g=ev(x);return val*1e10,g*1e10
    opt=minimize(f,x0,jac=True,bounds=bb,constraints=cons,method='SLSQP',options={'maxiter':60,'ftol':1e-10})
    B=base+np.einsum('i,ijk->jk',opt.x,dirs);valid=B.min()>=-1e-9 and B.max()<=1+1e-9;val=ev(opt.x)[0]
    runs.append(dict(start=x0.tolist(),x=opt.x.tolist(),delta=val,success=bool(opt.success),feasible=bool(valid)))
    if valid and val<best[0]:best=(val,opt.x.copy())
   controls[name]=dict(delta=best[0],x=best[1].tolist(),runs=runs)
  row=dict(triangle=[u,v,z],hard_probability=P[u,v],fractional=[P[u,z],P[v,z]],variables=names,controls=controls);rows.append(row);print(json.dumps(row),flush=True)
  meta['rows']=rows;meta['seconds']=time.monotonic()-start;(OUT/(mode+'.json')).write_text(json.dumps(meta,indent=2)+'\n')
 meta['triangles_available']=len(triangles);meta['distinct_types_selected']=len(selected)
meta['seconds']=time.monotonic()-start;meta['termination']='completed';(OUT/(mode+'.json')).write_text(json.dumps(meta,indent=2)+'\n');print('completed',meta['seconds'],flush=True)
