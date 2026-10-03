"""HVT2b: remove equal-new-mass restriction and permit two-type coherent replacement.
Source specialized from pair.py; previous receipts and implementation unchanged.
"""
import signal, time, os
signal.signal(signal.SIGALRM,signal.SIG_DFL); signal.alarm(175); START=time.time()
import sys, json, hashlib, itertools
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT))
from research.experiments.assumption_vertex_types.pair import PairModel, W,m,dump,density,OUT
signal.alarm(max(1,int(175-(time.time()-START))))
# Generate the same exact ordered-new-label contraction with arbitrary label masses.
# It is also saved verbatim as a separate, hash-bound evaluator for review.
src=(Path(__file__).with_name('pair.py')).read_text()
body=src[src.index('class PairModel:'):src.index('\ndef main():')]
body=body.replace('class PairModel:', 'class UnequalModel:').replace('def evaluate(self,x,e):','def evaluate(self,x,e,alpha):\n        rho=np.array([alpha,1-alpha])')
body=body.replace('c[1]+=.5*np.dot(z,h); G[1,a]+=sgn*1.5*self.m*h','c[1]+=rho[a]*np.dot(z,h); G[1,a]+=sgn*3*rho[a]*self.m*h')
body=body.replace('c[2]+=.25*V[a,b]*val; H[2,a,b]+=sgn*.25*val','c[2]+=rho[a]*rho[b]*V[a,b]*val; H[2,a,b]+=sgn*rho[a]*rho[b]*val')
body=body.replace('sgn*.5*V[a,b]', 'sgn*2*rho[a]*rho[b]*V[a,b]')
body=body.replace('c[3]+=z*v/8','c[3]+=z*v*rho[a]*rho[b]*rho[d]')
body=body.replace('*U[t]/8','*U[t]*rho[a]*rho[b]*rho[d]')
body=body.replace('*v/8','*v*rho[a]*rho[b]*rho[d]')
body=body.replace('c[4]+=np.prod(ed)/16','c[4]+=np.prod(ed)*np.prod(rho[list(ids)])')
body=body.replace('np.prod(np.delete(ed,p))/16','np.prod(np.delete(ed,p))*np.prod(rho[list(ids)])')
body=body.replace('def materialize(self,x,e):','def materialize(self,x,e,alpha):').replace('e/2,e/2','e*alpha,e*(1-alpha)')
PAIRS=list(itertools.combinations(range(4),2))
exec(body,globals())

def main():
    (OUT/'unequal-evaluator-snapshot.py').write_text(body)
    dump('active.json',{'pid':os.getpid(),'start_unix':START,'hard_deadline_unix':START+175,'stage':'unequal finite profiles','command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python research/experiments/assumption_vertex_types/unequal_pair.py'})
    rng=np.random.default_rng(930194)
    T=rng.uniform(size=(5,5)); T=(T+T.T)/2; tm=rng.dirichlet(np.ones(5)); mod=UnequalModel(T,tm)
    x=rng.uniform(size=13); e=.23; a=.27; f,g,ge,c=mod.evaluate(x,e,a); h=1e-5
    err=max(abs(g[i]-(mod.evaluate(x+np.eye(13)[i]*h,e,a)[0]-mod.evaluate(x-np.eye(13)[i]*h,e,a)[0])/(2*h)) for i in range(13))
    v,w=mod.materialize(x,e,a); ferr=abs(f-density(v,w)); assert max(err,ferr)<1e-8
    eq=PairModel(T,tm).evaluate(x,e)[0]; eqerr=abs(eq-mod.evaluate(x,e,.5)[0]); assert eqerr<1e-14
    dump('unequal-checks.json',{'fullroot_error':ferr,'gradient_error':err,'equal_control_error':eqerr})
    rows=[]; base=density(W,m)
    # Cases differ by a structural neighborhood, not merely starts.
    for case,removed in [('insert',[]),('one-to-two',[0]),('two-to-two',[0,37])]:
        old=np.array([i for i in range(len(m)) if i not in removed]); mass=sum(m[removed]) if removed else .025
        mod=UnequalModel(W[np.ix_(old,old)],m[old]/sum(m[old])); n=mod.n
        for seedoffset in range(3):
            if time.time()-START>130: break
            if case=='insert': Q=rng.uniform(size=(2,n))
            elif case=='one-to-two': Q=np.clip(W[0,old]+rng.normal(0,.3,(2,n)),0,1)
            else: Q=np.clip(W[np.ix_([0,37],old)]+rng.normal(0,.25,(2,n)),0,1)
            x=np.r_[Q.ravel(),rng.uniform(size=3)]; initial=np.r_[x,.2+.3*seedoffset]; t=time.time()
            def fg(z):
                x=z[:-1]; alpha=z[-1]; f,g,ge,c=mod.evaluate(x,mass,alpha)
                da=(mod.evaluate(x,mass,alpha+1e-5)[0]-mod.evaluate(x,mass,alpha-1e-5)[0])/2e-5
                return f*1e5,np.r_[g,da]*1e5
            r=minimize(fg,initial,jac=True,bounds=[(0,1)]*len(x)+[(1e-5,1-1e-5)],method='L-BFGS-B',options={'maxiter':250,'ftol':1e-14,'gtol':1e-8})
            x=r.x[:-1]; alpha=r.x[-1]; f,g,ge,c=mod.evaluate(x,mass,alpha); v,mw=mod.materialize(x,mass,alpha)
            fn=f'unequal-witness-{len(rows):02d}.json'; dump(fn,{'W':v.tolist(),'m':mw.tolist(),'F_search':f,'mode':case,'e':mass,'alpha':float(alpha)})
            row={'case':case,'removed':removed,'seed':930194,'seedoffset':seedoffset,'e':float(mass),'alpha':float(alpha),'F':f,'delta_vs_B192':f-base,'mass_derivative_at_fixed_profiles':ge,'success':bool(r.success),'message':str(r.message),'nit':r.nit,'seconds':time.time()-t,'witness':fn,'initial_vector':initial.tolist()}
            rows.append(row); dump('unequal-runs.json',rows); print(json.dumps({k:v for k,v in row.items() if k!='initial_vector'}),flush=True)
    dump('receipt-hvt2b.json',{'pid':os.getpid(),'start_unix':START,'end_unix':time.time(),'seconds':time.time()-START,'termination':'completed','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'specialized_evaluator_sha256':hashlib.sha256(body.encode()).hexdigest(),'seed':930194,'scope':'unequal pair masses, fixed total pair mass; local full attachment and new-new probability optimization; old kernel fixed'})
    dump('active.json',{'pid':None,'stage':'HVT2b completed','end_unix':time.time()}); print('DONE',time.time()-START,flush=True)
if __name__=='__main__':main()
