"""Check exhaustive coverage when reusing four N6 and two N7 certificates."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
out=Path('reports/energy-bootstrap-n7-001');old=Path('reports/energy-bootstrap-001')
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
cert=json.loads((old/'certificate.json').read_text());receipt=json.loads((old/'independent-check.json').read_text());assert receipt['certificate_sha256']==sha(old/'certificate.json')
tables=json.loads((out/'table-check-receipt.json').read_text());assert tables['hashes'][str(out/'coefficients.bin')]==sha(out/'coefficients.bin')
branches=[]
for b in cert['branches']:
 a,e=map(F,b['interval'])
 if (a,e) in [(F(5,16),F(3,8)),(F(3,8),F(7,16))]:
  name='0.3125_0.375' if a==F(5,16) else '0.375_0.4375';path=out/(name+'-certificate.json');b=json.loads(path.read_text());check=json.loads((out/(name+'-check.json')).read_text());assert check['certificate_sha256']==sha(path) and check['bound']==b['bound'] and check['coefficient_sha256']==sha(out/'coefficients.bin');level=7
 else:level=6;path=old/'certificate.json'
 branches.append({'interval':[str(a),str(e)],'bound':b['bound'],'level':level,'certificate':str(path),'certificate_sha256':sha(path)})
end=F(0)
for b in branches:
 a,e=map(F,b['interval']);assert a==end and e>a;end=e
assert end==1
bound=min(F(b['bound']) for b in branches);control=json.loads((out/'control-check.json').read_text());assert control['certificate_sha256']==sha(out/'control-certificate.json');gain=bound-F(control['bound']);assert gain>0
r={'bound':str(bound),'bound_decimal':float(bound),'N7_control_bound':control['bound'],'certified_increase':str(gain),'increase_decimal':float(gain),'branches':branches,'coverage':'[0,1] exactly','scope':'Universal graphon lower bound, exact computer-assisted certificate. Below published frontier; not a novelty claim.','source_sha256':sha(Path(__file__))}
(out/'combined-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps({k:v for k,v in r.items() if k!='branches'},indent=2))
