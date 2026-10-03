import numpy as np, sys, time, json
sys.path.insert(0,'experiments/round4_E5')
from phi import Phi
P=np.load('experiments/round4_E5/P.npy'); ph=Phi(P); m=ph.m; iu=np.triu(ph.frac,1); fr=ph.frac
out=sys.argv[1]; iters=int(sys.argv[2]); names=sys.argv[3].split(',')
tlimit=float(sys.argv[4]) if len(sys.argv)>4 else 250
def sym(X): X=np.triu(X,1); return X+X.T
rng=np.random.default_rng(11); c=P*(1-P)*fr
_,G3=ph.T3(c,True)
starts={'gradT3sign':-m*np.sign(G3)*fr,'m_rand':sym(m*rng.choice([-1,1],m.shape)),'c':c,
        'prev':np.load('reports/round4-E5-opt-001/A_gradT3sign.npy') if 'prev' in names else None}
res={}
for name in names:
    A=starts[name].copy(); t0=time.time()
    f=ph.delta(A)
    # optimal scale in [-1,1]
    ts=np.linspace(-1,1,401); vals=[ph.delta(np.clip(t*A,-m,m)) for t in (-1,-.5,0,.5,1)]
    co=np.polyfit([-1,-.5,0,.5,1],vals,4); t=ts[np.polyval(co,ts).argmin()]; A=np.clip(t*A,-m,m); f=ph.delta(A)
    step=0.5
    for it in range(iters):
        if time.time()-t0>tlimit: break
        f,G,a,b=ph.delta(A,True)
        D=-G*m*m
        D[(A>=m-1e-15)&(D>0)]=0; D[(A<=-m+1e-15)&(D<0)]=0
        sc=np.max(np.abs(D[fr])/m[fr]); 
        if sc==0: break
        D/=sc
        best=(f,None)
        for s in (step*2,step,step/2,step/8):
            An=np.clip(A+s*D,-m,m); fn=ph.delta(An)
            if fn<best[0]: best=(fn,An,s)
        if best[1] is None:
            step/=16
            if step<1e-6: break
            continue
        f,A,step=best[0],best[1],best[2]
        if it%10==0: print(name,it,f,a,b,'sat',round(float(np.mean(np.abs(A[iu])>=m[iu]-1e-12)),4),'step',step,round(time.time()-t0),flush=True)
    f,G,a,b=ph.delta(A,True)
    res[name]=dict(delta=f,T3=a,T4=b,sat=float(np.mean(np.abs(A[iu])>=m[iu]-1e-12)),time=time.time()-t0)
    np.save(out+f'/A_{name}.npy',A); print('FINAL',name,res[name],flush=True)
json.dump(res,open(out+'/opt.json','w'),indent=1)
