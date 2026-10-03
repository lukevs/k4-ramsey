"""Independent subset-based integer enumeration, without solver coefficient code."""
from itertools import combinations,permutations
from pathlib import Path
import json,time,hashlib
import numpy as np
start=time.monotonic();out=Path('reports/edge-optimality-001');d=np.load(out/'coefficients.npz');vertex=np.load(out/'vertex-coefficients.npz');graphs=d['graphs'];E=np.zeros_like(d['counts']);F=np.zeros_like(vertex['flag']);K=np.zeros_like(F)
for g,A in enumerate(graphs):
 for x,y in permutations(range(6),2):
  rest=set(range(6))-{x,y}
  for a,b in combinations(sorted(rest),2):
   s,t=sorted(rest-{a,b});es=[A[x,a],A[y,a],A[x,b],A[y,b],A[a,b]]
   derivative=int(all(es))-int(not any(es));i=int(A[x,s]+2*A[y,s]);j=int(A[x,t]+2*A[y,t])
   for k,l in [(i,j),(j,i)]:
    E[0,g,k,l]-=2*int(A[x,y])*derivative
    E[1,g,k,l]+=2*(1-int(A[x,y]))*derivative
 for xs in combinations(range(6),4):
  es=[A[a,b] for a,b in combinations(xs,2)];mono=int(all(es) or not any(es));s,t=sorted(set(range(6))-set(xs))
  for x in xs:
   i=int(A[x,s]);j=int(A[x,t])
   for k,l in [(i,j),(j,i)]:F[g,k,l]+=6;K[g,k,l]+=6*mono
assert np.array_equal(E,d['counts'])
assert np.array_equal(F,vertex['flag']) and np.array_equal(K,vertex['clique'])
# Check expectation on constant graphons, using independently enumerated graph orbit sizes.
from math import factorial
import networkx as nx
ps=[0,.25,.5,.75,1];errors=[]
for p in ps:
 probs=[]
 for A in graphs:
  G=nx.from_numpy_array(A);aut=sum(1 for _ in nx.algorithms.isomorphism.GraphMatcher(G,G).isomorphisms_iter());e=int(A.sum())//2
  probs.append(factorial(6)/aut*p**e*(1-p)**(15-e))
 probs=np.array(probs); f=np.array([(1-p)**2,p*(1-p),p*(1-p),p*p]);D=p**5-(1-p)**5
 expect=[-p*D*np.outer(f,f),(1-p)*D*np.outer(f,f)]
 for k in range(2):assert np.max(abs(np.einsum('g,gij->ij',probs,E[k]/720)-expect[k]))<1e-14
 v=np.array([1-p,p]);expected=(3767361/125000000-p**6-(1-p)**6)*np.outer(v,v)
 assert np.max(abs(np.einsum('g,gij->ij',probs,(3767361/125000000*F-K)/720)-expected))<1e-14
r={'graphs':len(graphs),'all_integer_coefficients_match':True,'constant_graphon_controls':ps,'seconds':time.monotonic()-start,'scope':'Independent subset enumeration of both edge localizers and vertex feature matrix; constant graphon expectation/sign controls; no proof of a higher bound.'}
(out/'independent-coefficients.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r))
