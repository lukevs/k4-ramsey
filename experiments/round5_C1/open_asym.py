"""Linear-in-d box rates for opening a 0/1 orbital by mean shift d with an arbitrary latent kernel
(new entry 1-d+D or d+D, E|D| <= 2d(1-d)), existing fractional kernels in the asym box (E D^2 <= W(1-W))."""
import numpy as np, json, sys
from base import base
p, h = 0.7791808266653855, 0.5342650498652971
W, typ, cls = base(p, h); n = 192; Q = 1 - W
fr = (W > 0) & (W < 1); sv = np.where(fr, np.sqrt(W*Q), 0.0)
nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
G = np.load('../../reports/round5-C1-char-001/G.npy')
c3 = lambda x, y, z: abs((W[x]*W[y]*W[z] - Q[x]*Q[y]*Q[z]).sum())
out = []
for T_, c in (('H', 1), ('D', 2)):
    m = (typ == T_) & (cls == c) & ~fr; np.fill_diagonal(m, False)
    slack = abs(G[m].sum()/2); r3 = r4 = 0.0
    for x, y in zip(*np.nonzero(m)):
        for z in nb[x]:
            if fr[z, y]: r3 += 3*4*c3(x, y, z)*2*sv[y, z]*sv[z, x]/n**4
        for z in nb[y]:
            for w in nb[z]:
                if fr[w, x]: r4 += 4*3*(W[x, z]*W[y, w] + Q[x, z]*Q[y, w])*2*sv[y, z]*sv[z, w]*sv[w, x]/n**4
    out.append(dict(type=T_, cls=['0', 'S', 'off'][c], slack=float(slack), cubic_rate=r3/2, quartic_rate=r4/2))
    print(out[-1], flush=True)
json.dump(out, open(sys.argv[1] + '/open_asym.json', 'w'), indent=1)
