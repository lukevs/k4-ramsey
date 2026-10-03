"""Seven-vertex mass-Hessian condition, with independent permutation checks."""
from pathlib import Path
from itertools import combinations,permutations
from fractions import Fraction as Q
import json,random,time
start=time.monotonic();out=Path('reports/edge-optimality-001');data=json.loads(Path('reports/lower-frontier-C-cut-001/cut.json').read_text());rows=[]
for row in data['coefficients']:
 E={tuple(sorted(e)) for e in row['edges']}
 def edge(a,b):return int(tuple(sorted((a,b))) in E)
 numerator=0
 for S in combinations(range(7),4):
  v=[edge(x,y) for x,y in combinations(S,2)]
  if not(all(v) or not any(v)):continue
  outside=set(range(7))-set(S)
  for a in outside:
   b,c=sorted(outside-{a});t=sum(edge(a,x) for x in S);eb=edge(a,b);ec=edge(a,c)
   numerator+=4*t*(t-1)-12*t*(eb+ec)+48*eb*ec
 rows.append({'index':row['index'],'edges':row['edges'],'positive':str(Q(numerator,5040))})
rng=random.Random(930)
for idx in rng.sample(range(1044),20)+[0,1043]:
 E={tuple(e) for e in rows[idx]['edges']};n=0
 def edge(a,b):return int(tuple(sorted((a,b))) in E)
 for x,y,u,v,a,b,c in permutations(range(7)):
  es=[edge(i,j) for i,j in combinations((x,y,u,v),2)]
  if all(es) or not any(es):n+=(edge(x,a)-edge(b,a))*(edge(y,a)-edge(c,a))
 assert Q(n,5040)==Q(rows[idx]['positive'])
screens={}
for name in ('control','cut'):
 y=json.loads(Path(f'reports/stationarity-cut-001/{name}.json').read_text())['moments']
 screens[name]=sum(w*float(Q(r['positive'])) for w,r in zip(y,rows))
report={'scope':'Optimizer-only averaged Hessian in mass direction h_a(x)=W(x,a)-d(a); expectation must be nonnegative.','permutation_checks':22,'screens':screens,'rows':rows,'seconds':time.monotonic()-start}
(out/'curvature.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({k:v for k,v in report.items() if k!='rows'}))
