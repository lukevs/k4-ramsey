"""Decompose the Z5 lift C(9;7,4,8) as base(7/9, 8/15) + pure latent lift; report T3..T6."""
import sys, numpy as np, json
sys.path.insert(0, '../round4_E9')
from lift import load_base, pairs, build
from expand import expansion
from base import base, Fval
sym, ph = load_base(); prs = pairs(sym)
g = np.array([ph[f"{i},{j}"] for i, j in prs]); m = 5
Wl = build(sym, prs, g, m, [1, 4], (7/9, 4/9, 8/9))
n = len(sym)
Wb = np.where(sym == 1, 1.0, 0.0); Wb[sym == 2] = 7/9; Wb[sym == 3] = 8/15; np.fill_diagonal(Wb, 0)
D = {}; lo = 1e9; hi = -1e9; rowerr = 0
for (i, j) in prs:
    blk = Wl[m*i:m*i+m, m*j:m*j+m] - Wb[i, j]
    rowerr = max(rowerr, np.abs(blk.mean(0)).max(), np.abs(blk.mean(1)).max())
    if np.abs(blk).max() < 1e-15: continue
    D[(i, j)] = blk; D[(j, i)] = blk.T
T = expansion(Wb, D, m)
F0 = Fval(base(7/9, 8/15)[0])
out = dict(rowmean_err=float(rowerr), F_base_7_9_8_15=F0, T3=T[0], T4=T[1], T5=T[2], T6=T[3], sum=float(sum(T)), F_pred=F0 + float(sum(T)), F_C=4198776398959/139314069504000,
           gain_vs_B192opt=0.030138977289665334 - F0 - float(sum(T)), base_level_cost=F0 - 0.030138977289665334)
print(json.dumps(out, indent=1)); json.dump(out, open(sys.argv[1] + '/z5decomp.json', 'w'), indent=1)
