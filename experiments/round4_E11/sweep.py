"""E11 sweep: vary the connection set C (group Z, 0 in C) keeping the 12-block type design.
usage: sweep.py OUTDIR mode   mode in f2_4 | f2_3 | zm | f2_5"""
import sys, json, time, itertools, random
import numpy as np
sys.path.insert(0, str(__import__('pathlib').Path(__file__).resolve().parent))
from family import T12, evalfam, opt, f2, zm
out = sys.argv[1]; mode = sys.argv[2]
p0, h0 = 32/41, 22/41
res = []
t0 = time.time()
def rec(name, grp):
    v = evalfam(T12, grp, p0, h0)
    res.append((v, name, grp))
if mode in ('f2_4', 'f2_3'):
    n = 4 if mode == 'f2_4' else 3
    for mask in range(2**(2**n - 1)):
        Sv = [i+1 for i in range(2**n - 1) if mask >> i & 1]
        rec(str(Sv), f2(n, Sv))
elif mode == 'zm':
    for m in range(4, 25):
        half = list(range(1, m//2 + 1))
        for mask in range(2**len(half)):
            Ss = set()
            for i, a in enumerate(half):
                if mask >> i & 1: Ss |= {a, (-a) % m}
            rec(f'Z{m}:{sorted(Ss)}', zm(m, Ss))
elif mode == 'f2_5':
    named = {'folded6cube': [1,2,4,8,16,31], 'clebsch_x_F2(blowup)': [1,2,4,8,15,16,17,18,20,24,31],
             'clebsch_in_hyperplane': [1,2,4,8,15]}
    for k, v in named.items(): rec(k, f2(5, v))
    # local search from random & from blowup, flip one element (fixed p,h)
    random.seed(11)
    for start in ([1,2,4,8,16,31], [1,2,4,8,15,16,17,18,20,24,31]):
        cur = set(start); cv = evalfam(T12, f2(5, cur), p0, h0)
        improved = True
        while improved and time.time() - t0 < 300:
            improved = False
            for e in random.sample(range(1, 32), 31):
                c2 = cur ^ {e}; v = evalfam(T12, f2(5, c2), p0, h0)
                if v < cv - 1e-13: cur, cv, improved = c2, v, True
        rec('LS_from_' + str(start), f2(5, sorted(cur)))
res.sort(key=lambda r: r[0])
print('evaluated', len(res), 'in', time.time() - t0)
top = []
for v, name, grp in res[:12]:
    fo, xo = opt(T12, grp)
    top.append({'name': name, 'q': len(grp[0]), 'C': sorted(grp[2]), 'F_fixed': v, 'F_opt_ph': fo, 'ph': xo})
    print(name, len(grp[2]), '/', len(grp[0]), 'fixed', v, 'opt', fo, xo, flush=True)
json.dump({'mode': mode, 'n_evaluated': len(res), 'top': top,
           'fixed_hist_best20': [(r[0], r[1]) for r in res[:20]]}, open(out + f'/{mode}.json', 'w'), indent=1)
