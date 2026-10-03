import sys, json, time; sys.path.insert(0, 'research/experiments/round4_E12')
import numpy as np
from homotopy import load_sym, fam, F, opt_levels
out = open(sys.argv[1], 'w'); sym = load_sym()
seeds = {"b192": [0, 1, 32/41, 22/41], "swap": [0, 1, 22/41, 32/41], "half": [0, 1, .5, .5], "fz": [.2, .8, .6, .4]}
paths = {"up": list(np.linspace(1, 2.5, 11)[1:]) + list(np.linspace(2.5, 1, 11)[1:]),
         "down": list(np.linspace(1, .6, 11)[1:]) + list(np.linspace(.6, 1, 11)[1:])}
IT = 15
for sn, s in seeds.items():
    for pn, lams in paths.items():
        lv = s; tot = 0
        for lam in lams:
            lv, Fv, r, b, ne = opt_levels(sym, lv, lam, IT, {0, 1, 2, 3}, None); tot += ne
        lv, Fv, r, b, ne = opt_levels(sym, lv, 1.0, 200, {0, 1, 2, 3}, None); tot += ne
        rec = dict(seed=sn, path=pn, lv=list(lv), F=Fv, red=r, blue=b, evals=tot); print(rec, flush=True); out.write(json.dumps(rec) + "\n")
    lv, Fv, r, b, ne = opt_levels(sym, s, 1.0, 20 * IT + 200, {0, 1, 2, 3}, None)
    rec = dict(seed=sn, path="control", lv=list(lv), F=Fv, red=r, blue=b, evals=ne); print(rec, flush=True); out.write(json.dumps(rec) + "\n")
