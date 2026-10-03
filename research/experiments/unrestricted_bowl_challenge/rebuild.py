from search import *
# Separate dynamics: L-BFGS-B box probabilities, softmax mass coordinates.
# These starts and rebuilds are exploratory, not part of the initial SLSQP comparison.
def polish(P,w,variable):
 n=len(w);ix=np.triu_indices(n);k=len(ix[0]);x=np.r_[P[ix],np.log(w)] if variable else P[ix]
 def unpack(x):
  W=np.zeros((n,n));W[ix]=x[:k];W[(ix[1],ix[0])]=x[:k]
  z=x[k:]-max(x[k:]) if variable else None;m=np.exp(z)/sum(np.exp(z)) if variable else w
  return W,m
 def fun(x):
  W,m=unpack(x);f,g,h=fg(W,m);G=g[ix]*np.where(ix[0]==ix[1],1,2)
  return f,np.r_[G,m*(h-np.dot(m,h))] if variable else G
 st=time.monotonic();r=minimize(fun,x,jac=True,method='L-BFGS-B',bounds=[(0,1)]*k+([(-15,15)]*n if variable else []),options={'maxiter':500,'ftol':1e-15,'gtol':1e-9,'maxls':40})
 W,m=unpack(r.x);return W,m,{'seconds':time.monotonic()-st,'iterations':r.nit,'success':bool(r.success),'message':r.message,'nfev':r.nfev}
for n in (6,10,16):
 for seed in (700,701,702,703):
  rng=np.random.default_rng(seed);A=rng.binomial(1,.5,(n,n)).astype(float);W=np.triu(A)+np.triu(A,1).T;m=np.ones(n)/n
  for variable in (False,True):
   P,w,meta=polish(W,m,variable);name=f'lb-n{n}-s{seed}-'+('variable' if variable else 'equal')
   meta.update(n=n,seed=seed,variable=variable,start_kind='independent_binary_lbfgs',initial_W=W.tolist(),initial_m=m.tolist(),pid=os.getpid());save(name,P,w,meta)
   # Coherent rank-two rebuild: replace interactions incident to one random pair,
   # copying a donor profile with opposite perturbations; masses unchanged.
   R=P.copy();a,b,donor=rng.choice(n,3,replace=False);v=rng.choice([-1.,1.],n)*.45
   for i in range(n):
    if i not in (a,b): R[a,i]=R[i,a]=np.clip(P[donor,i]+v[i],0,1);R[b,i]=R[i,b]=np.clip(P[donor,i]-v[i],0,1)
   R[a,a]=0;R[b,b]=1;R[a,b]=R[b,a]=rng.uniform()
   U,z,mm=polish(R,w,variable);mm.update(n=n,seed=seed,variable=variable,start_kind='coherent_pair_rebuild',parent=name,parent_objective=fg(P,w)[0],pair=[int(a),int(b)],donor=int(donor),initial_W=R.tolist(),initial_m=w.tolist(),pid=os.getpid());save(name+'-rebuild',U,z,mm)
