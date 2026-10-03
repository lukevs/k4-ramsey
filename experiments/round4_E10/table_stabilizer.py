"""E10a part 2: subgroup of G (all 46080 elements) preserving the active set, and
the subgroup acting on holonomies by a global character eps in {+1,-1}."""
import json, collections, sys
import numpy as np
sys.path.insert(0,'experiments/round4_E9')
from lift import load_base, pairs
from sympy.combinatorics import Permutation, PermutationGroup
sym, ph = load_base(); prs = pairs(sym); n=len(sym)
Ginact=np.zeros((n,n),bool); Gph=np.full((n,n),-1)
for i,j in prs:
    v=ph[f"{i},{j}"]
    if v<0: Ginact[i,j]=Ginact[j,i]=True
    else: Gph[i,j]=v%5; Gph[j,i]=(-v)%5
P=np.array(prs); I=P[:,0]; J=P[:,1]
act=collections.defaultdict(set)
for i,j in prs:
    if not Ginact[i,j]: act[i].add(j); act[j].add(i)
T=np.array([(i,j,k) for i in range(n) for j in act[i] if j>i for k in act[j] if k>j and k in act[i]])
def holv(a,b,c): return (Gph[a,b]+Gph[b,c]+Gph[c,a])%5
H0=holv(T[:,0],T[:,1],T[:,2])
d=json.load(open('reports/group-recovery-orbitals-001/generators.json'))
G=PermutationGroup([Permutation(p) for p in d['point_stabilizer_generators']+d['transitive_movers']])
stabA=[]; stabC=collections.Counter(); cnt=0
for s in G.generate():
    a=np.array(s.array_form); cnt+=1
    if not np.array_equal(Ginact[a[I],a[J]],Ginact[I,J]): continue
    h=holv(a[T[:,0]],a[T[:,1]],a[T[:,2]])
    r=set(((h*pow(int(x),-1,5))%5 for x,h in zip(H0,h)))
    stabA.append(s); stabC[tuple(sorted(r))]+=1
print('elements',cnt,'preserving active set',len(stabA),'ratio classes',stabC)
S=PermutationGroup(stabA) if stabA else None
print('stab order',S.order(), 'orbits sizes',sorted(len(o) for o in S.orbits()))
