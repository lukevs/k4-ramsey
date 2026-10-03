import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,json
from pathlib import Path
from scipy.optimize import minimize_scalar
out=Path('reports/flexible-mechanisms-001');old=json.loads(Path('reports/graph-arrangements-001/mixed-summary.json').read_text());p=.779180833031354;h=.5342651880306992
A=np.array([[int((i^j) in (1,2,4,8,15)) for j in range(16)] for i in range(16)]);R=A+2*np.eye(16,dtype=int);v=np.indices((16,)*4).reshape(4,-1);edges={3:[(0,1),(1,2),(2,0)],4:[(0,1),(1,2),(2,3),(3,0)],5:[(0,1),(0,2),(1,2),(0,3),(1,3)],6:[(0,1),(0,2),(1,2),(0,3),(1,3),(2,3)]}
# Precompute tuples as three latent relation indices for every coarse word.
rows=[(w['degree'],w['coefficient'],w['word'],[R[v[i],v[j]] for i,j in edges[w['degree']]]) for w in old['coarse_words']]
def objective(e,details=False):
 probs=np.array([[2*p-e,e,5*e-4*p],[16*h/10,0,0]]);D=probs-np.array([[p],[h]]);terms=np.zeros(4)
 for deg,c,word,rels in rows:
  prod=np.ones(16**4)
  for typ,rel in zip(word,rels):prod*=D[typ,rel]
  terms[deg-3]+=c*prod.mean()
 return (probs,terms) if details else sum(terms)*1e10
lo=max(0,2*p-1,4*p/5);hi=min(1,2*p,(1+4*p)/5)
r=minimize_scalar(objective,bounds=(lo,hi),method='bounded',options={'xatol':1e-14});pr,terms=objective(r.x,True)
best=json.loads((out/'ablation.json').read_text())['runs'][-1]
report=dict(constraint='P diagonal = 5 P edge - 4p; kills adjacency -3 eigenspace exactly. H diagonal=edge=0.',probabilities=pr.tolist(),terms=terms.tolist(),F=old['base_F']+float(sum(terms)),loss_vs_flexible=float(sum(terms))-best['delta'],fraction_gain_retained=float(sum(terms))/best['delta'],success=bool(r.success))
(out/'projector.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
