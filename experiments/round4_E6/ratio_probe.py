import sys, time, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, 'experiments/round4_E6')
from sprofile import profile
from partner import unpack
rng = np.random.default_rng(11); t0 = time.time()
for k in [6, 8, 10, 12]:
    best = (9, None)
    for r in range(25):
        if time.time() - t0 > 420: break
        x0 = np.concatenate([rng.normal(0, .5, k), rng.normal(0, 2.5, k*(k+1)//2)])
        f = lambda x: (lambda p: (1 - p[5]) / max(1 - p[3], 1e-9))(profile(*unpack(x, k)))
        res = minimize(f, x0, method='L-BFGS-B', options={'maxiter': 1500})
        if res.fun < best[0]: best = (res.fun, res.x)
    w, S = unpack(best[1], k); p = profile(w, S)
    print(k, 'min (1-K4)/(1-C4)', best[0], 'K4', p[5], 'C4', p[3], 'w', np.round(w, 3).tolist(), flush=True)
