import json,struct,itertools
from pathlib import Path
import numpy as np
from scipy import sparse
p=Path('reports/rooted-full-001');meta=json.loads((p/'metadata.json').read_text());graphs=json.loads(Path('reports/energy-bootstrap-n8-001/graphs8.json').read_text())
pairs=list(itertools.combinations(range(5),2));ix={p:i for i,p in enumerate(pairs)}
def perm(g,p):return sum(((g>>ix[tuple(sorted((p[a],p[b])))])&1)<<j for j,(a,b) in enumerate(pairs))
def canon(g):return min(perm(g,(0,1)+p) for p in itertools.permutations([2,3,4]))
codes=[canon(g) for g in range(1024)];reps=[sorted(set(codes[t::2])) for t in range(2)];lookup=[reps[g&1].index(codes[g]) for g in range(1024)]
lines=[str(len(graphs)),' '.join(map(str,graphs)),' '.join(map(str,lookup))]
for typ in range(2):
 m=meta['maps'][typ];swap=[reps[typ].index(canon(perm(g,(1,0,2,3,4)))) for g in reps[typ]];assert swap==m['swap']
 T=np.zeros((120,120),dtype=np.int64)
 for i in range(120):
  T[i,m['plus'][i]]=1
  if m['minus'][i]>=0:T[i,74+m['minus'][i]]=m['sign'][i]
 gram=T.T@T;assert np.count_nonzero(gram-np.diag(np.diag(gram)))==0 and np.min(np.diag(gram))>0
 for key in ['plus','minus','sign']:lines.append(' '.join(map(str,m[key])))
(p/'check-full.txt').write_text('\n'.join(lines)+'\n')
for b in meta['blocks']:
 C=sparse.load_npz(p/(b['name']+'.npz')).tocsc();C.sort_indices()
 with open(p/(b['name']+'-check.bin'),'wb') as f:
  f.write(struct.pack('iii',len(graphs),b['dimension'],C.nnz));C.indptr.astype(np.int32).tofile(f);C.indices.astype(np.int32).tofile(f);C.data.astype(np.int16).tofile(f)
