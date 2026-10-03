import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import sys,json,itertools as it,signal
from pathlib import Path
import numpy as np
import networkx as nx
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
out=Path('reports/energy-bootstrap-n7-001')
def pairs(n):return list(it.combinations(range(n),2))
def bits(A,vs):return sum(int(A[vs[i],vs[j]])<<k for k,(i,j) in enumerate(pairs(len(vs))))
graphs=[nx.to_numpy_array(g,dtype=np.int8) for g in nx.graph_atlas_g() if len(g)==7]
bs=[]
# Export ALL canonical rooted types at N7, with extras modulo their own labels.
for r in (1,3,5):
 s=(7+r)//2;k=s-r; pp=pairs(s);rootpairs=pairs(r)
 types=[nx.to_numpy_array(g,dtype=np.int8) for g in nx.graph_atlas_g() if len(g)==r]
 for A in types:
  typ=bits(A,list(range(r))); fixed={p:int(A[p]) for p in rootpairs}; free=[p for p in pp if p not in fixed]; groups={};lookup=[-1]*(1<<len(pp));flags=[]
  for f in range(1<<len(free)):
   B=np.zeros((s,s),dtype=np.int8)
   for (i,j),v in fixed.items():B[i,j]=B[j,i]=v
   for j,(a,b) in enumerate(free):B[a,b]=B[b,a]=(f>>j)&1
   code=bits(B,list(range(s)));canon=min(bits(B,list(range(r))+list(t)) for t in it.permutations(range(r,s)))
   if canon not in groups:groups[canon]=len(groups);flags.append(canon)
   lookup[code]=groups[canon]
  bs.append(dict(r=r,s=s,t=typ,d=len(groups),lookup=lookup,flags=flags))
meta={'graphs':[bits(A,list(range(7))) for A in graphs],'blocks':bs}
(out/'metadata.json').write_text(json.dumps(meta))
lines=[f'{len(bs)} {len(graphs)}',' '.join(map(str,meta['graphs']))]
for b in bs:lines+=[' '.join(str(b[k]) for k in ('r','s','t','d')),' '.join(map(str,b['lookup']))]
(out/'input.txt').write_text('\n'.join(lines)+'\n')
print('blocks',len(bs),'dimensions',[b['d'] for b in bs],flush=True)
