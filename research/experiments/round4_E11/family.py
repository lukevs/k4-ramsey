"""E11 family evaluator. W((x,s),(y,t)) = g_{T[s][t]}(x-y) on group Z (F2^n or Z_m) x [k].
g_Z = 0 on C, zo off C;  g_X = 1 on C, 0 off;  g_P = p on C, 0 off;  g_H = h at 0, 1 on C\\{0}, 0 off.
(zo=1 reproduces B192.)  Float64 search-side evaluator using translation invariance."""
import json, sys, time
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
RULE = json.load(open(ROOT/'research/experiments/round4_E11/rule.json'))
T12 = RULE['types']

def build(T, elems, sub, C, p, h, zo=1.0, extra=None):
    """elems: list of group elements; sub(x,y)-> element index of x-y; C: set of elem indices (contains 0 index)."""
    q = len(elems); k = len(T)
    D = np.array([[sub(x, y) for y in range(q)] for x in range(q)])
    inC = np.isin(D, list(C)); isZ = (D == 0)
    g = {'Z': np.where(inC, 0.0, zo), 'X': np.where(inC, 1.0, 0.0),
         'P': np.where(inC, p, 0.0), 'H': np.where(isZ, h, np.where(inC, 1.0, 0.0))}
    W = np.zeros((k*q, k*q))
    for s in range(k):
        for t in range(k):
            W[s*q:(s+1)*q, t*q:(t+1)*q] = g[T[s][t]]
    return W

def F(W, reps, wts):
    N = len(W); tot = 0.0
    for U in (W, 1.0 - W):
        for a, w in zip(reps, wts):
            X = U[a][None, :] * U
            Y = X @ U
            g = np.einsum('bc,bc->b', X, Y)
            tot += w * (U[a] @ g)
    return tot / N**4

def f2(n, Svecs):
    q = 2**n
    return list(range(q)), (lambda x, y: x ^ y), set([0] + list(Svecs))

def zm(m, Sset):
    return list(range(m)), (lambda x, y: (x - y) % m), set([0] + list(Sset))

def evalfam(T, grp, p, h, zo=1.0):
    elems, sub, C = grp; q = len(elems); k = len(T)
    W = build(T, elems, sub, C, p, h, zo)
    return F(W, [0], [k*q])  # vertex-transitive (Cayley on Z x Z3xZ2xZ2)

def opt(T, grp, zo_free=False, x0=(32/41, 22/41, 1.0)):
    from scipy.optimize import minimize
    if zo_free:
        f = lambda v: evalfam(T, grp, v[0], v[1], v[2])
        r = minimize(f, x0, method='Nelder-Mead', bounds=[(0,1)]*3, options={'xatol':1e-7,'fatol':1e-12,'maxiter':400})
    else:
        f = lambda v: evalfam(T, grp, v[0], v[1])
        r = minimize(f, x0[:2], method='Nelder-Mead', bounds=[(0,1)]*2, options={'xatol':1e-7,'fatol':1e-12,'maxiter':300})
    return r.fun, list(r.x)

if __name__ == '__main__':
    t = time.time()
    g4 = f2(4, [1, 2, 4, 8, 15])
    print('B192 rule value at 32/41,22/41:', repr(evalfam(T12, g4, 32/41, 22/41)), 1013294255057839/33620705806123008, time.time()-t)
    print('at 4/5,2/5:', repr(evalfam(T12, g4, 4/5, 2/5)), 3333439223/110592000000)
