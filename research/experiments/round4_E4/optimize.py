"""Optimise orbital probabilities of G/K kernels. Usage:
  optimize.py OUTDIR [--orders 240,120,...] [--starts N] [--seed S] [--maxn 1920]
"""
import argparse, json, os, sys, time
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coset_action import Base, CosetAction, density_grad, PARENT

ap = argparse.ArgumentParser()
ap.add_argument("out"); ap.add_argument("--orders", default="240,120,60,48,40,24")
ap.add_argument("--starts", type=int, default=3); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--maxiter", type=int, default=400); ap.add_argument("--budget", type=float, default=500)
ap.add_argument("--only", type=int, default=-1)
a = ap.parse_args()
os.makedirs(a.out, exist_ok=True)
T0 = time.time()
b = Base()
classes = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "subgroup_classes.json")))
orders = [int(x) for x in a.orders.split(",")]
par = np.array(json.loads(PARENT.read_text())["red_probability_numerators"]) / 65536
rng = np.random.default_rng(a.seed)
results = []
best_overall = (1.0, None)
for ci, K in enumerate(classes):
    if len(K) not in orders or (a.only >= 0 and ci != a.only): continue
    if time.time() - T0 > a.budget: break
    t1 = time.time()
    A = CosetAction(b, K).build(); A.verify_invariance()
    # pullback start: param value = parent value on projected pair (base, Q)
    x0 = np.zeros(A.npar)
    proj = np.arange(A.n) // A.m
    for Q in range(A.n): x0[A.row0[Q]] = par[0][proj[Q]]
    assert np.allclose(x0[A.P], par[np.ix_(proj, proj)])
    fun = lambda x: density_grad(x[A.P], A.row0, A.npar)
    f0, g0 = fun(x0)
    frac = (x0 > 0) & (x0 < 1)
    rec = {"class": ci, "K_order": len(K), "n": A.n, "params": int(A.npar), "pullback_f": f0,
           "fractional_params": int(frac.sum()), "runs": []}
    starts = [("pullback", x0)]
    for s in range(a.starts):
        x = x0.copy(); x[frac] = np.clip(x[frac] + rng.normal(0, 0.05, frac.sum()), 0, 1)
        starts.append((f"frac-perturb{s}", x))
    for s in range(a.starts):
        x = x0.copy(); x = np.clip(x + rng.normal(0, 0.08, A.npar) * (rng.random(A.npar) < 0.5), 0, 1)
        starts.append((f"all-perturb{s}", x))
    for name, xs in starts:
        if time.time() - T0 > a.budget: break
        r = minimize(fun, xs, jac=True, method="L-BFGS-B", bounds=[(0, 1)] * A.npar,
                     options={"maxiter": a.maxiter, "ftol": 1e-16, "gtol": 1e-12})
        rec["runs"].append({"start": name, "f": float(r.fun), "nit": int(r.nit)})
        print(ci, len(K), A.n, A.npar, name, f"{r.fun:.15f}", r.nit, f"{time.time()-T0:.0f}s", flush=True)
        if r.fun < best_overall[0]:
            best_overall = (float(r.fun), {"class": ci, "x": r.x.tolist(), "start": name})
            np.save(os.path.join(a.out, "best_x.npy"), r.x)
    rec["seconds"] = time.time() - t1
    results.append(rec)
    json.dump({"results": results, "best_f": best_overall[0],
               "best": best_overall[1]}, open(os.path.join(a.out, "summary.json"), "w"), indent=1)
print("best", best_overall[0])
