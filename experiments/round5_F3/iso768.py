# F3 task 1a: is E1's Z3 x Z2^8 Cayley state isomorphic to the published PPSS 768 graph?
import json, sys, hashlib, numpy as np
from collections import Counter
R = '/Users/luke.vanseters/code/github.com/lukevs/k4-ramsey/'
d = json.load(open(R + 'data/published_cayley_768.json'))
P = np.array([[int(c) for c in row] for row in d['red_rows']], dtype=np.int64)
assert set(d['weights']) == {1}
n = 768
S = [int(t) for t in open(R + 'experiments/round4_E1/s768_b7.txt').read().split()]
# encoding: dims 3x2^8, x = a*256 + bits (first digit most significant)
def add(x, y):
    return (((x >> 8) + (y >> 8)) % 3) * 256 + ((x & 255) ^ (y & 255))
def neg(x):
    return ((3 - (x >> 8)) % 3) * 256 + (x & 255)
Sset = set(S)
assert all(neg(s) in Sset for s in S) and 0 not in Sset
E = np.zeros((n, n), dtype=np.int64)
for x in range(n):
    for s in S:
        E[x, add(x, s)] = 1
assert (E == E.T).all()
print('diag P', int(np.trace(P)), 'symmetric P', bool((P == P.T).all()))
def val(A):
    B = 1 - A; np.fill_diagonal(B, 0)
    tot = 0
    for M in (A, B):
        M = M.astype(np.float64)
        # ordered K4 count = sum_{a,b} M_ab * (sum_c M_ac M_bc (sum_d M_ad M_bd M_cd))
        c = 0.0
        for a in range(n):
            v = M[a]; N = M * v[None, :] * v[:, None]  # N_bc = M_ab M_ac M_bc
            c += (N @ N * M).sum() if False else 0
        tot += c
    return tot
def k4count(M):
    # exact integer: sum over a of number of ordered triangles in neighbourhood of a
    M = M.astype(np.int64); tot = 0
    for a in range(n):
        nb = np.nonzero(M[a])[0]; Sub = M[np.ix_(nb, nb)].astype(np.float64)
        tot += int(round(np.trace(Sub @ Sub @ Sub)))
    return tot
for name, A in (('published', P), ('E1', E)):
    B = 1 - A; np.fill_diagonal(B, 0)
    num = k4count(A) + k4count(B)
    degs = Counter(A.sum(1).tolist())
    print(name, 'degrees', dict(degs), 'K4 ordered count R+B', num, 'value /768^4', num / n**4)
ev = {}
for name, A in (('published', P), ('E1', E)):
    ev[name] = np.sort(np.linalg.eigvalsh(A.astype(np.float64)))
    c = Counter(np.round(ev[name], 6).tolist())
    print(name, 'distinct eigenvalues', len(c), 'top', sorted(c.items())[-3:], 'bottom', sorted(c.items())[:3])
print('max |spectrum diff|', float(np.abs(ev['published'] - ev['E1']).max()))
# complement spectra too
for name, A in (('published', P), ('E1', E)):
    B = 1 - A; np.fill_diagonal(B, 0)
    print(name, 'complement spectrum head', np.round(np.sort(np.linalg.eigvalsh(B.astype(float)))[-3:], 6))
np.save('/private/tmp/claude-502/-Users-luke-vanseters-code-github-com-lukevs-k4-ramsey/382fcd3d-f458-48b1-884a-cba63c698656/scratchpad/E1adj.npy', E)
np.save('/private/tmp/claude-502/-Users-luke-vanseters-code-github-com-lukevs-k4-ramsey/382fcd3d-f458-48b1-884a-cba63c698656/scratchpad/Padj.npy', P)
