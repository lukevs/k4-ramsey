"""Exact dimensions for sampled symmetry reductions, independently counted."""
from itertools import permutations,combinations
from fractions import Fraction
import json
def fixed_root_action(sigma, free=3):
    r=len(sigma); total=0; perms=list(permutations(range(r,r+free)))
    for tau in perms:
        p=tuple(sigma)+tau
        unseen=set(e for e in combinations(range(r+free),2) if e[1]>=r)
        cycles=0
        while unseen:
            e=next(iter(unseen)); cycles+=1
            while e in unseen:
                unseen.remove(e); e=tuple(sorted((p[e[0]],p[e[1]])))
        total+=2**cycles
    return Fraction(total,len(perms))
e=fixed_root_action((0,1,2)); trans=fixed_root_action((1,0,2)); cyc=fixed_root_action((1,2,0))
assert (e,trans,cyc)==(816,152,24)
path_blocks=[(e+trans)/2,(e-trans)/2]
triangle_blocks=[(e+3*trans+2*cyc)/6,(e-3*trans+2*cyc)/6,(e-cyc)/3]
def symdim(blocks): return int(sum(x*(x+1)/2 for x in blocks))
assert symdim(path_blocks)==172648
assert symdim(triangle_blocks)==61636
print(json.dumps(dict(root1=dict(blocks=[46,44],symmetric_parameters=2071),
 root3_path=dict(blocks=list(map(int,path_blocks)),symmetric_parameters=symdim(path_blocks)),
 root3_triangle=dict(blocks=list(map(int,triangle_blocks)),
                     representation_multiplicities=[1,1,2],symmetric_parameters=symdim(triangle_blocks)),
 explanation='Blocks are multiplicity-space PSD dimensions from exact character counts; no basis-change matrices constructed.'),indent=2))
