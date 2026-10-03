# structure of banked F2^8 minima: density, ANF degree, Walsh spectrum (character values of S)
import numpy as np, sys, json, collections
bank=np.load(sys.argv[1]); n=256
def anf_deg(f):
    a=f.copy().astype(np.uint8)
    for i in range(8):
        step=1<<i
        for x in range(n):
            if x&step: a[x]^=a[x^step]
    return max((bin(x).count('1') for x in range(n) if a[x]),default=0)
def walsh(f):
    s=(1-2*f.astype(int)).astype(float)  # not needed
    H=np.array([[(-1)**bin(u&x).count('1') for x in range(n)] for u in range(n)])
    return H@f.astype(int)
H=np.array([[(-1)**bin(u&x).count('1') for x in range(n)] for u in range(n)])
for i in list(range(8))+[len(bank)//2]:
    f=np.zeros(n,np.uint8); f[1:]=bank[i]
    w=H@f.astype(int); ev=sorted(collections.Counter(w[1:].tolist()).items())
    print(i,'|S|',int(f.sum()),'anfdeg',anf_deg(f),'distinct eigen',len(ev),'eig range',w[1:].min(),w[1:].max(), 'top multiplicities',sorted(ev,key=lambda t:-t[1])[:4])
