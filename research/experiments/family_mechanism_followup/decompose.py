import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import signal,time,json,sys
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(160)
import numpy as np
from fractions import Fraction
from pathlib import Path
sys.path.insert(0,'research/experiments/round4_E5')
from load import load
from phi import Phi
start=time.monotonic();out=Path('reports/family-mechanism-followup-001')
N,Q,w=load();a=np.load('reports/round4-E5-depth1-001/a_int.npy');P=N/Q;A=a/Q
baseline=Phi(P);t3=baseline.T3(A);t4=baseline.T4(A)
receipt=json.loads(Path('reports/round4-E5-depth1-001/report.json').read_text())
assert abs(t3+t4-float(Fraction(receipt['exact_delta'])))<1e-20
patch=json.loads((out/'checked-patch.json').read_text());exact=json.loads((out/'exact-check.json').read_text());u,v=patch['edge'];rows=[]
for r,e in zip(patch['controls'],exact['rows']):
    B=P.copy();C=A.copy();B[u,v]=B[v,u]=r['parent_numerator']/Q;C[u,v]=C[v,u]=r['amplitude_numerator']/Q
    ph=Phi(B);c3=ph.T3(C);c4=ph.T4(C);total=float(Fraction(e['exact_delta']))
    rows.append(dict(name=r['name'],T3_change=c3-t3,T4_change=c4-t4,refinement_change=(c3-t3)+(c4-t4),parent_change_inferred_from_exact_total=total-((c3-t3)+(c4-t4)),exact_total=total))
    print(json.dumps(rows[-1]),flush=True)
(out/'decomposition.json').write_text(json.dumps(dict(baseline_T3=t3,baseline_T4=t4,rows=rows,seconds=time.monotonic()-start,scope='Floating cubic/quartic decomposition; total is independently exact; parent contribution inferred by subtraction'),indent=2)+'\n')
