"""Cheap separation test, not a new bound or solver run."""
import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,itertools,json,signal
from pathlib import Path
signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError()));signal.alarm(175)
z=np.load('reports/global-coupled-pilot-001/coefficients.npz');graphs=z['graphs6'];p=np.array(list(itertools.permutations(range(6))));co=[];switch=[]
for A in graphs:
 row=[]
 for B in (A,1-A):
  path=B[p[:,0],p[:,1]]*B[p[:,1],p[:,2]]*B[p[:,2],p[:,3]]
  matching=B[p[:,0],p[:,1]]*B[p[:,2],p[:,3]]*B[p[:,4],p[:,5]]
  row.append(int(path.sum())-int(matching.sum()))
 co.append(row)
 old=np.ones(len(p),dtype=int);oldb=old.copy();new=old.copy();newb=old.copy()
 for i,j in itertools.combinations(range(4),2):
  b=A[p[:,i],p[:,j]];old*=b;oldb*=1-b
  q=1-b if i==0 else b;new*=q;newb*=1-q
 switch.append(int((new+newb-old-oldb).sum()))
co=np.array(co);switch=np.array(switch);out=[]
for name in ['control','edges','vertex','both']:
 f=Path('reports/edge-optimality-001')/(name+'-result.json')
 if not f.exists():continue
 d=json.loads(f.read_text());q=np.array(d['primal']);out.append(dict(name=name,objective=d['objective'],odd_path_slack=(q@co/720).tolist(),complement_newclass_slack=float(q@switch/720)))
report=dict(scope='Numerical screening of saved N6 moments, no solve, no frontier bound. Odd-path RHS encoded as three disjoint edges, not cube of pseudo-edge density. Complement newclass condition valid only at minimizers.',runs=out,coefficients_denominator=720,odd_path_numerators=co.tolist(),complement_newclass_numerators=switch.tolist())
Path('reports/lower-bound-refresh-001/screen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(out,indent=2))
