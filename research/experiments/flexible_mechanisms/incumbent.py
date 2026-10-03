import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
import numpy as np,json,time,sys,signal
from pathlib import Path
from fractions import Fraction as Qf
signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
sys.path.insert(0,'research/experiments/round4_E5');from phi import Phi
from load import load
start=time.monotonic();N,Q,w=load();P=N/Q;ph=Phi(P);a=np.load('reports/round4-E5-depth1-001/a_int.npy');A=a/Q;fr=ph.frac;m=ph.m
# Control for integer saved matrix and baseline feasibility.
assert A.shape==P.shape and np.all(abs(A)<=m+1e-15) and np.all(A==A.T)
print('SETUP',time.monotonic()-start,flush=True)
controls={'original':A,'signs_only':m*np.sign(A),'magnitudes_only':abs(A),'uniform_positive':m}
# Projection onto dependence on parent probability alone, retaining feasibility.
proj=np.zeros_like(A)
for v in np.unique(N[fr]):proj[(N==v)&fr]=A[(N==v)&fr].mean()
controls['parent_probability_only']=proj
runs=[]
for name,B in controls.items():
 t3=ph.T3(B);t4=ph.T4(B)
 # All controls feasible for -1<=s<=1. Optimize scalar, including sign reversal.
 candidates=[-1.,0.,1.]
 if t4!=0:
  s=-3*t3/(4*t4)
  if abs(s)<=1:candidates.append(s)
 s=min(candidates,key=lambda s:t3*s**3+t4*s**4)
 r=dict(name=name,T3=t3,T4=t4,raw_delta=t3+t4,best_scalar=s,best_delta=t3*s**3+t4*s**4)
 runs.append(r);print(json.dumps(r),flush=True)
 Path('reports/flexible-mechanisms-001/incumbent-ablation.json').write_text(json.dumps(dict(runs=runs,seconds=time.monotonic()-start),indent=2)+'\n')
exact=[]
for depth in (1,2):
 d=json.loads(Path(f'reports/round4-E5-depth{depth}-001/report.json').read_text());n=d['classes']//2;den=n**4*d['Q']**6;t3=Qf(24*int(d['S3']),den);t4=Qf(3*int(d['S4']),den)
 assert t3+t4==Qf(d['exact_delta'])
 exact.append(dict(depth=depth,T3=str(t3),T4=str(t4),T3_decimal=float(t3),T4_decimal=float(t4),scale_derivative=float(3*t3+4*t4)))
 if depth==1:assert abs(float(t3)-runs[0]['T3'])<1e-20 and abs(float(t4)-runs[0]['T4'])<1e-20
Path('reports/flexible-mechanisms-001/incumbent-terms.json').write_text(json.dumps(dict(layers=exact,positive_amplitude_fraction=float(np.mean(A[fr]>0)),negative_amplitude_fraction=float(np.mean(A[fr]<0)),box_fraction=float(np.mean(abs(A[fr])>=m[fr]-1e-15)),seconds=time.monotonic()-start),indent=2)+'\n')
