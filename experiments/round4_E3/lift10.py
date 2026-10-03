# F2^10 probe: exact 2-blow-up of best F2^9 set, then first-improvement descent, then tabu while budget remains.
import numpy as np, sys, os, time, json; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from groups import *
out=sys.argv[1]; src=sys.argv[2]; budget=float(sys.argv[3]); T0=time.time()
G=Group(*elementary(10),'F2^10'); G.activate()
s9=np.zeros(512,np.uint8); s9[1:]=np.load(src); s10=np.concatenate([s9,s9]); s10[512]=0; x=s10[1:].copy()
v0=G.eval(x); print('lift value',v0/G.n**3,flush=True)
tot,b,ev=G.descend(x,7); print('descent',tot,G.n**3,tot/G.n**3,'evals',ev,'%.0fs'%(time.time()-T0),flush=True)
np.save(os.path.join(out,'best10.npy'),b); json.dump(dict(tot=int(tot),den=G.n**3,value=tot/G.n**3),open(os.path.join(out,'best10.json'),'w'))
k=0
while time.time()-T0<budget-60:
    t2,b2,ev=tabu(G,b,k+11,20,60); k+=1
    print('tabu20',t2,t2/G.n**3,'%.0fs'%(time.time()-T0),flush=True)
    if t2<tot: tot,b=t2,b2; np.save(os.path.join(out,'best10.npy'),b); json.dump(dict(tot=int(tot),den=G.n**3,value=tot/G.n**3),open(os.path.join(out,'best10.json'),'w'))
