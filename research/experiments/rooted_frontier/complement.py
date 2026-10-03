"""Find and explicitly verify colour-complement pairs of N8 representatives."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import json,itertools,time,signal
from collections import defaultdict
from pathlib import Path
import networkx as nx
signal.alarm(175);t0=time.monotonic();out=Path('reports/rooted-full-001');codes=json.loads(Path('reports/energy-bootstrap-n8-001/graphs8.json').read_text());pairs=list(itertools.combinations(range(8),2))
def graph(g):
 G=nx.Graph();G.add_nodes_from(range(8));G.add_edges_from(e for k,e in enumerate(pairs) if g>>k&1);return G
Gs=[graph(g) for g in codes];buckets=defaultdict(list)
for i,G in enumerate(Gs):buckets[nx.weisfeiler_lehman_graph_hash(G,iterations=3)].append(i)
comp=[-1]*len(Gs);witnesses=[]
for i,G in enumerate(Gs):
 if comp[i]>=0:continue
 H=nx.complement(G)
 for j in buckets[nx.weisfeiler_lehman_graph_hash(H,iterations=3)]:
  gm=nx.algorithms.isomorphism.GraphMatcher(H,Gs[j])
  if not gm.is_isomorphic():continue
  m=gm.mapping;assert len(set(m.values()))==8
  assert all(Gs[j].has_edge(m[a],m[b]) != G.has_edge(a,b) for a,b in pairs)
  comp[i]=j;comp[j]=i;witnesses.append({'i':i,'j':j,'permutation':[m[a] for a in range(8)]});break
 assert comp[i]>=0,i
assert all(comp[comp[i]]==i for i in range(len(Gs)))
r={'complement':comp,'witnesses':witnesses,'orbits':len(witnesses),'self_complementary':sum(i==j for i,j in enumerate(comp)),'seconds':time.monotonic()-t0,'all_permutations_explicitly_checked':True}
(out/'complement.json').write_text(json.dumps(r));print({k:v for k,v in r.items() if k not in ['complement','witnesses']},flush=True)
