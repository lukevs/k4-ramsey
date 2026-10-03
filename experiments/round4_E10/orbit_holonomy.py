"""E10a: is the Z5 holonomy table determined by symmetry?
Oriented active triangles; for each group element s, test hol(sT) = eps(s)*hol(T)."""
import json, collections, sys, random
sys.path.insert(0,'experiments/round4_E9')
from lift import load_base, pairs
from sympy.combinatorics import Permutation, PermutationGroup
sym, ph = load_base(); prs = pairs(sym); n=len(sym)
g={}; inact=set()
for i,j in prs:
    v=ph[f"{i},{j}"]
    if v>=0: g[(i,j)]=v%5; g[(j,i)]=(-v)%5
    else: inact.add((i,j))
def hol(a,b,c):
    try: return (g[(a,b)]+g[(b,c)]+g[(c,a)])%5
    except KeyError: return None
act=collections.defaultdict(set)
for (i,j) in g: act[i].add(j)
tris=[(i,j,k) for i in range(n) for j in act[i] if j>i for k in act[j] if k>j and k in act[i]]
# all PPH triangles of the symbol structure (active or not)
fr=collections.defaultdict(set)
for i,j in prs: fr[i].add(j); fr[j].add(i)
alltri=[(i,j,k) for i in range(n) for j in fr[i] if j>i for k in fr[j] if k>j and k in fr[i]]
print('active tris',len(tris),'all fractional tris',len(alltri),
      collections.Counter(tuple(sorted([sym[a,b],sym[b,c],sym[a,c]])) for a,b,c in alltri))
d=json.load(open('reports/group-recovery-orbitals-001/generators.json'))
gens=[Permutation(p) for p in d['point_stabilizer_generators']+d['transitive_movers']]
G=PermutationGroup(gens); print('|G|',G.order())
DS=G.derived_series(); print('derived',[H.order() for H in DS])
N=DS[-1]; orbs=list(N.orbits()); blk={v:k for k,o in enumerate(orbs) for v in o}
def ratio(s):
    """return Counter of hol(sT)/hol(T) over active tris with sT active (values in Z5*), and #lost"""
    c=collections.Counter(); lost=0
    for a,b,cc in tris:
        h=hol(a,b,cc); h2=hol(s(a),s(b),s(cc))
        if h2 is None: lost+=1; continue
        c[(h2*pow(h,-1,5))%5 if h else ('h0',h2)]+=1
    return c,lost
def pairstat(s):
    c=collections.Counter()
    for i,j in prs:
        a=(i,j) in inact; si,sj=sorted((s(i),s(j))); b=(si,sj) in inact
        c[(a,b)]+=1
    return c
print('generators:')
for k,s in enumerate(gens): print(k,ratio(s),dict(pairstat(s)))
random.seed(1)
# random elements: record character consistency
tally=collections.Counter()
for t in range(200):
    s=G.random(); c,lost=ratio(s); key=tuple(sorted(c.items(),key=str))
    tally[(len(c),lost)]+=1
print('random elements: (#distinct ratios, lost) ->',tally)
# subgroups: derived core N (960), block kernel K (1920)
def blockfix(s): return all(blk[s(v)]==blk[v] for v in range(n))
Kg=[]; 
while True:
    s=G.random()
    if blockfix(s): Kg.append(s)
    if len(Kg)>=4 and PermutationGroup(Kg).order()>=1920: break
K=PermutationGroup(Kg); print('|K|',K.order())
for name,H in (('N960',N),('K1920',K)):
    tl=collections.Counter(); ps=collections.Counter()
    for s in H.generators:
        c,lost=ratio(s); tl[(tuple(sorted(c.items(),key=str)),lost)]+=1; ps.update(pairstat(s))
    print(name,'gens ratio tallies',tl,'pairs',ps)
# orbit tables of unoriented triangles under N, K, G: sign via canonical orientation = hol in {1,4} as set? record hol of i<j<k
def orbit_table(H):
    idx={t:k for k,t in enumerate(alltri)}; par=list(range(len(alltri)))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for s in H.generators:
        for k,(a,b,c) in enumerate(alltri):
            t=tuple(sorted((s(a),s(b),s(c)))); par[f(k)]=f(idx[t])
    tab=collections.defaultdict(collections.Counter)
    for k,t in enumerate(alltri): tab[f(k)][hol(*t)]+=1
    return tab
for name,H in (('G',G),('N960',N),('K1920',K)):
    tab=orbit_table(H); 
    print(name,'#orbits',len(tab),'orbit hol tallies(i<j<k orientation):',collections.Counter(tuple(sorted(v.items(),key=str)) for v in tab.values()))
# pair orbits under G of P/H pairs: active/inactive split
def pair_orbits(H):
    idx={p:k for k,p in enumerate(prs)}; par=list(range(len(prs)))
    def f(x):
        while par[x]!=x: par[x]=par[par[x]]; x=par[x]
        return x
    for s in H.generators:
        for k,(i,j) in enumerate(prs): par[f(k)]=f(idx[tuple(sorted((s(i),s(j))))])
    tab=collections.defaultdict(collections.Counter)
    for k,p in enumerate(prs): tab[f(k)][(int(sym[p]),p in inact)]+=1
    return tab
for name,H in (('G',G),('N960',N),('K1920',K)):
    print(name,'pair orbits:',sorted(collections.Counter(tuple(sorted(v.items())) for v in pair_orbits(H).values()).items()))
# fractional 4-cycles among active pairs (holonomy distribution)
c4=collections.Counter(); seen=0
for a in range(n):
    for b in act[a]:
        if b<=a: continue
        for c in act[b]:
            if c<=a or c==a: continue
            for dd in act[c]:
                if dd<=a or dd==b or a not in act[dd]: continue
                if b>dd: continue  # count each 4-cycle once (a min, b<d)
                h=(g[(a,b)]+g[(b,c)]+g[(c,dd)]+g[(dd,a)])%5
                chord=(a in act[c]) or (b in act[dd])
                c4[(tuple(sorted([int(sym[a,b]),int(sym[b,c]),int(sym[c,dd]),int(sym[dd,a])])),chord,h)]+=1
print('active 4-cycles (types,has_active_chord,hol):',sorted(c4.items()))
