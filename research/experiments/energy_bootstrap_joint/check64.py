"""Independent rational verification, without importing optimizer/common/certifier."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import sys,json,struct,time,signal,hashlib
from pathlib import Path
from fractions import Fraction as F
import numpy as np
sys.path.insert(0,str(Path('research/experiments/clebsch_bowl').resolve()))
from check_coupled_certificate import exact_ldl
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175);t0=time.monotonic();out=Path('reports/energy-bootstrap-joint-001');base=Path('reports/energy-bootstrap-n7-001');name=sys.argv[1];path=out/(name+'-certificate.json');cert=json.loads(path.read_text());sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
assert cert['base_coefficients_sha256']==sha(base/'coefficients.bin')
prior=json.loads((base/'control-check.json').read_text());assert prior['coefficient_sha256']==cert['base_coefficients_sha256']
assert cert['observable_sha256']==sha(out/'observables.json');obs=json.loads((out/'observables.json').read_text());assert obs['denominator']==5040
inp=list(map(int,(out/'observable-input.txt').read_text().split()));want=[1044]
for code,r in zip(obs['graphs'],obs['rows']):want += [code]+r['X']+[v for row in r['J'] for v in row]
assert inp==want
receipt=json.loads((out/'observable-check-receipt.json').read_text());assert receipt['observable_sha256']==cert['observable_sha256'] and receipt['input_sha256']==sha(out/'observable-input.txt')
meta=json.loads((base/'metadata.json').read_text());assert obs['graphs']==meta['graphs']
f=open(base/'coefficients.bin','rb');nb,ng=struct.unpack('ii',f.read(8));Cs=[]
for _ in range(nb):
 d=struct.unpack('i',f.read(4))[0];Cs.append(np.fromfile(f,dtype=np.uint16,count=ng*d*d).reshape(ng,d,d))
x=np.fromfile(f,dtype=np.uint16,count=ng);z=np.fromfile(f,dtype=np.uint16,count=ng);c=np.fromfile(f,dtype=np.uint16,count=ng);P=np.fromfile(f,dtype=np.uint16,count=156*ng).reshape(156,ng);assert not f.read()
refpath=Path('reports/global-coupled-pilot-003/full-certificate.json');assert sha(refpath)==prior['base_certificate_sha256'];ref=json.loads(refpath.read_text())
for b in ref['blocks']:Cs.append(np.einsum('ag,aij->gij',P.astype(np.int64),np.array(b['C_integer'],dtype=np.int64)))
assert len(Cs)==len(cert['Q_integer'])==58;pen=[0]*ng;scale=cert['scale']
for C,Q in zip(Cs,cert['Q_integer']):
 d=len(Q);assert all(Q[i][j]==Q[j][i] for i in range(d) for j in range(d));exact_ldl(Q)
 for i in range(d):
  for j in range(d):
   if Q[i][j]:
    col=C[:,i,j]
    for g in np.flatnonzero(col):pen[g]+=int(col[g])*Q[i][j]
cfg=cert['config'];assert cfg['grid']==64;v=list(map(lambda t:F(t,64),cfg['box']));a,b,c1,d=v;assert 0<=a<b<=1 and 0<=c1<d<=1 and a+c1<=1
lower=[F(0),a,c1,F(0)];upper=[1-a-c1,b,d,1-a-c1];lams=list(map(lambda n:F(n,scale),cert['lambda_integer']));assert min(lams)>=0;slacks=[]
for g,row in enumerate(obs['rows']):
 p=list(map(lambda n:F(n,5040),row['X']));J=[[F(n,5040) for n in r] for r in row['J']];ineq=[]
 for i in range(4):ineq += [p[i]-lower[i],upper[i]-p[i],(lower[i]+upper[i])*p[i]-J[i][i]-lower[i]*upper[i]]
 if cfg['cross']:
  for i in range(4):
   for j in range(i+1,4):
    ineq += [J[i][j]-lower[i]*p[j]-lower[j]*p[i]+lower[i]*lower[j],J[i][j]-upper[i]*p[j]-upper[j]*p[i]+upper[i]*upper[j],upper[i]*p[j]+lower[j]*p[i]-J[i][j]-upper[i]*lower[j],lower[i]*p[j]+upper[j]*p[i]-J[i][j]-lower[i]*upper[j]]
 if cfg['ordered']:ineq.append(p[2]-p[1])
 assert len(ineq)==len(lams)
 slacks.append(F(int(c[g]),5040)-F(pen[g],5040*scale)-sum(l*v for l,v in zip(lams,ineq)))
bound=min(slacks);assert bound==F(cert['bound'])
r={'name':name,'bound':str(bound),'bound_decimal':float(bound),'exact_PSD_matrices':58,'config':cfg,'seconds':time.monotonic()-t0,'certificate_sha256':sha(path),'checker_sha256':sha(Path(__file__)),'observable_sha256':cert['observable_sha256'],'coefficient_sha256':cert['base_coefficients_sha256'],'scope':'Exact certificate on specified probability box and colour order. Global bound requires exhaustive coverage/complement argument.'}
(out/(name+'-check.json')).write_text(json.dumps(r,indent=2));print(json.dumps(r),flush=True)
