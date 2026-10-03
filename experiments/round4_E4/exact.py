"""Round an orbital kernel to q=65536, exact recount (transitive formula, C++ u128),
float cross-check, and write rational-step-graphon-v1 candidate.
  exact.py OUT --cls CI --x X.npy [--from-cls CJ]   (from-cls only to pick the same conjugate)
"""
import argparse, hashlib, json, os, subprocess, sys
from fractions import Fraction
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
from coset_action import Base, CosetAction, orbit_reps, density_grad_fast
ap = argparse.ArgumentParser(); ap.add_argument("out"); ap.add_argument("--cls", type=int, required=True)
ap.add_argument("--x", required=True); ap.add_argument("--from-cls", type=int, default=-1)
ap.add_argument("--q", type=int, default=65536)
a = ap.parse_args(); os.makedirs(a.out, exist_ok=True)
b = Base(); classes = json.load(open(os.path.join(HERE, "subgroup_classes.json")))
Kf = classes[a.cls]
if a.from_cls >= 0:
    Kc = set(classes[a.from_cls])
    for h in range(len(b.H)):
        S = sorted(int(b.mul[b.mul[h][s]][b.hinv[h]]) for s in Kf)
        if set(S) <= Kc: Kf = S; break
A = CosetAction(b, Kf).build(); A.verify_invariance()
x = np.load(a.x); q = a.q
num = np.rint(x * q).astype(np.int64)
M = num[A.P]
# exact G-invariance of the integer matrix (checked on all generators)
pts = np.arange(A.n)
for g in b.gens:
    im = A.act_G(g, pts); assert np.array_equal(M[np.ix_(im, im)], M)
reps, cnt = orbit_reps(A)
inp = f"{A.n} {q} {len(reps)}\n" + " ".join(map(str, reps)) + "\n" + "\n".join(" ".join(map(str, r)) for r in M) + "\n"
out = subprocess.run([os.path.join(HERE, "exact_count")], input=inp, capture_output=True, text=True, check=True).stdout
inner = {}
for line in out.split("\n"):
    if line.strip():
        c, bb, v = line.split(); inner[(int(c), int(bb))] = int(v)
tot = 0
for o, r in enumerate(reps):
    tot += int(cnt[o]) * (int(M[0, r]) * inner[(0, int(r))] + (q - int(M[0, r])) * inner[(1, int(r))])
val = Fraction(tot, q ** 6 * A.n ** 3)
ff, _ = density_grad_fast(M / q, reps, cnt, A.pid[np.arange(A.norb)], A.npar)
cand = {"schema": "rational-step-graphon-v1", "block_weights": [1] * A.n,
        "edge_probability_denominator": q, "red_probability_numerators": M.tolist()}
path = os.path.join(a.out, "graphon-candidate.json")
with open(path, "w") as fh: json.dump(cand, fh, separators=(",", ":")); fh.write("\n")
sha = hashlib.sha256(open(path, "rb").read()).hexdigest()
rep = {"cls": a.cls, "K": Kf, "n": A.n, "params": int(A.npar), "param_numerators": num.tolist(),
       "exact_fraction": f"{val.numerator}/{val.denominator}", "exact_decimal": float(val),
       "float_check": ff, "candidate_sha256": sha, "x_source": a.x,
       "method": "vertex-transitive exact count t=(1/n^3) sum_{b,c,d}; G-invariance of integer matrix checked on all 8 generators; search-code recount, NOT independent"}
json.dump(rep, open(os.path.join(a.out, "exact-report.json"), "w"), indent=1)
print(json.dumps({k: rep[k] for k in ("n", "exact_decimal", "float_check", "candidate_sha256")}))
