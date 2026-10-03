import sys, json, time; sys.path.insert(0, 'experiments/round4_E12')
import numpy as np
from homotopy import load_sym, fam, F, opt_full
src = sys.argv[1]; out = open(sys.argv[2], 'w'); T0 = time.time()
def sig(W):
    return dict(n0=int((W < 1e-9).sum()), n1=int((W > 1 - 1e-9).sum()), frac=int(((W > 1e-9) & (W < 1 - 1e-9)).sum()))
for tag in ["b192.up", "swap.down"]:
    W = np.load(f"{src}.{tag}.npy"); W, Fv, r, b, ne = opt_full(W, 1.0, 300)
    rec = dict(run="polish", tag=tag, F=Fv, red=r, blue=b, evals=ne, t=time.time() - T0, **sig(W)); print(rec, flush=True); out.write(json.dumps(rec) + "\n")
sym = load_sym(); rng = np.random.default_rng(7); n = rng.normal(0, .01, (192, 192)); n = (n + n.T) / 2
S = np.clip(fam(sym, [0, 1, .7792, .5343]) + n, 0, 1); np.fill_diagonal(S, 0)
for pn, lams in [("up", list(np.linspace(1, 2.5, 11)[1:]) + list(np.linspace(2.5, 1, 11)[1:])), ("control", [1.0] * 20)]:
    W = S.copy(); tot = 0
    for lam in lams:
        W, Fv, r, b, ne = opt_full(W, lam, 4); tot += ne
    W, Fv, r, b, ne = opt_full(W, 1.0, 150); tot += ne
    rec = dict(run="noisy", path=pn, F=Fv, red=r, blue=b, evals=tot, t=time.time() - T0, **sig(W)); print(rec, flush=True); out.write(json.dumps(rec) + "\n")
