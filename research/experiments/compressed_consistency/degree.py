import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import json,time,signal
from pathlib import Path
import numpy as np
import cvxpy as cp
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175 seconds')));signal.alarm(175)
start=time.monotonic();out=Path('reports/compressed-consistency-001');z=np.load('reports/global-coupled-pilot-001/coefficients.npz');P=z['P'];meta=json.loads(Path('reports/global-coupled-pilot-003/coefficient-metadata.json').read_text());w=json.loads(Path('reports/global-coupled-pilot-003/baseline-feasible-witness.json').read_text());w6=np.array(w['probability_numerators'])/w['denominator'];w5=P@w6
# Retain joint root-extension parity matrices on the star/triangle+isolated types.
Cs=[]
for idx in (6,7):
 fs=meta['extra'][idx]['flags'];parity=[sum((x>>i)&1 for i in (3,6,8,9)) for x in fs];R=np.array([[int(v==i) for v in parity] for i in range(5)])
 Cs.append(np.rint(720*np.einsum('ai,gij,bj->gab',R,z['N6_'+str(idx)],R)).astype(int))
# Low summary keeps edge count and monochromatic4 count, plus compressed5 rooted-flag
# marginals obtained by deleting either of the two extension vertices.
# Try edge-only and edge+K4 deletion distributions; every state is a realizable6graph signature.
runs=[]
for mode in ('root_degree',):
 m=[int(A.sum())//2 for A in z['graphs5']];k=np.rint(5*z['c5']).astype(int)
 labels=[0]*34;states=sorted(set(labels));C=np.array([[int(v==s) for v in labels] for s in states]);T=np.rint(6*C@P).astype(int)
 # Include each matrix row-sum deletion identity: 6->5 consistent with the SAME p5.
 # Root flag counts at5 derived from6 via marginalization by least squares, then exact-check.
 rowmaps=[]
 for B in Cs:
  marginal=B.sum(axis=2).T/720
  L=np.linalg.lstsq(P.T,marginal.T,rcond=None)[0].T
  # Coefficients are rational with denominator 120 from ordered5-root embeddings.
  L=np.rint(L*120).astype(int)
  assert np.max(abs(L/120@P-marginal))<1e-14
  rowmaps.append(L)
 signature=np.column_stack([T.T]+[B.reshape(156,25) for B in Cs]);unique,inv=np.unique(signature,axis=0,return_inverse=True);reps=[int(np.flatnonzero(inv==i)[0]) for i in range(len(unique))]
 TT=T[:,reps]/6;CC=[B[reps]/720 for B in Cs]
 print('STATES',mode,len(states),len(reps),flush=True)
 for fix in (True,False):
  p=cp.Variable(34);q=cp.Variable(len(reps));cons=[p>=0,q>=0,cp.sum(p)==1,cp.sum(q)==1,C@p==TT@q]
  for key in sorted(z.files):
   if key.startswith('N5_'):
    B=z[key];d=B.shape[1];cons.append(cp.reshape(B.reshape(34,d*d).T@p,(d,d),order='C')>>0)
  for B,L in zip(CC,rowmaps):
   M=cp.reshape(B.reshape(len(reps),25).T@q,(5,5),order='C');cons.extend([M>>0,cp.sum(M,axis=1)==(L/120)@p])
  if fix:cons.append(p==w5)
  prob=cp.Problem(cp.Minimize(0 if fix else z['c5']@p),cons)
  prob.solve(solver='CLARABEL',tol_gap_abs=1e-9,tol_feas=1e-9,tol_gap_rel=1e-9,max_iter=150,time_limit=60)
  r={'mode':mode,'fixed_witness':fix,'states':len(reps),'status':prob.status,'objective':float(prob.value),'p':None if p.value is None else p.value.tolist(),'q':None if q.value is None else q.value.tolist()};runs.append(r)
  print('RESULT',json.dumps({a:b for a,b in r.items() if a not in ('p','q')}),flush=True)
 np.savez_compressed(out/(mode+'-coefficients.npz'),C=C,T_integer=T[:,reps],Cs_integer=np.array([B[reps] for B in Cs]),rowmaps_integer=np.array(rowmaps),inv=inv,reps=reps)
(out/'degree-result.json').write_text(json.dumps({'runs':runs,'seconds':time.monotonic()-start,'scope':'Numerical compressed consistency pilot; no independently certified strengthening'},indent=2)+'\n')
