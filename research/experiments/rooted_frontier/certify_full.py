"""Round a complete-two-root dual; no promotion without separate checking."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import json,struct,signal,time,sys,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
from scipy import sparse
sys.path.insert(0,str(Path('research/experiments/energy_bootstrap_auto').resolve()))
from common import blocks
sys.path.insert(0,str(Path('research/experiments/clebsch_bowl').resolve()))
from check_coupled_certificate import exact_ldl
signal.alarm(175);t0=time.monotonic();out=Path('reports/rooted-full-001');src=Path('reports/energy-bootstrap-n8-001');scale=10**10
Cs,c7=blocks();dual=np.load(out/'full-dual.npz');qs=[]
def round_psd(Q):
 R=np.rint((Q+Q.T)*scale/2).astype(np.int64);shift=max(1,int(np.ceil(-np.linalg.eigvalsh(R.astype(float))[0]))+2)
 while True:
  S=R+shift*np.eye(len(R),dtype=np.int64)
  try:exact_ldl(S.tolist());break
  except AssertionError:shift*=2
 qs.append(S.tolist());return S
pen7=np.zeros(1044,dtype=object)
for i,C in enumerate(Cs):
 S=round_psd(dual[f'Q{i}']);assert sum(abs(int(x)) for x in S.ravel())*5040<2**62
 pen7+=C.reshape(1044,-1).astype(np.int64)@S.ravel()
with open(src/'coefficients.bin','rb') as f:
 n7,n8=struct.unpack('ii',f.read(8));idx=np.fromfile(f,dtype=np.uint16,count=n8*8).reshape(n8,8);X=np.fromfile(f,dtype=np.uint16,count=n8*11).reshape(n8,11);J=np.fromfile(f,dtype=np.uint16,count=n8*121).reshape(n8,121)
pen8=np.sum(pen7[idx],axis=1);S=round_psd(dual['Q58']);assert 70*sum(abs(int(x)) for x in S.ravel())<2**62;penJ=J.astype(np.int64)@S.ravel()
meta=json.loads((out/'metadata.json').read_text());penRoot=np.zeros(n8,dtype=object)
for i,b in enumerate(meta['blocks']):
 S=round_psd(dual[f'Q{59+i}']);C=sparse.load_npz(out/(b['name']+'.npz')).astype(np.int64);assert 1120*sum(abs(int(x)) for x in S.ravel())<2**62;penRoot+=C.T@S.ravel()
lam=[max(0,round(float(v)*scale)) for v in dual['lam']];assert len(lam)==3
L=F(57520950383,1966080000000);U=F(30139,1000000);slacks=[]
for g in range(n8):
 c=F(int(X[g,0])+int(X[g,-1]),70);mono=F(sum(int(J[g,j]) for j in [0,10,110,120]),70)
 constraints=[c-L,U-c,(L+U)*c-mono-L*U]
 slack=c-F(int(pen8[g]),40320*scale)-F(int(penJ[g]),70*scale)-F(int(penRoot[g]),1120*scale)-sum(F(a,scale)*b for a,b in zip(lam,constraints));slacks.append(slack)
bound=min(slacks);r={'bound':str(bound),'bound_decimal':float(bound),'L':str(L),'U':str(U),'scale':scale,'Q_integer':qs,'lambda_integer':lam,'seconds':time.monotonic()-t0,'scope':'Candidate exact dual on L<=F<=U. Independent coefficient/checker audit required; not promoted.','hashes':{}}
for p in [Path('reports/energy-bootstrap-n7-001/coefficients.bin'),src/'coefficients.bin',out/'metadata.json']+[out/(b['name']+'.npz') for b in meta['blocks']]:r['hashes'][str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
(out/'certificate.json').write_text(json.dumps(r));print(json.dumps({k:v for k,v in r.items() if k not in ['Q_integer','hashes']}),flush=True)
