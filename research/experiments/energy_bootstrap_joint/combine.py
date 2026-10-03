"""Exact rectangular coverage modulo colour complement; retain valid parent bounds."""
from pathlib import Path
from fractions import Fraction as F
import json,hashlib
out=Path('reports/energy-bootstrap-joint-001');sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest();certs=[]
for p in sorted(out.glob('*-check.json')):
 check=json.loads(p.read_text())
 if 'config' not in check:continue
 cp=out/(check['name']+'-certificate.json');assert check['certificate_sha256']==sha(cp);cert=json.loads(cp.read_text());assert cert['bound']==check['bound']
 assert cert['config']['ordered'] and cert['config']['grid'] in (64,128)
 certs.append({'name':check['name'],'box':[F(v,cert['config']['grid']) for v in cert['config']['box']],'bound':F(cert['bound']),'certificate':str(cp),'sha256':sha(cp)})
assert certs
lo,hi=F(5,16),F(7,16);breaks=sorted({lo,hi}|{v for c in certs for v in c['box'] if lo<=v<=hi});samples=sorted(set(breaks+[(a+b)/2 for a,b in zip(breaks,breaks[1:])]))
values=[];weak=[]
for x in samples:
 for y in samples:
  if x>y:continue
  available=[c for c in certs if c['box'][0]<=x<=c['box'][1] and c['box'][2]<=y<=c['box'][3]]
  assert available,('coverage gap',x,y)
  best=max(c['bound'] for c in available);values.append(best);weak.append((best,x,y,[c['name'] for c in available if c['bound']==best]))
# Four outer intervals apply to either p1(W) or p1(complement W)=p2(W).
old=Path('reports/energy-bootstrap-001');oc=json.loads((old/'certificate.json').read_text());orr=json.loads((old/'independent-check.json').read_text());assert orr['certificate_sha256']==sha(old/'certificate.json')
outer=[]
for b in oc['branches']:
 a,e=map(F,b['interval'])
 if e<=lo or a>=hi:outer.append((a,e,F(b['bound'])))
assert [(a,b) for a,b,_ in outer]==[(F(0),F(1,4)),(F(1,4),lo),(hi,F(1,2)),(F(1,2),F(1))]
bound=min(min(values),min(b for _,_,b in outer));prior=F(json.loads(Path('reports/energy-bootstrap-n7-001/combined-check.json').read_text())['bound']);worst=min(weak,key=lambda v:v[0])
record={'bound':str(bound),'bound_decimal':float(bound),'previous_bound':str(prior),'increase':str(bound-prior),'increase_decimal':float(bound-prior),'central_certificates':[{'name':c['name'],'box':[str(v) for v in c['box']],'bound':str(c['bound']),'certificate_sha256':c['sha256']} for c in certs],'central_coverage_samples':len(values),'coverage':'All arrangement cells, edges and vertices in [5/16,7/16]^2 with p1<=p2; colour complement covers reverse order; existing N6 bounds cover either coordinate outside the square.','weakest_sample':{'p1':str(worst[1]),'p2':str(worst[2]),'certificates':worst[3]},'source_sha256':sha(Path(__file__))}
# Keep chronological certificates rather than overwrite earlier combined results.
path=out/('combined-'+str(len(certs))+'-check.json');path.write_text(json.dumps(record,indent=2)+'\n');print(json.dumps({k:v for k,v in record.items() if k!='central_certificates'},indent=2))
