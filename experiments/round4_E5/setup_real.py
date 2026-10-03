import numpy as np, sys, time
sys.path.insert(0,'experiments/round4_E5')
from phi import Phi, k4_density, split
from load import load
N,Q,w=load(); P=N/Q
# small real case: principal 48-class subgraphon
idx=np.arange(48); Ws=P[np.ix_(idx,idx)]; ps=Phi(Ws)
rng=np.random.default_rng(0); S=rng.choice([-1,1],Ws.shape); S=np.triu(S,1); S=S+S.T
A=ps.m*S
print('sub frac',ps.frac.sum(),'tri',len(ps.tri))
for eps in (0.5,-1.0): print('subcheck',ps.delta(eps*A), k4_density(split(Ws,eps*A))-k4_density(Ws))
t=time.time(); ph=Phi(P); print('setup',time.time()-t,'tri',len(ph.tri))
t=time.time(); c=P*(1-P)*ph.frac
print('A=c: T3',ph.T3(c),'T4',ph.T4(c),time.time()-t)
t=time.time(); d,G,a,b=ph.delta(c,True); print('grad time',time.time()-t)
np.save('experiments/round4_E5/P.npy',P)
