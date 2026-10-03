"""Exact root-swap block diagonalization of both complete two-root N8 blocks."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import itertools,json,struct,time,signal
from pathlib import Path
import numpy as np
from scipy import sparse
signal.alarm(175);t0=time.monotonic()
src=Path('reports/rooted-frontier-001');out=Path('reports/rooted-full-001');out.mkdir(exist_ok=True)
with open(src/'events.bin','rb') as f:
 n,d,ne=struct.unpack('iii',f.read(12));reps=np.fromfile(f,dtype=np.int32,count=2*d).reshape(2,d)
E=np.memmap(src/'events.bin',dtype=np.uint16,mode='r',offset=12+8*d,shape=(n,ne,3));pairs=list(itertools.combinations(range(5),2));ix={v:i for i,v in enumerate(pairs)}
def relabel(g,p):return sum(((int(g)>>ix[tuple(sorted((p[a],p[b])))])&1)<<k for k,(a,b) in enumerate(pairs))
def canon(g):return min(relabel(g,(0,1)+p) for p in itertools.permutations((2,3,4)))
records=[];maps=[]
for typ in range(2):
 owner={int(v):i for i,v in enumerate(reps[typ])};swap=np.array([owner[canon(relabel(g,(1,0,2,3,4)))] for g in reps[typ]]);assert np.array_equal(swap[swap],np.arange(d))
 plus=np.full(d,-1);minus=np.full(d,-1);sign=np.zeros(d,dtype=np.int16);dp=dm=0
 for i in range(d):
  j=int(swap[i])
  if i>j:continue
  plus[i]=plus[j]=dp;dp+=1
  if i!=j:minus[i]=minus[j]=dm;sign[i]=1;sign[j]=-1;dm+=1
 assert dp+dm==d
 maps.append({'swap':swap.tolist(),'plus':plus.tolist(),'minus':minus.tolist(),'sign':sign.tolist()})
 take=E[:,:,0].ravel()==typ;col=np.repeat(np.arange(n,dtype=np.int32),ne)[take];a=E[:,:,1].ravel()[take];b=E[:,:,2].ravel()[take]
 # Explicitly check root-swap invariance of every coefficient, not only moments.
 raw=sparse.coo_matrix((np.ones(len(a),dtype=np.int16),(a.astype(np.int32)*d+b,col)),shape=(d*d,n)).tocsc()
 perm=(swap[:,None]*d+swap[None,:]).ravel();assert (raw-raw[perm]).nnz==0
 assert (raw-raw[np.arange(d*d).reshape(d,d).T.ravel()]).nnz==0
 del raw
 for parity,idx,sgn,dim in [('plus',plus,np.ones(d,dtype=np.int16),dp),('minus',minus,sign,dm)]:
  use=(idx[a]>=0)&(idx[b]>=0);row=idx[a[use]]*dim+idx[b[use]];val=sgn[a[use]]*sgn[b[use]]
  C=sparse.coo_matrix((val,(row,col[use])),shape=(dim*dim,n)).tocsc();C.eliminate_zeros();name=f'root{typ}-{parity}';sparse.save_npz(out/(name+'.npz'),C)
  records.append({'name':name,'type':typ,'parity':parity,'dimension':dim,'nnz':C.nnz,'bytes':C.data.nbytes+C.indices.nbytes+C.indptr.nbytes})
  print(records[-1],flush=True)
r={'graphs':n,'original_dimensions':[d,d],'denominator':ne,'blocks':records,'maps':maps,'root_swap_invariance_all_graphs':True,'transpose_symmetry_all_graphs':True,'seconds':time.monotonic()-t0}
(out/'metadata.json').write_text(json.dumps(r,indent=2));print('PASS',r['seconds'],flush=True)
