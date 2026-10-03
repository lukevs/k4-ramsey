import json, numpy as np, time, sys
from scipy.optimize import minimize
from base import base, Fval, rootedK4e
t0 = time.time()
f = lambda v: Fval(base(v[0], v[1])[0])
r = minimize(f, [0.779181, 0.534265], method='Nelder-Mead', options={'xatol':1e-9,'fatol':1e-15})
p, h = r.x; F0 = r.fun
print('opt p,h,F', p, h, repr(F0), time.time()-t0)
W, typ, cls = base(p, h); n = 192; Q = 1 - W
G = 12 * (rootedK4e(W) - rootedK4e(Q)) / n**4   # dF/d(W_uv=W_vu) jointly
# FD check
u, v = 0, 20; e = 1e-6; W2 = W.copy(); W2[u, v] += e; W2[v, u] += e
print('FD check', (Fval(W2) - F0)/e, G[u, v], typ[u, v], cls[u, v], W[u, v])
out = {'p': p, 'h': h, 'F': F0, 'orbitals': []}
for T in 'DZXPH':
    for c in range(3):
        m = (typ == T) & (cls == c); np.fill_diagonal(m, False)
        if not m.any(): continue
        vals = W[m]; g = G[m]
        # level derivative: moving all entries of the orbital by dL changes F by sum over unordered pairs of G
        dL = g.sum()/2
        lev = float(vals.mean())
        feas = 'free' if 0 < lev < 1 else ('up' if lev == 0 else 'down')
        slack = dL if lev == 0 else (-dL if lev == 1 else dL)
        out['orbitals'].append(dict(type=T, cls=['0', 'S', 'off'][c], level=lev, npairs_per_vertex=float(m.sum()/n),
            grad_per_entry=float(g.mean()), grad_spread=float(g.max()-g.min()), dF_dlevel=float(dL), feasible=feas, slack=float(slack)))
        print(out['orbitals'][-1])
sig = 1 - 2*W
ev = np.linalg.eigvalsh(sig)/n
vals, cnt = np.unique(np.round(ev, 9), return_counts=True)
out['sigma_spectrum'] = [[float(a), int(b)] for a, b in zip(vals, cnt)]
print('sigma spectrum', out['sigma_spectrum'])
evW = np.linalg.eigvalsh(W)/n
vals, cnt = np.unique(np.round(evW, 9), return_counts=True)
out['W_spectrum'] = [[float(a), int(b)] for a, b in zip(vals, cnt)]
fr = (W > 0) & (W < 1)
out['frac_entries'] = int(fr.sum()); out['frac_P'] = int((fr & (typ == 'P')).sum()); out['frac_H'] = int((fr & (typ == 'H')).sum())
A = fr.astype(float)
vals, cnt = np.unique(np.round(np.linalg.eigvalsh(A), 6), return_counts=True)
out['frac_graph_spectrum'] = [[float(a), int(b)] for a, b in zip(vals, cnt)]
print('frac', out['frac_entries'], out['frac_P'], out['frac_H'], out['frac_graph_spectrum'])
out['edge_density_red'] = float(W.mean()); out['tK4_red'] = float(np.einsum('ab,ac,ad,bc,bd,cd->', W, W, W, W, W, W, optimize=True)/n**4)
out['tK4_blue'] = F0 - out['tK4_red']
print('balance', out['edge_density_red'], out['tK4_red'], out['tK4_blue'])
json.dump(out, open(sys.argv[1] + '/char.json', 'w'), indent=1)
np.save(sys.argv[1] + '/W.npy', W); np.save(sys.argv[1] + '/typ.npy', typ); np.save(sys.argv[1] + '/G.npy', G)
print('time', time.time()-t0)
