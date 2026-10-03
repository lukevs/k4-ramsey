import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import sys,json,time,signal,hashlib
from fractions import Fraction as F
import numpy as np
from common import *
sys.path.insert(0,str(Path('research/experiments/clebsch_bowl').resolve()))
from check_coupled_certificate import exact_ldl
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175);t0=time.monotonic();name=sys.argv[1];cfg=json.loads((OUT/(name+'-config.json')).read_text());Cs,c=blocks();L,labels,_,_=inequalities(cfg);dual=np.load(OUT/(name+'-dual.npz'));scale=10**10;pen=np.zeros(len(c),dtype=object);qs=[]
for i,C in enumerate(Cs):
 Q=dual[f'Q{i}'];R=np.rint((Q+Q.T)*scale/2).astype(np.int64);shift=max(1,int(np.ceil(-np.linalg.eigvalsh(R.astype(float))[0]))+2)
 while True:
  S=R+shift*np.eye(len(R),dtype=np.int64)
  try:exact_ldl(S.tolist());break
  except AssertionError:shift*=2
 if sum(abs(int(v)) for v in S.ravel())*5040<2**62:pen+=C.reshape(len(c),-1).astype(np.int64)@S.ravel()
 else:pen+=C.reshape(len(c),-1).astype(object)@S.ravel().astype(object)
 qs.append(S.tolist())
lam=[max(0,round(float(v)*scale)) for v in dual['lam']]
slacks=[F(int(c[g])*scale-int(pen[g]),5040*scale)-F(sum(lam[j]*int(L[j,g]) for j in range(len(lam))),D*scale) for g in range(len(c))];bound=min(slacks)
r={'name':name,'config':cfg,'scale':scale,'Q_integer':qs,'lambda_integer':lam,'labels':labels,'bound':str(bound),'bound_decimal':float(bound),'seconds':time.monotonic()-t0,'base_coefficients_sha256':hashlib.sha256((BASE/'coefficients.bin').read_bytes()).hexdigest(),'observable_sha256':hashlib.sha256((OUT/'observables.json').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/(name+'-certificate.json')).write_text(json.dumps(r));print(json.dumps({k:v for k,v in r.items() if k not in ('Q_integer','lambda_integer','labels')}),flush=True)
