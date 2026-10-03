import json,subprocess,hashlib,itertools,random,time,signal
from pathlib import Path
signal.alarm(175)
root=Path('reports/assumption-discrete_basins-001');exe='experiments/assumption_discrete_basins/check_matrix'
def check(rows):
 n=len(rows);cmd=[exe];st=time.time();p=subprocess.run(cmd,input=str(n)+'\n'+'\n'.join(rows)+'\n',capture_output=True,text=True,timeout=170,check=True)
 return int(p.stdout.strip().splitlines()[-1].split()[1]),dict(command=cmd,seconds=time.time()-st,stdout=p.stdout)
rng=random.Random(1771);tiny=[]
for n in range(1,7):
 for rep in range(5):
  R=[[0]*n for _ in range(n)]
  for a in range(n):
   for b in range(a+1):R[a][b]=R[b][a]=rng.randrange(2)
  literal=sum(len({R[a][b],R[a][c],R[a][d],R[b][c],R[b][d],R[c][d]})==1 for a,b,c,d in itertools.product(range(n),repeat=4))
  v,_=check([''.join(map(str,r)) for r in R]);assert v==literal;tiny.append([n,rep,v])
results=[]
for p in root.glob('matrix-*.json'):
 d=json.loads(p.read_text())
 if 'red_rows' not in d:continue
 rows=d['red_rows'];assert all(rows[a][b]==rows[b][a] for a in range(len(rows)) for b in range(a))
 v,receipt=check(rows);r=dict(path=str(p),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),count=v,expected=d['best_count'],passed=v==d['best_count'],receipt=receipt);results.append(r);print(p.name,v,r['passed'],flush=True)
(root/'audit-matrix.json').write_text(json.dumps(dict(checker_sha256=hashlib.sha256(Path(exe+'.cpp').read_bytes()).hexdigest(),driver_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),tiny_literal_tests=tiny,results=results),indent=2));assert all(r['passed'] for r in results)
