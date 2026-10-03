"""Independent literal root/split enumeration; imports no Sage/KPS code."""
import json,time
from itertools import combinations, permutations
from fractions import Fraction
from collections import Counter
from functools import lru_cache
from pathlib import Path

start=time.monotonic()
edges5=list(combinations(range(5),2))
edges9=list(combinations(range(9),2))
def decode(s):
    _,uniformity,colours,n,t,encoding=s.split('.')
    n=int(n); value=int(encoding,36)
    return n,[(value>>i)&1 for i in reversed(range(n*(n-1)//2))]

@lru_cache(None)
def canonical(bits):
    lookup=dict(zip(edges5,bits))
    ans=[]
    for perm in permutations(range(1,5)):
        p=(0,)+perm
        ans.append(tuple(lookup[tuple(sorted((p[i],p[j])))] for i,j in edges5))
    return min(ans)

d=json.loads(Path('reports/lower-frontier-A-recovery/pilot.json').read_text())
flagkeys={s:canonical(tuple(decode(s)[1])) for s in d['flags']}
assert len(set(flagkeys.values()))==90
lookup={}
for i,orbit in enumerate(d['pair_orbits']):
    for x,y in orbit['pairs']:
        lookup[(flagkeys[x],flagkeys[y])]=i
results=[]
for row in d['rows']:
    n,bits=decode(row['graph']); G=dict(zip(edges9,bits)); counts=Counter()
    for root in range(9):
        free=[i for i in range(9) if i!=root]
        for S in combinations(free,4):
            T=tuple(i for i in free if i not in S)
            keys=[]
            for vertices in ((root,)+S,(root,)+T):
                keys.append(canonical(tuple(G[tuple(sorted((vertices[i],vertices[j])))] for i,j in edges5)))
            counts[lookup[tuple(keys)]]+=1
    for i in set(counts)|set(map(int,row['row'])):
        orbit_size=len(d['pair_orbits'][i]['pairs'])
        expected=Fraction(2*counts[i],630*orbit_size)
        assert expected==Fraction(row['row'].get(str(i),'0')),(row['graph'],i,expected,row['row'].get(str(i)))
    mono=sum(len({G[e] for e in combinations(S,2)})==1 for S in combinations(range(9),4))
    assert mono==row['objective_numerator']
    assert sum(counts.values())==630
    results.append(dict(graph=row['graph'],checked_nonzero_orbits=len(counts),ordered_root_splits=630,objective=mono))
print(json.dumps(dict(status='PASS',rows=results,seconds=time.monotonic()-start,
                      scope='Exact selected one-root N9 coefficient rows only; no SDP solution or bound.'),indent=2))
