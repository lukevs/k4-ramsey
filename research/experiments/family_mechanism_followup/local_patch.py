"""Full weighted K4 objective differences for a four-class internal patch.

Partition ordered tuples by number k of indices in S. Only k>=2 can change.
All repetitions, including coincident indices in S and its complement, remain.
"""
import itertools
import numpy as np

class LocalPatch:
    def __init__(self, W, weights, selected):
        self.S = np.array(selected)
        self.weights = weights
        outside = np.setdiff1d(np.arange(len(W)), self.S)
        ws, wo = weights[self.S], weights[outside]
        self.base = W[np.ix_(self.S, self.S)]
        self.parts = []
        for color, X in enumerate((W, 1-W)):
            Y = X[np.ix_(self.S, outside)]
            Z = X[np.ix_(outside, outside)]
            # Ordered (a,b), but symmetric off-diagonal pairs combined.
            pairs = np.array(list(itertools.combinations(range(len(ws)), 2)))
            c2 = []
            for a,b in pairs:
                v = wo*Y[a]*Y[b]
                c2.append(12*ws[a]*ws[b]*np.einsum('i,ij,j->',v,Z,v,optimize=False))
            triples = np.array(list(itertools.product(range(len(ws)),repeat=3)))
            c3 = np.array([4*ws[a]*ws[b]*ws[c]*np.dot(wo,Y[a]*Y[b]*Y[c]) for a,b,c in triples])
            quads = np.array(list(itertools.product(range(len(ws)),repeat=4)))
            c4 = np.prod(ws[quads],axis=1)
            for tuples, coeff in ((pairs,np.array(c2)),(triples,c3),(quads,c4)):
                edges = list(itertools.combinations(range(tuples.shape[1]),2))
                ii = np.stack([tuples[:,i] for i,j in edges],axis=1)
                jj = np.stack([tuples[:,j] for i,j in edges],axis=1)
                old = X[np.ix_(self.S,self.S)][ii,jj]
                self.parts.append((color,ii,jj,coeff,old))

    def evaluate(self, patch, directions=()):
        value=0.; gradient=np.zeros(len(directions))
        for color,ii,jj,coeff,old in self.parts:
            x=(patch if color==0 else 1-patch)[ii,jj]
            # Telescoping products avoid subtracting almost equal products.
            delta=np.zeros(len(coeff))
            for k in range(x.shape[1]):
                delta+=(x[:,k]-old[:,k])*np.prod(x[:,:k],axis=1)*np.prod(old[:,k+1:],axis=1)
            value+=np.dot(coeff,delta)
            for z,D in enumerate(directions):
                dx=D[ii,jj]*(1 if color==0 else -1)
                for k in range(x.shape[1]):
                    gradient[z]+=np.dot(coeff,dx[:,k]*np.prod(np.delete(x,k,axis=1),axis=1))
        return float(value),gradient

def directions():
    dp=np.zeros((4,4)); da=np.zeros((4,4))
    for i in range(2):
        for j in range(2):
            dp[i,2+j]=dp[2+j,i]=1
            da[i,2+j]=da[2+j,i]=(-1)**(i+j)
    return dp,da

def direct(W,w):
    total=0.
    for a,b,c,d in itertools.product(range(len(W)),repeat=4):
        vals=[W[i,j] for i,j in ((a,b),(a,c),(a,d),(b,c),(b,d),(c,d))]
        total+=w[a]*w[b]*w[c]*w[d]*(np.prod(vals)+np.prod(1-np.array(vals)))
    return float(total)
