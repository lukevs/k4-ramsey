"""E11 step 1: write B192 in F2^4 x [12] coordinates. Saves coords.json."""
import json, sys, itertools, collections
import numpy as np
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
B = np.array(json.loads((ROOT/"reports/literature-two-parameter-001/graphon-candidate.json").read_text())["red_probability_numerators"])
sym = np.zeros(B.shape, int); sym[B==65536]=1; sym[B==51064]=2; sym[B==35015]=3; np.fill_diagonal(sym,0)
from sympy.combinatorics import Permutation, PermutationGroup
d=json.load(open(ROOT/'reports/group-recovery-orbitals-001/generators.json'))
G=PermutationGroup([Permutation(p) for p in d['point_stabilizer_generators']+d['transitive_movers']])
orbs=[sorted(o) for o in G.derived_series()[-1].orbits()]
assert len(orbs)==12
S=[1,2,4,8,15]
def labelings(blk):
    """all bijections F2^4 -> blk that are Clebsch isomorphisms (0-graph)."""
    A={u:{v for v in blk if v!=u and sym[u,v]==0} for u in blk}
    out=[]
    for r in blk:
        nb=sorted(A[r])
        for perm in itertools.permutations(nb):
            lab={0:r}
            for s,v in zip(S,perm): lab[s]=v
            ok=True
            for i,j in itertools.combinations(range(5),2):
                com=[w for w in blk if w!=r and w not in A[r] and perm[i] in A[w] and perm[j] in A[w]]
                if len(com)!=1: ok=False;break
                lab[S[i]^S[j]]=com[0]
            if ok and len(lab)==16:
                # verify isomorphism
                if all((sym[lab[x],lab[y]]==0)==(bin(x^y).count('1') in (1,4) and (x^y) in S) for x in range(16) for y in range(16) if x!=y):
                    out.append(lab)
    return out
L0=labelings(orbs[0]); print('labelings of block0',len(L0))
lab=[None]*12; lab[0]=L0[0]
def M(s,t):
    return np.array([[sym[lab[s][x],lab[t][y]] for y in range(16)] for x in range(16)])
def transl(Mx):
    f={}
    for x in range(16):
        for y in range(16):
            z=x^y
            if f.setdefault(z,Mx[x,y])!=Mx[x,y]: return None
    return f
Ls={t:labelings(orbs[t]) for t in range(1,12)}
# greedy: choose labeling of t making M(0,t) translation-invariant; collect candidates
cands={}
for t in range(1,12):
    cands[t]=[]
    for L in Ls[t]:
        lab[t]=L
        f=transl(M(0,t))
        if f is not None: cands[t].append(L)
    print(t,'translation-invariant labelings vs block0:',len(cands[t]))
# backtrack for global consistency
order=list(range(1,12))
def bt(k):
    if k==len(order): return True
    t=order[k]
    for L in cands[t]:
        lab[t]=L
        if all(transl(M(u,t)) is not None for u in order[:k]):
            if bt(k+1): return True
    lab[t]=None; return False
print('global:',bt(0))
names={0:'0',1:'F',2:'P',3:'H'}
def cls(z): return 0 if z==0 else (1 if z in S else 2)
table={}
for s in range(12):
    for t in range(12):
        f=transl(M(s,t)); table[(s,t)]=''.join(names[f[z]] for z in range(16))
for s in range(12): print(s,' '.join(table[(s,t)] for t in range(12)))
json.dump({'blocks':orbs,'labels':[{str(k):int(v) for k,v in L.items()} for L in lab],
           'table':{f'{s},{t}':table[(s,t)] for s in range(12) for t in range(12)}},open(ROOT/'experiments/round4_E11/coords.json','w'))
