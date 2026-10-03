import ctypes, os, numpy as np
HERE=os.path.dirname(os.path.abspath(__file__))
lib=ctypes.CDLL(os.path.join(HERE,'libcay.so'))
I64P=ctypes.POINTER(ctypes.c_int64)
def elementary(k):  # F2^k
    n=1<<k; g=np.arange(n); return n, (g[:,None]^g[None,:]).astype(np.int32)
def semidirect_f2_c3(k=6, r=1):  # F2^k x| C3, A acts on r two-bit blocks by [[0,1],[1,1]]
    def A(v):
        out=v
        for b in range(r):
            x=(v>>(2*b))&1; y=(v>>(2*b+1))&1
            nx, ny = y, x^y
            out=(out & ~(3<<(2*b))) | (nx<<(2*b)) | (ny<<(2*b+1))
        return out
    def At(v,t):
        for _ in range(t): v=A(v)
        return v
    N=1<<k; n=3*N; mul=np.zeros((n,n),np.int32)
    for t in range(3):
        for v in range(N):
            for u in range(3):
                for w in range(N):
                    mul[t*N+v,u*N+w]=((t+u)%3)*N+(v^At(w,t))
    return n, mul
def cyclic_product(mods):
    import itertools
    els=list(itertools.product(*[range(q) for q in mods])); idx={e:i for i,e in enumerate(els)}
    n=len(els); mul=np.zeros((n,n),np.int32)
    for i,a in enumerate(els):
        for j,b in enumerate(els): mul[i,j]=idx[tuple((x+y)%q for x,y,q in zip(a,b,mods))]
    return n, mul
class Group:
    def __init__(self, n, mul, name):
        self.n=n; self.mul=np.ascontiguousarray(mul,np.int32); self.name=name
        self.e=int(np.where((mul==np.arange(n)[None,:]).all(1))[0][0])
        self.inv=np.array([int(np.where(mul[g]==self.e)[0][0]) for g in range(n)],np.int32)
        orb=-np.ones(n,np.int32); m=0
        for g in range(n):
            if g==self.e or orb[g]>=0: continue
            orb[g]=m; orb[self.inv[g]]=m; m+=1
        self.orb=orb; self.m=m
        self.osize=np.bincount(orb[orb>=0],minlength=m)
    def activate(self):
        lib.cay_init(self.n, self.mul.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), self.inv.ctypes.data_as(ctypes.POINTER(ctypes.c_int)), self.m, self.orb.ctypes.data_as(ctypes.POINTER(ctypes.c_int)))
    def eval(self, bits):
        b=np.ascontiguousarray(bits,np.uint8); out=(ctypes.c_int64*2)()
        tot=lib.cay_eval(self.e, b.ctypes.data_as(ctypes.c_char_p), out); return tot
    def descend(self, bits, seed):
        b=np.ascontiguousarray(bits.copy(),np.uint8); ev=ctypes.c_int64()
        tot=lib.cay_descend(self.e, b.ctypes.data_as(ctypes.c_char_p), ctypes.c_uint64(seed), ctypes.byref(ev))
        return tot, b, ev.value
    def value(self, tot): return tot/self.n**3
lib.cay_eval.restype=ctypes.c_int64; lib.cay_descend.restype=ctypes.c_int64
def brute(G, bits):
    n=G.n; S=np.zeros(n,bool); S[G.orb>=0]=bits[G.orb[G.orb>=0]]
    Aadj=S[G.mul[G.inv][:, :]] if False else S[G.mul[G.inv[:,None], np.arange(n)[None,:]]]  # Aadj[x,y]=S[x^-1 y]
    assert (Aadj==Aadj.T).all() and not Aadj.diagonal().any()
    Rm=Aadj.astype(np.int64); Bm=(~Aadj).astype(np.int64)
    def hom(M): # hom(K4,M) = sum_{a,b,c,d} prod of 6 edges
        tot=0
        for a in range(n):
            for b in range(n):
                if not M[a,b]: continue
                v=M[a]*M[b]; tot+= int(v @ (M*np.outer(v,v)).sum(1)) if False else int(((M*np.outer(v,v)).sum()))
        return tot
    return (hom(Rm)+hom(Bm))/n**4
lib.cay_tabu.restype=ctypes.c_int64
def tabu(G, bits, seed, steps, tenure):
    b=np.ascontiguousarray(bits.copy(),np.uint8); ev=ctypes.c_int64()
    tot=lib.cay_tabu(G.e, b.ctypes.data_as(ctypes.c_char_p), ctypes.c_uint64(seed), steps, tenure, ctypes.byref(ev))
    return tot, b, ev.value
