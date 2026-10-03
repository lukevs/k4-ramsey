import json,math,hashlib,platform
from fractions import Fraction as Q
from pathlib import Path
src=Path('reports/triangle-penalty-001')
d=json.loads((src/'coefficients.json').read_text());co={int(k):list(map(Q,v)) for k,v in d['coefficients'].items()}
eps=Q(3,10);a=-eps;b=eps
c={r:sum(z*a**(r-j)*b**j for j,z in enumerate(v)) for r,v in co.items()}
base=Q(d['base_F'])
def bound(rho):
 V=rho*(1-rho);m=max(rho,1-rho);B=c[4]-abs(c[5])*m
 assert B>0
 x=max(-rho**3,-c[3]*V/(2*B))
 lower=c[3]*x+B*x*x/V-c[6]*m*m*V*V
 return lower,dict(V=str(V),m=str(m),B=str(B),optimal_relaxed_triangle=str(x),floor_delta=str(lower),floor_F=str(base+lower),floor_decimal=float(base+lower))
records=json.loads((src/'screen.json').read_text())['records'];checks=[]
for r in records:
 rho=Q(r['rho']);V=rho*(1-rho);m=max(rho,1-rho)
 t3,t4,t5,t6=r['moments'];lo,info=bound(rho)
 assert t3*t3<=float(V)*t4+1e-13
 assert abs(t5)<=float(m)*t4+1e-13
 assert abs(t6)<=float(m*m*V*V)+1e-13
 F=base+sum(float(c[k])*r['moments'][k-3] for k in c)
 assert F>=float(base+lo)-1e-14
 if r['name'] in ('clebsch','C5x2','random_10_4_34'):
  checks.append(dict(name=r['name'],F=float(F),floor=info,spectral_ratio=t3*t3/(float(V)*t4),moments=r['moments']))
exact=json.loads((src/'exact-check.json').read_text())
for r in exact['results']:
 t3,t4,t5,t6=map(Q,r['moments']);rho=Q(2,5);V=rho*(1-rho);m=1-rho
 assert t3*t3<=V*t4 and abs(t5)<=m*t4 and abs(t6)<=m*m*V*V
 assert Q(r['F'])>=base+bound(rho)[0]
report=dict(coefficients={k:str(v) for k,v in c.items()},epsilon=str(eps),checks=checks,screen_checked=len(records),exact_checks=2,python=platform.python_version(),source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [src/'coefficients.json',src/'screen.json',src/'exact-check.json',Path(__file__)]})
Path('reports/spectral-bowl-001/check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
