"""E11: optimise interior levels only (P center, P on S, H center) in the 15-level family."""
import sys, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from multilevel import setup, buildW, base_levels, TY
from family import F
from scipy.optimize import minimize
q, ncls, cl, TT = setup(4)
v0 = np.concatenate([base_levels(0.7791808, 0.5342652)[ty] for ty in TY]).astype(float)
def f(x):
    v = v0.copy(); v[9], v[10], v[12] = x; return F(buildW(v, q, ncls, cl, TT), [0], [12*q])
r = minimize(f, [0.7791808, 0.7791808, 0.5342652], method='Nelder-Mead', options={'xatol':1e-8,'fatol':1e-14,'maxiter':600})
print(repr(f([0.7791808, 0.7791808, 0.5342652])), repr(r.fun), r.x)
