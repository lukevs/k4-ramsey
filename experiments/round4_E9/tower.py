"""Z2 voltage tower on top of the Z5 lift (C): W'_{(u,s),(v,t)} = W_uv + eps*D_uv*(-1)^{s+t}.
Character averaging kills eps^1 and eps^2 terms; the eps^3 term is
T = (4/N^4) sum_{ijk} D_ij D_ik D_jk (sum_l W_il W_jl W_kl - (1-W)_il (1-W)_jl (1-W)_kl) (red minus blue).
usage: tower.py outdir [eps]  -- computes T for D = fractional mask and (optionally) exact tower value at +-eps."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lift import load_base, pairs, build, evalgrad
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
sym, ph = load_base(); prs = pairs(sym); m = 5
g = np.array([ph[f"{i},{j}"] for i, j in prs])
W = build(sym, prs, g, m, [1, 4], (7/9, 4/9, 8/9)); N = len(W)
D = ((W > 1e-12) & (W < 1 - 1e-12)).astype(float)
def cubic(D):
    t = 0.0
    for l in range(0, N, m):   # Z5-shift invariance of W and D
        for U, sgn in ((W, 1.0), (1 - W, -1.0)):
            s = np.sqrt(U[:, l]); X = s[:, None] * D * s[None, :]
            t += sgn * m * np.einsum('ij,ji->', X @ X, X)
    return 4 * t / N**4
t0 = time.time(); T = cubic(D); print("T(mask)", T, time.time() - t0, flush=True)
rec = dict(T_mask=T)
if len(sys.argv) > 2:
    eps = float(sys.argv[2]) * (1 if T < 0 else -1)
    F0, _ = evalgrad(W, m, False)
    Wt = np.kron(np.ones((2, 2)), W) + eps * np.kron(np.array([[1, -1], [-1, 1]]), D)
    # reorder not needed: evalgrad stride m uses rep rows 0,m,..; tower invariant under Z5 shift within each layer
    Ft, _ = evalgrad(Wt, m, False)
    rec.update(F0=F0, eps=eps, F_tower=Ft, delta=Ft - F0, pred=eps**3 * T)
    print(rec, time.time() - t0, flush=True)
json.dump(rec, open(out / "tower.json", "w"))
