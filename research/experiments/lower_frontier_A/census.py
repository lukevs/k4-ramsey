"""Exact Burnside census; no graph enumeration, dependencies or floats."""
from itertools import combinations
from math import factorial
from collections import Counter
from fractions import Fraction
import json, time

def partitions(n, minimum=1):
    if not n:
        yield ()
    for k in range(minimum,n+1):
        for tail in partitions(n-k,k): yield (k,)+tail

def fixed_counts(n, roots=0):
    total=twisted=0
    for part in partitions(n-roots):
        z=1
        for length,count in Counter(part).items(): z*=length**count*factorial(count)
        multiplicity=factorial(n-roots)//z
        perm=list(range(roots)); offset=roots
        for length in part:
            perm += list(range(offset+1,offset+length))+[offset]
            offset+=length
        edges=set((i,j) for i,j in combinations(range(n),2) if j>=roots)
        lengths=[]
        while edges:
            e=next(iter(edges)); current=e; length=0
            while current in edges:
                edges.remove(current); length+=1
                current=tuple(sorted((perm[current[0]],perm[current[1]])))
            assert current==e
            lengths.append(length)
        total+=multiplicity*2**len(lengths)
        if all(x%2==0 for x in lengths): twisted+=multiplicity*2**len(lengths)
    den=factorial(n-roots)
    assert total%den==twisted%den==0
    return total//den,twisted//den

if __name__=='__main__':
    start=time.monotonic(); records=[]
    for n in range(1,10):
        ordinary,self_complementary=fixed_counts(n)
        reduced=(ordinary+self_complementary)//2
        records.append(dict(n=n,ordinary=ordinary,self_complementary=self_complementary,
                            colour_quotient=reduced,dense_schur_bytes=8*reduced**2,
                            packed_schur_bytes=8*reduced*(reduced+1)//2))
    flag_counts=[]
    for t in (1,3,5,7):
        m=(9+t)//2
        f,_=fixed_counts(m,t)
        types,sc=fixed_counts(t)
        flag_counts.append(dict(roots=t,flag_order=m,flags_per_fixed_type=f,
                               ordinary_types=types,colour_quotient_types=(types+sc)//2,
                               raw_symmetric_entries_per_type=f*(f+1)//2))
    assert [r['ordinary'] for r in records]==[1,2,4,11,34,156,1044,12346,274668]
    result=dict(counts=records,N9_flags=flag_counts,seconds=time.monotonic()-start)
    print(json.dumps(result,indent=2))
