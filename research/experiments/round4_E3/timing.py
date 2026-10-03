import numpy as np, time, sys; sys.path.insert(0,'.')
from groups import *
rng=np.random.default_rng(1)
for name,(n,mul) in [('F2^8',elementary(8)),('F2^6xC3r1',semidirect_f2_c3(6,1)),('Z4^4',cyclic_product([4,4,4,4])),('F2^7xC3r1',semidirect_f2_c3(7,1))]:
    G=Group(n,mul,name); G.activate(); t=time.time(); vals=[]; evs=0
    for s in range(10):
        tot,b,ev=G.descend(rng.integers(0,2,G.m).astype(np.uint8),s); vals.append(G.value(tot)); evs+=ev
    print(name,n,G.m,'%.3fs/descent'%((time.time()-t)/10),evs//10,'best %.8f med %.8f'%(min(vals),np.median(vals)),flush=True)
