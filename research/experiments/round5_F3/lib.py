"""F3 shared tools: Cayley kernels on abelian groups, K4 value+gradient, B192 reference,
symbol classification and pynauty canonical certificate for edge-coloured kernels."""
import json, numpy as np
from pathlib import Path
ROOT = Path('/Users/luke.vanseters/code/github.com/lukevs/k4-ramsey')
P0, H0 = 0.779181, 0.534265   # B192 continuous optimum levels (E11/E12)
B192_VAL = 0.030138977290

class Group:
    """product of cyclic groups, mixed radix, first factor most significant (pa.cpp encoding)."""
    def __init__(self, dims):
        self.dims = list(dims); n = 1
        for m in dims: n *= m
        self.n = n
        dig = np.zeros((n, len(dims)), int); r = np.arange(n)
        for i in range(len(dims) - 1, -1, -1):
            dig[:, i] = r % dims[i]; r = r // dims[i]
        self.dig = dig
        enc = lambda D: sum(D[:, i] * int(np.prod(dims[i + 1:])) for i in range(len(dims)))
        # sub[x, y] = y - x
        self.sub = np.zeros((n, n), int)
        for x in range(n):
            self.sub[x] = enc((dig - dig[x]) % np.array(dims))
        self.neg = self.sub[:, 0]
        orb = -np.ones(n, int); reps = []
        for g in range(n):
            if orb[g] < 0:
                orb[g] = len(reps); orb[self.neg[g]] = len(reps); reps.append(g)
        self.orb = orb; self.reps = reps; self.k = len(reps)
        self.mult = np.bincount(orb)

    def kernel(self, x):  # x: orbit values -> n x n matrix M[a,b] = w(b - a)
        return x[self.orb][self.sub]

def tk4_cayley(G, w):
    """t(K4, M) for vertex-transitive Cayley kernel, and G0[b] = sum_{c,d} w(c)w(b-c)... so that
    t = (1/n^3) sum_b w(b) G0[b];  d t / d w(g) (untied) = 6 G0[g] / n^3."""
    M = w[G.sub]; X = M * M[0][None, :]          # X[b, c] = M[b, c] M[0, c]
    G0 = np.einsum('bc,bc->b', X, X @ M)
    n = G.n
    return float(w @ G0) / n**3, G0

def F_cayley(G, x):
    """x: orbit values. returns F and gradient wrt orbit variables."""
    w = x[G.orb]
    r, Gr = tk4_cayley(G, w); b, Gb = tk4_cayley(G, 1 - w)
    gw = 6.0 * (Gr - Gb) / G.n**3
    gx = np.bincount(G.orb, weights=gw, minlength=G.k)
    return r + b, gx

def tk4_full(U):
    N = len(U); tot = 0.0
    for a in range(N):
        X = U[a][None, :] * U; tot += U[a] @ np.einsum('bc,bc->b', X, X @ U)
    return tot / N**4

def F_full(W):
    return tk4_full(W) + tk4_full(1 - W)

def b192_cayley(p=P0, h=H0):
    """E11 closed form on Z3 x Z2^6, element = a*64 + (z<<2 | e<<1 | s), z in F2^4."""
    G = Group([3, 2, 2, 2, 2, 2, 2])
    C = {0, 1, 2, 4, 8, 15}; S = C - {0}
    w = np.zeros(G.n)
    for g in range(G.n):
        a = g // 64; b = g % 64; z = b >> 2; e = (b >> 1) & 1; s = b & 1
        if s == 0:
            ty = 'Z' if e == 0 and a == 0 else ('H' if a == 0 else ('X' if e == 0 else 'Z'))
        else:
            ty = 'P' if a == 0 else 'Z'
        inC = z in C
        w[g] = {'Z': 0.0 if inC else 1.0, 'X': 1.0 if inC else 0.0, 'P': p if inC else 0.0,
                'H': (h if z == 0 else 1.0) if inC else 0.0}[ty]
    x = np.array([w[r] for r in G.reps])
    return G, x

def b192_literature_sym():
    B = np.array(json.loads((ROOT / 'reports/literature-two-parameter-001/graphon-candidate.json').read_text())['red_probability_numerators'])
    sym = np.full(B.shape, -1); sym[B == 0] = 0; sym[B == 65536] = 1; sym[B == 51064] = 2; sym[B == 35015] = 3
    assert (sym >= 0).all()
    return sym

def classify(W, tol=2e-3):
    """symbol matrix: 0,1, 2 = near P0, 3 = near H0, 4+ = other fractional clusters. returns sym, info."""
    sym = np.full(W.shape, -1)
    sym[W < 1e-6] = 0; sym[W > 1 - 1e-6] = 1
    sym[(sym < 0) & (np.abs(W - P0) < tol)] = 2
    sym[(sym < 0) & (np.abs(W - H0) < tol)] = 3
    other = sorted(set(np.round(W[sym < 0], 3).tolist()))
    for i, v in enumerate(other):
        sym[(sym < 0) & (np.abs(W - v) <= 0.0005 + 1e-12)] = 4 + i
    sym[sym < 0] = 99
    return sym, other

def certificate(sym):
    """pynauty certificate of an edge-coloured complete graph (colour = sym[i,j], diag = vertex colour)."""
    import pynauty
    n = len(sym); cols = sorted(set(sym[np.triu_indices(n, 1)].tolist()))
    diag = sorted(set(np.diag(sym).tolist()))
    L = max(1, int(np.ceil(np.log2(len(cols) + 1))))  # colour code c -> index+1 so that no code is 0?
    code = {c: i for i, c in enumerate(cols)}           # code 0 = no edge in any layer
    L = max(1, int(np.ceil(np.log2(len(cols)))) if len(cols) > 1 else 1)
    adj = {v: [] for v in range(n * L)}
    for l in range(L - 1):
        for i in range(n): adj[l * n + i].append((l + 1) * n + i)
    iu, ju = np.triu_indices(n, 1)
    for i, j in zip(iu.tolist(), ju.tolist()):
        c = code[sym[i, j]]
        for l in range(L):
            if (c >> l) & 1: adj[l * n + i].append(l * n + j)
    parts = []
    for l in range(L):
        for dv in diag:
            parts.append(set(l * n + i for i in range(n) if sym[i, i] == dv))
    g = pynauty.Graph(n * L, directed=False, adjacency_dict=adj, vertex_coloring=[p for p in parts if p])
    return pynauty.certificate(g), tuple(cols), tuple(diag)
