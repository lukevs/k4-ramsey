"""E10b: single reflection-bit (+phase) flip deltas via exact local recount c_A, then greedy."""
import json, sys, time, itertools
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/round4_E9")); sys.path.insert(0, str(ROOT / "experiments/round4_E10"))
from lift import load_base, pairs, evalgrad
from dlift import build
m = 5; S = [1, 4]

def cA_one(U, A):
    M = np.ones(len(U), bool); M[A] = False
    V = U[np.ix_(M, M)]; uA = U[np.ix_(A, M)]; UA = U[np.ix_(A, A)]
    X = uA[:, None, :] * V[None, :, :]          # X[a,b,c] = U_ac V_bc
    Y = X @ V
    N1 = np.einsum('ab,ab->', uA, np.einsum('abc,abc->ab', X, Y))
    Z = uA[:, None, :] * uA[None, :, :]         # z_{aa'}
    N2 = np.einsum('xy,xyc,cd,xyd->', UA, Z, V, Z)
    N3 = np.einsum('xy,xz,yz,xd,yd,zd->', UA, UA, UA, uA, uA, uA)
    N4 = np.einsum('xy,xz,xw,yz,yw,zw->', UA, UA, UA, UA, UA, UA)
    return 4*N1 + 6*N2 + 4*N3 + N4

def cA(W, A): return cA_one(W, A) + cA_one(1.0 - W, A)

def selftest():
    rng = np.random.default_rng(0); N = 13; U = rng.random((N, N)); U = (U + U.T)/2
    def tot(U): return np.einsum('ab,ac,ad,bc,bd,cd->', U, U, U, U, U, U)
    A = [2, 3, 7]; M = [k for k in range(N) if k not in A]
    Um = U[np.ix_(M, M)]
    print('selftest', tot(U) - tot(Um), cA_one(U, np.array(A)))

if __name__ == "__main__":
    selftest()
    sym, ph = load_base(); prs = pairs(sym); n = len(sym); N = n*m
    lv = (7/9, 4/9, 8/9)
    g = np.array([ph[f"{i},{j}"] for i, j in prs]); r = np.zeros(len(prs), int)
    W0 = build(sym, prs, g, r, m, S, lv)
    t = time.time(); F0, G = evalgrad(build(sym, prs, g, r, m, S, lv), m, True); print('F0', F0, time.time()-t)
    # first-order screen of (pair, reflection phase h)
    cand = []
    for k, (i, j) in enumerate(prs):
        if g[k] < 0: continue
        Gb = np.array([[G[i, m*j + ((b - a) % m)] for b in range(m)] for a in range(m)])
        old = W0[m*i:m*i+m, m*j:m*j+m]
        for h in range(m):
            r2 = r.copy(); g2 = g.copy(); r2[k] = 1; g2[k] = h
            A_ = np.arange(m)[:, None] + np.arange(m)[None, :]
            on = np.isin((A_ - h) % m, S)
            new = np.where(on, lv[1], 1.0) if sym[i, j] == 2 else np.where(on, 0.0, lv[2])
            d1 = 12 * np.sum(Gb * (new - old)) / N**4
            cand.append((d1, k, h))
    cand.sort(); print('n cand', len(cand), 'best first-order', cand[:5], 'frac<0', sum(c[0] < 0 for c in cand))
    # exact local deltas on top candidates
    base_cache = {}
    def exact_delta(Wc, k, newblk):
        i, j = prs[k]; A = np.arange(m*i, m*i+m)
        W2 = Wc.copy(); W2[m*i:m*i+m, m*j:m*j+m] = newblk; W2[m*j:m*j+m, m*i:m*i+m] = newblk.T
        return (cA(W2, A) - cA(Wc, A)) / N**4, W2
    def blk(k, h, rr):
        i, j = prs[k]; A_ = (np.arange(m)[:, None] + (1 if rr else -1)*np.arange(m)[None, :])
        on = np.isin((A_ - h) % m, S)
        return np.where(on, lv[1], 1.0) if sym[i, j] == 2 else np.where(on, 0.0, lv[2])
    t = time.time(); res = []
    for d1, k, h in cand[:40]:
        dx, _ = exact_delta(W0, k, blk(k, h, 1)); res.append((dx, d1, k, h))
    res.sort(); print('exact top (dx,d1,k,h):', res[:10], time.time()-t)
    # also sanity: exact delta of a pure rotation phase change on best pair agrees sign w/ first order
    # greedy accept
    Wc = W0.copy(); Fc = F0; acc = []; used = set()
    for dx, d1, k, h in res:
        if k in used: continue
        d, W2 = exact_delta(Wc, k, blk(k, h, 1))
        if d < -1e-15:
            Wc = W2; Fc += d; acc.append((k, h, d)); used.add(k)
    print('greedy accepted', len(acc), 'F', repr(Fc), 'gain vs C', Fc - F0)
    np.save(ROOT/'experiments/round4_E10/greedy_W.npy', Wc)
    json.dump({'accepted': [[int(k), int(h), float(d)] for k, h, d in acc], 'F_est': Fc, 'F0': F0},
              open(ROOT/'experiments/round4_E10/greedy.json', 'w'))
