"""HVT2: finite cooperative two-profile insertion and coherent replacement split."""
import os, time, signal
signal.signal(signal.SIGALRM,signal.SIG_DFL); signal.alarm(175); START=time.time()
import sys, json, itertools, hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
ROOT=Path(__file__).resolve().parents[3]; sys.path.insert(0,str(ROOT))
from research.experiments.assumption_vertex_types.insertion import W,m,dump,rooted,density,OUT
signal.alarm(max(1,int(175-(time.time()-START))))
PAIRS=list(itertools.combinations(range(4),2))
class PairModel:
    def __init__(self,W,m):
        self.W=W; self.m=m; self.n=len(m); self.F=density(W,m)
    def evaluate(self,x,e):
        Q=x[:2*self.n].reshape(2,self.n); B=np.array([[x[-3],x[-2]],[x[-2],x[-1]]])
        c=np.zeros(5); c[0]=self.F; G=np.zeros((5,2,self.n)); H=np.zeros((5,2,2))
        # c[k] averages over uniform new-class labels, conditional on k new roots.
        for A,U,V,sgn in [(self.W,Q,B,1),(1-self.W,1-Q,1-B,-1)]:
            for a in range(2):
                z=self.m*U[a]; T=(A*z)@A; h=np.sum(T*A*z[None,:],axis=1)
                c[1]+=.5*np.dot(z,h); G[1,a]+=sgn*1.5*self.m*h
            for a,b in itertools.product(range(2),repeat=2):
                z=self.m*U[a]*U[b]; Az=A@z; val=np.dot(z,Az)
                c[2]+=.25*V[a,b]*val; H[2,a,b]+=sgn*.25*val
                G[2,a]+=sgn*.5*V[a,b]*self.m*U[b]*Az
                G[2,b]+=sgn*.5*V[a,b]*self.m*U[a]*Az
            for a,b,d in itertools.product(range(2),repeat=3):
                v=np.dot(self.m,U[a]*U[b]*U[d]); z=V[a,b]*V[a,d]*V[b,d]
                c[3]+=z*v/8
                for r,s,t in [(a,b,d),(b,a,d),(d,a,b)]: G[3,r]+=sgn*z*self.m*U[s]*U[t]/8
                H[3,a,b]+=sgn*V[a,d]*V[b,d]*v/8
                H[3,a,d]+=sgn*V[a,b]*V[b,d]*v/8
                H[3,b,d]+=sgn*V[a,b]*V[a,d]*v/8
            for ids in itertools.product(range(2),repeat=4):
                ed=np.array([V[ids[i],ids[j]] for i,j in PAIRS]); c[4]+=np.prod(ed)/16
                for p,(i,j) in enumerate(PAIRS): H[4,ids[i],ids[j]]+=sgn*np.prod(np.delete(ed,p))/16
        fac=np.array([(1-e)**4,4*e*(1-e)**3,6*e*e*(1-e)**2,4*e**3*(1-e),e**4])
        dfac=np.array([-4*(1-e)**3,4*(1-e)**3-12*e*(1-e)**2,12*e*(1-e)**2-12*e*e*(1-e),12*e*e*(1-e)-4*e**3,4*e**3])
        gq=np.einsum('i,ijk->jk',fac,G); gb=np.einsum('i,ijk->jk',fac,H)
        return float(fac@c),np.r_[gq.ravel(),gb[0,0],gb[0,1]+gb[1,0],gb[1,1]],float(dfac@c),c
    def materialize(self,x,e):
        q=x[:2*self.n].reshape(2,self.n); v=np.zeros((self.n+2,self.n+2)); v[:self.n,:self.n]=self.W
        v[-2:,:self.n]=q; v[:self.n,-2:]=q.T; v[-2:,-2:]=[[x[-3],x[-2]],[x[-2],x[-1]]]
        return v,np.r_[(1-e)*self.m,e/2,e/2]

def main():
    dump('active.json',{'pid':os.getpid(),'start_unix':START,'hard_deadline_unix':START+175,'stage':'HVT2 pair','command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python research/experiments/assumption_vertex_types/pair.py'})
    rng=np.random.default_rng(930193); model=PairModel(W,m)
    # Independent tiny full-root checks with nonzero probability diagonals.
    T=rng.uniform(size=(4,4)); T=(T+T.T)/2; tm=rng.dirichlet(np.ones(4)); tiny=PairModel(T,tm)
    x=rng.uniform(.1,.9,11); e=.173; f,g,ge,c=tiny.evaluate(x,e); h=1e-5
    ge_err=abs(ge-(tiny.evaluate(x,e+h)[0]-tiny.evaluate(x,e-h)[0])/(2*h))
    gerr=max(abs(g[i]-(tiny.evaluate(x+np.eye(11)[i]*h,e)[0]-tiny.evaluate(x-np.eye(11)[i]*h,e)[0])/(2*h)) for i in range(11))
    V,mw=tiny.materialize(x,e); ferr=abs(f-density(V,mw)); assert max(ge_err,gerr,ferr)<1e-8
    dump('pair-checks.json',{'fullroot_error':ferr,'q_and_B_gradient_error':gerr,'mass_gradient_error':ge_err})
    rows=[]; runid=0
    rootrows=json.loads((OUT/'rooted-runs.json').read_text()); novel=np.array(next(r['q'] for r in rootrows if r['name']=='uniform1'))
    for mode in ['insert','replace-split']:
        if mode=='insert': mod=model; masses=[.01,.05,.15]; starts=['novel-complement','different-rows','random']
        else:
            old=np.arange(1,len(m)); mod=PairModel(W[np.ix_(old,old)],m[old]/sum(m[old])); masses=[m[0]]; starts=['opposite-perturb','independent-perturb','random']
        for e0 in masses:
            for name in starts:
                if time.time()-START>130: break
                if name=='novel-complement': Q=np.array([novel,1-novel])
                elif name=='different-rows': Q=W[[0,37]].copy()
                elif name=='opposite-perturb':
                    d=rng.uniform(-.7,.7,mod.n); Q=np.clip([W[0,1:]+d,W[0,1:]-d],0,1)
                elif name=='independent-perturb': Q=np.clip(W[0,1:]+rng.normal(0,.35,(2,mod.n)),0,1)
                else: Q=rng.uniform(size=(2,mod.n))
                x0=np.r_[Q.ravel(),rng.uniform(size=3)]; t=time.time()
                def fg(x):
                    f,g,_,_=mod.evaluate(x,e0); return f*1e4,g*1e4
                r=minimize(fg,x0,jac=True,bounds=[(0,1)]*len(x0),method='L-BFGS-B',options={'maxiter':250,'ftol':1e-14,'gtol':1e-8})
                x=r.x; fixed=mod.evaluate(x,e0)[0]
                if mode=='insert':
                    def joint(z):
                        f,g,ge,c=mod.evaluate(z[:-1],z[-1]); return f*1e4,np.r_[g,ge]*1e4
                    rr=minimize(joint,np.r_[x,e0],jac=True,bounds=[(0,1)]*len(x)+[(1e-8,.3)],method='L-BFGS-B',options={'maxiter':200,'ftol':1e-14,'gtol':1e-8})
                    x=rr.x[:-1]; e=rr.x[-1]
                else: rr=r; e=e0
                F=mod.evaluate(x,e)[0]; V,mw=mod.materialize(x,e)
                fn=f'pair-witness-{runid:02d}.json'; dump(fn,{'W':V.tolist(),'m':mw.tolist(),'F_search':F,'mode':mode,'e':e})
                Q=x[:2*mod.n].reshape(2,mod.n); distances=np.sqrt(np.sum(mod.m*(mod.W[None,:,:]-Q[:,None,:])**2,axis=2))
                row={'id':runid,'mode':mode,'start':name,'seed':930193,'fixed_e':float(e0),'fixed_mass_F':fixed,'e':float(e),'F':F,'delta_vs_B192':F-model.F,'pair_profile_rms':float(np.sqrt(np.dot(mod.m,(Q[0]-Q[1])**2))),'nearest_old_profile_rms':distances.min(axis=1).tolist(),'nit_fixed':r.nit,'nit_final':rr.nit,'success_fixed':bool(r.success),'success_final':bool(rr.success),'message_final':str(rr.message),'seconds':time.time()-t,'witness':fn,'initial_x':x0.tolist()}
                rows.append(row); dump('pair-runs.json',rows); print(json.dumps({k:v for k,v in row.items() if k!='initial_x'}),flush=True); runid+=1
    dump('receipt-hvt2.json',{'hypothesis':'HVT2','pid':os.getpid(),'start_unix':START,'end_unix':time.time(),'seconds':time.time()-START,'termination':'completed','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seed':930193,'scope':'joint 2x192 insertion attachments, all three new-new probabilities; finite e then joint e; replacement split deletes class0 and uses two free profiles with its total mass; original old kernel fixed'})
    dump('active.json',{'pid':None,'stage':'HVT2 completed','end_unix':time.time()}); print('DONE',time.time()-START,flush=True)
if __name__=='__main__':main()
