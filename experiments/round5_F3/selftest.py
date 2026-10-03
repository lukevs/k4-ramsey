import sys, time, numpy as np
sys.path.insert(0, '/Users/luke.vanseters/code/github.com/lukevs/k4-ramsey/experiments/round5_F3')
from lib import *
G, x = b192_cayley()
t = time.time(); F, g = F_cayley(G, x); print('B192 cayley F', repr(F), 'eval s', time.time() - t)
W = G.kernel(x); print('full-eval F', repr(F_full(W)))
rng = np.random.default_rng(0); y = rng.random(G.k); F1, g1 = F_cayley(G, y)
for i in rng.choice(G.k, 4, replace=False):
    e = np.zeros(G.k); e[i] = 1e-6
    print('fd check', i, (F_cayley(G, y + e)[0] - F_cayley(G, y - e)[0]) / 2e-6, g1[i])
symC, oth = classify(W); symL = b192_literature_sym()
from collections import Counter
print('cayley sym counts', Counter(symC.ravel().tolist()), 'lit', Counter(symL.ravel().tolist()))
cC = certificate(symC); cL = certificate(symL)
print('certificate equal (E11 closed form vs literature B192):', cC == cL)
