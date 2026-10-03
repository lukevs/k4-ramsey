"""Coset actions G/K (K <= H = Stab_G(0)) of the recovered degree-192 group,
their orbitals, and a float objective/gradient for orbital probability kernels.

Points of G/K are pairs (u, j): u in 0..191 (the G/H coset r_u H) and j an index
of the coset h_j K in H/K.  Point index = u*m + j, base point (0, K) = 0.
"""
import json
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
REPS = ROOT / "reports/group-recovery-quotient-001/quotient-automorphisms.json"
STAB = ROOT / "reports/group-recovery-stabilizer-001/stabilizer.json"
GENS = ROOT / "reports/group-recovery-orbitals-001/generators.json"
PARENT = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"


def inv(p):
    q = np.empty_like(p); q[p] = np.arange(len(p)); return q


class Base:
    def __init__(self):
        self.reps = np.array(json.loads(REPS.read_text()), dtype=np.int64)
        self.H = np.array(json.loads(STAB.read_text()), dtype=np.int64)
        g = json.loads(GENS.read_text())
        self.gens = [np.array(x, dtype=np.int64) for x in g["point_stabilizer_generators"] + g["transitive_movers"]]
        self.n0 = self.reps.shape[1]
        assert all(self.reps[u][0] == u for u in range(self.n0))
        assert all(h[0] == 0 for h in self.H)
        self.hidx = {h.tobytes(): i for i, h in enumerate(self.H)}
        nh = len(self.H)
        # multiplication table: mul[a][b] = index of H[a] o H[b]  (apply b first)
        self.mul = np.array([[self.hidx[self.H[a][self.H[b]].tobytes()] for b in range(nh)] for a in range(nh)])
        self.e = self.hidx[np.arange(self.n0).tobytes()]
        self.hinv = np.array([self.hidx[inv(h).tobytes()] for h in self.H])
        self.repinv = np.array([inv(r) for r in self.reps])

    def cocycle(self, x):
        """c(x,v) = r_{x(v)}^{-1} x r_v in H, for all v."""
        out = np.empty(self.n0, dtype=np.int64)
        for v in range(self.n0):
            y = self.repinv[x[v]][x[self.reps[v]]]
            out[v] = self.hidx[y.tobytes()]
        return out

    def subgroup(self, gen_idx):
        S = {self.e}; todo = [self.e]
        while todo:
            a = todo.pop()
            for g in gen_idx:
                b = self.mul[g][a]
                if b not in S: S.add(b); todo.append(b)
        return frozenset(S)


class CosetAction:
    def __init__(self, base, K):
        b = base; self.b = b
        K = sorted(K); self.K = K
        nh = len(b.H)
        # cosets hK
        coset_of = -np.ones(nh, dtype=np.int64); cos = []
        order = [b.e] + [h for h in range(nh) if h != b.e]
        for h in order:
            if coset_of[h] < 0:
                c = len(cos); cos.append(h)
                for k in K: coset_of[b.mul[h][k]] = c
        self.m = m = len(cos); self.cosrep = cos; self.coset_of = coset_of
        self.n = n = b.n0 * m
        # left action of H on H/K: L[g][j]
        self.L = np.array([[coset_of[b.mul[g][cos[j]]] for j in range(m)] for g in range(nh)])
        self.Hc = np.array([b.cocycle(h) for h in b.H])  # Hc[h][v]
        self.Rc = np.array([b.cocycle(b.repinv[u]) for u in range(b.n0)])  # c(r_u^{-1}, v)

    def act_H(self, h, pts):
        v, j = pts // self.m, pts % self.m
        v2 = self.b.H[h][v]
        c = self.Hc[h][v]
        j2 = self.L[c, j]
        return v2 * self.m + j2

    def act_rinv(self, u, pts):
        v, j = pts // self.m, pts % self.m
        v2 = self.b.repinv[u][v]
        c = self.Rc[u][v]
        j2 = self.L[c, j]
        return v2 * self.m + j2

    def act_G(self, x, pts):
        c = self.b.cocycle(x)
        v, j = pts // self.m, pts % self.m
        return x[v] * self.m + self.L[c[v], j]

    def build(self):
        n, m, b = self.n, self.m, self.b
        pts = np.arange(n)
        # K-orbits on points (union find via BFS)
        orb = -np.ones(n, dtype=np.int64); nor = 0
        imgs = [self.act_H(k, pts) for k in self.K]
        for s in range(n):
            if orb[s] >= 0: continue
            orb[s] = nor; todo = [s]
            while todo:
                a = todo.pop()
                for im in imgs:
                    c = im[a]
                    if orb[c] < 0: orb[c] = nor; todo.append(c)
            nor += 1
        self.orb = orb; self.norb = nor
        # x_P^{-1} = h^{-1} r_u^{-1}, P = (u, h_j K) with h = cosrep[j]
        R = np.empty((n, n), dtype=np.int64)
        for u in range(b.n0):
            step = self.act_rinv(u, pts)
            for j in range(m):
                hinv = b.hinv[self.cosrep[j]]
                R[u * m + j] = orb[self.act_H(hinv, step)]
        self.R = R
        # pairing
        pair = R[:, 0]  # orbital of (Q, base) indexed by Q... need per orbital
        inv_of = np.empty(nor, dtype=np.int64)
        for Q in range(n):
            inv_of[orb[Q]] = R[Q, 0]
        assert np.all(R.T == inv_of[R]), "pairing inconsistent"
        # undirected param ids
        pid = -np.ones(nor, dtype=np.int64); npar = 0
        for o in range(nor):
            if pid[o] < 0:
                pid[o] = npar; pid[inv_of[o]] = npar; npar += 1
        self.pid = pid; self.npar = npar
        self.P = pid[R]  # n x n param matrix
        assert np.array_equal(self.P, self.P.T)
        self.row0 = self.P[0]
        self.sizes = np.bincount(self.row0, minlength=npar)
        return self

    def verify_invariance(self):
        pts = np.arange(self.n)
        for g in self.b.gens:
            im = self.act_G(g, pts)
            assert np.array_equal(self.P[np.ix_(im, im)], self.P), "not G-invariant"
        return True


def density_grad(W, row0, npar):
    """f = t(K4,W)+t(K4,1-W) for a vertex-transitive step graphon; gradient per param."""
    n = W.shape[0]
    f = 0.0; g = np.zeros(npar)
    for M, sgn in ((W, 1.0), (1.0 - W, -1.0)):
        w = M[0]
        B = M * w[None, :]
        BW = B @ M
        S0 = np.einsum('ij,ij->i', BW, B)  # S(0,b)
        t = np.dot(w, S0) / n ** 3
        f += t
        g += sgn * 6.0 * np.bincount(row0, weights=S0, minlength=npar) / n ** 3
    return f, g


def orbit_reps(A):
    """First point and size of each directed K-orbit (orbit of the base stabilizer)."""
    reps = np.full(A.norb, -1, dtype=np.int64)
    for Q in range(A.n - 1, -1, -1): reps[A.orb[Q]] = Q
    cnt = np.bincount(A.orb, minlength=A.norb).astype(float)
    return reps, cnt


def density_grad_fast(W, reps, cnt, rep_pid, npar):
    n = W.shape[0]
    f = 0.0; g = np.zeros(npar)
    for M, sgn in ((W, 1.0), (1.0 - W, -1.0)):
        w = M[0]
        Br = M[reps] * w[None, :]            # r x n
        BW = Br @ M                          # r x n
        S = np.einsum('ij,ij->i', BW, Br)    # S0 at reps
        f += np.dot(cnt * w[reps], S) / n ** 3
        g += sgn * 6.0 * np.bincount(rep_pid, weights=cnt * S, minlength=npar) / n ** 3
    return f, g


def projection(A_fine, A_coarse):
    """Map points of G/K_fine to G/K_coarse (K_fine <= K_coarse), via coset reps."""
    m2 = A_fine.m
    jmap = np.array([A_coarse.coset_of[A_fine.cosrep[j]] for j in range(m2)])
    pts = np.arange(A_fine.n)
    return (pts // m2) * A_coarse.m + jmap[pts % m2]
