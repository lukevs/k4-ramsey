"""C1 ceiling: tracial Gram (moment) relaxation of the pure-latent lift problem over B192.
Upper-bounds  -(T3+T4+T5+T6)  over ALL lifts W' = W + D, D supported on fractional pairs,
D_uv(x,y) kernels on a probability space with mean-zero rows, |D_uv| <= min(W_uv, 1-W_uv)."""
import numpy as np, cvxpy as cp, scipy.sparse as sp, json, sys, time, itertools, os
from base import base, Fval
p = float(os.environ.get('P', 0.7791808266653855)); h = float(os.environ.get('H', 0.5342650498652971))
W, typ, cls = base(p, h); n = 192; Q = 1 - W
fr = (W > 0) & (W < 1); a = np.where(fr, np.minimum(W, Q), 0.0)
nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
USE_T5 = '--noT5' not in sys.argv
def tr(v, t): return (v // 16)*16 + ((v % 16) ^ t)
def canon(walk):
    k = len(walk); best = None
    for seq in (walk, walk[::-1]):
        for r in range(k):
            s = seq[r:] + seq[:r]; t = s[0] % 16
            c = tuple(tr(v, t) for v in s)
            if best is None or c < best: best = c
    return best
idx = {}
def var(key):
    if key not in idx: idx[key] = len(idx)
    return idx[key]
t0 = time.time()
obj = {}  # var -> coefficient
def add(k, c): obj[k] = obj.get(k, 0.0) + c
for x in range(n):
    for y in nb[x]:
        for z in nb[y]:
            if fr[z, x]:
                add(var(canon((x, y, z))), 4*(W[x]*W[y]*W[z] - Q[x]*Q[y]*Q[z]).sum()/n**4)
            for w in nb[z]:
                if fr[w, x]:
                    add(var(canon((x, y, z, w))), 3*(W[x, z]*W[y, w] + Q[x, z]*Q[y, w])/n**4)
print('objective vars', len(idx), time.time()-t0)
# Gram blocks
blocks = []
for aa in [s*16 for s in range(12)]:
    for b in range(n):
        words = ([(aa, b)] if fr[aa, b] else []) + [(aa, c, b) for c in nb[aa] if fr[c, b]]
        if not words: continue
        d = len(words); ent = []
        for i in range(d):
            for j in range(d):
                w1, w2 = words[i], words[j]
                cyc = list(w2) + list(w1[::-1])[1:-1]
                ent.append(var(canon(tuple(cyc))))
        blocks.append((d, ent, words))
print('blocks', len(blocks), 'max size', max(b[0] for b in blocks), 'vars', len(idx), time.time()-t0)
# diamonds (T5 worst case): u >= |moment| with u <= a_xy sqrt(q_z q_w)
dia = {}; box5 = 0.0; box6 = 0.0
for x in range(n):
    for y in nb[x]:
        cn = [z for z in nb[x] if fr[z, y]]
        for z in cn:
            for w in cn:
                if z != w and fr[z, w]: box6 += 2*a[x, y]*a[x, z]*a[y, z]*a[x, w]*a[y, w]*a[z, w]/n**4
                cf = 6*abs(W[z, w] - Q[z, w])/n**4
                box5 += cf*a[x, y]*a[x, z]*a[y, z]*a[x, w]*a[y, w]
                if cf == 0: continue
                qz = var(canon((x, z, y, z))); qw = var(canon((x, w, y, w)))
                key = (min(qz, qw), max(qz, qw), round(a[x, y], 12))
                dia[key] = dia.get(key, 0.0) + cf
print('diamond classes', len(dia))
N = len(idx); z = cp.Variable(N)
cons = []
# length-2 closed walks: s_e <= a_e^2 ; 4-walk diagonal bounds
for key, i in list(idx.items()):
    if len(key) == 2:
        cons.append(z[i] <= a[key[0], key[1]]**2)
for (d, ent, words) in blocks:
    S = cp.Variable((d, d), symmetric=True)
    cons.append(S >> 0)
    cons.append(cp.vec(S, order='C') == z[ent])
    for wd in words:
        if len(wd) == 3:
            x, c, b = wd; qi = idx[canon((x, c, b, c))]
            cons.append(z[qi] <= a[x, c]**2 * z[idx[canon((c, b))]])
            cons.append(z[qi] <= a[c, b]**2 * z[idx[canon((x, c))]])
ci = np.zeros(N); 
for k, c in obj.items(): ci[k] = c
expr = ci @ z
if USE_T5:
    keys = list(dia); u = cp.Variable(len(keys), nonneg=True)
    for j, (qa, qb, ax) in enumerate(keys):
        if qa == qb: cons.append(u[j] <= ax*z[qa])
        else: cons.append(cp.bmat([[z[qa], u[j]/ax], [u[j]/ax, z[qb]]]) >> 0)
    expr = expr - np.array([dia[k] for k in keys]) @ u
prob = cp.Problem(cp.Minimize(expr), cons)
print('solving', N, 'vars', time.time()-t0, flush=True)
prob.solve(solver=cp.CLARABEL, verbose=False)
val = prob.value
zz = z.value
T3 = sum(obj[k]*zz[k] for k in obj if len(next(kk for kk, v in idx.items() if v == k)) == 3) if False else None
inv = {v: k for k, v in idx.items()}
T3 = sum(c*zz[k] for k, c in obj.items() if len(inv[k]) == 3)
T4 = sum(c*zz[k] for k, c in obj.items() if len(inv[k]) == 4)
res = dict(status=prob.status, relaxed_min=val, T3=T3, T4=T4, T5worst=(val - T3 - T4) if USE_T5 else None,
           box_T6=box6, box_T5=box5, gain_ceiling=-val + box6 + (0 if USE_T5 else box5),
           time=time.time()-t0)
res['p'] = p; res['h'] = h; res['F_base'] = Fval(W); res['F_floor'] = res['F_base'] - res['gain_ceiling']
print(json.dumps(res, indent=1))
json.dump(res, open(sys.argv[1] + '/sdp.json', 'w'), indent=1)
np.save(sys.argv[1] + '/z.npy', zz)
json.dump({str(k): v for k, v in idx.items()}, open(sys.argv[1] + '/idx.json', 'w'))
