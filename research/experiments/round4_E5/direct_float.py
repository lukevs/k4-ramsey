"""Independent direct float recount t(K4,W)+t(K4,1-W) of a rational-step-graphon-v1 (uniform weights).
Optional arg 'pairsym': use global sign-swap automorphism (classes 2u,2u+1 equivalent) to halve work."""
import numpy as np, json, sys, time
d=json.load(open(sys.argv[1])); Q=d['edge_probability_denominator']
W=np.array(d['red_probability_numerators'],dtype=np.float64)/Q; n=W.shape[0]
rows=range(0,n,2) if 'pairsym' in sys.argv else range(n); mult=2 if 'pairsym' in sys.argv else 1
tot=0.0; t0=time.time()
for X in (W,1-W):
    for a in rows:
        V=X[a][None,:]*X
        tot+=mult*(X[a]*((V@X)*V).sum(1)).sum()
        if a==rows[0]*0+ (10 if mult==1 else 20): print('eta',(time.time()-t0)/(11 if mult==1 else 11)*len(rows)*2,flush=True)
print('F',repr(tot/n**4),'time',time.time()-t0)
