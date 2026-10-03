import json,sys,random,time,subprocess,hashlib
from pathlib import Path
sys.path.insert(0,str(Path('experiments/relation_engine').resolve()))
from run_v2 import normalize,validate,fixture_text
out=Path('reports/graph-arrangements-001');data=json.loads((out/'graphs.json').read_text());binary=Path('experiments/relation_engine/engine_v2').resolve();start=time.monotonic();runs=[];checks={}
# Exact direct integer graph validation (no reliance on generator metadata).
for name,d in data.items():
 A=d['adjacency'];n=len(A);degrees=[sum(r) for r in A];assert min(degrees)==max(degrees)
 adj=set();non=set()
 for i in range(n):
  assert A[i][i]==0
  for j in range(i):
   assert A[i][j]==A[j][i]
   (adj if A[i][j] else non).add(sum(A[i][k]*A[j][k] for k in range(n)))
 expected={'higman_sims':(100,22,{0},{6}),'M22':(77,16,{0},{4}),'gewirtz':(56,10,{0},{2})}[name]
 assert (n,degrees[0],adj,non)==expected
 checks[name]={'n':n,'degree':degrees[0],'adjacent_common':list(adj),'nonadjacent_common':list(non),'ambient_group_sizes':{str(g):d['ambient_groups'].count(g) for g in set(d['ambient_groups'])}}
(out/'graph-checks.json').write_text(json.dumps(checks,indent=2)+'\n')
for name in ('gewirtz','M22','higman_sims'):
 d=data[name];A=d['adjacency'];n=len(A)
 for partition in ('plain','ambient','anchor'):
  labels=[0]*n if partition=='plain' else d['ambient_groups'] if partition=='ambient' else [0 if i==0 else 1 if A[0][i] else 2 for i in range(n)]
  keys=sorted({(min(labels[i],labels[j]),max(labels[i],labels[j]),2 if i==j else A[i][j]) for i in range(n) for j in range(n)})
  index={k:i for i,k in enumerate(keys)};ids=[[index[(min(labels[i],labels[j]),max(labels[i],labels[j]),2 if i==j else A[i][j])] for j in range(n)] for i in range(n)]
  for seed in (0,1):
   if time.monotonic()-start>500:break
   rng=random.Random(930+seed);q=10000
   # Bias near a graph-based coloring, or perturb a half-probability parent.
   p=[(5000 if k[2]==2 else 9000 if k[2]==1 else 3000) if seed==0 else rng.randrange(3500,6501) for k in keys]
   cfg={'schema':'relation-engine-config-v1','mode':'matrix','n':n,'q':q,'relation_count':len(keys),'relation_ids':ids,'probability_numerators':p,'constraint_group_ids':[-2]*len(keys)}
   x=normalize(cfg);validate(x);tag=f'{name}-{partition}-{seed}';folder=out/tag;folder.mkdir(exist_ok=True);(folder/'config.json').write_text(json.dumps(cfg));(folder/'relations.json').write_text(json.dumps(keys));(folder/'fixture.txt').write_text(fixture_text(x))
   t=time.monotonic()
   try:
    proc=subprocess.run([str(binary),str(folder/'fixture.txt'),str(folder/'native.json')],text=True,capture_output=True,timeout=170) if not (folder/'native.json').exists() else subprocess.CompletedProcess([],0,stdout='Reused completed native report after summary-key correction.',stderr='')
    (folder/'run.log').write_text(proc.stdout+proc.stderr);assert proc.returncode==0,proc.stderr
    r=json.loads((folder/'native.json').read_text());summary={k:r[k] for k in ('parent_decimal','optimized_decimal','rounded_decimal','free_projected_kkt_inf','termination_reason')};summary.update(tag=tag,n=n,relations=len(keys),seconds=time.monotonic()-t)
   except subprocess.TimeoutExpired:summary={'tag':tag,'timeout':170}
   runs.append(summary);print(json.dumps(summary),flush=True);(out/'summary.json').write_text(json.dumps({'checks':checks,'runs':runs,'seconds':time.monotonic()-start,'binary_sha256':hashlib.sha256(binary.read_bytes()).hexdigest()},indent=2)+'\n')
