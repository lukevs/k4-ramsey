"""E11: one-sided derivatives of F w.r.t. the 15 (type,class) levels at the B192 2-param optimum."""
import sys, json, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from multilevel import setup, buildW, base_levels, TY
from family import F
q, ncls, cl, TT = setup(4)
bl = base_levels(0.7791808, 0.5342652)
v0 = np.concatenate([bl[ty] for ty in TY]).astype(float)
f = lambda v: F(buildW(v, q, ncls, cl, TT), [0], [12*q])
F0 = f(v0); out = []
for i in range(15):
    e = np.zeros(15); d = 1e-6 * (1 if v0[i] < 0.5 else -1); e[i] = d
    g = (f(v0 + e) - F0) / abs(d)   # derivative in feasible direction
    out.append((TY[i//3], ['center','S','rest'][i%3], float(v0[i]), g))
    print(out[-1])
json.dump(out, open(sys.argv[1] + '/kkt.json', 'w'), indent=1)
