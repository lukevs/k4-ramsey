"""Independent endpoint-multiplicity integer counter, copied read-only from family followup. Uniform class weights; includes repeats and arbitrary diagonals."""
import numpy as np
import itertools

def change(N,Q,a,b,new):
    idx=np.array([i for i in range(len(N)) if i!=a and i!=b],dtype=int);total=0
    for color in (0,1):
        X=N if color==0 else Q-N
        old=int(X[a,b]);z=int(new if color==0 else Q-new)
        aa=int(X[a,a]);bb=int(X[b,b])
        va=X[a,idx].astype(object);vb=X[b,idx].astype(object);v=va*vb
        C=sum(int(v[i])*int(np.dot(X[k,idx].astype(object),v)) for i,k in enumerate(idx))
        C2=aa*int(np.dot(va*va,vb))+bb*int(np.dot(va,vb*vb))
        total+=12*(z-old)*C+12*(z*z-old*old)*C2+4*(z**3-old**3)*(aa**3+bb**3)+6*(z**4-old**4)*aa*bb
    return total

def direct(N,Q):
    total=0
    for indices in itertools.product(range(len(N)),repeat=4):
        r=b=1
        for i,j in itertools.combinations(indices,2):
            r*=int(N[i,j]);b*=Q-int(N[i,j])
        total+=r+b
    return total
