"""Round4-E9: generalized twisted cyclic lifts of B192 (search side, float64).
Fine class (i,a), i in B192, a in Z_m, index m*i+a.  Circulant blocks:
  P inactive: p0; P active phase g: x if (a-b-g) mod m in S else 1;
  H phase g: 0 if (a-b-g) in S else y;  0/F/diag unchanged.
m=5, S={1,4}, Z5 phase table from lane P reproduces C(9;7,4,8)."""
import json, sys, time
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
PHASE = ROOT / "reports/association-scheme-phase-two-amplitude-001/phase-assignment.json"

def load_base():
    B = np.array(json.loads(BASE.read_text())["red_probability_numerators"])
    sym = np.zeros(B.shape, int)  # 0 zero,1 F,2 P,3 H
    sym[B == 65536] = 1; sym[B == 51064] = 2; sym[B == 35015] = 3
    np.fill_diagonal(sym, 0)
    ph = json.loads(PHASE.read_text())
    return sym, ph

def pairs(sym):
    n = len(sym)
    return [(i, j) for i in range(n) for j in range(i + 1, n) if sym[i, j] >= 2]

def build(sym, prs, g, m, S, lv):
    """g: array over prs, -1 inactive, else phase in Z_m (for i<j). lv=(p0,x,y)."""
    p0, x, y = lv
    n = len(sym); N = n * m
    base = np.where(sym == 1, 1.0, 0.0)
    W = np.kron(base, np.ones((m, m)))
    d = (np.arange(m)[:, None] - np.arange(m)[None, :]) % m
    for k, (i, j) in enumerate(prs):
        gk = g[k]
        if gk < 0:
            blk = np.full((m, m), p0)
        else:
            on = np.isin((d - gk) % m, S)
            blk = np.where(on, x, 1.0) if sym[i, j] == 2 else np.where(on, 0.0, y)
        W[m*i:m*i+m, m*j:m*j+m] = blk
        W[m*j:m*j+m, m*i:m*i+m] = blk.T
    return W

def evalgrad(W, m, want_grad=True):
    N = len(W); reps = range(0, N, m)
    tot = 0.0; G = np.zeros((N // m, N)) if want_grad else None
    for col, U in ((0, W), (1, 1.0 - W)):
        for r, a in enumerate(reps):
            X = U[a][None, :] * U           # X[b,c] = U_ac U_bc
            Y = X @ U
            g = np.einsum('bc,bc->b', X, Y)  # sum_{c,d} U_ac U_bc U_ad U_bd U_cd
            tot += m * (U[a] @ g)
            if want_grad:
                G[r] += (g if col == 0 else -g)
    return tot / N**4, G

if __name__ == "__main__":
    sym, ph = load_base(); prs = pairs(sym)
    g = np.array([ph[f"{i},{j}"] for i, j in prs])
    t = time.time()
    W = build(sym, prs, g, 5, [1, 4], (7/9, 4/9, 8/9))
    F, _ = evalgrad(W, 5, False)
    print(repr(F), 4198776398959/139314069504000, time.time() - t)
