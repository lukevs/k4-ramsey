"""Screen disjoint four-vertex / three-vertex factorization at N7 witnesses."""
from itertools import combinations,permutations
from pathlib import Path
import json,time,hashlib
from fractions import Fraction as F
t0=time.monotonic();out=Path('reports/mixed-motif-screen-001');p4=list(combinations(range(4),2));p7=list(combinations(range(7),2));positions={e:i for i,e in enumerate(p4)}
canon=[]
for code in range(64):
 canon.append(min(sum(((code>>positions[tuple(sorted((v[i],v[j])))])&1)<<k for k,(i,j) in enumerate(p4)) for v in permutations(range(4))))
types=sorted(set(canon));assert len(types)==11;index={v:i for i,v in enumerate(types)};graphs=json.loads(Path('reports/energy-bootstrap-n7-001/metadata.json').read_text())['graphs'];rows=[]
for code in graphs:
 E={e for k,e in enumerate(p7) if code>>k&1};x=[0]*11;joint=[[0]*4 for _ in range(11)]
 for vs in combinations(range(7),4):
  c=sum((tuple(sorted((vs[a],vs[b]))) in E)<<k for k,(a,b) in enumerate(p4));i=index[canon[c]];rest=[v for v in range(7) if v not in vs];j=sum(e in E for e in combinations(rest,2));x[i]+=144;joint[i][j]+=144
 assert sum(x)==5040 and [sum(r) for r in joint]==x
 rows.append({'x4':x,'joint43':joint})
obs=json.loads(Path('reports/energy-bootstrap-joint-001/observables.json').read_text());runs=[]
for name,path in [('N7_control','reports/energy-bootstrap-n7-001/control.json'),('triple_factorization_diagnostic','reports/energy-bootstrap-auto-001/diagnostic.json')]:
 d=json.loads(Path(path).read_text());q=d['primal'];x4=[sum(w*r['x4'][i]/5040 for w,r in zip(q,rows)) for i in range(11)];x3=[sum(w*r['X'][j]/5040 for w,r in zip(q,obs['rows'])) for j in range(4)];delta=[[sum(w*r['joint43'][i][j]/5040 for w,r in zip(q,rows))-x4[i]*x3[j] for j in range(4)] for i in range(11)];worst=max(((abs(delta[i][j]),i,j) for i in range(11) for j in range(4)))
 runs.append({'name':name,'objective':d['objective'],'max_abs_violation':worst[0],'worst_four_vertex_code':types[worst[1]],'worst_triple_edges':worst[2],'K4_and_empty_four_violations':{'red':delta[index[63]],'blue':delta[index[0]]},'x3':x3,'x4':x4})
(out/'coefficients.json').write_text(json.dumps({'denominator':5040,'four_types':types,'graphs':graphs,'rows':rows}));result={'runs':runs,'seconds':time.monotonic()-t0,'numerical_screen_only':True,'scope':'No new SDP or bound; point exclusion does not establish optimum improvement. Coefficients need independent recount before certification.','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
