"""Lift orbit probabilities from a coarse orbit partition to a finer one on the same group table."""
import sys, json, numpy as np
coarse, fine, res, out = sys.argv[1:5]
def orbs(g):
    a = np.fromfile(g + '.bin', dtype=np.int32, count=2); n, K = a
    o = np.fromfile(g + '.bin', dtype=np.int32, count=2 + n)[2:]
    return n, K, o
n1, K1, o1 = orbs(coarse); n2, K2, o2 = orbs(fine); assert n1 == n2
d = json.load(open(res)); p = [x / d['q'] for x in d['P']]
q = [None] * K2
for x in range(n2):
    v = p[o1[x]]
    if q[o2[x]] is None: q[o2[x]] = v
    assert q[o2[x]] == v, "fine orbit not inside coarse orbit"
open(out, 'w').write(' '.join(map(str, q)))
print('lifted', K1, '->', K2)
