import sys, numpy as np, itertools
pre=sys.argv[1]; q=int(sys.argv[2]); P=list(map(int,sys.argv[3:]))
a=np.fromfile(pre+'.bin',dtype=np.int32); n,K=a[0],a[1]; orb=a[2:2+n]; D=a[2+n:].reshape(n,n)
W=np.array(P,dtype=object)[orb[D]]  # W[x,y]=P[orb(y-x)]
Bm=q-W
tot=0
for M in (W,Bm):
    for i,j,k,l in itertools.product(range(n),repeat=4):
        tot+=M[i,j]*M[i,k]*M[i,l]*M[j,k]*M[j,l]*M[k,l]
print("brute num (times n) =",tot, "cay num should be tot/n =", tot//n, tot%n)
