import numpy as np, time, sys; sys.path.insert(0,'.')
from groups import *
rng=np.random.default_rng(2)
for name,(n,mul) in [('F2^6xC3r1',semidirect_f2_c3(6,1)),('F2^6xC3r2',semidirect_f2_c3(6,2)),('F2^8',elementary(8))]:
    G=Group(n,mul,name); G.activate()
    for steps in [100,300]:
        t=time.time(); vals=[]
        for s in range(6):
            tot,b,ev=tabu(G,rng.integers(0,2,G.m).astype(np.uint8),s,steps,max(3,G.m//12)); vals.append(G.value(tot))
        print(name,steps,'%.3fs'%((time.time()-t)/6),'best %.8f med %.8f'%(min(vals),np.median(vals)),flush=True)
