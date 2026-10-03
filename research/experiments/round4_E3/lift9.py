# F2^9 probe: tabu from (a) lifts of banked F2^8 minima (S9 = {(x,b): x in S8 or (x=0,b=1 chosen)}) and (b) random seeds.
import numpy as np, sys, os, time, json; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from groups import *
out=sys.argv[1]; bankf=sys.argv[2]; budget=float(sys.argv[3]); steps=int(sys.argv[4])
G=Group(*elementary(9),'F2^9'); G.activate(); rng=np.random.default_rng(5); T0=time.time()
bank=np.load(bankf); res=[]
k=0
while time.time()-T0<budget:
    arm='lift' if k%2==0 else 'random'
    if arm=='lift':
        s8=np.zeros(256,np.uint8); s8[1:]=bank[(k//2)%len(bank)]
        s9=np.concatenate([s8,s8]); s9[256]=0   # exact 2-blow-up (twins blue) = same step graphon value
        x=s9[1:]
    else: x=(rng.random(511)<0.5).astype(np.uint8)
    v0=G.eval(x); tot,b,ev=tabu(G,x,k+1,steps,40); res.append(dict(arm=arm,seed_val=v0/G.n**3,val=tot/G.n**3,tot=int(tot)))
    print(res[-1],'%.0fs'%(time.time()-T0),flush=True)
    if tot==min(r['tot'] for r in res): np.save(os.path.join(out,'best9.npy'),b)
    k+=1
json.dump(res,open(os.path.join(out,'results.json'),'w'))
