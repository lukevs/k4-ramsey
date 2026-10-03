"""Round 5 F1: dense sign-split (rank-one +-A) machinery with an arbitrary support mask,
B192 in Cayley coordinates (F2^4 x Z3 x Z2 x Z2), orbital labels, first-order slacks.
Search-side float64.  Conventions follow research/experiments/round4_E5/phi.py:
  Delta(A) = T3 + T4,  T3 = 4/n^4 sum_{uvw} A_uv A_vw A_wu K_uvw,
  K_uvw = sum_z (p_uz p_vz p_wz - q_uz q_vz q_wz),
  T4 = 3/n^4 sum_{uvwz} A_uv A_vw A_wz A_zu (p_uw p_vz + q_uw q_vz).
Gradients are w.r.t. the symmetric pair parameter (A_uv = A_vu moved together)."""
import sys, numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'research/experiments/round4_E11'))
S4 = {1, 2, 4, 8, 15}
C4 = {0} | S4

def blocks():
    return [(a, e, s) for a in range(3) for e in range(2) for s in range(2)]

def btype(da, de, ds):
    if ds == 0:
        if da == 0 and de == 0: return 'D'
        if da == 0 and de == 1: return 'H'
        if de == 0: return 'X'
        return 'Z'
    return 'P' if da == 0 else 'Z'

def labels():
    """per entry: block type, z-class (0,S,off), orbital id (canonical (da,de,ds,z))."""
    bl = blocks(); n = 192
    ty = np.empty((n, n), dtype='<U1'); zc = np.zeros((n, n), int); orb = np.zeros((n, n), int)
    for i, (a, e, s) in enumerate(bl):
        for j, (b, f, t) in enumerate(bl):
            da = (a - b) % 3; da = min(da, 3 - da)  # symmetric pair canonical
            de, ds = e ^ f, s ^ t
            for x in range(16):
                for y in range(16):
                    z = x ^ y
                    u, v = 16 * i + x, 16 * j + y
                    ty[u, v] = btype((a - b) % 3, de, ds)
                    zc[u, v] = 0 if z == 0 else (1 if z in S4 else 2)
                    orb[u, v] = ((da * 2 + de) * 2 + ds) * 16 + z
    return ty, zc, orb

def level(tyc, zc, p, h):
    tab = {'D': (0, 0, 1), 'Z': (0, 0, 1), 'X': (1, 1, 0), 'P': (p, p, 0), 'H': (h, 1, 0)}
    return tab[tyc][zc]

def b192(p, h, ty=None, zc=None):
    if ty is None: ty, zc, _ = labels()
    W = np.zeros(ty.shape)
    for T in 'DZXPH':
        for c in range(3):
            W[(ty == T) & (zc == c)] = level(T, c, p, h)
    np.fill_diagonal(W, 0.0)
    return W

def Fdens(W):
    n = W.shape[0]; tot = 0.0
    for X in (W, 1 - W):
        for a in range(n):
            V = X[a][None, :] * X
            tot += (X[a] * ((V @ X) * V).sum(1)).sum()
    return tot / n**4

def Fdens_root(W):
    n = W.shape[0]; tot = 0.0
    for X in (W, 1 - W):
        V = X[0][None, :] * X
        tot += (X[0] * ((V @ X) * V).sum(1)).sum()
    return tot / n**3

def gradF(W):
    """dF/dW_uv for the symmetric pair parameter (u != v)."""
    n = W.shape[0]; G = np.zeros_like(W)
    for sgn, X in ((1, W), (-1, 1 - W)):
        for a in range(n):
            # R[a,b] = sum_{w,z} X_aw X_bw X_az X_bz X_wz
            Y = X * X[a][None, :]            # Y[b,w] = X_bw X_aw
            G[a] += sgn * ((Y @ X) * Y).sum(1)
    return 12.0 / n**4 * G   # pair parameter: 6 edges x 2 orientations

class Lift:
    def __init__(self, P, mask):
        self.P = P; self.Q = 1 - P; self.n = P.shape[0]
        self.mask = mask.copy(); np.fill_diagonal(self.mask, False)
        self.m = np.minimum(P, 1 - P) * self.mask

    def K_row(self, u):
        return (self.P * self.P[u]) @ self.P.T - (self.Q * self.Q[u]) @ self.Q.T

    def val_grad(self, A, grad=True):
        n = self.n; t3 = 0.0; t4 = 0.0
        G3 = np.zeros_like(A); G4 = np.zeros_like(A)
        for u in range(n):
            Ku = self.K_row(u)                     # Ku[v,w]
            Au = A[u]
            # sum_{v,w} A_uv A_vw A_wu K_uvw
            B = A * Ku                             # B[v,w]=A_vw K_uvw
            Bv = B @ Au                            # Bv[v] = sum_w A_vw K_uvw A_wu
            t3 += Au @ Bv
            if grad: G3[u] += Bv                   # d/dA_uv (first slot); x3 slots, pair x2 below
            for X in (self.P, self.Q):
                M = (A * X[u][None, :]) @ A        # M[v,z] = sum_w A_vw X_uw A_wz
                g = (M * X) @ Au                   # g[v] = sum_z M[v,z] X_vz A_zu
                t4 += Au @ g
                if grad: G4[u] += g
        c3 = 4.0 / n**4; c4 = 3.0 / n**4
        val3, val4 = c3 * t3, c4 * t4
        if not grad: return val3 + val4, val3, val4
        G = c3 * 3 * 2 * G3 + c4 * 4 * 2 * G4
        G = 0.5 * (G + G.T)
        return val3 + val4, G, val3, val4

def optimize_A(L, A0, tlimit=120, iters=400, verbose=True, tag=''):
    import time
    m = L.m; fr = L.mask
    A = np.clip(A0, -m, m); t0 = time.time()
    f = L.val_grad(A, False)[0]; step = 0.25
    for it in range(iters):
        if time.time() - t0 > tlimit: break
        f, G, a, b = L.val_grad(A, True)
        D = -G * m * m
        D[(A >= m - 1e-15) & (D > 0)] = 0; D[(A <= -m + 1e-15) & (D < 0)] = 0
        sc = np.max(np.abs(D[fr]) / np.maximum(m[fr], 1e-300))
        if sc == 0: break
        D /= sc; best = (f, None, None)
        for s in (step * 2, step, step / 2, step / 8):
            An = np.clip(A + s * D, -m, m); fn = L.val_grad(An, False)[0]
            if fn < best[0]: best = (fn, An, s)
        if best[1] is None:
            step /= 16
            if step < 1e-7: break
            continue
        f, A, step = best
        if verbose and it % 20 == 0: print(tag, it, f, a, b, round(time.time() - t0), flush=True)
    return A, f
