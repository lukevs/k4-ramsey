"""First-order test for composition/substitution products (EZL Lemma-6 style nesting):
replacing diagonal block i by an internal graphon sigma' changes mono at first order only
through its mean; compute d mono / d(sigma_ii) for all i jointly, and the XOR / vertex-insertion
first-order certificates at the trivial partner."""
import sys, numpy as np
sys.path.insert(0, 'experiments/round4_E6')
from sprofile import load, profile, mono, MULT
w, s = load(sys.argv[1]); a = profile(w, s)
print('diag sigma values', np.unique(np.round(np.diag(s), 6)))
h = 1e-4
m0 = mono(a); m1 = mono(profile(w, s - h * np.diag(np.sign(np.diag(s)))))
print('mono', m0, 'd mono/d(|sigma_ii| decrease, all i) =', (m1 - m0) / h)
# XOR partner shrink certificate: d/deps F(1-eps h) = hbar * (-sum n_S a_S |S|)/32
size = np.array([0, 2, 2, 4, 4, 6])
print('XOR first-order rate (per unit mean shrink):', -(MULT * a * size).sum() / 32)
r = np.linspace(-1, 1, 20001)
aM, aP, aC, apaw, aK = a[1:]
g = 12*aM*(r-1) + 12*aP*(r*r+2*r-3) + 12*aC*(r*r-1) + 12*apaw*(r**3+2*r*r+r-4) + 4*aK*(r**3-1)
print('vertex-insertion rate min over r in [-1,1):', g[:-1].min() / 32, 'at r=', r[g[:-1].argmin()])
