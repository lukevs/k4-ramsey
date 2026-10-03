import numpy as np, sys
sys.path.insert(0,'experiments/round4_E5')
from exact import exact_delta
from fractions import Fraction
import itertools
rng=np.random.default_rng(3); Q=64; n=6
N=rng.integers(0,Q+1,(n,n)); N=np.triu(N,1); N=N+N.T
N[0,1]=N[1,0]=0; N[2,3]=N[3,2]=Q
m=np.minimum(N,Q-N); a=np.triu(rng.integers(-100,100,(n,n))%(m+1)*rng.choice([-1,1],(n,n)),1); a=a+a.T
def lit(Mat,q):
    n=len(Mat); tot=0
    for vs in itertools.product(range(n),repeat=4):
        r=b=1
        for x,y in itertools.combinations(range(4),2):
            p=int(Mat[vs[x]][vs[y]]); r*=p; b*=q-p
        tot+=r+b
    return Fraction(tot,n**4*q**6)
N2=np.zeros((2*n,2*n),int); s=[1,-1]
for i in range(2):
    for j in range(2): N2[i::2,j::2]=N+a*s[i]*s[j]
d,S3,S4=exact_delta(N,Q,a); print(d, lit(N2,Q)-lit(N,Q), d==lit(N2,Q)-lit(N,Q))
