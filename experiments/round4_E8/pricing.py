import json, sys, time, numpy as np
from scipy.optimize import minimize
rng = np.random.default_rng(int(sys.argv[2]) if len(sys.argv) > 2 else 0)
d = json.load(open(sys.argv[1]))
den = d["edge_probability_denominator"]
A = np.array(d["red_probability_numerators"], dtype=float) / den
bw = np.array(d["block_weights"], float); m = bw / bw.sum()
n = len(m); B = 1 - A

def parts(r):
    u = m * r; v = m * (1 - r)
    Mu = A * (A @ (u[:, None] * A)); Mv = B * (B @ (v[:, None] * B))
    gu = Mu @ u; gv = Mv @ v
    return u @ gu + v @ gv, 3 * m * (gu - gv)

def Fval(A, m):
    return sum(m[i] * (lambda u, v: u @ (A*(A@(u[:,None]*A))) @ u + v @ ((1-A)*((1-A)@(v[:,None]*(1-A)))) @ v)(m*A[i], m*(1-A[i])) for i in range(len(m)))

# tiny validation: literal extra class with brute-force 4-tuple count
def brute(A, m):
    n = len(m); t = 0.0
    import itertools
    for q in itertools.product(range(n), repeat=4):
        w = np.prod([m[x] for x in q]); red = blue = 1.0
        for a in range(4):
            for b in range(a+1, 4):
                red *= A[q[a], q[b]]; blue *= 1 - A[q[a], q[b]]
        t += w * (red + blue)
    return t
k = 4; At = rng.random((k, k)); At = (At + At.T) / 2; mt = rng.random(k); mt /= mt.sum()
F0 = brute(At, mt); r = rng.random(k)
mA, mm = A, m
A, B, m = At, 1 - At, mt
Rr, _ = parts(r)
eps = 1e-5; A2 = np.zeros((k+1, k+1)); A2[:k,:k] = At; A2[k,:k] = r; A2[:k,k] = r; A2[k,k] = 0.3
m2 = np.append(mt*(1-eps), eps)
print("validate: numeric dF/deps", (brute(A2, m2) - F0)/eps, "formula 4(R-F)", 4*(Rr-F0), "F via avg R", Fval(At, mt), F0)
A, B, m = mA, 1 - mA, mm

t0 = time.time()
Rows = np.array([parts(A[i])[0] for i in range(n)])
F = m @ Rows
print("F", F, "R(rows) min/max dev", (Rows - F).min(), (Rows - F).max(), "time", time.time() - t0, flush=True)

def f(r):
    v, g = parts(r); return v, g
best = (np.inf, None)
starts = []
idx = rng.choice(n, 12, replace=False)
for i in idx: starts.append(("row%d" % i, A[i].copy()))
for i in idx[:4]: starts.append(("rowpert%d" % i, np.clip(A[i] + 0.2*rng.standard_normal(n), 0, 1)))
for i in idx[:4]: starts.append(("round%d" % i, np.round(A[i])))
for i in idx[:4]: starts.append(("flip%d" % i, 1 - A[i]))
for s in range(6): starts.append(("rand%d" % s, rng.random(n)))
for s in range(3): starts.append(("half%d" % s, 0.5 + 0.01*rng.standard_normal(n)))
for s in range(3): starts.append(("mix%d" % s, np.clip(0.5*A[rng.integers(n)] + 0.5*A[rng.integers(n)], 0, 1)))
for name, r0 in starts:
    if time.time() - t0 > 480: break
    res = minimize(f, r0, jac=True, method="L-BFGS-B", bounds=[(0, 1)]*n, options=dict(maxiter=3000, ftol=1e-15, gtol=1e-12))
    dist = np.abs(A - res.x).max(axis=1).min()
    print(f"{name}: R0-F={f(r0)[0]-F:.3e} Rmin-F={res.fun-F:.3e} it={res.nit} Linf-to-nearest-row={dist:.3e} frac-interior={np.mean((res.x>1e-9)&(res.x<1-1e-9)):.3f}", flush=True)
    if res.fun < best[0]: best = (res.fun, res.x)
print("BEST R-F", best[0] - F)
np.save(sys.argv[3] if len(sys.argv) > 3 else "best_r.npy", best[1])
