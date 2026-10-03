"""C1: exact expansion data for pure-latent lifts of B192.
Delta F = sum_H (1/n^4) sum_{ordered slots} M_H * (prod_{e notin H} W + (-1)^|H| prod Q).
Surviving H (all slot degrees >=2): triangle (x4), C4 (x3), diamond (x6), K4 (x1)."""
import numpy as np, json, sys, itertools, collections
from base import base
p, h = 0.7791808266653855, 0.5342650498652971
W, typ, cls = base(p, h); n = 192; Q = 1 - W; sig = 1 - 2*W
fr = (W > 0) & (W < 1)
a = np.where(fr, np.minimum(W, Q), 0.0)          # box radius
nb = [list(np.nonzero(fr[u])[0]) for u in range(n)]
comp = np.zeros(n, int) - 1; c = 0
for s in range(n):
    if comp[s] >= 0: continue
    st = [s]; comp[s] = c
    while st:
        u = st.pop()
        for v in nb[u]:
            if comp[v] < 0: comp[v] = c; st.append(v)
    c += 1
ft = lambda u, v: typ[u, v]
# triangle coefficient c3(a,b,c) = sum_d (W W W - Q Q Q)
tris = [(x, y, z) for x in range(n) for y in nb[x] for z in nb[y] if fr[z, x] and z != x]
c3 = {t: float((W[t[0]]*W[t[1]]*W[t[2]] - Q[t[0]]*Q[t[1]]*Q[t[2]]).sum()) for t in tris}
tt = collections.Counter(''.join(sorted([ft(x, y), ft(y, z), ft(z, x)])) for (x, y, z) in tris)
v3 = collections.Counter(round(v, 10) for v in c3.values())
# 4-walks (closed, consecutive fractional) with coefficient W_ac W_bd + Q_ac Q_bd (W_uu=0)
c4types = collections.Counter(); c4vals = collections.Counter()
nw4 = 0
for x in range(n):
    for y in nb[x]:
        for z in nb[y]:
            for w in nb[z]:
                if not fr[w, x]: continue
                nw4 += 1
                deg = ('xz' if x == z else '') + ('yw' if y == w else '')
                cf = W[x, z]*W[y, w] + Q[x, z]*Q[y, w]
                key = (deg or 'nondeg', ''.join([ft(x, y), ft(y, z), ft(z, w), ft(w, x)]))
                c4types[key] += 1; c4vals[(deg or 'nondeg', round(float(cf), 8))] += 1
# diamonds: slots a,b adjacent to all; c,d adjacent to a,b; cd free (coefficient -(sigma_cd)); K4 all six
dia = 0; k4 = 0; box5 = 0.0; box6 = 0.0
for x in range(n):
    for y in nb[x]:
        cn = [z for z in nb[x] if fr[z, y]]
        for z in cn:
            for w in cn:
                # ordered diamond with spine (x,y), wings z,w (z may equal w? then slot z=w: edges xz,yz,xw,yw -> same pair twice; allowed as independent latents)
                dia += 1
                box5 += abs(W[z, w] - Q[z, w]) * a[x, y]*a[x, z]*a[y, z]*a[x, w]*a[y, w]
                if z != w and fr[z, w]:
                    k4 += 1; box6 += 2*a[x, y]*a[x, z]*a[y, z]*a[x, w]*a[y, w]*a[z, w]
# multiplicities: diamond appears in 6 H-choices, each ordered placement: our loop counts ordered (spine x,y ordered, wings ordered) = one labeled H
box5 *= 6/n**4
box6 *= 1/n**4
box3 = 4/n**4*sum(abs(c3[t])*a[t[0], t[1]]*a[t[1], t[2]]*a[t[2], t[0]] for t in tris)
out = dict(components=int(c), comp_sizes=[int((comp == i).sum()) for i in range(c)],
           ordered_triangles=len(tris), triangle_types=dict(tt), c3_values={str(k): v for k, v in v3.items()},
           closed_4walks=nw4, c4_types={str(k): v for k, v in c4types.items()}, c4_coeffs={str(k): v for k, v in c4vals.items()},
           ordered_diamonds=dia, ordered_K4=k4, box_T3=box3, box_T5=box5, box_T6=box6)
print(json.dumps(out, indent=1))
json.dump(out, open(sys.argv[1] + '/walks.json', 'w'), indent=1)
