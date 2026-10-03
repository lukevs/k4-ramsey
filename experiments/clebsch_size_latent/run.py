import os
for k in ['VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']: os.environ[k]='1'
import sys,time,json,itertools,hashlib,signal
from pathlib import Path
import numpy as np
from scipy.optimize import minimize
sys.dont_write_bytecode=True
sys.path.insert(0,'experiments/round4_E5')
from phi import Phi
START=time.time(); signal.signal(signal.SIGALRM,lambda *a: (_ for _ in ()).throw(TimeoutError())); signal.alarm(175)
OUT=Path('reports/clebsch-size-latent-001')
edges=list(itertools.combinations(range(4),2))
def literal(P,w):
    return sum(np.prod(w[list(t)])*(np.prod([P[t[i],t[j]] for i,j in edges])+np.prod([1-P[t[i],t[j]] for i,j in edges])) for t in itertools.product(range(len(w)),repeat=4))
def coeff(P,A):
    ph=Phi(P); c3=ph.T3(A); c4=ph.T4(A); c5=c6=0.; n=len(P)
    for u in range(n):
        for v in np.flatnonzero(A[u]):
            ids=np.flatnonzero(A[u]*A[v]); z=A[u,ids]*A[v,ids]
            c5+=A[u,v]*(z @ (2*P[np.ix_(ids,ids)]-1) @ z)
            c6+=A[u,v]*(z @ A[np.ix_(ids,ids)] @ z)
    return np.array([c3,c4,6*c5/n**4,2*c6/n**4])
def moments(K,w):
    M=np.sqrt(w)[:,None]*K*np.sqrt(w)[None,:]; M2=M@M
    h3=np.sum(M2*M); h4=np.sum(M2*M2)
    h5=h6=0.
    for u in range(len(w)):
        for v in range(len(w)):
            z=w*K[u]*K[v]
            h5+=w[u]*w[v]*K[u,v]*z.sum()**2
            h6+=w[u]*w[v]*K[u,v]*(z@K@z)
    return np.array([h3,h4,h5,h6])
rng=np.random.default_rng(2917)
# Tiny diagonal-zero amplitude fits Phi, but probability diagonals nonzero.
P=rng.uniform(.2,.8,(3,3)); P=(P+P.T)/2
A=rng.uniform(-.08,.08,(3,3)); A=(A+A.T)/2; np.fill_diagonal(A,0)
w=np.array([.2,.3,.5]); R=rng.uniform(-.5,.5,(3,3)); R=(R+R.T)/2; H=np.eye(3)-np.ones((3,1))*w; K=H@R@H.T
c=coeff(P,A); W=np.kron(P,np.ones((3,3)))+np.kron(A,K)
actual=literal(W,np.tile(w/3,3))-literal(P,np.ones(3)/3); predicted=c@moments(K,w)
assert abs(actual-predicted)<2e-15,(actual,predicted)
# Split the final latent label into two identical copies with arbitrary masses.
idx=[0,1,2,2]; wd=np.array([.2,.3,.17,.33]); Kd=K[np.ix_(idx,idx)]
dup=literal(np.kron(P,np.ones((4,4)))+np.kron(A,Kd),np.tile(wd/3,3))
original=literal(W,np.tile(w/3,3)); assert abs(dup-original)<2e-15
validation=dict(tiny_direct_delta=actual,polynomial_delta=predicted,error=actual-predicted,duplicate_error=dup-original)
print('VALIDATION',validation,flush=True)
P=np.load('experiments/round4_E5/P.npy'); A=np.load('reports/round4-E5-depth1-001/a_int.npy')/65536
assert np.max(np.abs(A)-np.minimum(P,1-P))<1e-15
c=coeff(P,A); baseline_delta=c[0]+c[1]; parent=.03013890356539909
exact_delta=-775895085614712958567643070937/93461343453626897313548933925961728000
assert abs(baseline_delta-exact_delta)<1e-20
print('COEFFICIENTS',c,'elapsed',time.time()-START,flush=True)
json.dump(dict(validation=validation,coefficients=c.tolist(),binary_delta=baseline_delta,parent=parent),open(OUT/'coefficients.json','w'),indent=2)
# K = H R H^T gives weighted row centering. Enforce actual entrywise bounds.
results=[]; best=(baseline_delta,np.array([[1.,-1.],[-1.,1.]]),np.array([.5,.5]))
for k in [3,4]:
    iu=np.triu_indices(k)
    def decode(x):
        w=np.r_[x[-(k-1):],1-x[-(k-1):].sum()]
        R=np.zeros((k,k)); R[iu]=x[:len(iu[0])]; R=R+R.T-np.diag(R.diagonal()); H=np.eye(k)-np.ones((k,1))*w
        return H@R@H.T,w
    def fun(x):
        K,w=decode(x)
        if np.min(w)<0:return 1e10
        return float(c@moments(K,w)*1e9)
    def con(x):
        K,w=decode(x); return np.r_[1-K.ravel(),1+K.ravel(),w[-1]-.02]
    for seed in range(12):
        if time.time()-START>145:break
        w=rng.dirichlet(np.ones(k)*5)
        if seed==0:
            w=np.r_[.5,np.full(k-1,.5/(k-1))]; s=np.r_[1.,-np.ones(k-1)]; R=np.outer(s,s)
        else:
            R=rng.uniform(-.8,.8,(k,k));R=(R+R.T)/2
        x=np.r_[R[iu],w[:-1]]
        res=minimize(fun,x,method='SLSQP',bounds=[(-4,4)]*len(iu[0])+[(.02,.96)]*(k-1),constraints=[dict(type='ineq',fun=con)],options=dict(maxiter=180,ftol=1e-11))
        K,w=decode(res.x); feasible=np.min(con(res.x))>=-1e-8
        value=float(c@moments(K,w))
        results.append(dict(k=k,seed=seed,delta=value,success=bool(res.success),feasible=bool(feasible),nit=res.nit,weights=w.tolist(),kernel=K.tolist()))
        if feasible and value<best[0]-1e-16: best=(value,K,w)
        print('FIT',k,seed,value,'gain',value-baseline_delta,'ok',feasible,flush=True)
report=dict(hypothesis='H-A1',validation=validation,coefficients=c.tolist(),parent=parent,binary_baseline=parent+baseline_delta,binary_exact_delta=exact_delta,best_density=parent+best[0],gain_vs_binary=best[0]-baseline_delta,gap_to_incumbent=parent+best[0]-.030138887566497220,results=results,elapsed=time.time()-START,threads={k:os.environ[k] for k in ['VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},termination='bounded_multistart_completed')
if best[0]<baseline_delta-1e-16:
    np.savez(OUT/'candidate.npz',P=P,A=A,kernel=best[1],latent_weights=best[2])
    report['candidate_rule']='W[(u,a),(v,b)]=P[u,v]+A[u,v]*kernel[a,b]; weights=latent_weights[a]/960; copy totals unchanged'
report['sha256']={p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['experiments/clebsch_size_latent/run.py','experiments/round4_E5/P.npy','reports/round4-E5-depth1-001/a_int.npy']}
json.dump(report,open(OUT/'report.json','w'),indent=2)
print('FINAL', {k:v for k,v in report.items() if k not in ['results','sha256']},flush=True)
