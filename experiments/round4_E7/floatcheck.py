# float sanity check of a rational-step-graphon-v1 candidate using translation by row 0 (valid for Cayley kernels; also checks row-shift structure)
import sys, json, numpy as np
d=json.load(open(sys.argv[1])); q=d['edge_probability_denominator']
W=np.array(d['red_probability_numerators'],dtype=np.float64)/q; n=len(W)
tot=0.0
for M in (W, 1-W):
    for a in [0, 5, 400]:
        s=0.0
        for b in range(n):
            v=M[a]*M[b]; s+=M[a,b]*(v@M@v)
        print(a, s/n**3)
    tot=None
