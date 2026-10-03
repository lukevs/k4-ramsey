"""Power-iterate the eps^3 form direction D <- grad T(D) (masked, normalised), then exact tower eval at given eps list."""
import json, sys, time
import numpy as np
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from lift import load_base, pairs, build, evalgrad
out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
epss = [float(e) for e in sys.argv[2].split(',')]; iters = int(sys.argv[3])
sym, ph = load_base(); prs = pairs(sym); m = 5
g = np.array([ph[f"{i},{j}"] for i, j in prs])
W = build(sym, prs, g, m, [1, 4], (7/9, 4/9, 8/9)); N = len(W)
mask = ((W > 1e-12) & (W < 1 - 1e-12)).astype(float)
perm = np.array([(k // m) * m + (k + 1) % m for k in range(N)])
def cubic_grad(D):
    t = 0.0; G = np.zeros((N, N))
    for l in range(0, N, m):
        for U, sgn in ((W, 1.0), (1 - W, -1.0)):
            s = np.sqrt(U[:, l]); X = s[:, None] * D * s[None, :]; X2 = X @ X
            t += sgn * m * np.einsum('ij,ji->', X2, X)
            G += sgn * m * 3 * s[:, None] * X2 * s[None, :]
    Gs = G.copy(); P = np.arange(N)
    for _ in range(m - 1):
        P = perm[P]; Gs[np.ix_(P, P)] += G
    return 4 * t / N**4, 4 * (Gs / m) / N**4
D = mask.copy(); T, G = cubic_grad(D); hist = [T]
for _ in range(iters):
    D = mask * G; D = (D + D.T) / 2; D /= np.abs(D).max()
    T, G = cubic_grad(D); hist.append(T); print("T", T, flush=True)
F0, _ = evalgrad(W, m, False); rec = dict(F0=F0, T_hist=hist, evals=[])
for e in epss:
    eps = e * (1 if T < 0 else -1)
    Wt = np.kron(np.ones((2, 2)), W) + eps * np.kron(np.array([[1, -1], [-1, 1]]), D)
    assert Wt.min() >= 0 and Wt.max() <= 1
    Ft, _ = evalgrad(Wt, m, False)
    rec["evals"].append(dict(eps=eps, F=Ft, delta=Ft - F0, pred3=eps**3 * T)); print(rec["evals"][-1], flush=True)
    json.dump(rec, open(out / "tower.json", "w"))
np.save(out / "D.npy", D)
