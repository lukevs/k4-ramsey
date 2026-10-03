"""Separate exact certificate audit. Does not import solve/certify/generate.
New tensor entries are bound to the independent exhaustive C++ table check.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import sys,json,struct,itertools as it,hashlib,time,signal
from pathlib import Path
from fractions import Fraction as F
import numpy as np
sys.path.insert(0,str(Path('experiments/clebsch_bowl').resolve()))
from check_coupled_certificate import exact_ldl
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
out=Path('reports/energy-bootstrap-n7-001');mode=sys.argv[1];t0=time.monotonic();meta=json.loads((out/'metadata.json').read_text());certpath=out/(mode.replace(',','_')+'-certificate.json');cert=json.loads(certpath.read_text());scale=cert['scale'];sha=hashlib.sha256((out/'coefficients.bin').read_bytes()).hexdigest();assert cert['coefficient_sha256']==sha
# Check the semantic definition and completeness of every rooted-flag lookup.
def edges(n):return list(it.combinations(range(n),2))
def relabel(code,n,v):
 pos={p:k for k,p in enumerate(edges(n))};return sum(((code>>pos[tuple(sorted((v[i],v[j])))])&1)<<k for k,(i,j) in enumerate(edges(len(v))))
for r in (1,3,5):
 rootcovered=set()
 for b in [b for b in meta['blocks'] if b['r']==r]:
  orbit={relabel(b['t'],r,p) for p in it.permutations(range(r))};assert not rootcovered.intersection(orbit);rootcovered.update(orbit)
  flags={}
  for index,code in enumerate(b['flags']):
   for tail in it.permutations(range(r,b['s'])):
    f=relabel(code,b['s'],tuple(range(r))+tail);assert f not in flags or flags[f]==index;flags[f]=index
  for code,index in enumerate(b['lookup']):
   matches=relabel(code,b['s'],range(r))==b['t'];assert matches==(code in flags)
   assert index==flags.get(code,-1)
 assert rootcovered==set(range(1<<(r*(r-1)//2)))
# Read independently enumerated new tensors.
f=open(out/'coefficients.bin','rb');nb,ng=struct.unpack('ii',f.read(8));Cs=[]
for b in meta['blocks']:
 d=struct.unpack('i',f.read(4))[0];assert d==b['d'];Cs.append(np.fromfile(f,dtype=np.uint16,count=ng*d*d).reshape(ng,d,d))
x=np.fromfile(f,dtype=np.uint16,count=ng);z=np.fromfile(f,dtype=np.uint16,count=ng);c=np.fromfile(f,dtype=np.uint16,count=ng);P=np.fromfile(f,dtype=np.uint16,count=156*ng).reshape(156,ng);assert not f.read()
# Rebuild deletion marginal independently from graph6 relabeling dictionary.
oldmeta=json.loads(Path('reports/global-coupled-pilot-003/coefficient-metadata.json').read_text());g6=[sum(A[i][j]<<k for k,(i,j) in enumerate(edges(6))) for A in oldmeta['graphs6']];owner={}
for g,code in enumerate(g6):
 for v in it.permutations(range(6)):owner[relabel(code,6,v)]=g
assert len(owner)==32768
for g,code in enumerate(meta['graphs']):
 counts=[0]*156
 for vs in it.combinations(range(7),6):counts[owner[relabel(code,7,vs)]]+=1
 assert counts==P[:,g].tolist()
refpath=Path('reports/global-coupled-pilot-003/full-certificate.json');ref=json.loads(refpath.read_text());oldids=[]
for b in cert['blocks'][nb:]:
 idx=b['base_reference'];assert idx not in oldids;oldids.append(idx);B=np.array(ref['blocks'][idx]['C_integer'],dtype=np.int64);Cs.append(np.einsum('ag,aij->gij',P.astype(np.int64),B))
assert set(oldids)==set(range(19)) and len(Cs)==len(cert['blocks'])==58
pen=[0]*ng
for B,b in zip(Cs,cert['blocks']):
 Q=b['Q_integer'];d=len(Q);assert all(Q[i][j]==Q[j][i] for i in range(d) for j in range(d));exact_ldl(Q)
 # Independent summation by matrix entry; each vector multiply is safely bounded.
 for i in range(d):
  for j in range(d):
   q=Q[i][j]
   if q:
    col=B[:,i,j]
    for g in np.flatnonzero(col):pen[g]+=q*int(col[g])
a=b=F(0);lam=F(cert['lambda_integer'],scale);assert lam>=0
if cert['interval'] is not None:a,b=map(F,cert['interval'])
slacks=[F(int(c[g]),5040)-F(pen[g],5040*scale)-lam*((a+b)*F(int(x[g]),5040)-F(int(z[g]),5040)) for g in range(ng)]
bound=min(slacks)+lam*a*b;assert bound==F(cert['bound'])
r={'mode':mode,'bound':str(bound),'bound_decimal':float(bound),'exact_PSD_matrices':58,'coefficient_sha256':sha,'certificate_sha256':hashlib.sha256(certpath.read_bytes()).hexdigest(),'base_certificate_sha256':hashlib.sha256(refpath.read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.monotonic()-t0,'scope':'Exact branch dual, lookup semantics and deletion marginal. New tensors separately independently enumerated by check_tables.cpp; inherited N6 flag certificate reused.'}
(out/(mode.replace(',','_')+'-check.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
