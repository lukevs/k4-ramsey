import os
for key in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS','VECLIB_MAXIMUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[key]='1'
import numpy as np
from scipy.optimize import minimize
import scipy, json, time, signal, sys, hashlib
from pathlib import Path
signal.signal(signal.SIGALRM,signal.SIG_DFL)
signal.alarm(max(1,min(170,int(1790745600-time.time())))) # deadline 2026-09-30 05:20 UTC
OUT=Path('reports/unrestricted-bowl-challenge-001')

def fg(W,m):
    n=len(m); out=0.; gm=np.zeros(n); gW=np.zeros((n,n))
    for P,sgn in ((W,1),(1-W,-1)):
        B=P[:,:,None]*P[:,None,:] # i,j,k -> Pij Pik
        # missing edge (i,j), summing k,l with all other five edges
        C=np.einsum('ik,jk,il,jl,kl,k,l->ij',P,P,P,P,P,m,m,optimize=True)
        gW+=sgn*6*m[:,None]*m[None,:]*C
        cond=np.einsum('ij,ij,j->i',P,C,m,optimize=True)
        gm+=4*cond
        out+=np.dot(m,cond)
    return out,gW,gm

def optimize(W,m,variable,maxiter=180):
    n=len(m); ix=np.triu_indices(n); sz=len(ix[0]); x=np.r_[W[ix],m] if variable else W[ix]
    def unpack(x):
        P=np.zeros((n,n)); P[ix]=x[:sz]; P[(ix[1],ix[0])]=x[:sz]
        return P,x[sz:] if variable else m
    def fun(x):
        P,w=unpack(x); f,g,h=fg(P,w); gg=g[ix]*np.where(ix[0]==ix[1],1,2)
        return 1000*f,1000*np.r_[gg,h] if variable else 1000*gg
    cons=[{'type':'eq','fun':lambda x:x[sz:].sum()-1,'jac':lambda x:np.r_[np.zeros(sz),np.ones(n)]}] if variable else []
    st=time.monotonic(); r=minimize(fun,x,jac=True,bounds=[(0,1)]*len(x),constraints=cons,method='SLSQP',options={'maxiter':maxiter,'ftol':1e-10})
    P,w=unpack(r.x); return P,w,{'objective':float(r.fun/1000),'iterations':r.nit,'success':bool(r.success),'message':r.message,'seconds':time.monotonic()-st,'nfev':r.nfev}

def save(name,P,w,meta):
    f,g,h=fg(P,w); n=len(w)
    rowdist=[float(np.sqrt(np.dot(w,(P[i]-P[j])**2))) for i in range(n) for j in range(i)]
    meta.update(W=P.tolist(),m=w.tolist(),objective=f,effective_mass_classes=float(1/np.dot(w,w)),tiny_masses=int(sum(w<1e-6)),fractional_entries=int(sum((P[np.triu_indices(n)]>1e-6)&(P[np.triu_indices(n)]<1-1e-6))),nearest_rows=min(rowdist),nearly_identical_row_pairs=sum(x<1e-5 for x in rowdist))
    with (OUT/(name+'.json')).open('x') as f: json.dump(meta,f,indent=2)
    print(name,meta['objective'],meta['seconds'],flush=True)

if __name__=='__main__':
    n=int(sys.argv[1]); seed=int(sys.argv[2]); rng=np.random.default_rng(seed)
    A=rng.uniform(.05,.95,(n,n)) if seed%2==0 else rng.beta(.25,.25,(n,n))
    W=np.triu(A)+np.triu(A,1).T; m=np.ones(n)/n
    for variable in (False,True):
        P,w,meta=optimize(W,m,variable)
        meta.update(n=n,seed=seed,variable=variable,start_kind='uniform' if seed%2==0 else 'heterogeneous_beta',initial_W=W.tolist(),initial_m=m.tolist(),pid=os.getpid(),numpy=np.__version__,scipy=scipy.__version__)
        save(f'n{n}-s{seed}-'+('variable' if variable else 'equal'),P,w,meta)
