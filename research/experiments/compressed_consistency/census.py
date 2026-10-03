from pathlib import Path
import json,itertools as it,time
import numpy as np
start=time.monotonic();z=np.load('reports/global-coupled-pilot-001/coefficients.npz');g5=z['graphs5'];g6=z['graphs6'];P=z['P'];den=6
m5=[int(A.sum())//2 for A in g5]
def tri(A):return sum(all(A[a,b] for a,b in it.combinations(S,2)) for S in it.combinations(range(len(A)),3))
def mono(A):return sum(len({int(A[a,b]) for a,b in it.combinations(S,2)})==1 for S in it.combinations(range(len(A)),4))
features={'edge_count':[(m,) for m in m5],'edge_triangle':[(m,tri(A)) for m,A in zip(m5,g5)],'edge_monoK4':[(m,mono(A)) for m,A in zip(m5,g5)],'degree_sequence':[tuple(sorted(map(int,A.sum(axis=1)))) for A in g5],'full_N5':list(range(34))}
result={}
for name,f in features.items():
 vals=sorted(set(f));C=np.array([[int(x==v) for x in f] for v in vals]);T=np.rint(6*C@P).astype(int);hist=[tuple(T[:,i]) for i in range(156)]
 result[name]={'lower_states':len(vals),'upper_deletion_profiles':len(set(hist))}
print(json.dumps(result,indent=2));Path('reports/compressed-consistency-001/census.json').write_text(json.dumps(result,indent=2)+'\n')
