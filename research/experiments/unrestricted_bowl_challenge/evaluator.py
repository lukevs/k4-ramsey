"""Frozen independent ordered-tuple homomorphism evaluator; never used to search."""
import itertools, math

def evaluate(W, m):
    n=len(m)
    assert len(W)==n and all(len(r)==n for r in W)
    assert min(m)>=0 and abs(sum(m)-1)<1e-10
    assert all(0<=W[i][j]<=1 and abs(W[i][j]-W[j][i])<1e-12 for i in range(n) for j in range(n))
    terms=[]; distinct=[]
    for a,b,c,d in itertools.product(range(n),repeat=4):
        ps=[W[a][b],W[a][c],W[a][d],W[b][c],W[b][d],W[c][d]]
        v=m[a]*m[b]*m[c]*m[d]*(math.prod(ps)+math.prod(1-p for p in ps))
        terms.append(v)
        if len({a,b,c,d})==4: distinct.append(v)
    f=math.fsum(terms); dis=math.fsum(distinct)
    return {'objective':f,'distinct_contribution':dis,'repeat_contribution':f-dis}
