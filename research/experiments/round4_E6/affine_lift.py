"""Affine-lift / Boolean-combination products (H-R4-E6 extension).
Product graphon on [0,1]x[k]: sigma((x,a),(y,b)) = g_ab + d_ab * sigma1(x,y), |g|+|d|<=1.
Covers XOR (g=0), AND/OR with independent small factor (affine in p1), constant patches.
mono = (1/32) E_{a1..a4} sum_{T subset E(K4)} c_T(a) t(T, sigma1),
c_T = prod_{e in T} d_e * (prod_{e notin T}(1+g_e) +/- prod_{e notin T}(1-g_e))/2, sign + iff |T| even.
Needs all 11 signed subgraph densities of sigma1."""
import sys, itertools, time, numpy as np
from scipy.optimize import minimize
sys.path.insert(0, 'research/experiments/round4_E6')
from sprofile import load, profile, mono

EDGES = list(itertools.combinations(range(4), 2))

def iso_type(T):
    es = [EDGES[i] for i in range(6) if T >> i & 1]
    deg = sorted([sum(v in e for e in es) for v in range(4)], reverse=True)
    m = len(es)
    tri = any(all(tuple(sorted(p)) in es for p in itertools.combinations(c, 2)) for c in itertools.combinations(range(4), 3))
    if m == 0: return 'empty'
    if m == 1: return 'K2'
    if m == 2: return 'P3' if deg[0] == 2 else '2K2'
    if m == 3: return 'K3' if tri else ('K13' if deg[0] == 3 else 'P4')
    if m == 4: return 'paw' if tri else 'C4'
    if m == 5: return 'diamond'
    return 'K4'

def densities(w, s, K4=None):
    A = s * w[None, :]; d = s @ w; e = w @ d
    A2 = A @ A; A3diag = np.einsum('ab,ba->a', A2, A)
    M = (s * w[None, :]) @ s
    t = dict(empty=1.0, K2=e, **{'2K2': e * e}, P3=w @ (d * d), K3=A3diag.sum(),
             P4=(w * d) @ s @ (w * d), K13=w @ d ** 3, C4=np.trace(A2 @ A2), paw=A3diag @ d,
             diamond=w @ (s * M * M) @ w)
    if K4 is None:
        K4 = profile(w, s)[5]
    t['K4'] = K4
    return t

TYPES = [iso_type(T) for T in range(64)]
TSIZE = np.array([bin(T).count('1') for T in range(64)])
INT = np.array([[T >> i & 1 for i in range(6)] for T in range(64)], bool)  # 64x6

def mono_lift(tvec, v, G, D):
    k = len(v)
    tup = np.array(list(itertools.product(range(k), repeat=4)))            # N x 4
    wt = v[tup].prod(1)
    ge = np.stack([G[tup[:, i], tup[:, j]] for i, j in EDGES], 1)          # N x 6
    de = np.stack([D[tup[:, i], tup[:, j]] for i, j in EDGES], 1)
    total = 0.0
    for T in range(64):
        inT = INT[T]
        pd = de[:, inT].prod(1)
        pp = (1 + ge[:, ~inT]).prod(1); pm = (1 - ge[:, ~inT]).prod(1)
        c = pd * (pp + pm if TSIZE[T] % 2 == 0 else pp - pm) / 2
        total += tvec[T] * (wt * c).sum()
    return total / 32

def unpack(x, k):
    th = x[:k]; v = np.exp(th - th.max()); v /= v.sum()
    m = k * (k + 1) // 2; iu = np.triu_indices(k)
    Dm = np.zeros((k, k)); Gm = np.zeros((k, k))
    dd = np.tanh(x[k:k + m]); gg = (1 - np.abs(dd)) * np.tanh(x[k + m:])
    Dm[iu] = dd; Gm[iu] = gg
    Dm = Dm + Dm.T - np.diag(np.diag(Dm)); Gm = Gm + Gm.T - np.diag(np.diag(Gm))
    return v, Gm, Dm

if __name__ == '__main__':
    w, s = load(sys.argv[1]); t = densities(w, s)
    print('densities', t, flush=True)
    tvec = np.array([t[TYPES[T]] for T in range(64)])
    one = np.ones(1); print('trivial lift', mono_lift(tvec, one, np.zeros((1, 1)), np.ones((1, 1))), flush=True)
    # check vs direct recount of explicit product on tiny random case
    rng = np.random.default_rng(2); w1 = rng.random(3); w1 /= w1.sum(); s1 = rng.uniform(-1, 1, (3, 3)); s1 = (s1 + s1.T) / 2
    v = rng.random(2); v /= v.sum(); G = np.array([[.2, -.3], [-.3, .1]]); D = np.array([[.5, .6], [.6, -.7]])
    t1 = densities(w1, s1); tv1 = np.array([t1[TYPES[T]] for T in range(64)])
    big = np.kron(v, w1); S = np.kron(G, np.ones((3, 3))) + np.kron(D, s1)
    print('lift check', mono(profile(np.kron(v, w1)[np.argsort(np.arange(6))], S)), mono_lift(tv1, v, G, D), flush=True)
    rng = np.random.default_rng(0); t0 = time.time()
    for k in [2, 3, 4]:
        best = (9, None); m = k * (k + 1) // 2
        for r in range(int(sys.argv[2])):
            if time.time() - t0 > 450: break
            x0 = np.concatenate([rng.normal(0, .5, k), rng.normal(0, 1.5, m), rng.normal(0, 1, m)])
            res = minimize(lambda x: mono_lift(tvec, *unpack(x, k)), x0, method='L-BFGS-B', options={'maxiter': 2000})
            if res.fun < best[0]: best = (res.fun, res.x)
        v, G, D = unpack(best[1], k)
        print(f'k={k} best {best[0]:.14f} v={np.round(v,4).tolist()} G={np.round(G,4).tolist()} D={np.round(D,4).tolist()}', flush=True)
