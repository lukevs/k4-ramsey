"""R2 sanity: which order-240 subgroups H of W(B6) give a 192-point action with
subdegree multiset matching the recovered quotient (24 suborbits; the fractional
P/H neighbours lie in suborbits of sizes 5,1,5,1 (P) and 1 (H))."""
import itertools, collections
n=6
def mul(a,b):  # signed perm as tuple of (perm, signs): apply b then a
    pa,sa=a; pb,sb=b
    return (tuple(pa[pb[i]] for i in range(n)), tuple(sb[i]*sa[pb[i]] for i in range(n)))
perms=list(itertools.permutations(range(n)))
signs=list(itertools.product([1,-1],repeat=n))
e=(tuple(range(n)),(1,)*n)
def gen_group(gens):
    G={e}; fr=[e]
    while fr:
        nf=[]
        for x in fr:
            for g in gens:
                y=mul(g,x)
                if y not in G: G.add(y); nf.append(y)
        fr=nf
    return G
neg=(tuple(range(n)),(-1,)*n)
# S5 fixing 0
s5fix=[((0,2,1,3,4,5),(1,)*6),((0,2,3,4,5,1),(1,)*6)]
# PGL(2,5) on P^1(F5) = {0..4, inf=5}: x->x+1, x->2x, x->-1/x
def mob(f):
    return tuple(f(x) for x in range(6))
inv={1:1,2:3,3:2,4:4}
def t1(x): return 5 if x==5 else (x+1)%5
def t2(x): return 5 if x==5 else (2*x)%5
def t3(x): return 0 if x==5 else (5 if x==0 else (-inv[x])%5)
pgl=[(mob(t1),(1,)*6),(mob(t2),(1,)*6),(mob(t3),(1,)*6)]
def sgnperm(p):
    s=1;p=list(p)
    for i in range(n):
        while p[i]!=i:
            j=p[i]; p[i],p[j]=p[j],p[i]; s=-s
    return s
cands={
 'C2(-1) x S5fix':s5fix+[neg],
 'C2(-1) x PGL25':pgl+[neg],
 'flip0 x S5fix':s5fix+[(tuple(range(6)),(-1,1,1,1,1,1))],
 'PGL25 twisted by sign*(-1)':[(p,(sgnperm(p),)*6) for p,_ in pgl]+[neg],
 'S5fix twisted sign*(-1)':[(p,(sgnperm(p),)*6) for p,_ in s5fix]+[neg],
}
G=gen_group([((1,0,2,3,4,5),(1,)*6),((1,2,3,4,5,0),(1,)*6),(tuple(range(6)),(-1,1,1,1,1,1))])
print('|W(B6)|',len(G))
def inverse(a):
    p,s=a; q=[0]*n; t=[0]*n
    for i in range(n): q[p[i]]=i
    # a: x_i -> s_i at p[i]; inverse
    for i in range(n): t[p[i]]=s[i]
    return (tuple(q),tuple(t))
for name,gens in cands.items():
    H=gen_group(gens)
    if len(H)!=240: print(name,'order',len(H)); continue
    # cosets gH
    rep={};cos=[]
    for g in G:
        if g in rep: continue
        c=frozenset(mul(g,h) for h in H); idx=len(cos); cos.append(c)
        for x in c: rep[x]=idx
    # suborbits of H on cosets
    seen=set(); sub=[]
    for i,c in enumerate(cos):
        if i in seen: continue
        g=next(iter(c)); orb={rep[mul(h,g)] for h in H}
        seen|=orb; sub.append(len(orb))
    print(name,'points',len(cos),'suborbits',len(sub),sorted(collections.Counter(sub).items()))
