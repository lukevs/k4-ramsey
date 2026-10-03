import numpy as np, json, sys, itertools
from base import base
from scipy.optimize import minimize
p, h = 0.7791808266653855, 0.5342650498652971
W, typ, cls = base(p, h); n = 192; Q = 1 - W
fr = (W > 0) & (W < 1); a = np.where(fr, np.minimum(W, Q), 0.0)
nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
G = np.load('../../../reports/round5-C1-char-001/G.npy')
out = {}
# (1) rank-one sign lift reference: D = eps*lam*a*s(x)s(y), eps_H=-1, eps_P=+1 (all triangles -1)
isH = (typ == 'H')
def r1(lP, lH):
    Dm = np.where(fr, a*np.where(isH, -lH, lP), 0.0)   # moments = products of Dm entries
    T3 = 4*np.einsum('ab,bc,ca,abc->', Dm, Dm, Dm, np.einsum('ad,bd,cd->abc', W, W, W) - np.einsum('ad,bd,cd->abc', Q, Q, Q), optimize=True)/n**4
    D2 = Dm @ Dm
    T4 = 3*(np.einsum('ac,bd,ab,bc,cd,da->', W, W, Dm, Dm, Dm, Dm, optimize=True) + np.einsum('ac,bd,ab,bc,cd,da->', Q, Q, Dm, Dm, Dm, Dm, optimize=True))/n**4
    return T3, T4
res = minimize(lambda v: sum(r1(*np.clip(v, 0, 1))), [0.5, 0.5], method='Nelder-Mead')
lP, lH = np.clip(res.x, 0, 1); T3, T4 = r1(lP, lH)
out['rank1_sign_lift'] = dict(lamP=float(lP), lamH=float(lH), T3=float(T3), T4=float(T4), dF=float(T3+T4))
print(out['rank1_sign_lift'])
# (2) refinement (row-term) second-order check: M_u[v,w] = 12/n^4 sum_d (W_vw W_ud W_vd W_wd + Q...), v,w in N(u)
u = 0; N0 = nb[u]
M = np.zeros((len(N0), len(N0)))
for i, v in enumerate(N0):
    for j, w in enumerate(N0):
        M[i, j] = 12*((W[v, w]*W[u]*W[v]*W[w]).sum() + (Q[v, w]*Q[u]*Q[v]*Q[w]).sum())/n**4
ev = np.linalg.eigvalsh(M)
out['row_term_M0_eigs'] = [float(x) for x in ev]
print('row-term M_0 eigenvalues', ev)
# (3) opening a 0/1 orbital by mean shift d with kernel |D|<=d: linear-in-d box rate of new cubic/quartic/diamond gains
def open_rate(mask):
    # new pair set E1 (entries of mask), existing fractional E0; leading order: exactly one edge from E1 in each term
    b = np.where(mask, 1.0, 0.0)   # per unit d
    A0 = a
    C3 = np.abs(np.einsum('ad,bd,cd->abc', W, W, W) - np.einsum('ad,bd,cd->abc', Q, Q, Q))
    r3 = 4*3*np.einsum('ab,bc,ca,abc->', b, A0, A0, C3, optimize=True)/n**4
    r4 = 3*4*(np.einsum('ac,bd,ab,bc,cd,da->', W, W, b, A0, A0, A0, optimize=True) + np.einsum('ac,bd,ab,bc,cd,da->', Q, Q, b, A0, A0, A0, optimize=True))/n**4
    return r3, r4
for T in 'DZXH':
    for c in range(3):
        m = (typ == T) & (cls == c) & ~fr; np.fill_diagonal(m, False)
        if not m.any(): continue
        slack = abs(G[m].sum()/2)
        r3, r4 = open_rate(m)
        out.setdefault('opening', []).append(dict(type=T, cls=['0','S','off'][c], slack_per_unit_level=float(slack), cubic_box_rate=float(r3), quartic_box_rate=float(r4)))
        print(out['opening'][-1])
json.dump(out, open(sys.argv[1] + '/extras.json', 'w'), indent=1)
