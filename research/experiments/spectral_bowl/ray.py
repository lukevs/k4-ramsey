"""Rational interval certificate covering every feasible a=-epsilon,b=epsilon."""
import json,time,signal
from fractions import Fraction as Q
from pathlib import Path
signal.signal(signal.SIGALRM,lambda *_:(_ for _ in ()).throw(TimeoutError()));signal.alarm(175)
src=Path('reports/triangle-penalty-001');d=json.loads((src/'coefficients.json').read_text());base=Q(d['base_F'])
k={int(r):sum(Q(z)*(-1)**(int(r)-j) for j,z in enumerate(v)) for r,v in d['coefficients'].items()}
assert k[3]>0 and k[4]>0 and k[6]>0
records=json.loads((src/'screen.json').read_text())['records'];out=[];start=time.monotonic()
for rho,name in [(Q(5,16),'clebsch'),(Q(2,5),'random_10_4_34')]:
 V=rho*(1-rho);m=max(rho,1-rho)
 U=min(Q(32,41)/(1-rho),Q(9,41)/rho,Q(22,41)/rho,Q(19,41)/(1-rho))
 count=4000;lowest=None;winning=None
 for i in range(count):
  lo=U*i/count;hi=U*(i+1)/count
  # If x=t3>=0, dropping the nonnegative cubic costs nothing.
  B=k[4]*lo**4-abs(k[5])*m*hi**5
  rem=k[6]*hi**6*m*m*V*V
  if B>0:
   x=max(-rho**3,-k[3]*hi**3*V/(2*B))
   floor=k[3]*hi**3*x+B*x*x/V-rem
  else:floor=-k[3]*hi**3*rho**3+B*V*V-rem
  if lowest is None or floor<lowest:lowest=floor;winning=[str(lo),str(hi)]
 rec=next(r for r in records if r['name']==name);p=[float(k[r])*rec['moments'][r-3] for r in (3,4,5,6)]
 f=lambda e:sum(v*e**r for r,v in zip((3,4,5,6),p))
 j=min(range(10001),key=lambda j:f(float(U)*j/10000));l=float(U)*max(0,j-1)/10000;h=float(U)*min(10000,j+1)/10000
 for _ in range(70):
  x=l+(h-l)/3;y=h-(h-l)/3
  if f(x)<f(y):h=y
  else:l=x
 e=(l+h)/2
 out.append(dict(rho=str(rho),epsilon_max=str(U),intervals=count,rigorous_floor=str(base+lowest),floor_decimal=float(base+lowest),worst_interval=winning,comparison_graph=name,numerical_best_epsilon=e,numerical_graph_F=float(base)+f(e),gap=float(base)+f(e)-float(base+lowest)))
report=dict(results=out,seconds=time.monotonic()-start,scope='Regular [0,1] latent kernels with fixed rho; feasibility range guarantees all entries; a=-epsilon,b=epsilon; coarse p=32/41,h=22/41. Rational spectral inequality certificate, conditional on saved coarse expansion.')
Path('reports/spectral-bowl-001/ray.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
