"""E10b stage 3: exact deltas of two reflection bits sharing a fiber (interaction test), both phases scanned."""
import json, sys, time, collections
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments/round4_E9")); sys.path.insert(0, str(ROOT / "experiments/round4_E10"))
from lift import load_base, pairs
from dlift import build
from flips import cA
m = 5; S = [1, 4]; T0 = time.time(); BUDGET = 200
sym, ph = load_base(); prs = pairs(sym); n = len(sym); N = n*m; lv = (7/9, 4/9, 8/9)
g = np.array([ph[f"{i},{j}"] for i, j in prs]); r = np.zeros(len(prs), int)
W0 = build(sym, prs, g, r, m, S, lv)
single = {k: d for d, k, h in json.load(open(ROOT/'experiments/round4_E10/single_h0.json'))}
def blk(k, h):
    i, j = prs[k]; A_ = np.arange(m)[:, None] + np.arange(m)[None, :]
    on = np.isin((A_ - h) % m, S)
    return np.where(on, lv[1], 1.0) if sym[i, j] == 2 else np.where(on, 0.0, lv[2])
def put(W, k, b):
    i, j = prs[k]; W[m*i:m*i+m, m*j:m*j+m] = b; W[m*j:m*j+m, m*i:m*i+m] = b.T
inc = collections.defaultdict(list)
for k, (i, j) in enumerate(prs):
    if g[k] >= 0: inc[i].append(k)
order = sorted(single, key=single.get)
res = []; cache = {}
for k1 in order:
    i = prs[k1][0]
    if i not in cache: cache[i] = cA(W0, np.arange(m*i, m*i+m))
    for k2 in inc[i]:
        if k2 == k1: continue
        for h2 in range(m):
            if time.time() - T0 > BUDGET: break
            W2 = W0.copy(); put(W2, k1, blk(k1, 0)); put(W2, k2, blk(k2, h2))
            d = (cA(W2, np.arange(m*i, m*i+m)) - cache[i]) / N**4
            res.append((d, d - single[k1] - single[k2], k1, k2, h2))
    if time.time() - T0 > BUDGET: break
res.sort()
print('pairs evaluated', len(res), 'n<0', sum(x[0] < 0 for x in res))
print('best 8 (delta, interaction, k1, k2, h2):', [tuple(float(v) if isinstance(v, float) else int(v) for v in x) for x in res[:8]])
it = [x[1] for x in res]; print('interaction min/max', min(it), max(it))
