import json,itertools as it,hashlib
from pathlib import Path
from fractions import Fraction as F
out=Path('reports/energy-bootstrap-joint-001');meta=json.loads(Path('reports/energy-bootstrap-n7-001/metadata.json').read_text());pairs=list(it.combinations(range(7),2));triples=list(it.combinations(range(7),3));rows=[]
for code in meta['graphs']:
 E={p for k,p in enumerate(pairs) if code>>k&1};types={t:sum(p in E for p in it.combinations(t,2)) for t in triples};X=[0]*4;J=[[0]*4 for _ in range(4)]
 for t in triples:
  i=types[t];X[i]+=144
  for s in it.combinations([v for v in range(7) if v not in t],3):J[i][types[s]]+=36
 assert sum(X)==5040 and sum(map(sum,J))==5040
 assert [sum(r) for r in J]==X and J==list(map(list,zip(*J)))
 rows.append({'X':X,'J':J})
(out/'observables.json').write_text(json.dumps({'denominator':5040,'graphs':meta['graphs'],'rows':rows}))
configs={}
for name,a,b,c,d in [('LL',20,24,20,24),('LH',20,24,24,28),('HH',24,28,24,28)]:configs[name]={'name':name,'box':[a,b,c,d],'grid':64,'cross':True,'ordered':True}
for name,cfg in configs.items():(out/(name+'-config.json')).write_text(json.dumps(cfg))
print('Generated',len(rows),'four-pattern joint rows')
