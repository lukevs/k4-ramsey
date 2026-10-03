"""R2 sanity: structural invariants of the recovered degree-192 group (order 46080)."""
import json, collections
from sympy.combinatorics import Permutation, PermutationGroup
d=json.load(open('reports/group-recovery-orbitals-001/generators.json'))
gens=[Permutation(p) for p in d['point_stabilizer_generators']+d['transitive_movers']]
G=PermutationGroup(gens); print('order',G.order(),'transitive',G.is_transitive(),'solvable',G.is_solvable)
ds=G.derived_series(); print('derived series orders',[H.order() for H in ds])
print('center',G.center().order())
bl=G.minimal_blocks(); print('minimal block systems (#blocks):',[len(set(b)) for b in bl])
# elements orders distribution of G via random sampling is slow; count of Sylow-2 order
print('max normal abelian? derived subgroup abelian:', ds[1].is_abelian if len(ds)>1 else None)
N=ds[-1]; print('last derived term order',N.order(), 'orbits',sorted(collections.Counter(len(o) for o in N.orbits()).items()))
# restrict perfect core to one 16-point orbit: suborbits of its point stabilizer
orb=sorted(N.orbits()[0] if False else list(N.orbits())[0]); idx={v:i for i,v in enumerate(orb)}
R=PermutationGroup([Permutation([idx[g(v)] for v in orb]) for g in N.generators])
print('restricted order',R.order())
S=R.stabilizer(0); print('stab order',S.order(),'suborbits',sorted(len(o) for o in S.orbits()))
# G's point stabilizer (sympy) suborbits and quotient action on the 12 core-orbits
orbs=list(N.orbits()); where={v:k for k,o in enumerate(orbs) for v in o}
Q=PermutationGroup([Permutation([where[g(next(iter(o)))] for o in orbs]) for g in G.generators])
print('action on 12 core orbits: order',Q.order(),'transitive',Q.is_transitive(),'blocks',[len(set(b)) for b in Q.minimal_blocks()])
