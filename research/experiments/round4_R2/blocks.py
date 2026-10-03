"""R2 sanity: 12x12 block structure of B192 over the Clebsch core orbits; srg check of intra-block graph."""
import json, collections, sys
import numpy as np
sys.path.insert(0,'research/experiments/round4_E9')
from lift import load_base
from sympy.combinatorics import Permutation, PermutationGroup
sym,_=load_base(); n=len(sym)
d=json.load(open('reports/group-recovery-orbitals-001/generators.json'))
G=PermutationGroup([Permutation(p) for p in d['point_stabilizer_generators']+d['transitive_movers']])
orbs=[sorted(o) for o in G.derived_series()[-1].orbits()]
A=(sym[np.ix_(orbs[0],orbs[0])]==0).astype(int); np.fill_diagonal(A,0)
k=A.sum(1)[0]; A2=A@A
lam={int(A2[i,j]) for i in range(16) for j in range(16) if i!=j and A[i,j]}; mu={int(A2[i,j]) for i in range(16) for j in range(16) if i!=j and not A[i,j]}
print('intra-block 0-graph: k',k,'lambda',lam,'mu',mu,'eig',np.round(np.linalg.eigvalsh(A),3))
pat=collections.Counter()
for a in range(12):
    row=[]
    for b in range(12):
        if a==b: continue
        c=collections.Counter(int(x) for x in sym[np.ix_(orbs[a],orbs[b])].ravel())
        row.append(tuple(c.get(s,0) for s in range(4)))
    pat[tuple(sorted(collections.Counter(row).items()))]+=1
print('per-block multiset of (#0,#F,#P,#H) over the 11 other blocks:',pat)
