import signal,time,os
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
START=time.time()
import sys,json,hashlib
from pathlib import Path
import numpy as np
from scipy.optimize import linprog
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import experiments.assumption_symmetry_insertion.pilot as p
# Import installs the same175s alarm; restore initial deadline.
signal.alarm(max(1,175-int(time.time()-START)))
p.F=p.density(p.W,p.m);p.dump('boundary-active.json',{'pid':os.getpid(),'start':START,'deadline':START+175})
chars=np.array([[(-1)**((x&s).bit_count()) for s in range(16)] for x in range(16)],float)/4
A=np.array([[int((x^y) in [1,2,4,8,15]) for y in range(16)] for x in range(16)])
ev=np.diag(chars.T@A@chars).round().astype(int);constant=np.kron(np.eye(12),chars[:,[0]])
rows=[]
for eig in [1,-3]:
 guided=np.kron(np.eye(12),chars[:,np.r_[0,np.where(ev==eig)[0]]]);dim=guided.shape[1]
 for seed in [601,602,603]:
  rng=np.random.default_rng(seed);raw=rng.normal(size=(p.n,dim-12));raw-=constant@(constant.T@raw);Q=np.linalg.qr(raw)[0];random=np.column_stack([constant,Q]);z=rng.normal(size=dim)
  for label,B in [('guided',guided),('random',random)]:
   lp=linprog(z,A_ub=np.vstack([B,-B]),b_ub=np.full(2*p.n,.5),bounds=[(None,None)]*dim,method='highs',options={'threads':1})
   assert lp.success,lp.message
   q0=np.clip(.5+B@lp.x,0,1)
   row=p.fit(B,q0,f'boundary_{label}_eig{eig}',seed,budget=150)
   row.update(start_R=p.rooted(q0)[0],start_q=q0.tolist(),start_active=int(np.sum((q0<1e-8)|(q0>1-1e-8))),orthogonality_error=float(abs(B.T@B-np.eye(dim)).max()),lp_nit=int(lp.nit))
   rows.append(row);p.dump('boundary-runs.json',rows)
# matched release (same150 call allowance) of all12 final points
for best in list(rows):
 if time.time()-START>140:break
 rows.append(p.fit(None,np.array(best['q']),best['label']+'_release',best['seed'],budget=150,release=True));p.dump('boundary-runs.json',rows)
p.dump('boundary-receipt.json',{'pid':os.getpid(),'start':START,'end':time.time(),'seconds':time.time()-START,'termination':'completed','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'pilot_sha256':hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest(),'F':p.F,'lp_threads':1,'note':'Three seeds per affine subspace;150 rooted calls each, plus equal150-call release; LP setup additional and reported as structural cost, no superiority claim.'})
p.dump('boundary-active.json',{'pid':None,'stage':'completed','end':time.time()})
