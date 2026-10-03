"""Bounded actual N9 rows using unmodified KPS public verifier utilities."""
import json, time, resource, random, multiprocessing as mp
from pathlib import Path
from itertools import combinations
mp.cpu_count = lambda: 2
from utilities import Coloring, get_colorings
from verify import get_orbits, get_flowers, get_pair_densities

start = time.monotonic()
def emit(event, **kw):
    print(json.dumps(dict(event=event, elapsed=time.monotonic()-start, **kw)), flush=True)

t = Coloring(1, ncolors=2)
a = t.automorphisms(color_invariant=True)
t.make_ftype(color_invariant=True)
flags = sorted(get_colorings(5, ncolors=2, seeds=[t], color_invariant=False, mp=None, verbose=False))
emit('flags', count=len(flags), automorphism_order=int(a.order()))
obs, pos, fg, _ = get_orbits(a, flags, True)
emit('orbits', flag_orbits=len(obs), pair_orbits=len(pos), group_order=int(fg.order()))
orbit_map = {t: {pair:(i,m) for i,(orbit,m) in enumerate(pos) for pair in orbit}}
flowers = get_flowers(9,[1])
rng = random.Random(20260930)
examples = [[0]*36, [1]*36,
            [int(i<4 and j<4) for i,j in combinations(range(9),2)],
            [int((i-j)%9 in (1,8)) for i,j in combinations(range(9),2)]]
examples += [[rng.randrange(2) for _ in range(36)] for _ in range(8)]
rows=[]
for k,edges in enumerate(examples):
    g=Coloring(9,2,edge_colors=edges)
    tm=time.monotonic()
    row=get_pair_densities(g,{t:flags},orbit_map,flowers,True)[t]
    seconds=time.monotonic()-tm
    # The routine stores each orbit-average matrix entry, not total orbit mass.
    # Frobenius product against the all-ones matrix must equal one.
    mass=sum(v*len(pos[i][0])/int(fg.order()) for i,v in row.items())
    assert mass == 1, (k,mass)
    complement=Coloring(9,2,edge_colors=[1-e for e in edges])
    crow=get_pair_densities(complement,{t:flags},orbit_map,flowers,True)[t]
    assert row == crow
    count=sum(len({edges[list(combinations(range(9),2)).index(e)] for e in combinations(S,2)})==1
              for S in combinations(range(9),4))
    entry=dict(graph=str(g), seconds=seconds, nonzero_pair_orbits=len(row),
               objective_numerator=count, objective_denominator=126,
               mass=str(mass), row={str(i):str(v) for i,v in row.items()})
    rows.append(entry)
    emit('row', index=k, seconds=seconds, nnz=len(row), monochromatic_k4=count, mass=str(mass))
    Path('pilot.json').write_text(json.dumps(dict(flags=[str(f) for f in flags],
         pair_orbits=[dict(pairs=[[str(x),str(y)] for x,y in orbit],multiplicity=int(m)) for orbit,m in pos],
         rows=rows),indent=2))
emit('complete', maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
