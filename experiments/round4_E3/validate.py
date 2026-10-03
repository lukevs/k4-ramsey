import numpy as np, sys; sys.path.insert(0,__import__('os').path.dirname(__file__))
from groups import *
rng=np.random.default_rng(0)
for name,(n,mul) in [('Z12',cyclic_product([12])),('F2^4',elementary(4)),('F2^2xC3',semidirect_f2_c3(2,1)),('Z2xZ4xZ3',cyclic_product([2,4,3]))]:
    G=Group(n,mul,name); G.activate()
    for t in range(4):
        bits=rng.integers(0,2,G.m).astype(np.uint8)
        a=G.value(G.eval(bits)); b=brute(G,bits)
        print(name,n,G.m,a,b,abs(a-b)<1e-15)
