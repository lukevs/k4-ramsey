import search
from search import np,fg,OUT
from evaluator import evaluate
import json, fractions, itertools, math, hashlib
rng=np.random.default_rng(410)
checks=[]
for n in (1,2,3,4):
    W=rng.uniform(.1,.9,(n,n));W=(W+W.T)/2;m=rng.dirichlet(np.ones(n)); f,g,h=fg(W,m)
    ref=evaluate(W.tolist(),m.tolist()); errors=[]
    for i in range(n):
        for j in range(i,n):
            D=np.zeros_like(W);D[i,j]=D[j,i]=1;eps=1e-6
            fd=(fg(W+eps*D,m)[0]-fg(W-eps*D,m)[0])/(2*eps)
            errors.append(abs(fd-g[i,j]*(1 if i==j else 2)))
    for i in range(n):
        D=np.eye(n)[i];eps=1e-6
        errors.append(abs((fg(W,m+eps*D)[0]-fg(W,m-eps*D)[0])/(2*eps)-h[i]))
    perm=rng.permutation(n)
    row={'n':n,'oracle_error':abs(ref['objective']-f),'gradient_error':max(errors),'complement_error':abs(f-fg(1-W,m)[0]),'permutation_error':abs(f-fg(W[np.ix_(perm,perm)],m[perm])[0]),'repeat_contribution':ref['repeat_contribution']}
    assert max(row[k] for k in ('oracle_error','complement_error','permutation_error'))<1e-12
    assert max(errors)<1e-8
    checks.append(row)
# Exact rational repeated-index fixture, and split invariance.
Q=fractions.Fraction; W=[[Q(1,3),Q(2,5)],[Q(2,5),Q(3,4)]];m=[Q(2,7),Q(5,7)]; exact=Q(0)
for a,b,c,d in itertools.product(range(2),repeat=4):
    ps=[W[a][b],W[a][c],W[a][d],W[b][c],W[b][d],W[c][d]]
    exact+=m[a]*m[b]*m[c]*m[d]*(math.prod(ps)+math.prod(1-p for p in ps))
P=np.array(W,dtype=float);w=np.array(m,dtype=float);idx=[0,0,1];split=fg(P[np.ix_(idx,idx)],np.array([w[0]/2,w[0]/2,w[1]]))[0]
assert abs(float(exact)-fg(P,w)[0])<1e-14 and abs(split-float(exact))<1e-14
report={'checks':checks,'exact_fixture':str(exact),'split_error':abs(split-float(exact)),'evaluator_sha256':hashlib.sha256(open('experiments/unrestricted_bowl_challenge/evaluator.py','rb').read()).hexdigest()}
with (OUT/'validation.json').open('x') as f:json.dump(report,f,indent=2)
print(json.dumps(report,indent=2))
