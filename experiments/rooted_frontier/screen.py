import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import json,itertools,struct,sys,signal,time
from pathlib import Path
import numpy as np
signal.alarm(175);t0=time.monotonic();out=Path('reports/rooted-frontier-001')
with open(out/'events.bin','rb') as f:
 n,d,ne=struct.unpack('iii',f.read(12));reps=np.fromfile(f,dtype=np.int32,count=2*d).reshape(2,d)
E=np.memmap(out/'events.bin',dtype=np.uint16,mode='r',offset=12+8*d,shape=(n,ne,3))
roundno=int(sys.argv[1]) if len(sys.argv)>1 else 0
source=Path('reports/energy-bootstrap-n8-001/cut-result.json') if roundno==0 else out/f'solve-{roundno-1}.json'
q=np.array(json.loads(source.read_text())['primal8']);q=q/q.sum()
if roundno==0:
 # Independent dictionary/adjacency enumeration, compared as multisets (not ordering).
 from collections import Counter
 graphs=json.loads(Path('reports/energy-bootstrap-n8-001/graphs8.json').read_text())
 pairs=list(itertools.combinations(range(8),2));p5=list(itertools.combinations(range(5),2));perms=list(itertools.permutations(range(2,5)))
 lookup=[{int(v):i for i,v in enumerate(r)} for r in reps]
 for gi in [0,1,13,101,3001,n-1]:
  adj=[[0]*8 for _ in range(8)]
  for k,(a,b) in enumerate(pairs):adj[a][b]=adj[b][a]=(graphs[gi]>>k)&1
  expected=Counter()
  def flag(v):
   return min(sum(adj[v[p[a]]][v[p[b]]]<<k for k,(a,b) in enumerate(p5)) for perm in perms for p in [(0,1)+perm])
  for a,b in itertools.permutations(range(8),2):
   rest=set(range(8))-{a,b};typ=adj[a][b]
   for s in itertools.combinations(sorted(rest),3):
    i=lookup[typ][flag([a,b]+list(s))];j=lookup[typ][flag([a,b]+sorted(rest-set(s)))];expected[typ,i,j]+=1
  assert expected==Counter(map(tuple,E[gi].tolist())),gi
 (out/'coefficient-check.json').write_text(json.dumps({'passed':True,'fixtures':[0,1,13,101,3001,n-1],'method':'Separate adjacency and permutation implementation; full event multiset per fixture.','denominator':ne,'dimensions':[d,d]},indent=2))
encoded=np.array(E[:,:,0],dtype=np.int32)*d*d+np.array(E[:,:,1],dtype=np.int32)*d+E[:,:,2]
M=np.bincount(encoded.ravel(),weights=np.repeat(q/ne,ne),minlength=2*d*d).reshape(2,d,d)
cuts=[];vectors=[];records=[]
for typ in range(2):
 assert np.max(abs(M[typ]-M[typ].T))<1e-12
 vals,vecs=np.linalg.eigh(M[typ]);records.append({'type':typ,'min_eigenvalue':float(vals[0]),'negative_below_1e-8':int(sum(vals < -1e-8))})
 for k in np.where(vals < -1e-8)[0][:24]:
  # Quantize the direction so each inequality has rational coefficients.
  v=np.rint(vecs[:,k]*100000).astype(np.int64);coeff=np.empty(n,dtype=np.int64)
  for first in range(0,n,256):
   e=E[first:first+256];coeff[first:first+len(e)]=np.sum((e[:,:,0]==typ)*v[e[:,:,1]]*v[e[:,:,2]],axis=1,dtype=np.int64)
  cuts.append(coeff);vectors.append({'type':typ,'vector':v.tolist(),'denominator':ne*100000**2,'violation':float(coeff@q/(ne*100000**2))})
np.savez_compressed(out/f'cuts-{roundno}.npz',coefficients=np.array(cuts,dtype=np.int64),denominator=ne*100000**2)
r={'round':roundno,'source':str(source),'matrices':records,'cuts':vectors,'seconds':time.monotonic()-t0,'numerical_only':True}
(out/f'screen-{roundno}.json').write_text(json.dumps(r,indent=2));print(json.dumps({k:v for k,v in r.items() if k!='cuts'}),flush=True);print('cuts',len(cuts),flush=True)
