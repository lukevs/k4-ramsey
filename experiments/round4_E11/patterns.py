"""E11: discrete neighbourhood — replace one block-type's (center,S,rest) pattern by any of {0,1,p,h}^3, re-optimise (p,h)."""
import sys, json, itertools, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from multilevel import setup, buildW, TY
from family import F
from scipy.optimize import minimize
q, ncls, cl, TT = setup(4)
base = {'D': '001', 'Z': '001', 'X': '110', 'P': 'pp0', 'H': 'h10'}
def val(pat, p, h):
    m = {'0': 0.0, '1': 1.0, 'p': p, 'h': h}
    v = np.array([m[c] for ty in TY for c in pat[ty]]); return F(buildW(v, q, ncls, cl, TT), [0], [12*q])
def optpat(pat):
    best = (1, None)
    for x0 in [(0.78, 0.53), (0.4, 0.2)]:
        r = minimize(lambda x: val(pat, *np.clip(x, 0, 1)), x0, method='Nelder-Mead', options={'xatol':1e-7,'fatol':1e-13,'maxiter':200})
        if r.fun < best[0]: best = (r.fun, list(np.clip(r.x, 0, 1)))
    return best
res = []
for ty in TY:
    for s in itertools.product('01ph', repeat=3):
        pat = dict(base); pat[ty] = ''.join(s)
        if pat == base: continue
        fv, x = optpat(pat); res.append((fv, ty, ''.join(s), x))
res.sort(key=lambda r: r[0])
for r in res[:10]: print(r)
json.dump({'base': optpat(base), 'top': res[:30]}, open(sys.argv[1] + '/patterns.json', 'w'), indent=1, default=float)
