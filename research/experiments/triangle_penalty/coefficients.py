import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import sys,json,time
from pathlib import Path
from fractions import Fraction as Q
import numpy as np
sys.path.insert(0,str(Path('research/experiments/round5_C1').resolve()))
from base import base
start=time.monotonic();W,typ,cls=base(32/41,22/41);D=41;A=np.rint(D*W).astype(np.int64);B=D-A;n=len(W);fr=(A>0)&(A<D);nb=[list(np.flatnonzero(row)) for row in fr];hc=(typ=='H').astype(int);C={r:[0]*(r+1) for r in (3,4,5,6)}
for x in range(n):
 for y in nb[x]:
  for z in nb[y]:
   if fr[z,x]:C[3][hc[x,y]+hc[y,z]+hc[z,x]]+=4*int(np.sum(A[x]*A[y]*A[z]-B[x]*B[y]*B[z]))
   for t in nb[z]:
    if fr[t,x]:C[4][hc[x,y]+hc[y,z]+hc[z,t]+hc[t,x]]+=3*int(A[x,z]*A[y,t]+B[x,z]*B[y,t])
  cn=[z for z in nb[x] if fr[z,y]]
  for z in cn:
   for t in cn:
    k=hc[x,y]+hc[x,z]+hc[y,z]+hc[x,t]+hc[y,t];C[5][k]+=6*int(2*A[z,t]-D)
    if fr[z,t]:C[6][k+hc[z,t]]+=2
exact={r:[Q(v,n**4*D**(6-r)) for v in values] for r,values in C.items()}
assert all(v==0 for k,v in enumerate(exact[3]) if k!=1) and exact[3][1]>0
K=sum(sum(abs(v) for v in exact[r]) for r in (4,5,6))
report={'base_p':'32/41','base_h':'22/41','base_F':'1013294255057839/33620705806123008','coefficients':{r:[str(v) for v in vs] for r,vs in exact.items()},'cubic_coefficient':str(exact[3][1]),'uniform_remainder_coefficient_eps_le_1':str(K),'K_decimal':float(K),'seconds':time.monotonic()-start}
Path('reports/triangle-penalty-001/coefficients.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
