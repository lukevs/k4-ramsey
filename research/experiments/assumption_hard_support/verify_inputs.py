import os,signal,time,json,hashlib,itertools,sys
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS'):os.environ[k]='1'
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(170)
import numpy as np
from pathlib import Path
start=time.monotonic();results=[]
paths=['reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json','reports/round4-E5-depth1-001/graphon-candidate.json','reports/round4-E5-depth2-001/graphon-candidate.json']
for i in (1,2):
 a=json.loads(Path(paths[i-1]).read_text());b=json.loads(Path(paths[i]).read_text());N=np.array(a['red_probability_numerators']);M=np.array(b['red_probability_numerators']);A=np.load('reports/round4-E5-depth%d-001/a_int.npy'%i)
 assert a['edge_probability_denominator']==b['edge_probability_denominator'];assert len(set(a['block_weights']))==len(set(b['block_weights']))==1
 for s,t in itertools.product(range(2),repeat=2):assert np.array_equal(M[s::2,t::2],N+(-1)**(s+t)*A)
 results.append(dict(layer=i,exact_entrywise_split_match=True,n=len(M),parent_sha256=hashlib.sha256(Path(paths[i-1]).read_bytes()).hexdigest(),child_sha256=hashlib.sha256(Path(paths[i]).read_bytes()).hexdigest()))
patch=json.load(open('reports/assumption-hard_support-001/candidate-patch.json'));N=np.array(json.load(open(paths[2]))['red_probability_numerators']);Q=patch['denominator']
for u,v,old,new in patch['changes']:assert N[u,v]==N[v,u]==old and 0<=new<=Q
result=dict(pid=os.getpid(),utc=time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime()),results=results,patch_old_values_and_box_verified=True,seconds=time.monotonic()-start,command='OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python research/experiments/assumption_hard_support/verify_inputs.py',timeout_seconds=170)
Path('reports/assumption-hard_support-001/input-verification.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
