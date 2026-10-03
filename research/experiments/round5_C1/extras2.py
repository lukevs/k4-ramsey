import numpy as np, json, sys
from base import base
from expand import expansion
from scipy.optimize import minimize
p, h = 0.7791808266653855, 0.5342650498652971
W, typ, cls = base(p, h); n = 192; Q = 1 - W
fr = (W > 0) & (W < 1); a = np.where(fr, np.minimum(W, Q), 0.0)
nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
G = np.load('../../../reports/round5-C1-char-001/G.npy')
out = {}
S2 = np.array([[1., -1.], [-1., 1.]])  # s(x)s(y), s=+-1, E s = 0
def r1(lP, lH):
    D = {}
    for u in range(n):
        for v in nb[u]:
            D[(u, v)] = a[u, v]*(-lH if typ[u, v] == 'H' else lP)*S2
    return expansion(W, D, 2)
res = minimize(lambda v: sum(r1(*np.clip(v, 0, 1))), [0.6, 0.6], method='Nelder-Mead', options={'maxiter': 60, 'xatol': 1e-4})
lP, lH = np.clip(res.x, 0, 1); T = r1(lP, lH)
out['rank1_sign_lift_B192'] = dict(lamP=float(lP), lamH=float(lH), T3=T[0], T4=T[1], T5=T[2], T6=T[3], dF=float(sum(T)))
print(out['rank1_sign_lift_B192'], flush=True)
u = 0; N0 = nb[u]
M = np.array([[12*((W[v, w]*W[u]*W[v]*W[w]).sum() + (Q[v, w]*Q[u]*Q[v]*Q[w]).sum())/n**4 for w in N0] for v in N0])
out['row_term_M0_eigs'] = [float(x) for x in np.linalg.eigvalsh(M)]
print('row-term M_0 eigs', out['row_term_M0_eigs'], flush=True)
c3 = lambda x, y, z: abs((W[x]*W[y]*W[z] - Q[x]*Q[y]*Q[z]).sum())
for T_ in 'DZXH':
    for c in range(3):
        m = (typ == T_) & (cls == c) & ~fr; np.fill_diagonal(m, False)
        if not m.any(): continue
        slack = abs(G[m].sum()/2)
        r3 = r4 = 0.0
        for x, y in zip(*np.nonzero(m)):
            for z in nb[x]:
                if fr[z, y]: r3 += 3*4*c3(x, y, z)*a[y, z]*a[z, x]/n**4
            for z in nb[y]:
                for w in nb[z]:
                    if fr[w, x]: r4 += 4*3*(W[x, z]*W[y, w] + Q[x, z]*Q[y, w])*a[y, z]*a[z, w]*a[w, x]/n**4
        # per unit mean shift d of every entry of the orbital: cost slack*d; gain <= (r3+r4)*d/2 (unordered pairs counted twice)
        out.setdefault('opening', []).append(dict(type=T_, cls=['0', 'S', 'off'][c], slack=float(slack), cubic_rate=r3/2, quartic_rate=r4/2))
        print(out['opening'][-1], flush=True)
json.dump(out, open(sys.argv[1] + '/extras.json', 'w'), indent=1)
