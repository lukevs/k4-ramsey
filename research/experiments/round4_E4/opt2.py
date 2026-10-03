"""Fast orbital optimiser on one G/K class with optional warm start from a coarser class.
  opt2.py OUT --cls CI [--from-cls CJ --from-x X.npy] [--starts N] [--sigma s] [--budget sec]
"""
import argparse, json, os, sys, time
import numpy as np
from scipy.optimize import minimize
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from coset_action import (Base, CosetAction, density_grad_fast, orbit_reps, projection, PARENT)

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--cls", type=int, required=True)
ap.add_argument("--from-cls", type=int, default=-1); ap.add_argument("--from-x", default="")
ap.add_argument("--starts", type=int, default=2); ap.add_argument("--sigma", type=float, default=0.03)
ap.add_argument("--seed", type=int, default=7); ap.add_argument("--maxiter", type=int, default=5000)
ap.add_argument("--budget", type=float, default=520)
ap.add_argument("--from-within", type=int, default=-1)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True); T0 = time.time()
b = Base(); classes = json.load(open(os.path.join(HERE, "subgroup_classes.json")))
Kf = classes[a.cls]
if a.from_cls >= 0:
    Kc = set(classes[a.from_cls]); ok = None
    if a.from_within >= 0:  # coarse class was itself run as a conjugate inside from_within
        W0 = set(classes[a.from_within])
        for h in range(len(b.H)):
            S = set(int(b.mul[b.mul[h][s]][b.hinv[h]]) for s in Kc)
            if S <= W0: Kc = S; break
    KcList = sorted(Kc)
    for h in range(len(b.H)):
        S = sorted(int(b.mul[b.mul[h][s]][b.hinv[h]]) for s in Kf)
        if set(S) <= Kc: ok = S; break
    assert ok is not None, "no conjugate contained"; Kf = ok
A = CosetAction(b, Kf).build(); A.verify_invariance()
reps, cnt = orbit_reps(A); rep_pid = A.pid[np.arange(A.norb)]
# row0[reps[o]] should equal pid[o]
assert np.array_equal(A.row0[reps], rep_pid)
fun = lambda x: density_grad_fast(x[A.P], reps, cnt, rep_pid, A.npar)
if a.from_cls >= 0:
    C = CosetAction(b, KcList).build()
    xc = np.load(a.from_x); pr = projection(A, C)
    x0 = np.zeros(A.npar)
    for Q in range(A.n): x0[A.row0[Q]] = xc[C.row0[pr[Q]]]
    assert np.allclose(x0[A.P], xc[C.P][np.ix_(pr, pr)])
else:
    par = np.array(json.loads(PARENT.read_text())["red_probability_numerators"]) / 65536
    pr = np.arange(A.n) // A.m; x0 = np.zeros(A.npar)
    for Q in range(A.n): x0[A.row0[Q]] = par[0][pr[Q]]
f0, g0 = fun(x0)
print(f"class {a.cls} |K|={len(classes[a.cls])} n={A.n} params={A.npar} start f={f0:.15f} ({time.time()-T0:.0f}s)", flush=True)
rng = np.random.default_rng(a.seed)
frac = (x0 > 1e-9) & (x0 < 1 - 1e-9)
starts = []
for s in range(a.starts):
    x = x0.copy(); x[frac] = np.clip(x[frac] + rng.normal(0, a.sigma, frac.sum()), 0, 1); starts.append((f"frac{s}", x))
best = (f0, x0)
for name, xs in starts:
    if time.time() - T0 > a.budget: break
    r = minimize(fun, xs, jac=True, method="L-BFGS-B", bounds=[(0, 1)] * A.npar,
                 options={"maxiter": a.maxiter, "ftol": 1e-17, "gtol": 1e-13})
    print(name, f"{r.fun:.15f}", r.nit, r.message, f"{time.time()-T0:.0f}s", flush=True)
    if r.fun < best[0]:
        best = (float(r.fun), r.x); np.save(os.path.join(a.out, "best_x.npy"), r.x)
        json.dump({"cls": a.cls, "K_order": len(classes[a.cls]), "n": A.n, "params": int(A.npar),
                   "f": best[0], "start": name, "from_cls": a.from_cls, "from_x": a.from_x},
                  open(os.path.join(a.out, "summary.json"), "w"), indent=1)
print("best", best[0])
