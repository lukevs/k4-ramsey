"""Probe the inequality t(K4,s) <= t(C4,s) for symmetric step kernels |s|<=1 (would make the
XOR-partner negative near-global, since the incumbent needs (1-b_K)/(1-b_C) < 3a_C/|a_K| ~ 0.325)."""
import sys, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, 'experiments/round4_E6')
from sprofile import profile
from partner import unpack
rng = np.random.default_rng(5); worst = -9
for k in [2, 3, 4, 5, 6, 8]:
    for r in range(15):
        x0 = np.concatenate([rng.normal(0, .5, k), rng.normal(0, 2, k*(k+1)//2)])
        def f(x):
            p = profile(*unpack(x, k)); return -(p[5] - p[3])
        res = minimize(f, x0, method='L-BFGS-B', options={'maxiter': 2000})
        # ratio test away from trivial
        p = profile(*unpack(res.x, k)); worst = max(worst, -res.fun)
    print(k, 'max t(K4)-t(C4) found', worst, flush=True)
# ratio (1-K)/(1-C) minimum
best = 9
for k in [2, 3, 4, 6]:
    for r in range(15):
        x0 = np.concatenate([rng.normal(0, .5, k), rng.normal(0, 2, k*(k+1)//2)])
        def f(x):
            p = profile(*unpack(x, k)); return (1 - p[5]) / max(1 - p[3], 1e-9)
        res = minimize(f, x0, method='L-BFGS-B', options={'maxiter': 2000}); best = min(best, res.fun)
    print(k, 'min (1-K4)/(1-C4)', best, flush=True)
