import numpy as np, sys
sys.path.insert(0,'research/experiments/round4_E5')
from phi import Phi, k4_density, split
rng=np.random.default_rng(1)
for trial in range(3):
    n=9
    W=rng.random((n,n)); W=(W+W.T)/2
    mask=rng.random((n,n))<0.3; mask=np.triu(mask,1); mask=mask|mask.T
    W[mask]=np.round(W[mask]) ; np.fill_diagonal(W,0)
    ph=Phi(W)
    S=rng.choice([-1,1],(n,n)); S=np.triu(S,1); S=S+S.T
    A=ph.m*S*rng.random((n,n)); A=np.triu(A,1); A=A+A.T
    for eps in (0.3,-0.7,1.0):
        pred=k4_density(W)+ph.delta(eps*A)
        direct=k4_density(split(W,eps*A))
        print(trial,eps,pred,direct,pred-direct)
    # gradient check
    d,G,_,_=ph.delta(A,True); E=np.zeros_like(A); i,j=np.argwhere(ph.frac)[0]; E[i,j]=E[j,i]=1e-6
    print('grad',G[i,j],(ph.delta(A+E)-ph.delta(A-E))/2e-6)
