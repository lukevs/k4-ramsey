"""E11: give one block type (X, P or H) its own Clebsch-type set C' = a + {0}uS', S' any 5 vectors in general position
summing to 0 (168 sets x 16 translates); others keep C. For H: h at a, 1 on C'\\{a}."""
import sys, json, itertools, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from family import F
from design import types
from scipy.optimize import minimize
T = types(3, 2); q = 16
D = np.array([[x ^ y for y in range(q)] for x in range(q)])
C0 = {0, 1, 2, 4, 8, 15}
sets = set()
for S in itertools.combinations(range(1, 16), 5):
    if S[0]^S[1]^S[2]^S[3]^S[4] == 0 and all(a^b^c != 0 for a,b,c in itertools.combinations(S,3)) and all(a^b!=0 for a,b in itertools.combinations(S,2)):
        # general position: no 3 or 4 sum to 0
        if all(a^b^c^d != 0 for a,b,c,d in itertools.combinations(S,4)): sets.add(frozenset((0,)+S))
print('clebsch sets containing 0:', len(sets))
def build(Cs, p, h):
    g = {}
    for ty in 'ZXPH':
        Cset, a = Cs[ty]; inC = np.isin(D ^ a, list(Cset)); ctr = (D == a)
        g[ty] = {'Z': np.where(inC, 0., 1.), 'X': np.where(inC, 1., 0.), 'P': np.where(inC, p, 0.), 'H': np.where(ctr, h, np.where(inC, 1., 0.))}[ty]
    W = np.zeros((12*q, 12*q))
    for s in range(12):
        for t in range(12): W[s*q:(s+1)*q, t*q:(t+1)*q] = g[T[s][t]]
    return W
base = {ty: (C0, 0) for ty in 'ZXPH'}
res = []
for ty in 'XPH':
    for Cs in sets:
        for a in range(16):
            cs = dict(base); cs[ty] = (Cs, a)
            res.append((F(build(cs, 32/41, 22/41), [0], [192]), ty, sorted(Cs), a))
res.sort(key=lambda r: r[0])
b0 = F(build(base, 32/41, 22/41), [0], [192]); print('base', b0)
out = []
seen = 0
for r in res[:40]:
    if r[0] >= b0 - 1e-15 and seen >= 3: continue
    seen += 1
    cs = dict(base); cs[r[1]] = (set(r[2]), r[3])
    o = minimize(lambda x: F(build(cs, *np.clip(x,0,1)), [0], [192]), (0.78, 0.53), method='Nelder-Mead', options={'xatol':1e-7,'fatol':1e-13})
    out.append({'F_fixed': r[0], 'type': r[1], 'C': r[2], 'shift': r[3], 'F_opt': o.fun, 'ph': list(o.x)}); print(out[-1], flush=True)
    if len(out) >= 8: break
print('distinct fixed values (best 10):', sorted(set(round(r[0], 12) for r in res))[:10])
json.dump(out, open(sys.argv[1] + '/twist.json', 'w'), indent=1, default=float)
