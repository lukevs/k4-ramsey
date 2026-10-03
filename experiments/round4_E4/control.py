"""Step 1 control + subgroup census."""
import json, sys, time
from collections import Counter
import numpy as np
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from coset_action import Base, CosetAction, density_grad, PARENT

t0 = time.time()
b = Base()
H = frozenset(range(len(b.H)))
A = CosetAction(b, H).build(); A.verify_invariance()
par = np.array(json.loads(PARENT.read_text())["red_probability_numerators"])
p = np.zeros(A.npar, dtype=np.int64)
for v in range(A.n): p[A.row0[v]] = par[0][v]
ok = np.array_equal(p[A.P], par)
q = 65536
W = p[A.P] / q
f, g = density_grad(W, A.row0, A.npar)
print("n", A.n, "directed orbitals", A.norb, "undirected params", A.npar, "reproduces parent", ok)
print("f", repr(f), "target 0.03013897728988013 diff", f - 0.03013897728988013)
# finite-difference gradient check
x = p / q; eps = 1e-6
for k in range(3):
    x2 = x.copy(); x2[k] += eps
    f2, _ = density_grad(x2[A.P], A.row0, A.npar)
    print("fd", k, (f2 - f) / eps, g[k])
print("params", list(p), "sizes", list(A.sizes))
print("grad", [f"{v:.3e}" for v in g])
# subgroup census (1- and 2-generated)
nh = len(b.H); subs = set()
for a in range(nh):
    subs.add(b.subgroup([a]))
cyc = list(subs)
for a in range(nh):
    for c in range(a + 1, nh):
        subs.add(b.subgroup([a, c]))
subs.add(H)
# conjugacy classes under H
cls = {}
for S in subs:
    key = min(tuple(sorted(b.mul[b.mul[h][s]][b.hinv[h]] for s in S)) for h in range(nh))
    cls[key] = S
print("subgroups", len(subs), "classes", len(cls))
orders = Counter(len(S) for S in cls.values())
print(sorted(orders.items()))
json.dump(sorted([sorted(int(s) for s in S) for S in cls.values()], key=lambda s: -len(s)),
          open(__file__.rsplit('/', 1)[0] + "/subgroup_classes.json", "w"))
print("seconds", time.time() - t0)
