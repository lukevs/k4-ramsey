"""E11: free levels per (block-type, difference-class) on Q x (Z3xZ2xZ2 design).
Q=F2^4 classes {0},S,rest ; Q=F2^5=F2^4xF2 classes (cls4, bit) -> 6 classes.
Block types: D (same block), Z, X, P, H.  Search-side float64."""
import sys, json, time
import numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from family import F
from design import types
from scipy.optimize import minimize
S4 = {1, 2, 4, 8, 15}
def cls4(z): return 0 if z == 0 else (1 if z in S4 else 2)
TY = ['D', 'Z', 'X', 'P', 'H']
def base_levels(p, h):   # per type, per cls4 (center,S,rest)
    return {'D': [0, 0, 1], 'Z': [0, 0, 1], 'X': [1, 1, 0], 'P': [p, p, 0], 'H': [h, 1, 0]}
def setup(nbits):
    q = 16 * 2**(nbits - 4)
    ncls = 3 * 2**(nbits - 4)
    cl = np.array([[cls4((x ^ y) & 15) + 3 * ((x ^ y) >> 4) for y in range(q)] for x in range(q)])
    T = types(3, 2); k = 12
    TT = [[('D' if s == t else T[s][t]) for t in range(k)] for s in range(k)]
    return q, ncls, cl, TT
def buildW(vec, q, ncls, cl, TT):
    L = {ty: vec[i*ncls:(i+1)*ncls] for i, ty in enumerate(TY)}
    k = len(TT); W = np.zeros((k*q, k*q))
    for s in range(k):
        for t in range(k):
            W[s*q:(s+1)*q, t*q:(t+1)*q] = np.asarray(L[TT[s][t]])[cl]
    return W
def run(nbits, p, h):
    q, ncls, cl, TT = setup(nbits)
    bl = base_levels(p, h)
    v0 = np.concatenate([np.tile(bl[ty], 2**(nbits-4)) for ty in TY]).astype(float)
    f = lambda v: F(buildW(v, q, ncls, cl, TT), [0], [12*q])
    F0 = f(v0); t0 = time.time()
    r = minimize(f, v0, method='L-BFGS-B', bounds=[(0, 1)]*len(v0), options={'eps': 1e-7, 'ftol': 1e-15, 'gtol': 1e-10, 'maxiter': 200})
    return F0, r.fun, r.x, time.time() - t0
if __name__ == '__main__':
    out = sys.argv[1]; res = {}
    for nbits in (4, 5):
        F0, F1, x, dt = run(nbits, 0.7791808, 0.5342652)
        res[nbits] = {'F_base': F0, 'F_opt': F1, 'levels': [round(float(a), 6) for a in x], 'secs': dt}
        print(nbits, F0, F1, np.round(x, 4), dt, flush=True)
    json.dump(res, open(out + '/multilevel.json', 'w'), indent=1)
