"""E10b stage 2: exact single-bit deltas on many pairs (h=0 and h=g), gauge control, pair-greedy."""
import json, sys, time
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "research/experiments/round4_E9")); sys.path.insert(0, str(ROOT / "research/experiments/round4_E10"))
from lift import load_base, pairs
from dlift import build
from flips import cA
m = 5; S = [1, 4]; T0 = time.time(); BUDGET = 440
sym, ph = load_base(); prs = pairs(sym); n = len(sym); N = n*m; lv = (7/9, 4/9, 8/9)
g = np.array([ph[f"{i},{j}"] for i, j in prs]); r = np.zeros(len(prs), int)
W0 = build(sym, prs, g, r, m, S, lv)
def blk(k, h, rr):
    i, j = prs[k]; A_ = (np.arange(m)[:, None] + (1 if rr else -1)*np.arange(m)[None, :])
    on = np.isin((A_ - h) % m, S)
    return np.where(on, lv[1], 1.0) if sym[i, j] == 2 else np.where(on, 0.0, lv[2])
cache = {}
def delta(k, h, Wc=W0, key=True):
    i, j = prs[k]; A = np.arange(m*i, m*i+m)
    if (i, key) not in cache: cache[(i, key)] = cA(Wc, A)
    W2 = Wc.copy(); b = blk(k, h, 1); W2[m*i:m*i+m, m*j:m*j+m] = b; W2[m*j:m*j+m, m*i:m*i+m] = b.T
    return (cA(W2, A) - cache[(i, key)]) / N**4
# gauge control: negate fiber 0 -> every active pair (0,j) (0<j) becomes reflection with phase -g (block (0,j): on iff -a-b-g in S iff a+b+g in S)
i0 = 0; ks = [k for k, (i, j) in enumerate(prs) if i == i0 and g[k] >= 0]
Wg = W0.copy()
for k in ks:
    i, j = prs[k]; b = blk(k, (-g[k]) % m, 1); Wg[m*i:m*i+m, m*j:m*j+m] = b; Wg[m*j:m*j+m, m*i:m*i+m] = b.T
A = np.arange(0, m); print('gauge control (all pairs at fiber 0 reflected, phase -g):', (cA(Wg, A) - cA(W0, A))/N**4, 'npairs', len(ks))
res = []
act = [k for k in range(len(prs)) if g[k] >= 0]
for k in act:
    if time.time() - T0 > BUDGET: break
    res.append((delta(k, 0), k, 0))
print('evaluated', len(res), 'of', len(act), 'time', time.time()-T0)
res.sort()
print('best 10:', [(float(d), k, h) for d, k, h in res[:10]], 'n<0', sum(d < 0 for d, _, _ in res),
      'min', res[0][0], 'median', res[len(res)//2][0])
json.dump([[float(d), int(k), int(h)] for d, k, h in res], open(ROOT/'research/experiments/round4_E10/single_h0.json', 'w'))
