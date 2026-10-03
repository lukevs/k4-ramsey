"""Exact cubic+quartic line for rank-one sign split W' = W + A (x) sigma sigma^T.
Delta(A) = T3(A) + T4(A) exactly (all other even-subgraph terms vanish), where
T3 = 4/n^4 sum_{u,v,w ordered} A_uv A_vw A_wu sum_z (p_uz p_vz p_wz - q_uz q_vz q_wz)
T4 = 3/n^4 sum_{u,v,w,z ordered} A_uv A_vw A_wz A_zu (p_uw p_vz + q_uw q_vz)
Repeated class indices included (A_uu=0, p_uu from W). Uniform class weights."""
import numpy as np

class Phi:
    def __init__(self, P):
        self.P = P; self.Qm = 1.0 - P; n = P.shape[0]; self.n = n
        self.frac = (P > 0) & (P < 1); np.fill_diagonal(self.frac, False)
        self.nbr = [np.nonzero(self.frac[u])[0] for u in range(n)]
        self.m = np.minimum(P, 1 - P) * self.frac
        # triangle list u<v<w in support with K = sum_z(ppp-qqq)
        tri = []; K = []
        for u in range(n):
            Nu = self.nbr[u]; Nu = Nu[Nu > u]
            if len(Nu) < 2: continue
            sub = self.frac[np.ix_(Nu, Nu)]
            a, b = np.nonzero(np.triu(sub, 1))
            if len(a) == 0: continue
            v, w = Nu[a], Nu[b]
            Kp = ((P[u] * P[v]) * P[w]).sum(1) - ((self.Qm[u] * self.Qm[v]) * self.Qm[w]).sum(1)
            tri.append(np.stack([np.full_like(v, u), v, w], 1)); K.append(Kp)
        self.tri = np.concatenate(tri) if tri else np.zeros((0, 3), int)
        self.K = np.concatenate(K) if K else np.zeros(0)

    def T3(self, A, grad=False):
        u, v, w = self.tri.T; n = self.n
        c = 24.0 / n**4 * self.K
        val = (A[u, v] * A[v, w] * A[w, u] * c).sum()
        if not grad: return val
        G = np.zeros_like(A)
        np.add.at(G, (u, v), c * A[v, w] * A[w, u])
        np.add.at(G, (v, w), c * A[u, v] * A[w, u])
        np.add.at(G, (w, u), c * A[u, v] * A[v, w])
        G = G + G.T  # dF/dA_e for symmetric edge, stored both sides
        return val, G

    def T4(self, A, grad=False):
        n = self.n; val = 0.0; G = np.zeros_like(A) if grad else None
        for X in (self.P, self.Qm):
            for u in range(n):
                Nu = self.nbr[u]
                if len(Nu) == 0: continue
                au = A[u, Nu]
                Y = au[:, None] * A[Nu, :]                  # Y[v,w]=A_uv A_vw
                S = (Y * X[u]) @ Y.T                          # sum_w X_uw Y_vw Y_zw
                val += (S * X[np.ix_(Nu, Nu)]).sum()
                if grad:
                    # g_uv = 4 sum_{w,z} A_vw A_wz A_zu X_uw X_vz, v in Nu
                    M = A[:, Nu] * au[None, :] @ X[np.ix_(Nu, Nu)]  # M[w,v]=sum_z A_wz A_uz X_zv
                    g = np.einsum('vw,wv->v', A[Nu, :] * X[u][None, :], M)
                    G[u, Nu] += 4 * g
        val *= 3.0 / n**4
        if not grad: return val
        G *= 3.0 / n**4
        G = G + G.T
        return val, G

    def delta(self, A, grad=False):
        if not grad: return self.T3(A) + self.T4(A)
        a, ga = self.T3(A, True); b, gb = self.T4(A, True)
        return a + b, ga + gb, a, b

def k4_density(W):
    """direct t(K4,W)+t(K4,1-W) for small step graphon, uniform weights"""
    n = W.shape[0]; tot = 0.0
    for X in (W, 1 - W):
        for a in range(n):
            V = X[a][None, :] * X            # V[b,c]=X_ac X_bc
            tot += (X[a][:, None] * ((V @ X) * V).sum(1)[:, None]).sum() if False else (X[a] * ((V @ X) * V).sum(1)).sum()
    return tot / n**4

def split(W, A):
    n = W.shape[0]; W2 = np.zeros((2 * n, 2 * n)); s = np.array([1, -1])
    for a in range(2):
        for b in range(2):
            W2[a::2, b::2] = W + A * s[a] * s[b]
    return W2
