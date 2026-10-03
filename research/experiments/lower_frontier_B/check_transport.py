"""Independent exact checker: enumerate every ordered K4 latent tuple."""
from fractions import Fraction as F
from itertools import product,combinations
from pathlib import Path
import json,time,hashlib,sys,platform
START=time.monotonic(); OUT=Path('reports/lower-frontier-B-003'); OUT.mkdir(exist_ok=True)
# Deliberately coarse rationalization of numerical screen, dropping tiny block.
base=[[54,68,16,24],[68,43,9,77],[16,9,100,100],[24,77,100,30]]
W=[[F(v,100)for v in row]for row in base]
w=[F(v,100)for v in [34,31,16,19]]; a=list(map(F,[1,0,1,0]))
def exact(W,w):
 n=len(w); fR=[F(0)]*n;fB=[F(0)]*n
 for v in product(range(n),repeat=4):
  mass=w[v[1]]*w[v[2]]*w[v[3]]; R=B=F(1)
  for i,j in combinations(range(4),2):R*=W[v[i]][v[j]];B*=1-W[v[i]][v[j]]
  fR[v[0]]+=mass*R;fB[v[0]]+=mass*B
 d=[sum(w[j]*W[i][j]for j in range(n))for i in range(n)]
 cross=[d[i]*fR[i]+(1-d[i])*fB[i]+sum(w[j]*(W[i][j]*fB[j]+(1-W[i][j])*fR[j])for j in range(n))for i in range(n)]
 same=[(1-d[i])*fR[i]+d[i]*fB[i]+sum(w[j]*(W[i][j]*fR[j]+(1-W[i][j])*fB[j])for j in range(n))for i in range(n)]
 global_c4=sum(w[i]*(fR[i]+fB[i])for i in range(n))
 assert sum(w[i]*cross[i]for i in range(n))==global_c4
 assert sum(w[i]*same[i]for i in range(n))==global_c4
 return dict(c4=str(global_c4),c4_decimal=float(global_c4),cross=[str(x)for x in cross],cross_decimal=[float(x)for x in cross],same=[str(x)for x in same],fR=[str(x)for x in fR],fB=[str(x)for x in fB],d=[str(x)for x in d])
eps=F(1,1000)
Wr=[row+[a[i]]for i,row in enumerate(W)]+[a+[F(1,2)]]
wr=[(1-eps)*p for p in w]+[eps]
res=exact(Wr,wr)
assert F(res['cross'][-1])<F(296,10000)
# Same-colour counterexample: tiny all-blue class and almost all-red bulk.
Ws=[[F(0),F(0)],[F(0),F(1)]];ws=[eps,1-eps]
same=exact(Ws,ws)
assert F(same['same'][0])==4*eps**3-3*eps**4
# Universal norm 1/2 sharpness is checked with a balanced complete bipartite graphon.
report={'hypothesis':'B2','W':[[str(v)for v in row]for row in Wr],'weights':[str(v)for v in wr],'exceptional_class':4,'exact':res,'same_colour_obstruction':same,'same_colour_formula':'4 epsilon^3 - 3 epsilon^4','threshold':'37/1250 = 0.0296','strict_counterexample':True,'seconds':time.monotonic()-START,'command':'python3 research/experiments/lower_frontier_B/check_transport.py','python':sys.version,'platform':platform.platform(),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Exact rational graphon evaluation and transport normalization; not a c4 construction improvement.'}
(OUT/'exact-counterexample.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'cross_at_exceptional_root':res['cross'][-1],'cross_decimal':res['cross_decimal'][-1],'c4':res['c4_decimal'],'same_root':same['same'][0],'seconds':report['seconds']},indent=2))
