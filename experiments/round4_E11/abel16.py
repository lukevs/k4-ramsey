"""E11: exhaustive symmetric connection sets C (0 in C) on abelian groups of order 16 (and 8, 32 partially), design kept."""
import sys, json, itertools, time, numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from family import T12, evalfam, opt
def grp(mods):
    els = list(itertools.product(*[range(m) for m in mods])); idx = {e: i for i, e in enumerate(els)}
    sub = lambda x, y: idx[tuple((a - b) % m for a, b, m in zip(els[x], els[y], mods))]
    neg = lambda x: idx[tuple((-a) % m for a, m in zip(els[x], mods))]
    orbs = []; seen = {0}
    for x in range(1, len(els)):
        if x in seen: continue
        o = {x, neg(x)}; seen |= o; orbs.append(o)
    return els, sub, orbs
out = {}
for mods in [(4, 4), (2, 8), (2, 2, 4), (16,), (2, 4)]:
    els, sub, orbs = grp(mods); t0 = time.time(); res = []
    for mask in range(2**len(orbs)):
        C = {0}
        for i, o in enumerate(orbs):
            if mask >> i & 1: C |= o
        res.append((evalfam(T12, (els, sub, C), 32/41, 22/41), sorted(C)))
    res.sort()
    fo, xo = opt(T12, (els, sub, set(res[0][1])))
    out[str(mods)] = {'n_sets': len(res), 'best_fixed': res[0][0], 'best_C': [els[i] for i in res[0][1]], 'best_opt': fo, 'ph': list(xo)}
    print(mods, len(res), res[0][0], [els[i] for i in res[0][1]], 'opt', fo, round(time.time()-t0, 1), flush=True)
json.dump(out, open(sys.argv[1] + '/abel16.json', 'w'), indent=1, default=float)
