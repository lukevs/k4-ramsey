import sys, json, time; sys.path.insert(0, 'research/experiments/round4_E12')
import numpy as np
from homotopy import load_sym, fam, F, opt_full
out = open(sys.argv[1], 'w'); sym = load_sym(); N = 192; T0 = time.time(); TL = float(sys.argv[2])
rng = np.random.default_rng(1)
tur = (np.arange(N)[:, None] % 3 != np.arange(N)[None, :] % 3).astype(float)
noise = rng.normal(0, .02, (N, N)); noise = (noise + noise.T) / 2
tur = np.clip(tur * .9 + .05 + noise, 0, 1); np.fill_diagonal(tur, 0)
seeds = {"b192": fam(sym, [0, 1, 32/41, 22/41]), "swap": fam(sym, [0, 1, 22/41, 32/41]), "turan3": tur}
paths = {"up": list(np.linspace(1, 2.5, 11)[1:]) + list(np.linspace(2.5, 1, 11)[1:]),
         "down": list(np.linspace(1, .6, 11)[1:]) + list(np.linspace(.6, 1, 11)[1:])}
IT = 4; POL = 20
def sig(W):
    return dict(n0=int((W < 1e-9).sum()), n1=int((W > 1 - 1e-9).sum()), frac=int(((W > 1e-9) & (W < 1 - 1e-9)).sum()))
for sn, s in seeds.items():
    for pn, lams in list(paths.items()) + [("control", [1.0] * 20)]:
        if time.time() - T0 > TL: break
        W = s.copy(); tot = 0
        for lam in lams:
            W, Fv, r, b, ne = opt_full(W, lam, IT); tot += ne
        W, Fv, r, b, ne = opt_full(W, 1.0, POL); tot += ne
        rec = dict(seed=sn, path=pn, F=Fv, red=r, blue=b, evals=tot, dist_seed=float(np.abs(W - s).mean()), t=time.time() - T0, **sig(W))
        print(rec, flush=True); out.write(json.dumps(rec) + "\n"); np.save(sys.argv[1] + f".{sn}.{pn}.npy", W)
