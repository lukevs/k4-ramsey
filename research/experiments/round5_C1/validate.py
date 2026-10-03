import numpy as np, sys, time
from base import base
sys.path.insert(0, '../round4_E11'); from family import F
from expand import expansion
p, h = 0.7791808266653855, 0.5342650498652971
W, typ, cls = base(p, h); n = 192; Q = 1 - W
fr = (W > 0) & (W < 1); a = np.minimum(W, Q)
rng = np.random.default_rng(int(sys.argv[1])); m = 3
D = {}
J = np.eye(m) - 1/m
for u in range(n):
    for v in range(u+1, n):
        if fr[u, v]:
            K = J @ rng.standard_normal((m, m)) @ J
            K *= 0.95*a[u, v]/np.abs(K).max()
            D[(u, v)] = K; D[(v, u)] = K.T
t = time.time(); T = expansion(W, D, m); print('expansion', T, sum(T), time.time()-t)
N = n*m; Wl = np.zeros((N, N))
for u in range(n):
    for v in range(n):
        Wl[u*m:(u+1)*m, v*m:(v+1)*m] = W[u, v] + (D[(u, v)] if (u, v) in D else 0)
assert Wl.min() >= 0 and Wl.max() <= 1
F0 = F(W, [0], [n]); t = time.time()
F1 = F(Wl, list(range(N)), [1.0]*N)
print('direct dF', F1 - F0, 'expansion', sum(T), 'diff', F1 - F0 - sum(T), time.time()-t)
