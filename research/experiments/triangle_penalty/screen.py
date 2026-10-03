import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import json,math,itertools as it,time,signal
from pathlib import Path
from fractions import Fraction as Q
import numpy as np,networkx as nx
from scipy.optimize import minimize_scalar
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s')));signal.alarm(175)
start=time.monotonic();out=Path('reports/triangle-penalty-001');d=json.loads((out/'coefficients.json').read_text());co={int(r):np.array([float(Q(v)) for v in vs]) for r,vs in d['coefficients'].items()}
def moments(A):
 n=len(A);rho=float(A[0].sum())/n;S=A-rho;S2=S@S;t6=0
 for a in range(n):
  X=S[a][None,:]*S;Y=X@S;t6+=S[a]@np.einsum('bc,bc->b',X,Y)
 return np.array([np.trace(S2@S)/n**3,np.sum(S2*S2)/n**4,np.sum(S*S2*S2)/n**4,t6/n**4])
records=[];graphs={}
for G in nx.graph_atlas_g():
 n=len(G)
 if n<4:continue
 ds=list(dict(G.degree()).values())
 if min(ds)==max(ds) and 0<ds[0]<n-1:graphs['atlas_'+str(n)+'_'+str(len(graphs))]=G
for n,k in [(8,3),(8,4),(10,4),(12,4),(12,6),(15,6),(16,5)]:
 for seed in range(35):graphs[f'random_{n}_{k}_{seed}']=nx.random_regular_graph(k,n,seed=seed)
# Equal-mass blowups of C5 preserve degree density2/5.
for m in (1,2,3):
 G=nx.Graph();G.add_nodes_from(range(5*m));G.add_edges_from((i,j) for i in G for j in G if i<j and ((i//m-j//m)%5 in (1,4)));graphs[f'C5x{m}']=G
for n in (4,6,8,10,12):graphs['Kbb'+str(n)]=nx.complete_bipartite_graph(n//2,n//2)
graphs['cube']=nx.cubical_graph()
graphs['clebsch']=nx.Graph([(x,x^s) for x in range(16) for s in (1,2,4,8,15)])
for name,G in graphs.items():
 A=nx.to_numpy_array(G,nodelist=sorted(G));n=len(A);k=int(A[0].sum());rho=Q(k,n);mu=moments(A);tau=Q(sum(nx.triangles(G).values())*2,n**3);assert abs(mu[0]-(float(tau)-float(rho)**3))<1e-14
 # fixed direction a=-epsilon,b=epsilon: exact same amplitude comparison
 pol=[float(mu[r-3]*sum(co[r][j]*(-1)**(r-j) for j in range(r+1))) for r in (3,4,5,6)]
 upper=min(float(Q(32,41)/(1-rho)),float(Q(9,41)/rho),float(Q(22,41)/rho),float(Q(19,41)/(1-rho)))
 record={'name':name,'n':n,'k':k,'rho':str(rho),'tau':str(tau),'moments':mu.tolist(),'poly3to6':pol,'upper_epsilon':upper,'edges':list(G.edges())};records.append(record)
comparisons=[]
for rho in set(r['rho'] for r in records):
 group=[r for r in records if r['rho']==rho];free=[r for r in group if Q(r['tau'])==0];tri=[r for r in group if Q(r['tau'])>0]
 for eps in (.01,.1,.3,.5):
  valid=lambda r:eps<=r['upper_epsilon'];f=[r for r in free if valid(r)];t=[r for r in tri if valid(r)]
  if not f or not t:continue
  val=lambda r:sum(c*eps**(i+3) for i,c in enumerate(r['poly3to6']))
  bestf=min(f,key=val);bestt=min(t,key=val)
  comparisons.append({'rho':rho,'epsilon':eps,'best_trianglefree':bestf['name'],'free_delta':val(bestf),'best_with_triangles':bestt['name'],'triangle_delta':val(bestt),'triangle_beats_best_free':val(bestt)<val(bestf)-1e-14})
report={'records':records,'comparisons':comparisons,'seconds':time.monotonic()-start};(out/'screen.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps({'graphs':len(records),'comparisons':comparisons,'seconds':report['seconds']},indent=2))
