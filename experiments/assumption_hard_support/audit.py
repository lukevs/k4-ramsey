import os,signal,time,json,sys,itertools,hashlib
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(170)
import numpy as np
from pathlib import Path
from fractions import Fraction
from integer_oracle import change,direct
sys.path.insert(0,'experiments/family_mechanism_followup');from local_patch import LocalPatch
OUT=Path('reports/assumption-hard_support-001');start=time.monotonic();rng=np.random.default_rng(93043)
meta=dict(pid=os.getpid(),start_utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),seed=93043,timeout_seconds=170,command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/assumption_hard_support/audit.py',tiny=[],checks=[])
print(json.dumps(meta),flush=True)
for n in (2,3,5,7):
 Q=13;N=rng.integers(Q+1,size=(n,n));N=np.triu(N)+np.triu(N,1).T;V=N.copy();num=0
 for u,v in itertools.combinations(range(min(n,4)),2):
  new=int(rng.integers(Q+1));num+=change(V,Q,u,v,new);V[u,v]=V[v,u]=new
 assert num==direct(V,Q)-direct(N,Q)
 meta['tiny'].append(dict(n=n,exact_delta_numerator=num,nonzero_diagonals=True))
# Use stored FULL real incumbent; independent materialization from search's split input.
p=Path('reports/round4-E5-depth2-001/graphon-candidate.json');raw=json.loads(p.read_text());Q=raw['edge_probability_denominator'];N=np.array(raw['red_probability_numerators'],dtype=np.int64);n=len(N);assert len(set(raw['block_weights']))==1
r=json.loads((OUT/'depth2.json').read_text());best=min(r['rows'],key=lambda row:row['controls']['amplitude_only']['delta']);nodes=best['parent_nodes'];S=[2*u+s for u in nodes for s in range(2)];model=LocalPatch(N/Q,np.ones(n)/n,S)
meta['incumbent_sha256']=hashlib.sha256(p.read_bytes()).hexdigest();meta['nodes']=nodes;meta['denominator']=Q;meta['n']=n
# Round all amplitude shifts together; hard bridges remain unchanged in best candidate.
for name in ('amplitude_only','joint','finite_barrier_probe'):
 V=N.copy();patch=V[np.ix_(S,S)].copy();x=best['controls']['amplitude_only' if name=='finite_barrier_probe' else name]['x'];changes=[]
 if name=='finite_barrier_probe':
  for i,j in itertools.combinations(range(4),2):
   if [i,j] not in [f['edge'] for f in best['fractional']]:
    for s,t in itertools.product(range(2),repeat=2):patch[2*i+s,2*j+t]=patch[2*j+t,2*i+s]=Q//2
 for k,f in enumerate(best['fractional']):
  i,j=f['edge'];shift=int(round(Q*x[k+1]))
  for s,t in itertools.product(range(2),repeat=2):patch[2*i+s,2*j+t]+=(-1)**(s+t)*shift;patch[2*j+t,2*i+s]=patch[2*i+s,2*j+t]
 assert patch.min()>=0 and patch.max()<=Q
 num=0
 for i,j in itertools.combinations(range(8),2):
  a,b=S[i],S[j];new=int(patch[i,j])
  if new!=V[a,b]:
   num+=change(V,Q,a,b,new);changes.append([a,b,int(V[a,b]),new]);V[a,b]=V[b,a]=new
 delta=Fraction(num,n**4*Q**6);pred=model.evaluate(patch/Q)[0];err=abs(float(delta)-pred);assert err<max(1e-21,abs(float(delta))*1e-9),(err,pred,float(delta))
 row=dict(name=name,changes=changes,exact_delta=str(delta),decimal=float(delta),polynomial=pred,absolute_disagreement=err);meta['checks'].append(row);meta['seconds']=time.monotonic()-start;(OUT/'audit.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(row),flush=True)
 if name=='joint':
  baseline=Fraction(json.load(open('reports/round4-E5-depth2-001/report.json'))['predicted_density']);candidate=dict(schema='sparse-rational-symmetric-patch-v1',parent=str(p),parent_sha256=meta['incumbent_sha256'],denominator=Q,changes=changes,exact_relative_delta=str(delta),conditional_density=str(baseline+delta),conditional_decimal=float(baseline+delta),scope='Independent integer relative count; saved incumbent absolute baseline reused; no full absolute recount; parent audit required; no promotion')
  (OUT/'candidate-patch.json').write_text(json.dumps(candidate,indent=2)+'\n')
meta['seconds']=time.monotonic()-start;meta['termination']='completed';meta['scope']='Independent endpoint-multiplicity exact relative recount vs partition polynomial; real3840 matrix read directly, all repeats/diagonals; no full absolute recount';(OUT/'audit.json').write_text(json.dumps(meta,indent=2)+'\n');print('completed',meta['seconds'],flush=True)
