import numpy as np,json
from pathlib import Path
z=np.load('reports/global-coupled-pilot-001/coefficients.npz');meta=json.loads(Path('reports/global-coupled-pilot-003/coefficient-metadata.json').read_text());w=json.loads(Path('reports/global-coupled-pilot-003/baseline-feasible-witness.json').read_text());q=np.array(w['probability_numerators'])/w['denominator']
result=[]
for idx,b in enumerate(meta['extra']):
 if b['roots']!=4:continue
 # flags on5 vertices: bits involving extra vertex are positions3,6,8,9
 fs=b['flags'];degree=[sum((x>>i)&1 for i in (3,6,8,9)) for x in fs]
 for mode in ('degree','parity','extreme','all'):
  cls=degree if mode=='degree' else [v%2 for v in degree] if mode=='parity' else [0 if v==0 else 2 if v==4 else 1 for v in degree] if mode=='extreme' else list(range(len(fs)))
  R=np.array([[int(v==i) for v in cls] for i in sorted(set(cls))]);C=np.einsum('ai,gij,bj->gab',R,z['N6_'+str(idx)],R)
  eig=np.linalg.eigvalsh(np.einsum('g,gij->ij',q,C))[0]
  signatures=np.rint(C*720).astype(int).reshape(156,-1)
  result.append({'index':idx,'type':b['type'],'mode':mode,'dim':len(R),'min_eigenvalue':float(eig),'states':len({tuple(v) for v in signatures})})
print(json.dumps(sorted(result,key=lambda r:r['min_eigenvalue'])[:20],indent=2));Path('reports/compressed-consistency-001/screen.json').write_text(json.dumps(result,indent=2)+'\n')
