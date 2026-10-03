import os
for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[k]='1'
import numpy as np,json,signal,time,hashlib
from pathlib import Path
signal.alarm(175)
root=Path('reports/assumption-discrete_basins-001')
def obj(W):
 n=len(W);total=0
 for P in [W,1-W]:
  V=P*P[0][None,:]
  total+=np.sum(P[0]*np.sum((V@P)*V,axis=1))
 return float(total/n**3)
results=[]
for name in ['recovery-covered-downhill','f2-s1101-downhill','f2-s1102-downhill','f2-s1103-downhill']:
 st=time.time();p=root/(name+'.json');d=json.loads(p.read_text());s=np.array(d['generators']);n=len(s);idx=np.arange(n);A=s[idx[:,None]^idx[None,:]];xs=np.linspace(0,1,7);ys=np.array([obj(.5+x*(A-.5)) for x in xs]);coef=np.polynomial.polynomial.polyfit(xs,ys,6);rs=np.polynomial.polynomial.polyroots(np.polynomial.polynomial.polyder(coef));ts=[0.,1.]+[float(r.real) for r in rs if abs(r.imag)<1e-7 and 0<r.real<1];t=min(ts,key=lambda t:np.polynomial.polynomial.polyval(t,coef));W=.5+t*(A-.5);value=obj(W);V=W[0][:,None]*W;B=1-W;Z=B[0][:,None]*B;independent=float((np.trace(V@V@V)+np.trace(Z@Z@Z))/n**3);assert abs(value-independent)<1e-12
 results.append(dict(source=str(p),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),t=t,objective=value,independent_trace=independent,binary_objective=d['best_rooted_count']/d['denominator'],coefficients=coef.tolist(),sample_points=xs.tolist(),sample_values=ys.tolist(),seconds=time.time()-st));print(name,t,value,flush=True)
(root/'polish.json').write_text(json.dumps(dict(scope='one-dimensional scalar interpolation W=.5+t*(A-.5), t in [0,1]; not full continuous polish',source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),results=results),indent=2))
