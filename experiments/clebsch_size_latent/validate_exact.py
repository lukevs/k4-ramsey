import os
for key in ['VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']:os.environ[key]='1'
from fractions import Fraction as F
from itertools import product,combinations
import json,time,signal
signal.alarm(175); start=time.time()
E=list(combinations(range(4),2))
P=[[F(3,8),F(5,8),F(1,2)],[F(5,8),F(1,4),F(3,8)],[F(1,2),F(3,8),F(7,8)]]
A=[[F(0),F(1,8),F(-1,8)],[F(1,8),F(0),F(1,8)],[F(-1,8),F(1,8),F(0)]]
w=[F(1,6),F(2,6),F(3,6)]; s=[F(1),F(1,4),F(-1,2)]
K=[[x*y for y in s] for x in s]
assert sum(x*y for x,y in zip(w,s))==0
# Integer direct recount: full matrix denominator 512, masses [1,2,3] per base.
Q=512; N=[[int(Q*(P[u][v]+A[u][v]*K[a][b])) for v in range(3) for b in range(3)] for u in range(3) for a in range(3)]
weights=[1,2,3]*3
def literal(N,Q,w):
    total=0
    for ids in product(range(len(w)),repeat=4):
        r=b=mass=1
        for i in ids:mass*=w[i]
        for i,j in E:r*=N[ids[i]][ids[j]];b*=Q-N[ids[i]][ids[j]]
        total+=mass*(r+b)
    return F(total,sum(w)**4*Q**6)
f=literal(N,Q,weights); f0=literal([[int(8*x) for x in row] for row in P],8,[1]*3)
# Independent exact edge-subset enumeration, grouped by edge count.
terms={i:F(0) for i in range(1,7)}
for mask in range(1,64):
    chosen=[i for i in range(6) if mask>>i&1]; deg=[0]*4
    for e in chosen:
        i,j=E[e];deg[i]+=1;deg[j]+=1
    moments=[sum(w[a]*s[a]**d for a in range(3)) for d in deg]
    moment=F(1)
    for x in moments:moment*=x
    if not moment:continue
    total=F(0)
    for ids in product(range(3),repeat=4):
        r=b=F(1)
        for e,(i,j) in enumerate(E):
            if e in chosen:r*=A[ids[i]][ids[j]];b*=-A[ids[i]][ids[j]]
            else:r*=P[ids[i]][ids[j]];b*=1-P[ids[i]][ids[j]]
        total+=(r+b)/81
    terms[len(chosen)]+=moment*total
assert f-f0==sum(terms.values())
# Duplicate final type unequally: original mass 3 becomes 1+2.
idx=[3*u+a for u in range(3) for a in [0,1,2,2]]
fd=literal([[N[i][j] for j in idx] for i in idx],Q,[1,2,1,2]*3)
assert fd==f
report=dict(exact_density=str(f),exact_delta=str(f-f0),exact_polynomial_delta=str(sum(terms.values())),exact_duplicate_equal=fd==f,terms={k:str(v) for k,v in terms.items()},elapsed=time.time()-start)
json.dump(report,open('reports/clebsch-size-latent-001/exact-validation.json','w'),indent=2)
print(report)
