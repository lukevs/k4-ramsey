import os
os.environ['OPENBLAS_NUM_THREADS']='1'
import numpy as np,json,hashlib
from pathlib import Path
out=Path('reports/flexible-mechanisms-001');old=json.loads(Path('reports/graph-arrangements-001/mixed-summary.json').read_text());data=json.loads((out/'alignment.json').read_text());ab=json.loads((out/'ablation.json').read_text());p=.779180833031354;h=.5342651880306992
A=np.array([[int((i^j) in (1,2,4,8,15)) for j in range(16)] for i in range(16)]);rel=A+2*np.eye(16,dtype=int);v=np.indices((16,)*4).reshape(4,-1)
edges={3:[(0,1),(1,2),(2,0)],4:[(0,1),(1,2),(2,3),(3,0)],5:[(0,1),(0,2),(1,2),(0,3),(1,3)],6:[(0,1),(0,2),(1,2),(0,3),(1,3),(2,3)]}
errors=[]
for r in ab['runs']+data['runs']:
 perm=r.get('permutation',list(range(16)));probs=np.array(r['probabilities']);P=(probs[0]-p)[rel];H=(probs[1]-h)[rel[np.ix_(perm,perm)]]
 assert np.max(abs(P.sum(1)))<1e-12 and np.max(abs(H.sum(1)))<1e-12
 assert probs.min()>-1e-8 and probs.max()<1+1e-8
 vals=np.zeros(4)
 for w in old['coarse_words']:
  prod=np.ones(16**4)
  for (i,j),t in zip(edges[w['degree']],w['word']):prod*=(P if t==0 else H)[v[i],v[j]]
  vals[w['degree']-3]+=w['coefficient']*prod.mean()
 error=float(np.max(abs(vals-r['terms'])));assert error<1e-18;errors.append(error)
 if r['label']=='both_diagonals':
  # Exact Clebsch eigenspaces: adjacency 1 multiplicity10 and -3 multiplicity5.
  modes=[]
  for lam,mult in [(1,10),(-3,5)]:
   lp=(probs[0,1]-probs[0,0])*lam+probs[0,2]-probs[0,0]
   lh=(probs[1,1]-probs[1,0])*lam+probs[1,2]-probs[1,0]
   modes.append(dict(adjacency_eigenvalue=lam,multiplicity=mult,P_eigenvalue=lp/16,H_eigenvalue=lh/16,P_squared_mass=mult*(lp/16)**2))
  eig=np.linalg.eigvalsh(A);assert np.allclose(eig,[-3]*5+[1]*10+[5])
  spectral=dict(modes=modes,fraction_P_squared_mass_in_negative_H=modes[0]['P_squared_mass']/sum(x['P_squared_mass'] for x in modes),trace_PPH=float(np.trace(P@P@H)/16**3),commutator=float(np.linalg.norm(P@H-H@P)))
report=dict(direct_ordered_tuple_cases=len(errors),max_error=max(errors),spectral=spectral,scope='Independent latent tuple products vs grouped polynomial; uses same saved coarse coefficients, no full 3072-class recount.')
(out/'check.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
files=list(Path('experiments/flexible_mechanisms').glob('*.py'))+list(out.glob('*.json'))
(out/'manifest.json').write_text(json.dumps({str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},indent=2)+'\n')
