"""Round4-E12: lambda-homotopy F_lam = t(K4,W) + lam*t(K4,1-W) (search side, float64).
Families: (a) B192 symbol levels (z,f,p,h) at N=192; (b) full 192x192 kernel (diag fixed 0),
projected gradient.  Evaluator copied in spirit from research/experiments/round4_E9/lift.py (m=1)."""
import json, sys, time
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"

def load_sym():
    B = np.array(json.loads(BASE.read_text())["red_probability_numerators"])
    sym = np.zeros(B.shape, int); sym[B == 65536] = 1; sym[B == 51064] = 2; sym[B == 35015] = 3
    np.fill_diagonal(sym, 0); return sym

def tk4(U, grad=False):
    N = len(U); tot = 0.0; G = np.zeros((N, N)) if grad else None
    for a in range(N):
        X = U[a][None, :] * U; g = np.einsum('bc,bc->b', X, X @ U)
        tot += U[a] @ g
        if grad: G[a] = g
    return tot / N**4, G

def F(W, lam, grad=False):
    r, Gr = tk4(W, grad); b, Gb = tk4(1 - W, grad)
    g = None
    if grad:
        N = len(W); g = 12.0 / N**4 * (Gr - lam * Gb); np.fill_diagonal(g, 0)
    return r + lam * b, r, b, g

def fam(sym, lv):
    z, f, p, h = lv; W = np.choose(sym, [z, f, p, h]).astype(float); np.fill_diagonal(W, 0); return W

def opt_levels(sym, lv, lam, iters, free, log):
    """projected gradient on levels via chain rule from full gradient."""
    lv = np.array(lv, float); masks = [(sym == k) for k in range(4)]
    for m in masks: np.fill_diagonal(m, False)
    Fv, r, b, g = F(fam(sym, lv), lam, True); step = 0.5; nev = 1
    for _ in range(iters):
        dl = np.array([g[m].sum() / 2 if k in free else 0.0 for k, m in enumerate(masks)])
        while True:
            nl = np.clip(lv - step * dl, 0, 1); Fn, rn, bn, gn = F(fam(sym, nl), lam, True); nev += 1
            if Fn < Fv or step < 1e-6: break
            step *= 0.5
        if Fn >= Fv: break
        lv, Fv, r, b, g = nl, Fn, rn, bn, gn; step *= 1.5
    return lv, Fv, r, b, nev

def opt_full(W, lam, iters):
    Fv, r, b, g = F(W, lam, True); step = 0.5 * len(W)**2; nev = 1
    for _ in range(iters):
        while True:
            Wn = np.clip(W - step * g, 0, 1); np.fill_diagonal(Wn, 0)
            Fn, rn, bn, gn = F(Wn, lam, True); nev += 1
            if Fn < Fv or step < 1e-3: break
            step *= 0.5
        if Fn >= Fv: break
        W, Fv, r, b, g = Wn, Fn, rn, bn, gn; step *= 1.3
    return W, Fv, r, b, nev
