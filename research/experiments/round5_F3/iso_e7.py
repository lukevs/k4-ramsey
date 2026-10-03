# F3 task 1b: does E7's Z2^2 (H-) quotient equal B192 (as a symbol pattern, up to isomorphism)?
# Also task 1a follow-up: eigenvalue multiset differences E1 vs published PPSS 768.
import sys, json, itertools, numpy as np
from collections import Counter
sys.path.insert(0, '/Users/luke.vanseters/code/github.com/lukevs/k4-ramsey/research/experiments/round5_F3')
from lib import *
E7 = ROOT / 'research/experiments/round4_E7'
d = json.load(open(ROOT / 'reports/round4-E7-run012/full.cont3.frac.json')); P = np.array(d['P']); q = d['q']
a = np.fromfile(E7 / 'g/2_6_1_0_r12.bin', dtype=np.int32); n = int(a[0]); orb = a[2:2 + n]
p = P[orb].astype(np.int64)
X = np.arange(n) // 12; T = np.arange(n) % 12
def add(g, h): return ((X[g] ^ X[h]) * 12 + (T[g] + T[h]) % 12)
Hs = [0, 1 * 12 + 0, 56 * 12 + 6, add(1 * 12, 56 * 12 + 6)]   # H = <(1,0),(56,6)>
assert all(add(h, h) == 0 for h in Hs)
Wfull = np.array([[p[(X[i] ^ X[j]) * 12 + (T[j] - T[i]) % 12] for j in range(n)] for i in range(n)]) / q
print('E7 768 kernel F', F_full(Wfull))
coset = -np.ones(n, int); reps = []
for g in range(n):
    if coset[g] < 0:
        for h in Hs: coset[add(g, h)] = len(reps)
        reps.append(g)
m = len(reps)
# block-average quotient (graphon quotient onto the H-coset partition of the vertex set)
Q = np.zeros((m, m)); cnt = np.zeros((m, m))
np.add.at(Q, (coset[:, None], coset[None, :]), Wfull); np.add.at(cnt, (coset[:, None], coset[None, :]), 1)
Q /= cnt
print('quotient order', m, 'F', F_full(Q))
sym, other = classify(Q, tol=2e-3)
print('quotient symbol counts', Counter(sym.ravel().tolist()), 'other clusters', other)
fr = Q[(Q > 1e-6) & (Q < 1 - 1e-6)]
print('fractional value range near P', fr[np.abs(fr - P0) < 2e-3].min(), fr[np.abs(fr - P0) < 2e-3].max())
symL = b192_literature_sym()
print('diag symbols', Counter(np.diag(sym).tolist()))
print('B192-isomorphic symbol pattern (pynauty):', certificate(sym) == certificate(symL))
# how far is the quotient from exact B192 levels? replace P/H cells by optimum levels and re-evaluate
W2 = np.choose(np.clip(sym, 0, 3), [0.0, 1.0, P0, H0]); print('quotient with B192 levels F', F_full(W2))
# undo averaging: does E7 768 kernel itself have B192 pattern at 0/1 cells? fraction of H-coset blocks non-constant
blk = {}
for i in range(n):
    for j in range(n):
        blk.setdefault((coset[i], coset[j]), set()).add(p[(X[i] ^ X[j]) * 12 + (T[j] - T[i]) % 12])
nc = sum(1 for v in blk.values() if len(v) > 1)
print('non-constant quotient blocks', nc, 'of', m * m, '; 0/1 blocks all constant:',
      all(len(v) == 1 for k, v in blk.items() if sym[k] in (0, 1)))
# spectra diff E1 vs PPSS
SP = '/private/tmp/claude-502/-Users-luke-vanseters-code-github-com-lukevs-k4-ramsey/382fcd3d-f458-48b1-884a-cba63c698656/scratchpad/'
ev = {k: Counter(np.round(np.linalg.eigvalsh(np.load(SP + k + 'adj.npy').astype(float)), 5).tolist()) for k in ('E1', 'P')}
print('eigenvalue multiplicity differences (E1 - published):',
      {v: ev['E1'][v] - ev['P'][v] for v in sorted(set(ev['E1']) | set(ev['P'])) if ev['E1'][v] != ev['P'][v]})
