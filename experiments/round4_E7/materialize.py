"""Materialize a frac result as rational-step-graphon-v1 JSON; print SHA-256 and predicted fraction."""
import sys, json, hashlib
from fractions import Fraction
import numpy as np
grp, res, out = sys.argv[1:4]
r = json.load(open(res))
a = np.fromfile(grp + '.bin', dtype=np.int32); n, K = int(a[0]), int(a[1])
orb = a[2:2 + n]; D = a[2 + n:].reshape(n, n)
P = np.array(r['P'], dtype=np.int64)
M = P[orb[D]]
assert (M == M.T).all() and (np.diag(M) == 0).all()
doc = {"schema": "rational-step-graphon-v1", "block_weights": [1] * n,
       "edge_probability_denominator": int(r['q']), "red_probability_numerators": M.tolist()}
s = json.dumps(doc, separators=(',', ':'))
open(out, 'w').write(s)
fr = Fraction(int(r['num']), int(r['den']))
print("sha256", hashlib.sha256(s.encode()).hexdigest())
print("predicted", fr.numerator, "/", fr.denominator, float(fr))
