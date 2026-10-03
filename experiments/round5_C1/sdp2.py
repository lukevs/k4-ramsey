"""C1 ceiling: tracial Gram (moment) relaxation of the pure-latent lift problem over B192.
Upper-bounds  -(T3+T4+T5+T6)  over ALL lifts W' = W + D, D supported on fractional pairs,
D_uv(x,y) kernels on a probability space with mean-zero rows, |D_uv| <= min(W_uv, 1-W_uv)."""
import numpy as np, cvxpy as cp, scipy.sparse as sp, json, sys, time, itertools, os
from base import base, Fval
p = float(os.environ.get('P', 0.7791808266653855)); h = float(os.environ.get('H', 0.5342650498652971))
W, typ, cls = base(p, h); n = 192; Q = 1 - W
fr = (W > 0) & (W < 1)
BOX = os.environ.get('BOX', 'asym')  # 'sym': |D|<=min(W,1-W) (old, too strict); 'asym': D in [-W,1-W]
if BOX == 'sym':
    vv = np.where(fr, np.minimum(W, Q)**2, 0.0); MM = np.where(fr, np.minimum(W, Q), 0.0)
else:
    vv = np.where(fr, W*Q, 0.0); MM = np.where(fr, np.maximum(W, Q), 0.0)  # E D^2 <= W(1-W) (Bhatia-Davis), sup|D| <= max
a = MM
nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
USE_T5 = '--noT5' not in sys.argv
LOCALIZE = os.environ.get('LOCALIZE', '0') == '1'
SCHUR = os.environ.get('SCHUR', '0') == '1'
CENTER = os.environ.get('CENTER', '0') == '1'
K4PATH = os.environ.get('K4PATH', '0') == '1'
assert not CENTER or LOCALIZE
# On mean-zero functions D = W-p agrees with W and with -(1-W).
# Both nonnegative kernels have constant row/column sums p and 1-p.
# Schur's bound therefore gives ||D||op <= min(p,1-p), even in the true box.
op2 = np.where(fr, np.minimum(W,Q)**2, 0.0) if SCHUR else vv
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
def dkey(x, y, z, w):
    best = None
    for (u, v) in ((x, y), (y, x)):
        t = u % 16
        k = ('D', tr(u, t), tr(v, t), tuple(sorted((tr(z, t), tr(w, t)))))
        if best is None or k < best: best = k
    return best
box5 = 0.0; box6 = 0.0; k4groups = {}
for x in range(n):
    for y in nb[x]:
        cn = [z for z in nb[x] if fr[z, y]]
        for z in cn:
            for w in cn:
                if z != w and fr[z, w]: box6 += 2*MM[x, y]*MM[z, w]*np.sqrt(vv[x, z]*vv[y, z]*vv[x, w]*vv[y, w])/n**4
                if K4PATH and z != w and fr[z,w]:
                    vertices = (x,y,z,w)
                    key = min(tuple(sorted(tr(v,t % 16) for v in vertices)) for t in vertices)
                    k4groups[key] = k4groups.get(key,0.0)+2/n**4
                box5 += 6*abs(W[z, w] - Q[z, w])*a[x, y]*a[x, z]*a[y, z]*a[x, w]*a[y, w]/n**4
                add(var(dkey(x, y, z, w)), float(os.environ.get("T5W", 1))*6*(W[z, w] - Q[z, w])/n**4)
print('objective vars', len(idx), time.time()-t0)
# Gram blocks
blocks = []
for aa in [s*16 for s in range(12)]:
    for b in range(n):
        words = ([(aa, b)] if fr[aa, b] else []) + [(aa, c, b) for c in nb[aa] if fr[c, b]]
        if not words: continue
        had = [('H', c) for (_, c, _) in words[1:]] if fr[aa, b] else []
        allw = words + had
        d = len(allw); ent = []   # (i,j,varindex) known links
        for i in range(d):
            for j in range(d):
                w1, w2 = allw[i], allw[j]
                if w1[0] != 'H' and w2[0] != 'H':
                    cyc = list(w2) + list(w1[::-1])[1:-1]
                    ent.append((i, j, var(canon(tuple(cyc)))))
                elif w1[0] == 'H' and w2[0] != 'H' and len(w2) == 3:
                    ent.append((i, j, var(dkey(aa, b, w1[1], w2[1])))); ent.append((j, i, var(dkey(aa, b, w1[1], w2[1]))))
        blocks.append((d, ent, allw))
print('blocks', len(blocks), 'max size', max(b[0] for b in blocks), 'vars', len(idx), time.time()-t0)
N = len(idx); z = cp.Variable(N)
cons = []
# length-2 closed walks: s_e <= a_e^2 ; 4-walk diagonal bounds
for key, i in list(idx.items()):
    if len(key) == 2:
        cons.append(z[i] <= vv[key[0], key[1]])
for (d, ent, words) in blocks:
    S = cp.Variable((d, d), symmetric=True)
    cons.append(S >> 0)
    I = [e[0] for e in ent]; J = [e[1] for e in ent]; V = [e[2] for e in ent]
    cons.append(S[I, J] == z[V])
    if LOCALIZE and words[0][0] != 'H' and len(words[0]) == 2:
        # Pointwise D in [-p,1-p]. For path functions s_c(x,y),
        # A=E[ss^T], B=E[D ss^T], C=E[D^2 ss^T].
        # Thus p A+B, (1-p) A-B, and p(1-p)A+(1-2p)B-C
        # are PSD. B contains the diamond moments. This couples their
        # signs and magnitude using the true asymmetric probability box.
        path_i = [i for i,w in enumerate(words) if w[0] != 'H' and len(w) == 3]
        had_i = [i for i,w in enumerate(words) if w[0] == 'H']
        assert len(path_i) == len(had_i)
        if path_i:
            u, v = words[0]
            lev = W[u,v]
            AA = S[np.ix_(path_i,path_i)]
            BB = S[np.ix_(had_i,path_i)]
            CC = S[np.ix_(had_i,had_i)]
            cons.append(BB == BB.T)
            cons.extend([lev*AA+BB >> 0, (1-lev)*AA-BB >> 0,
                         lev*(1-lev)*AA+(1-2*lev)*BB-CC >> 0])
            if CENTER:
                # E[D]=E[s_c]=0; E[D s_c] is the triangle moment.
                # Add the constant feature, forcing triangles, diamonds and
                # path covariances to come from the same probability space.
                ell = len(path_i)
                zero_row = np.zeros((1,ell))
                tri = S[np.ix_([0],path_i)]
                cross = S[np.ix_([0],had_i)]
                A1 = cp.bmat([[np.ones((1,1)),zero_row],[zero_row.T,AA]])
                B1 = cp.bmat([[np.zeros((1,1)),tri],[tri.T,BB]])
                C1 = cp.bmat([[cp.reshape(S[0,0],(1,1),order='C'),cross],[cross.T,CC]])
                cons.extend([lev*A1+B1 >> 0, (1-lev)*A1-B1 >> 0,
                             lev*(1-lev)*A1+(1-2*lev)*B1-C1 >> 0])
                mean = cp.hstack([np.zeros((1,1+ell)),tri])
                cons.append(cp.bmat([[np.ones((1,1)),mean],[mean.T,S]]) >> 0)
    for k, wd in enumerate(words):
        if wd[0] == 'H':
            xx, c, bb = words[0][0], wd[1], words[0][1]
            cons.append(S[k, k] <= MM[xx, bb]**2 * z[idx[canon((xx, c, bb, c))]])
            # |S_c(i,j)| <= sqrt(rowvar_xc(i) rowvar_cb(j)) <= sqrt(v_xc v_cb)  =>  E[D^2 S_c^2] <= v_xc v_cb E[D^2]
            cons.append(S[k, k] <= vv[xx, c]*vv[c, bb] * z[idx[canon((xx, bb))]])
        elif len(wd) == 3:
            x, c, b = wd; qi = idx[canon((x, c, b, c))]
            cons.append(z[qi] <= op2[x, c] * z[idx[canon((c, b))]])
            cons.append(z[qi] <= op2[c, b] * z[idx[canon((x, c))]])
ci = np.zeros(N); 
for k, c in obj.items(): ci[k] = c
expr = ci @ z
if K4PATH:
    # Center both two-edge path functions before applying the opposite
    # edge's operator norm. Their squared L2 masses are at most
    # v_xz v_yz - ||D_xz D_zy||HS^2, which is already a C4 variable.
    k4keys = list(k4groups)
    k4abs = cp.Variable(len(k4keys),nonneg=True)
    for j,vertices in enumerate(k4keys):
        for x,y in itertools.combinations(vertices,2):
            zz,ww = [v for v in vertices if v not in (x,y)]
            rz = vv[x,zz]*vv[y,zz]-z[idx[canon((x,zz,y,zz))]]
            rw = vv[x,ww]*vv[y,ww]-z[idx[canon((x,ww,y,ww))]]
            factor = MM[x,y]*np.sqrt(op2[zz,ww])
            cons.append(cp.bmat([[rz,k4abs[j]/factor],[k4abs[j]/factor,rw]]) >> 0)
    expr -= np.array([k4groups[k] for k in k4keys]) @ k4abs
prob = cp.Problem(cp.Minimize(expr*float(os.environ.get("SCALE", 1))), cons)
print('solving', N, 'vars', time.time()-t0, flush=True)
prob.solve(solver=cp.CLARABEL, verbose=False)
val = prob.value/float(os.environ.get("SCALE", 1))
zz = z.value
T3 = sum(obj[k]*zz[k] for k in obj if len(next(kk for kk, v in idx.items() if v == k)) == 3) if False else None
inv = {v: k for k, v in idx.items()}
T3 = sum(c*zz[k] for k, c in obj.items() if len(inv[k]) == 3)
T4 = sum(c*zz[k] for k, c in obj.items() if len(inv[k]) == 4 and inv[k][0] != 'D')
T5 = sum(c*zz[k] for k, c in obj.items() if inv[k][0] == 'D')
res = dict(status=prob.status, relaxed_min=val, T3=T3, T4=T4, T5=T5,
           box_T6=box6, box_T5=box5, gain_ceiling=-val + (0 if K4PATH else box6),
           time=time.time()-t0)
res['box'] = BOX; res['p'] = p; res['h'] = h; res['F_base'] = Fval(W); res['F_floor'] = res['F_base'] - res['gain_ceiling']
res['localize'] = LOCALIZE
res['schur_operator_bound'] = SCHUR
res['centered_constant_feature'] = CENTER
res['k4_centered_path_bound'] = K4PATH
if K4PATH:
    res['T6_worst'] = -float(np.array([k4groups[k] for k in k4keys]) @ k4abs.value)
    res['k4_moment_classes'] = len(k4keys)
res['max_constraint_violation'] = max(float(np.max(c.violation())) for c in cons)
print(json.dumps(res, indent=1))
json.dump(res, open(sys.argv[1] + '/sdp.json', 'w'), indent=1)
np.save(sys.argv[1] + '/z.npy', zz)
json.dump({str(k): v for k, v in idx.items()}, open(sys.argv[1] + '/idx.json', 'w'))
