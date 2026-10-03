"""E10b: D5 (dihedral) voltage lift of B192.  Copied/adapted from round4_E9/lift.py.
Pair (i<j), phase g, reflection bit r: on-pattern iff (a - b - g) mod 5 in S (r=0)
or (a + b - g) mod 5 in S (r=1).  Block (j,i) = transpose, so W is symmetric and the
reflection rule (a+b) is symmetric under swapping endpoints (g_ji = g_ij for r=1)."""
import json, sys, time
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/experiments/round4_E9"))
from lift import load_base, pairs

def build(sym, prs, g, r, m, S, lv):
    p0, x, y = lv
    n = len(sym)
    W = np.kron(np.where(sym == 1, 1.0, 0.0), np.ones((m, m)))
    A = np.arange(m)[:, None]; B = np.arange(m)[None, :]
    dm = (A - B) % m; dp = (A + B) % m
    for k, (i, j) in enumerate(prs):
        if g[k] < 0:
            blk = np.full((m, m), p0)
        else:
            d = dp if r[k] else dm
            on = np.isin((d - g[k]) % m, S)
            blk = np.where(on, x, 1.0) if sym[i, j] == 2 else np.where(on, 0.0, y)
        W[m*i:m*i+m, m*j:m*j+m] = blk
        W[m*j:m*j+m, m*i:m*i+m] = blk.T
    return W

def full(W, grad=True):
    """F = t(K4,W)+t(K4,1-W); Gm[a,b] = rooted K4 count difference (blue - red)."""
    N = len(W); tot = 0.0
    Gm = np.zeros((N, N)) if grad else None
    for sgn, U in ((1, W), (-1, 1.0 - W)):
        for a in range(N):
            X = U[a][None, :] * U
            Y = X @ U
            ga = np.einsum('bc,bc->b', X, Y)
            tot += U[a] @ ga
            if grad: Gm[a] += sgn * ga
    return tot / N**4, Gm

if __name__ == "__main__":
    sym, ph = load_base(); prs = pairs(sym)
    g = np.array([ph[f"{i},{j}"] for i, j in prs]); r = np.zeros(len(prs), int)
    t = time.time()
    W = build(sym, prs, g, r, 5, [1, 4], (7/9, 4/9, 8/9))
    F, _ = full(W, grad=False)
    print(repr(F), 4198776398959/139314069504000, F - 4198776398959/139314069504000, time.time() - t)
