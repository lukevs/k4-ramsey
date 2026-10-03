import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS'): os.environ[k]='1'
import signal,time,json,sys,itertools
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(170)
from pathlib import Path
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from local_patch import LocalPatch,directions,direct
sys.path.insert(0,'research/experiments/round4_E5')
from load import load
from phi import split
OUT=Path('reports/family-mechanism-followup-001');OUT.mkdir(exist_ok=True)
start=time.monotonic();dp,da=directions()

if sys.argv[1]=='tiny':
    rng=np.random.default_rng(829);tests=[]
    for n in (3,4):
        P=rng.uniform(.2,.8,(n,n));P=(P+P.T)/2
        A=rng.uniform(-.1,.1,(n,n));A=(A+A.T)/2;np.fill_diagonal(A,0)
        W=split(P,A);w=rng.uniform(.2,1,n);w=w/w.sum();w=np.repeat(w/2,2)
        S=[0,1,2,3];model=LocalPatch(W,w,S);B=model.base+.013*dp-.007*da
        V=W.copy();V[np.ix_(S,S)]=B
        predicted,g=model.evaluate(B,(dp,da));observed=direct(V,w)-direct(W,w)
        fd=[(model.evaluate(B+1e-6*D)[0]-model.evaluate(B-1e-6*D)[0])/2e-6 for D in (dp,da)]
        assert abs(predicted-observed)<2e-14
        assert np.max(abs(g-fd))<1e-10
        tests.append(dict(n=n,delta=predicted,direct_delta=observed,gradient=g.tolist(),gradient_error=float(np.max(abs(g-fd)))))
    (OUT/'tiny.json').write_text(json.dumps(dict(tests=tests,seconds=time.monotonic()-start),indent=2)+'\n')
    print(json.dumps(tests),flush=True)
else:
    N,Q,w=load();a=np.load('reports/round4-E5-depth1-001/a_int.npy');P=N/Q;A=a/Q
    assert np.allclose(w,1/len(w))
    W=split(P,A);weights=np.repeat(w/2,2)
    mask=np.triu((abs(a)==np.minimum(N,Q-N))&(a!=0),1)
    edges=np.argwhere(mask);rng=np.random.default_rng(829);rng.shuffle(edges)
    rows=[]
    for u,v in edges[:40]:
        if time.monotonic()-start>140: break
        p,b=P[u,v],A[u,v];S=[2*u,2*u+1,2*v,2*v+1]
        model=LocalPatch(W,weights,S);base=model.base
        def ev(x):return model.evaluate(base+x[0]*dp+x[1]*da,(dp,da))
        def fun(x):
            f,g=ev(x);return f*1e12,g*1e12
        controls={}
        for name,z,limits in [('parent',0,(abs(b)-p,1-abs(b)-p)),('amplitude',1,(-min(p,1-p)-b,min(p,1-p)-b))]:
            def scalar(t):
                x=np.zeros(2);x[z]=t;return fun(x)[0]
            opt=minimize_scalar(scalar,bounds=limits,method='bounded',options={'xatol':1e-12})
            t=min([0.,*limits,float(opt.x)],key=scalar);x=np.zeros(2);x[z]=t
            controls[name]=dict(x=x.tolist(),delta=ev(x)[0])
        # qplus and qminus directly enforce the exact lifted boxes.
        q0=np.array([p+b,p-b])
        def transformed(q):
            x=np.array([(q.sum()-q0.sum())/2,((q[0]-q[1])-(q0[0]-q0[1]))/2])
            f,g=fun(x);return f,np.array([(g[0]+g[1])/2,(g[0]-g[1])/2])
        opt=minimize(transformed,q0,jac=True,bounds=[(0,1),(0,1)],method='L-BFGS-B',options={'maxiter':80,'ftol':1e-15,'gtol':1e-10})
        q=opt.x;x=np.array([(q.sum()-q0.sum())/2,((q[0]-q[1])-(q0[0]-q0[1]))/2])
        candidates=[x,np.zeros(2),*[np.array(r['x']) for r in controls.values()]];x=min(candidates,key=lambda z:ev(z)[0])
        controls['joint']=dict(x=x.tolist(),delta=ev(x)[0],optimizer_success=bool(opt.success))
        row=dict(edge=[int(u),int(v)],p=float(p),a=float(b),gradient=ev([0,0])[1].tolist(),controls=controls)
        rows.append(row);print(json.dumps(row),flush=True)
    (OUT/'screen.json').write_text(json.dumps(dict(rows=rows,seconds=time.monotonic()-start,scope='Independent single-parent-edge patches of depth1; not combined and not depth2',seed=829),indent=2)+'\n')
