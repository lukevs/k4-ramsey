import sys, numpy as np
sys.path.insert(0, 'experiments/round5_F1'); sys.path.insert(0, 'experiments/round4_E5')
from core import *
from phi import split
rng = np.random.default_rng(1)
n = 9
W = rng.choice([0, 1, .3, .6, .8], (n, n)); W = np.triu(W, 1); W = W + W.T
mask = (rng.random((n, n)) < 0.7); mask = np.triu(mask, 1); mask = mask | mask.T
L = Lift(W, mask)
A = (rng.random((n, n)) * 2 - 1) * L.m; A = np.triu(A, 1); A = A + A.T
f, G, a, b = L.val_grad(A)
d = Fdens(split(W, A)) - Fdens(W)
print('delta', f, 'direct', d, 'diff', f - d)
e = 1e-6; errs = []
for (u, v) in [(0, 1), (2, 5), (3, 7), (1, 8)]:
    if not mask[u, v]: continue
    A2 = A.copy(); A2[u, v] += e; A2[v, u] += e
    errs.append((L.val_grad(A2, False)[0] - f) / e - G[u, v])
print('grad err', errs, 'scale', np.abs(G).max())
Gf = gradF(W); errs = []
for (u, v) in [(0, 1), (2, 5), (3, 7)]:
    W2 = W.copy(); W2[u, v] += e; W2[v, u] += e
    errs.append((Fdens(W2) - Fdens(W)) / e - Gf[u, v])
print('gradF err', errs, 'scale', np.abs(Gf).max())
ty, zc, orb = labels(); Wb = b192(32/41, 22/41, ty, zc)
print('B192 F', repr(Fdens_root(Wb)), 1013294255057839/33620705806123008, 'frac', ((Wb > 0) & (Wb < 1)).sum(), 'sym', (Wb == Wb.T).all())
