"""Independent invariant-root recount and exact deletion factorization audit."""
from pathlib import Path
from itertools import combinations,permutations
import json,time
import numpy as np
start=time.monotonic();out=Path('reports/compressed-consistency-001');z=np.load('reports/global-coupled-pilot-001/coefficients.npz');g5=z['graphs5'];g6=z['graphs6'];patterns=[(1,1,1,3),(0,2,2,2)]
# Independently construct all5 labelled isomorphism lookups and6->5 deletion.
pairs5=list(combinations(range(5),2));lookup={}
for i,A in enumerate(g5):
 for p in permutations(range(5)):
  bits=sum(int(A[p[a],p[b]])<<k for k,(a,b) in enumerate(pairs5));assert bits not in lookup or lookup[bits]==i;lookup[bits]=i
assert len(lookup)==1024
D=np.zeros((34,156),dtype=int)
for j,A in enumerate(g6):
 for p in combinations(range(6),5):
  bits=sum(int(A[p[a],p[b]])<<k for k,(a,b) in enumerate(pairs5));D[lookup[bits],j]+=1
assert np.array_equal(D,np.rint(z['P']*6).astype(int))
checks={}
for mode in ('edge','edge_k4','root_degree'):
 a=np.load(out/(mode+'-coefficients.npz'));dim=5 if mode=='root_degree' else 2
 B=np.zeros((2,156,dim,dim),dtype=int);L=np.zeros((2,dim,34),dtype=int)
 for n,graphs in [(5,g5),(6,g6)]:
  for gi,A in enumerate(graphs):
   for S in combinations(range(n),4):
    deg=tuple(sorted(sum(int(A[x,y]) for y in S if x!=y) for x in S))
    if deg not in patterns:continue
    k=patterns.index(deg);outside=sorted(set(range(n))-set(S));ds=[sum(int(A[x,y]) for y in S) for x in outside]
    if dim==2:ds=[v%2 for v in ds]
    if n==5:L[k,ds[0],gi]+=6
    else:
     i,j=ds;B[k,gi,i,j]+=6;B[k,gi,j,i]+=6
 assert np.array_equal(L,a['rowmaps_integer'])
 assert np.array_equal(B,a['Cs_integer'][:,a['inv']])
 assert np.array_equal(a['T_integer'][:,a['inv']],a['C']@D)
 for k in range(2):assert np.array_equal(L[k]@D,B[k].sum(axis=2).T)
 # Assess saved numerical feasible extension, not an exact infeasibility claim.
 report=json.loads((out/('degree-result.json' if mode=='root_degree' else 'result.json')).read_text())
 r=next(r for r in report['runs'] if r['mode']==mode and r['fixed_witness']);p=np.array(r['p']);q=np.array(r['q'])
 residual=max(abs(a['C']@p-a['T_integer']/6@q));eig=[]
 for k in range(2):
  M=np.einsum('g,gij->ij',q,a['Cs_integer'][k]/720);eig.append(float(np.linalg.eigvalsh(M)[0]));residual=max(residual,max(abs(M.sum(axis=1)-L[k]/120@p)))
 checks[mode]={'states':len(q),'exact_all_graph_map_checks':True,'numerical_extension_residual':float(residual),'min_eigenvalues':eig,'minimum_probability':float(q.min())}
result={'checks':checks,'labelled5coverage':len(lookup),'seconds':time.monotonic()-start,'scope':'Independent root-degree invariant counting, all graph deletion identities and compression maps exact; feasible extension only numerical.'}
(out/'independent-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
