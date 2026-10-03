"""Tower direction D = alpha_type on fractional entries of (C) by type (p0,x,y); scan sign patterns of T, eval best."""
import json, sys, itertools
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lift import load_base, pairs, build, evalgrad
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True); eps0 = float(sys.argv[2])
sym, ph = load_base(); prs = pairs(sym); m = 5
g = np.array([ph[f"{i},{j}"] for i, j in prs])
W = build(sym, prs, g, m, [1, 4], (7/9, 4/9, 8/9)); N = len(W)
masks = [np.isclose(W, v).astype(float) for v in (7/9, 4/9, 8/9)]
def cubic(D):
    t = 0.0
    for l in range(0, N, m):
        for U, sgn in ((W, 1.0), (1 - W, -1.0)):
            s = np.sqrt(U[:, l]); X = s[:, None] * D * s[None, :]
            t += sgn * m * np.einsum('ij,ji->', X @ X, X)
    return 4 * t / N**4
res = []; AMP = [float(v) for v in sys.argv[3].split(",")]
for a in [tuple(AMP)]:
    D = sum(ai * mk for ai, mk in zip(a, masks)); T = cubic(D); res.append((abs(T), a, T)); print(a, T, flush=True)
_, a, T = max(res); D = sum(ai * mk for ai, mk in zip(a, masks))
eps = eps0 * (1 if T < 0 else -1)  # amplitudes carried by alpha
Wt = np.kron(np.ones((2, 2)), W) + eps * np.kron(np.array([[1, -1], [-1, 1]]), D)
assert Wt.min() >= 0 and Wt.max() <= 1
F0, _ = evalgrad(W, m, False); Ft, _ = evalgrad(Wt, m, False)
rec = dict(scan=[(list(r[1]), r[2]) for r in res], alpha=list(a), eps=eps, F0=F0, F=Ft, delta=Ft - F0, pred3=eps**3 * T)
print(rec); json.dump(rec, open(out / "tower.json", "w"))
