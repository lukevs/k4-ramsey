import numpy as np, sys, time, json
sys.path.insert(0,'experiments/round4_E5')
from phi import Phi
P=np.load('experiments/round4_E5/P.npy'); ph=Phi(P); m=ph.m; iu=np.triu(ph.frac,1)
out=sys.argv[1]; iters=int(sys.argv[2])
def sym(X): X=np.triu(X,1); return X+X.T
def quartic_coeffs(A,D):
    ts=np.array([-2,-1,0,1,2.]); vals=[ph.delta(A+t*D) for t in ts]
    return np.polyfit(ts,vals,4)
rng=np.random.default_rng(7); c=P*(1-P)*ph.frac
starts={'c':c,'m_rand':sym(m*rng.choice([-1,1],m.shape)),'c_rand':sym(c*rng.choice([-1,1],m.shape))}
_,G3=ph.T3(c,True); starts['gradT3sign']=-m*np.sign(G3)*ph.frac
res={}
for name,A0 in starts.items():
    # best scale first
    co=quartic_coeffs(np.zeros_like(A0),A0)  # delta(t A0)
    ts=np.linspace(-1,1,2001); v=np.polyval(co,ts); t=ts[v.argmin()]
    A=np.clip(t*A0,-m,m); f=ph.delta(A); hist=[f]; t0=time.time()
    for it in range(iters):
        f,G,a,b=ph.delta(A,True)
        D=-G*m*m
        D=np.where((A>=m-1e-15)&(D>0),0,D); D=np.where((A<=-m+1e-15)&(D<0),0,D)
        co=quartic_coeffs(A,D)
        # feasible range for t
        with np.errstate(divide='ignore',invalid='ignore'):
            up=np.where(D>0,(m-A)/D,np.where(D<0,(-m-A)/D,np.inf))
        tmax=np.min(up[ph.frac]) if np.isfinite(up[ph.frac]).any() else 1.0
        tbig=max(tmax,1e-12)*50
        ts=np.linspace(0,tbig,4001); vv=np.polyval(co,ts); tb=ts[vv.argmin()]
        Anew=np.clip(A+tb*D,-m,m); fn=ph.delta(Anew)
        if fn>f:
            ts=np.linspace(0,tmax,2001); tb=ts[np.polyval(co,ts).argmin()]; Anew=np.clip(A+tb*D,-m,m); fn=ph.delta(Anew)
        if fn>=f: break
        A=Anew; hist.append(fn)
        if it%20==0: print(name,it,fn,a,b,'sat',np.mean(np.abs(A[iu])>=m[iu]-1e-12),time.time()-t0,flush=True)
    f,G,a,b=ph.delta(A,True)
    res[name]=dict(delta=f,T3=a,T4=b,sat=float(np.mean(np.abs(A[iu])>=m[iu]-1e-12)),iters=len(hist)-1)
    np.save(out+f'/A_{name}.npy',A); print('FINAL',name,res[name],flush=True)
json.dump(res,open(out+'/opt.json','w'),indent=1)
