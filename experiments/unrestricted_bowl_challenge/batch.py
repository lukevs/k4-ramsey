from search import *
# Frozen paired initial conditions: random binary, sharp heterogeneous, and random block models.
for n in (6,10,16):
 for seed in range(500,506):
    rng=np.random.default_rng(seed);kind=seed%3
    if kind==0:
        A=rng.binomial(1,.5,(n,n)).astype(float)
    elif kind==1:
        A=rng.beta(.08,.08,(n,n))
    else:
        labels=rng.integers(0,3,n);Q=rng.uniform(0,1,(3,3));Q=np.triu(Q)+np.triu(Q,1).T
        A=np.clip(Q[labels[:,None],labels[None,:]]+rng.normal(0,.15,(n,n)),0,1)
    W=np.triu(A)+np.triu(A,1).T;m=np.ones(n)/n
    for variable in (False,True):
        P,w,meta=optimize(W,m,variable,maxiter=300)
        meta.update(n=n,seed=seed,variable=variable,start_kind=['independent_binary','sharp_beta','random_three_block'][kind],initial_W=W.tolist(),initial_m=m.tolist(),pid=os.getpid())
        save(f'n{n}-s{seed}-'+('variable' if variable else 'equal'),P,w,meta)
