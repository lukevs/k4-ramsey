"""Independent integer arithmetic audit of the saved seven-class artifact."""
from pathlib import Path
from fractions import Fraction as F
import json,itertools,hashlib,time
START=time.monotonic();p=Path('reports/lower-frontier-B-006/exact-counterexample.json');j=json.loads(p.read_text())
A=[[int(F(v)*100)for v in row]for row in j['W']];m=[int(F(v)*10**6)for v in j['weights']];n=len(m)
assert sum(m)==10**6 and all(F(j['weights'][i])==F(m[i],10**6)for i in range(n))
assert all(F(j['W'][i][k])==F(A[i][k],100)for i in range(n)for k in range(n))
R=[];B=[]
# Multiply triangle tensor first, then each root's three attachments.
tri=[]
for b,c,d in itertools.product(range(n),repeat=3):
 mass=m[b]*m[c]*m[d]
 tri.append((b,c,d,mass*A[b][c]*A[b][d]*A[c][d],mass*(100-A[b][c])*(100-A[b][d])*(100-A[c][d])))
for a in range(n):
 R.append(sum(t*A[a][b]*A[a][c]*A[a][d]for b,c,d,t,u in tri))
 B.append(sum(u*(100-A[a][b])*(100-A[a][c])*(100-A[a][d])for b,c,d,t,u in tri))
assert [F(v,10**30)for v in R]==list(map(F,j['exact']['fR']))
assert [F(v,10**30)for v in B]==list(map(F,j['exact']['fB']))
d=[sum(m[b]*A[a][b]for b in range(n))for a in range(n)]
cross=[d[a]*R[a]+(10**8-d[a])*B[a]+sum(m[b]*(A[a][b]*B[b]+(100-A[a][b])*R[b])for b in range(n))for a in range(n)]
same=[(10**8-d[a])*R[a]+d[a]*B[a]+sum(m[b]*(A[a][b]*R[b]+(100-A[a][b])*B[b])for b in range(n))for a in range(n)]
assert list(map(lambda v:F(v,10**38),cross))==list(map(F,j['exact']['cross']))
assert list(map(lambda v:F(v,10**38),same))==list(map(F,j['exact']['same']))
a=j['exceptional_class'];maximum=max(F(cross[a],10**38),F(same[a],10**38),F(R[a]+B[a],10**30))
assert maximum<F(28750881,10**9)
# Integer global averaging identities, with the necessary denominator factor.
obj=sum(m[a]*(R[a]+B[a])for a in range(n))
assert sum(m[a]*cross[a]for a in range(n))==10**8*obj
assert sum(m[a]*same[a]for a in range(n))==10**8*obj
out={'checked':True,'algorithm':'Independent integer triangle tensor followed by root attachments; no imports from search or Fraction enumerator.','maximum':str(maximum),'margin_to_checked_N6':str(F(28750881,10**9)-maximum),'input_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.monotonic()-START,'processes_remaining':0}
Path('reports/lower-frontier-B-006/independent-integer-audit.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
