"""HVT1: unrestricted single absent vertex attachment oracle on B192."""
import signal, time, os
signal.signal(signal.SIGALRM, signal.SIG_DFL)
signal.alarm(175)
START=time.time()
import json, hashlib, sys, platform
from pathlib import Path
from fractions import Fraction
import numpy as np
import scipy
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from experiments.clebsch_bowl.audit_weighted import density
OUT=ROOT/'reports/assumption-vertex_types-001'
SOURCE=ROOT/'reports/clebsch-size-coarse-002/weighted-k12.json'
D=json.loads(SOURCE.read_text()); W=np.array(D['red_probability_numerators'],float)/D['edge_probability_denominator']
m=np.array([float(Fraction(v)) for v in D['block_weights']]); m/=sum(m)

def dump(name,data):
    p=OUT/name; tmp=p.with_suffix('.tmp'); tmp.write_text(json.dumps(data,indent=2)+'\n'); tmp.replace(p)

def rooted(q,W=W,m=m):
    f=0.; g=np.zeros(len(q))
    for A,z,sign in [(W,q,1),(1-W,1-q,-1)]:
        v=m*z; B=(A*v)@A
        h=np.sum(B*A*v[None,:],axis=1)
        f+=np.dot(v,h); g+=sign*3*m*h
    return float(f),g

def coefficients(q,d,F,W=W,m=m):
    r=rooted(q,W,m)[0]
    v=m*q*q; u=m*(1-q)**2
    r2=d*np.dot(v,W@v)+(1-d)*np.dot(u,(1-W)@u)
    r3=d**3*np.dot(m,q**3)+(1-d)**3*np.dot(m,(1-q)**3)
    return np.array([F,r,r2,r3,d**6+(1-d)**6])

def polynomial(e,c):
    return float(sum(k*e**i*(1-e)**(4-i)*c[i] for i,k in enumerate([1,4,6,4,1])))

def materialize(q,d,e):
    V=np.empty((len(W)+1,len(W)+1)); V[:-1,:-1]=W; V[-1,:-1]=V[:-1,-1]=q; V[-1,-1]=d
    return V,np.r_[m*(1-e),e]

def main():
    dump('active.json',{'pid':os.getpid(),'start_unix':START,'hard_deadline_unix':START+175,'stage':'baseline and HVT1','command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/assumption_vertex_types/insertion.py'})
    F=density(W,m); print('BASE',F,flush=True)
    rng=np.random.default_rng(930192)
    q=rng.uniform(size=len(m)); _,g=rooted(q); eps=1e-5
    err=max(abs((rooted(q+np.eye(len(m))[i]*eps)[0]-rooted(q-np.eye(len(m))[i]*eps)[0])/(2*eps)-g[i]) for i in [0,1,15,48,99,191])
    existing=np.array([rooted(row)[0] for row in W])
    # Exact graphon duplicate/split control, in floating arithmetic.
    ids=list(range(len(m)))+[0]; v=W[np.ix_(ids,ids)]; mw=np.r_[m,m[0]*.37]; mw[0]*=.63
    split=density(v,mw)
    polychecks=[]
    for e,d in [(.0001,.31),(.13,.77)]:
        v,mw=materialize(q,d,e); polychecks.append(abs(polynomial(e,coefficients(q,d,F))-density(v,mw)))
    checks={'base_F':F,'existing_root_min':float(existing.min()),'existing_root_max':float(existing.max()),'existing_weighted_mean':float(m@existing),'gradient_error':err,'split_error':abs(F-split),'finite_polynomial_errors':polychecks}
    assert max(err,abs(F-split),*polychecks)<1e-8,checks
    dump('checks.json',checks); print('CHECKS',json.dumps(checks),flush=True)
    starts=[('existing0',W[0].copy()),('half',np.full(len(m),.5))]
    for i in range(3): starts.append((f'uniform{i}',rng.uniform(size=len(m))))
    for i in range(3): starts.append((f'binary{i}',rng.integers(0,2,len(m)).astype(float)))
    for i in range(4): starts.append((f'perturbed_row{i}',np.clip(W[i*17]+rng.normal(0,.25,len(m)),0,1)))
    rows=[]
    for name,q0 in starts:
        if time.time()-START>135: break
        t=time.time(); r=minimize(lambda q:(rooted(q)[0]*1e3,rooted(q)[1]*1e3),q0,jac=True,bounds=[(0,1)]*len(m),method='L-BFGS-B',options={'maxiter':160,'ftol':1e-14,'gtol':1e-8})
        q=r.x; R=rooted(q)[0]; distances=np.sqrt(np.sum(m*(W-q)**2,axis=1))
        row={'name':name,'seed':930192,'R':R,'R_minus_F':R-F,'insertion_slope':4*(R-F),'q':q.tolist(),'start_q':q0.tolist(),'nearest_old_row':int(distances.argmin()),'nearest_old_row_weighted_rms':float(distances.min()),'success':bool(r.success),'message':str(r.message),'nit':r.nit,'nfev':r.nfev,'seconds':time.time()-t}
        rows.append(row); dump('rooted-runs.json',rows); print(json.dumps({k:v for k,v in row.items() if k not in ['q','start_q']}),flush=True)
    best=min(rows,key=lambda r:r['R']); q=np.array(best['q']); finite=[]
    for e0 in [.001,.02,.15]:
        r=minimize(lambda x: polynomial(x[0],coefficients(q,x[1],F)),[e0,.5],bounds=[(1e-8,.3),(0,1)],method='Nelder-Mead',options={'maxiter':300,'xatol':1e-11,'fatol':1e-16})
        e,d=r.x; c=coefficients(q,d,F); val=polynomial(e,c)
        finite.append({'e':e,'d':d,'F':val,'delta':val-F,'coefficients':c.tolist(),'success':bool(r.success)})
    dump('finite-single.json',{'profile':best['name'],'runs':finite,'tiny_mass':{'e':1e-6,'d':.5,'delta':polynomial(1e-6,coefficients(q,.5,F))-F}})
    dump('receipt-hvt1.json',{'hypothesis':'HVT1','pid':os.getpid(),'start_unix':START,'end_unix':time.time(),'seconds':time.time()-START,'termination':'completed','input':str(SOURCE.relative_to(ROOT)),'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256((ROOT/'experiments/clebsch_bowl/audit_weighted.py').read_bytes()).hexdigest(),'python':sys.version,'numpy':np.__version__,'scipy':scipy.__version__,'platform':platform.platform(),'threads':{k:os.environ.get(k) for k in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']},'scope':'all 192 old classes, normalized rational-input weights, unrestricted new attachment vector; all repeats and diagonals; numerical, no global or exact certification'})
    dump('active.json',{'pid':None,'stage':'HVT1 completed','end_unix':time.time()})
    print('DONE',time.time()-START,flush=True)
if __name__=='__main__':main()
