"""R2 sanity: gauge-invariant content of the Z5 phase table (triangle holonomies),
and how active/inactive pairs sit relative to the 12 Clebsch (16-point) core orbits."""
import json, collections, sys
sys.path.insert(0,'research/experiments/round4_E9')
from lift import load_base, pairs
from sympy.combinatorics import Permutation, PermutationGroup
sym, ph = load_base(); prs = pairs(sym); n=len(sym)
g={}
for i,j in prs:
    v=ph[f"{i},{j}"]
    if v>=0: g[(i,j)]=v%5; g[(j,i)]=(-v)%5
act=collections.defaultdict(set)
for (i,j) in g: act[i].add(j)
hol=collections.Counter(); typ=collections.Counter()
for i in range(n):
    for j in act[i]:
        if j<=i: continue
        for k in act[j]:
            if k<=j or k not in act[i]: continue
            h=(g[(i,j)]+g[(j,k)]+g[(k,i)])%5
            t=tuple(sorted([sym[i,j],sym[j,k],sym[i,k]]))
            hol[(t,h)]+=1
print('active-triangle holonomy counts ((sym types),hol):',sorted(hol.items()))
d=json.load(open('reports/group-recovery-orbitals-001/generators.json'))
G=PermutationGroup([Permutation(p) for p in d['point_stabilizer_generators']+d['transitive_movers']])
N=G.derived_series()[-1]; orbs=list(N.orbits()); where={v:k for k,o in enumerate(orbs) for v in o}
c=collections.Counter()
for i,j in prs:
    v=ph[f"{i},{j}"]; c[(int(sym[i,j]),'same16' if where[i]==where[j] else 'cross', 'inactive' if v<0 else 'active')]+=1
print('pair placement:',sorted(c.items()))
c2=collections.Counter((int(sym[i,j]), where[i]==where[j]) for i in range(n) for j in range(n) if i!=j)
print('all symbols same/cross 16-orbit:',sorted(c2.items()))
