"""Independent integer enumeration of the latent motifs in the screen's pair."""
import itertools,json
from fractions import Fraction as Q
from pathlib import Path
out=Path('reports/triangle-penalty-001')
data=json.loads((out/'screen.json').read_text())
coeff=json.loads((out/'coefficients.json').read_text())
co={int(r):list(map(Q,v)) for r,v in coeff['coefficients'].items()}
a,b=-Q(3,10),Q(3,10)
results=[]
for name in ('C5x2','random_10_4_34'):
 rec=next(r for r in data['records'] if r['name']==name)
 n=rec['n'];A=[[0]*n for _ in range(n)]
 for i,j in rec['edges']:A[i][j]=A[j][i]=1
 assert all(sum(row)==4 for row in A) and n==10
 M=[[5*x-2 for x in row] for row in A]
 assert all(sum(row)==0 for row in M)
 totals=[0]*4
 for i,j,k in itertools.product(range(n),repeat=3):totals[0]+=M[i][j]*M[j][k]*M[k][i]
 for i,j,k,l in itertools.product(range(n),repeat=4):
  totals[1]+=M[i][j]*M[j][k]*M[k][l]*M[l][i]
  totals[2]+=M[i][j]*M[i][k]*M[j][k]*M[i][l]*M[j][l]
  totals[3]+=M[i][j]*M[i][k]*M[i][l]*M[j][k]*M[j][l]*M[k][l]
 mu=[Q(totals[0],n**3*5**3)]+[Q(totals[r-3],n**4*5**r) for r in (4,5,6)]
 tau=sum(A[i][j]*A[j][k]*A[k][i] for i,j,k in itertools.product(range(n),repeat=3))
 assert mu[0]==Q(tau,n**3)-Q(2,5)**3
 terms=[mu[r-3]*sum(c*a**(r-j)*b**j for j,c in enumerate(co[r])) for r in (3,4,5,6)]
 delta=sum(terms)
 levels={t:[v+amp*s for s in (-Q(2,5),Q(3,5))] for t,v,amp in [('P',Q(32,41),a),('H',Q(22,41),b)]}
 assert all(0<=v<=1 for vs in levels.values() for v in vs)
 assert all(abs(float(m)-f)<1e-14 for m,f in zip(mu,rec['moments']))
 results.append({'name':name,'triangle_count':tau//6,'tau':str(Q(tau,n**3)),'moments':list(map(str,mu)),'terms':list(map(str,terms)),'delta':str(delta),'delta_decimal':float(delta),'F':str(Q(coeff['base_F'])+delta),'levels':{k:list(map(str,v)) for k,v in levels.items()}})
diff=Q(results[1]['delta'])-Q(results[0]['delta'])
assert Q(results[0]['delta'])>0>Q(results[1]['delta']) and diff<0
report={'method':'Pure Python integer ordered-tuple enumeration; exact rational substitution into coarse expansion. No full lifted-matrix recount.','results':results,'triangle_minus_trianglefree':str(diff),'difference_decimal':float(diff)}
(out/'exact-check.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
