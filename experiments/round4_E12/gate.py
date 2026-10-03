import sys, time; sys.path.insert(0, 'experiments/round4_E9'); sys.path.insert(0, 'experiments/round4_E12')
import numpy as np
from homotopy import load_sym, fam, F
sym = load_sym(); t = time.time()
Fv, r, b, _ = F(fam(sym, [0, 1, 32/41, 22/41]), 1.0); print("B192(32/41,22/41)", Fv, r, b, (r-b)/Fv, time.time()-t, flush=True)
from lift import load_base, pairs, build
s, ph = load_base(); prs = pairs(s); g = np.array([ph[f"{i},{j}"] for i, j in prs])
W = build(s, prs, g, 5, [1, 4], (7/9, 4/9, 8/9)); N = len(W); t = time.time()
def t5(U):
    tot = 0.0
    for a in range(0, N, 5):
        X = U[a][None, :] * U; tot += 5 * (U[a] @ np.einsum('bc,bc->b', X, X @ U))
    return tot / N**4
r, b = t5(W), t5(1 - W); print("C(9;7,4,8)", r + b, r, b, (r-b)/(r+b), time.time()-t)
