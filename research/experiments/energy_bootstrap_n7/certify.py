import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import sys,json,signal,struct,hashlib,time
from pathlib import Path
from fractions import Fraction as F
import numpy as np
sys.path.insert(0,str(Path('research/experiments/clebsch_bowl').resolve()))
from check_coupled_certificate import exact_ldl
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
out=Path('reports/energy-bootstrap-n7-001');mode=sys.argv[1];t0=time.monotonic();scale=10**10
f=open(out/'coefficients.bin','rb');nb,ng=struct.unpack('ii',f.read(8));Cs=[]
for i in range(nb):
 d=struct.unpack('i',f.read(4))[0];Cs.append(np.fromfile(f,dtype=np.uint16,count=ng*d*d).reshape(ng,d,d))
x=np.fromfile(f,dtype=np.uint16,count=ng).astype(np.int64);z=np.fromfile(f,dtype=np.uint16,count=ng).astype(np.int64);c=np.fromfile(f,dtype=np.uint16,count=ng).astype(np.int64);P=np.fromfile(f,dtype=np.uint16,count=156*ng).reshape(156,ng).astype(np.int64);assert not f.read()
src=np.load('reports/global-coupled-pilot-001/coefficients.npz');old=[np.einsum('hg,hij->gij',src['P'],src[k]) for k in sorted(src.files) if k.startswith('N5_')]+[src[k] for k in sorted(src.files) if k.startswith('N6_')]
ref=json.loads(Path('reports/global-coupled-pilot-003/full-certificate.json').read_text());lookup={np.array(b['C_integer'],dtype=np.int64).tobytes():i for i,b in enumerate(ref['blocks'])};ids=[]
for B in old:
 Bi=np.rint(B*720).astype(np.int64);ids.append(lookup[Bi.tobytes()]);Cs.append(np.einsum('ag,aij->gij',P,Bi).astype(np.uint16))
name=mode.replace(',','_');dual=np.load(out/(name+'-dual.npz'));pen=np.zeros(ng,dtype=object);blocks=[]
for i,C in enumerate(Cs):
 Q=dual[f'Q{i}'];R=np.rint((Q+Q.T)*scale/2).astype(np.int64);shift=max(1,int(np.ceil(-np.linalg.eigvalsh(R.astype(float))[0]))+2)
 while True:
  S=R+shift*np.eye(len(R),dtype=np.int64)
  try:exact_ldl(S.tolist());break
  except AssertionError:shift*=2
 if sum(abs(int(v)) for v in S.ravel())*5040<2**62:
  pen+=C.reshape(ng,-1).astype(np.int64)@S.ravel()
 else:
  pen+=C.reshape(ng,-1).astype(object)@S.ravel().astype(object)
 blocks.append({'Q_integer':S.tolist(),'base_reference':ids[i-nb] if i>=nb else None})
 # Aggregate uses arbitrary-precision Python integers.
lam=0;interval=None;li=np.zeros(ng,dtype=np.int64);const=F(0)
if mode!='control':
 a,b=map(F,mode.split(','));interval=[str(a),str(b)];lam=max(0,round(float(dual['lam'])*scale));li=np.array([int(16*(a+b))*int(xx)-16*int(zz) for xx,zz in zip(x,z)],dtype=np.int64);const=-a*b
# Exact rational scalar combination, avoiding overflow from extra common denominator.
slacks=[F(int(cc)*scale-int(pp),5040*scale)-F(lam*int(ll),16*5040*scale) for cc,pp,ll in zip(c,pen,li)]
bound=min(slacks)-F(lam,scale)*const
r={'mode':mode,'interval':interval,'scale':scale,'lambda_integer':lam,'blocks':blocks,'bound':str(bound),'bound_decimal':float(bound),'seconds':time.monotonic()-t0,'coefficient_sha256':hashlib.sha256((out/'coefficients.bin').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(out/(name+'-certificate.json')).write_text(json.dumps(r));print(json.dumps({k:v for k,v in r.items() if k!='blocks'}),flush=True)
