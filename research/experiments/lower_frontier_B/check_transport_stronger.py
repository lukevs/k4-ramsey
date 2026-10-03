"""Independent exact checker: enumerate every ordered K4 latent tuple."""
from fractions import Fraction as F
from itertools import product,combinations
from pathlib import Path
import json,time,hashlib,sys,platform
START=time.monotonic(); OUT=Path('reports/lower-frontier-B-006'); OUT.mkdir(exist_ok=True)
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

# Merge the numerically duplicated classes and round all entries coarsely.
M=[[79,13,100,27,13,27],[13,100,13,100,7,18],[100,13,32,71,13,71],[27,100,71,40,18,73],[13,7,13,18,100,100],[27,18,71,73,100,40]]
W=[[F(v,100)for v in row]for row in M]
w=[F(v,100)for v in [19,15,15,18,15,18]];a=list(map(F,[1,1,0,0,1,0]))
eps=F(1,10000)
Wr=[row+[a[i]]for i,row in enumerate(W)]+[a+[F(1,2)]]
wr=[(1-eps)*p for p in w]+[eps]
res=exact(Wr,wr)
values=[F(res['cross'][-1]),F(res['same'][-1]),F(res['fR'][-1])+F(res['fB'][-1])]
threshold=F(28750881,1000000000)
assert max(values)<threshold
parent=Path('reports/lower-frontier-B-005/screen.json')
report={'hypothesis':'B2-minimax','W':[[str(v)for v in row]for row in Wr],'weights':[str(v)for v in wr],'exceptional_class':6,'exact':res,'local_at_exceptional_root':str(values[2]),'max_of_three':str(max(values)),'threshold':str(threshold),'margin':str(threshold-max(values)),'strict_counterexample':True,'seconds':time.monotonic()-START,'command':'python3 research/experiments/lower_frontier_B/check_transport_stronger.py','python':sys.version,'platform':platform.platform(),'sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'parent_sha256':hashlib.sha256(parent.read_bytes()).hexdigest(),'scope':'Exact rational positive-mass counterexample to ALL convex combinations of three pointwise transport functionals; not a c4 upper-bound improvement.'}
(OUT/'exact-counterexample.json').write_text(json.dumps(report,indent=2)+'\n')
print({k:float(v)for k,v in zip(['cross','same','local'],values)})
print('max_exact',str(max(values)),'c4',res['c4_decimal'],'seconds',report['seconds'])
