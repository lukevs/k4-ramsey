"""Cross-check a saved candidate JSON without the orbital parameterisation:
(i) rebuild generator images on n points, verify integer-matrix invariance and
transitivity (orbit of 0 = all points); (ii) exact transitive count re-based at
random vertices a (matrix relabelled so a is first) must agree for every a.
  crosscheck.py CAND.json EXACT_REPORT.json
"""
import json, os, subprocess, sys
from fractions import Fraction
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from coset_action import Base, CosetAction
cand = json.load(open(sys.argv[1])); rep = json.load(open(sys.argv[2]))
M = np.array(cand["red_probability_numerators"], dtype=np.int64); q = cand["edge_probability_denominator"]; n = len(M)
b = Base(); A = CosetAction(b, rep["K"]); pts = np.arange(n)
imgs = [A.act_G(g, pts) for g in b.gens]
for im in imgs:
    assert sorted(im.tolist()) == list(range(n)); assert np.array_equal(M[np.ix_(im, im)], M)
seen = {0}; todo = [0]
while todo:
    u = todo.pop()
    for im in imgs:
        v = int(im[u])
        if v not in seen: seen.add(v); todo.append(v)
assert len(seen) == n, "not transitive"
print("invariant under 8 generators, transitive on", n)
rng = np.random.default_rng(11); vals = []
for a in [0] + rng.choice(n, 1, replace=False).tolist():
    perm = np.r_[a, np.delete(np.arange(n), a)]
    Mp = M[np.ix_(perm, perm)]
    # all rows b as reps (no orbit compression): full n^3 exact sum
    inp = f"{n} {q} {n}\n" + " ".join(map(str, range(n))) + "\n" + "\n".join(" ".join(map(str, r)) for r in Mp) + "\n"
    out = subprocess.run([os.path.join(HERE, "exact_count")], input=inp, capture_output=True, text=True, check=True).stdout
    tot = 0
    for line in out.split("\n"):
        if line.strip():
            c, bb, v = map(int, line.split()); w = int(Mp[0, bb]); tot += (w if c == 0 else q - w) * v
    val = Fraction(tot, q ** 6 * n ** 3); vals.append(val); print("base", a, float(val), flush=True)
assert all(v == vals[0] for v in vals)
assert f"{vals[0].numerator}/{vals[0].denominator}" == rep["exact_fraction"]
print("MATCH", rep["exact_fraction"])
