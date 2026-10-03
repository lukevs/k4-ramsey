"""Phase + level local search for Z_m twisted lift.  usage: opt.py outdir m S(csv) init(z5|rand|file) seconds [p0 x y]"""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lift import load_base, pairs, build, evalgrad

out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
m = int(sys.argv[2]); S = [int(s) % m for s in sys.argv[3].split(',')]
init = sys.argv[4]; T = float(sys.argv[5])
lv = np.array([float(v) for v in sys.argv[6:9]]) if len(sys.argv) > 8 else np.array([7/9, 4/9, 8/9])
sym, ph = load_base(); prs = pairs(sym); K = len(prs)
rng = np.random.default_rng(int(sys.argv[9]) if len(sys.argv) > 9 else 1)
if init == 'z5':
    g = np.array([ph[f"{i},{j}"] for i, j in prs]); assert m == 5
elif init == 'rand':
    g = rng.integers(-1, m, K)
else:
    g = np.array(json.loads(Path(init).read_text())["g"])
t0 = time.time(); log = open(out / "log.jsonl", "a")
d = (np.arange(m)[:, None] - np.arange(m)[None, :]) % m
isP = np.array([sym[i, j] == 2 for i, j in prs])

def rowvals(k, gk, lv):
    """block row 0 values over b (d = -b mod m)."""
    p0, x, y = lv; dd = (-np.arange(m)) % m
    if gk < 0:
        return np.full(m, p0 if isP[k] else np.nan)
    on = np.isin((dd - gk) % m, S)
    return np.where(on, x, 1.0) if isP[k] else np.where(on, 0.0, y)

W = build(sym, prs, g, m, S, lv); F, G = evalgrad(W, m)
best = F; print("start", m, S, F, flush=True)
frac = 0.2; it = 0
while time.time() - t0 < T:
    it += 1
    # phase proposals
    gains = np.zeros(K); newg = g.copy()
    for k, (i, j) in enumerate(prs):
        Gr = G[i, m*j:m*j+m]; cur = rowvals(k, g[k], lv)
        opts = list(range(m)) + ([-1] if isP[k] else [])
        vals = [Gr @ (rowvals(k, o, lv) - cur) for o in opts]
        o = int(np.argmin(vals)); gains[k] = vals[o]; newg[k] = opts[o]
    order = np.argsort(gains); nimp = int((gains < -1e-15).sum())
    improved = False
    while nimp > 0:
        nt = max(1, int(frac * nimp)); trial = g.copy(); trial[order[:nt]] = newg[order[:nt]]
        W2 = build(sym, prs, trial, m, S, lv); F2, G2 = evalgrad(W2, m)
        if F2 < best:
            g, W, F, G, best = trial, W2, F2, G2, F2; improved = True; frac = min(0.5, frac * 1.5); break
        frac /= 3
        if nt == 1: break
        if time.time() - t0 > T: break
    # level gradient step (dF/dlevel via chain rule on rep rows; relative scale only)
    dl = np.zeros(3)
    for k, (i, j) in enumerate(prs):
        Gr = G[i, m*j:m*j+m]; dd = (-np.arange(m)) % m
        if g[k] < 0: dl[0] += Gr.sum(); continue
        on = np.isin((dd - g[k]) % m, S)
        if isP[k]: dl[1] += Gr[on].sum()
        else: dl[2] += Gr[~on].sum()
    step = 0.02 / (np.abs(dl).max() + 1e-300)
    for _ in range(3):
        lv2 = np.clip(lv - step * dl, 0, 1)
        W2 = build(sym, prs, g, m, S, lv2); F2, G2 = evalgrad(W2, m)
        if F2 < best:
            lv, W, F, G, best = lv2, W2, F2, G2, F2; improved = True; break
        step /= 4
    rec = dict(it=it, m=m, F=best, lv=lv.tolist(), inactive=int((g < 0).sum()), frac=frac, t=time.time() - t0)
    print(json.dumps(rec), flush=True); log.write(json.dumps(rec) + "\n"); log.flush()
    if not improved and frac < 1e-3: break
json.dump(dict(m=m, S=S, F=best, lv=lv.tolist(), g=g.tolist()), open(out / "best.json", "w"))
print("final", m, best)
