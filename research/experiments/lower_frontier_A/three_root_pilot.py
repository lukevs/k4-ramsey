"""Profile the two complement-quotiented three-root N9 blocks, no solve."""
import json,time,resource,multiprocessing as mp
from pathlib import Path
mp.cpu_count=lambda:2
from utilities import Coloring,get_colorings
from verify import get_orbits,get_flowers,get_pair_densities
start=time.monotonic()
def emit(event,**kw):
    print(json.dumps(dict(event=event,elapsed=time.monotonic()-start,**kw)),flush=True)
flags={}; orbit_map={}; types=[]
for t in sorted(get_colorings(3,2,color_invariant=True,mp=None,verbose=False)):
    a=t.automorphisms(color_invariant=True); t.make_ftype(color_invariant=True)
    tm=time.monotonic()
    flags[t]=sorted(get_colorings(6,2,seeds=[t],color_invariant=False,mp=None,verbose=False))
    emit('flags',type=str(t),count=len(flags[t]),seconds=time.monotonic()-tm)
    tm=time.monotonic()
    obs,pos,fg,_=get_orbits(a,flags[t],True)
    orbit_map[t]={p:(i,m) for i,(orbit,m) in enumerate(pos) for p in orbit}
    record=dict(type=str(t),flags=len(flags[t]),group_order=int(fg.order()),flag_orbits=len(obs),
                pair_orbits=len(pos),orbit_seconds=time.monotonic()-tm)
    types.append(record); emit('orbits',**record)
    Path('three-root.json').write_text(json.dumps(dict(types=types),indent=2))
rows=[]
for source in json.loads(Path('pilot.json').read_text())['rows'][4:8]:
    g=Coloring.from_string(source['graph']); tm=time.monotonic()
    row=get_pair_densities(g,flags,orbit_map,get_flowers(9,[3]),True)
    seconds=time.monotonic()-tm
    comp=Coloring(9,2,edge_colors=[1-e for e in g.edge_colors])
    assert row==get_pair_densities(comp,flags,orbit_map,get_flowers(9,[3]),True)
    rec=dict(graph=str(g),seconds=seconds,nnz=sum(len(r) for r in row.values()),
             row={str(t):{str(i):str(v) for i,v in r.items()} for t,r in row.items()})
    rows.append(rec); emit('row',graph=str(g),seconds=seconds,nnz=rec['nnz'])
    Path('three-root.json').write_text(json.dumps(dict(types=types,rows=rows),indent=2))
emit('complete',maxrss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
