from sage.all import graphs
import json
from pathlib import Path
H=graphs.HigmanSimsGraph(relabel=False)
vs=sorted(H.vertices(sort=False));idx={v:i for i,v in enumerate(vs)}
a=vs[0];b=sorted(H.neighbors(a))[0]
subsets={'higman_sims':vs,'M22':[v for v in vs if v!=a and not H.has_edge(a,v)],'gewirtz':[v for v in vs if v not in (a,b) and not H.has_edge(a,v) and not H.has_edge(b,v)]}
data={}
for name,S in subsets.items():
 A=[[int(H.has_edge(x,y)) for y in S] for x in S]
 data[name]={'adjacency':A,'labels':S,'ambient_groups':[int(v[0]) for v in S]}
Path('/home/researcher/graph-arrangements.json').write_text(json.dumps(data)+'\n')
print({k:len(v['adjacency']) for k,v in data.items()})
