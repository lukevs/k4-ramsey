"""E11: B192 as a Cayley graphon on F2^4 x Z_m x Z2 x Z_r (m=3, r=2 gives B192).
Block (a,e,sig); block type by difference (da,de,ds):
 ds=0: da=0,de=0 -> Z (intra) ; da=0,de=1 -> H ; da!=0,de=0 -> X ; da!=0,de=1 -> Z
 ds!=0: da=0 -> P ; da!=0 -> Z
usage: design.py OUTDIR"""
import sys, json, time, itertools
import numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from family import build, F, f2, T12
from scipy.optimize import minimize

def types(m, r, Pmode='a0'):
    bl = [(a, e, s) for a in range(m) for e in range(2) for s in range(r)]
    T = []
    for (a, e, s) in bl:
        row = []
        for (b, f, t) in bl:
            da, de, ds = (a-b) % m, e ^ f, (s-t) % r
            if ds == 0:
                row.append('Z' if (da == 0) == (de == 0) and not (da != 0 and de == 0) and not (da == 0 and de == 1) else
                           ('H' if da == 0 else 'X'))
            else:
                row.append('P' if da == 0 else 'Z')
        T.append(row)
    return T

def val(T, grp, p, h, zo=1.0):
    elems, sub, C = grp; q = len(elems)
    W = build(T, elems, sub, C, p, h, zo)
    return F(W, [0], [len(W)])   # Cayley => vertex-transitive: single root

if __name__ == '__main__':
    out = sys.argv[1]
    g4 = f2(4, [1, 2, 4, 8, 15])
    T = types(3, 2)
    # check isomorphic to B192 by value
    print('m=3,r=2 value', repr(val(T, g4, 32/41, 22/41)), 'B192', 1013294255057839/33620705806123008, flush=True)
    rows = []
    for (m, r) in [(3,2),(2,2),(4,2),(5,2),(6,2),(3,1),(3,3),(2,3),(4,3),(2,4),(3,4),(2,1),(4,1)]:
        t0 = time.time(); T = types(m, r)
        f = lambda v: val(T, g4, *v)
        best = None
        for x0 in [(0.78, 0.53), (0.6, 0.3), (0.9, 0.8)]:
            rr = minimize(f, x0, method='Nelder-Mead', bounds=[(0,1)]*2, options={'xatol':1e-7,'fatol':1e-13,'maxiter':250})
            if best is None or rr.fun < best.fun: best = rr
        rows.append({'m': m, 'r': r, 'blocks': 2*m*r, 'classes': 32*m*r, 'F': best.fun, 'ph': list(best.x)})
        print(rows[-1], round(time.time()-t0, 1), flush=True)
    json.dump(rows, open(out + '/design.json', 'w'), indent=1)
