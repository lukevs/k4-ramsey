"""Exact sanity checks on actual independent pattern probabilities in each box."""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
import json,hashlib
out=Path('reports/energy-bootstrap-joint-001');cases=0
for path in out.glob('*-config.json'):
 cfg=json.loads(path.read_text());a,b,c,d=[F(x,cfg['grid']) for x in cfg['box']]
 lower=[F(0),a,c,F(0)];upper=[1-a-c,b,d,1-a-c]
 for p1,p2,t in product([a,(a+b)/2,b],[c,(c+d)/2,d],[F(0),F(1,2),F(1)]):
  if p1>p2 or p1+p2>1:continue
  rest=1-p1-p2;p=[t*rest,p1,p2,(1-t)*rest]
  assert sum(p)==1
  for i in range(4):
   assert lower[i]<=p[i]<=upper[i]
   assert (lower[i]+upper[i])*p[i]-p[i]**2-lower[i]*upper[i]==(p[i]-lower[i])*(upper[i]-p[i])>=0
  for i in range(4):
   for j in range(i+1,4):
    assert p[i]*p[j]-lower[i]*p[j]-lower[j]*p[i]+lower[i]*lower[j]==(p[i]-lower[i])*(p[j]-lower[j])>=0
    assert p[i]*p[j]-upper[i]*p[j]-upper[j]*p[i]+upper[i]*upper[j]==(upper[i]-p[i])*(upper[j]-p[j])>=0
    assert upper[i]*p[j]+lower[j]*p[i]-p[i]*p[j]-upper[i]*lower[j]==(upper[i]-p[i])*(p[j]-lower[j])>=0
    assert lower[i]*p[j]+upper[j]*p[i]-p[i]*p[j]-lower[i]*upper[j]==(p[i]-lower[i])*(upper[j]-p[j])>=0
  cases+=1
r={'exact_probability_vectors_checked':cases,'all_factor_identities_pass':True,'scope':'Sanity checks supplement the elementary factor identities; not the global certificate.','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()};(out/'box-identity-check.json').write_text(json.dumps(r,indent=2));print(json.dumps(r))
