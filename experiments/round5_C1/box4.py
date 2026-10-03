import numpy as np, json, sys
from base import base
p, h = 0.7791808266653855, 0.5342650498652971
W, typ, cls = base(p, h); n = 192; Q = 1 - W
fr = (W > 0) & (W < 1); a = np.where(fr, np.minimum(W, Q), 0.0)
nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
neg4 = 0.0; posdeg = 0.0
for x in range(n):
    for y in nb[x]:
        for z in nb[y]:
            for w in nb[z]:
                if not fr[w, x]: continue
                cf = W[x, z]*W[y, w] + Q[x, z]*Q[y, w]
                m = a[x, y]*a[y, z]*a[z, w]*a[w, x]
                if x == z or y == w: posdeg += cf*m
                else: neg4 += cf*m
print('box nondeg T4', 3*neg4/n**4, ' max degenerate (>=0) T4', 3*posdeg/n**4)
w = json.load(open('../../reports/round5-C1-walks-001/walks.json'))
tot = w['box_T3'] + 3*neg4/n**4 + w['box_T5'] + w['box_T6']
print('crude rigorous box ceiling on gain', tot, 'B192 - ceiling', 0.030138977289665334 - tot)
