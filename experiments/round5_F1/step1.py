"""Step 1: B192 continuous optimum, pure-lift control A* (support = B192 fractional),
marginal opening test for every 0/1 entry: rate |dPhi/dA_e| vs first-order slack g_e."""
import sys, json, time, numpy as np
sys.path.insert(0, 'experiments/round5_F1')
from core import *
from scipy.optimize import minimize
out = sys.argv[1]; tl = float(sys.argv[2]) if len(sys.argv) > 2 else 150
ty, zc, orb = labels()
f = lambda v: Fdens_root(b192(v[0], v[1], ty, zc))
r = minimize(f, [0.779181, 0.534265], method='Nelder-Mead', options={'xatol': 1e-9, 'fatol': 1e-16, 'maxiter': 300})
p, h = map(float, r.x); F0 = float(r.fun); print('B192 opt', p, h, repr(F0), flush=True)
W = b192(p, h, ty, zc); fr = (W > 0) & (W < 1)
L = Lift(W, fr)
c = W * (1 - W) * fr
_, G3, _, _ = L.val_grad(c, True)
A0 = -L.m * np.sign(G3)
# scale search
ts = np.linspace(-1, 1, 41); vals = [L.val_grad(t * A0, False)[0] for t in ts]
A0 = ts[int(np.argmin(vals))] * A0
A, fA = optimize_A(L, A0, tlimit=tl, tag='pure')
fA, G, a3, a4 = L.val_grad(A, True)
print('pure lift', fA, a3, a4, 'sat', float(np.mean(np.abs(A[fr]) >= L.m[fr] - 1e-12)), flush=True)
np.save(out + '/A_pure.npy', A)
t0 = time.time(); Gf = gradF(W); print('gradF', time.time() - t0, flush=True)
np.save(out + '/gradF.npy', Gf); np.save(out + '/Gphi.npy', G)
zo = (~fr); np.fill_diagonal(zo, False)
# slack: cost per unit move into interior (W=1 -> decrease, W=0 -> increase)
slack = np.where(W >= 1, -Gf, Gf)
rate = np.abs(G)
net = rate - slack
rows = []
for T in 'DZXPH':
    for cc in range(3):
        sel = zo & (ty == T) & (zc == cc)
        if sel.sum() == 0: continue
        rows.append(dict(type=T, zc=cc, level=float(W[sel][0]), count=int(sel.sum()),
                         slack_mean=float(slack[sel].mean()), slack_min=float(slack[sel].min()),
                         rate_mean=float(rate[sel].mean()), rate_max=float(rate[sel].max()),
                         net_max=float(net[sel].max())))
        print(rows[-1], flush=True)
# per-orbital
orows = []
for o in np.unique(orb[zo]):
    sel = zo & (orb == o)
    orows.append(dict(orb=int(o), type=str(ty[sel][0]), zc=int(zc[sel][0]), count=int(sel.sum()),
                      slack=float(slack[sel].mean()), rate_mean=float(rate[sel].mean()), rate_max=float(rate[sel].max())))
orows.sort(key=lambda d: d['slack'] - d['rate_max'])
print('best orbitals by slack - rate_max:'); [print(o) for o in orows[:10]]
print('global max net (rate-slack) over 0/1 entries', float(net[zo].max()), 'min slack', float(slack[zo].min()))
json.dump(dict(p=p, h=h, F0=F0, pure_delta=fA, T3=a3, T4=a4, levels=rows, orbitals=orows[:40]), open(out + '/step1.json', 'w'), indent=1)
