import numpy as np, sys, time, json
sys.path.insert(0,'research/experiments/round4_E5')
from phi import Phi
cand,out,tlimit=sys.argv[1],sys.argv[2],float(sys.argv[3])
d=json.load(open(cand)); Q=d['edge_probability_denominator']
P=np.array(d['red_probability_numerators'],dtype=np.float64)/Q
t0=time.time(); ph=Phi(P); m=ph.m; fr=ph.frac; iu=np.triu(fr,1)
print('setup',time.time()-t0,'n',P.shape[0],'frac',fr.sum(),'tri',len(ph.tri),flush=True)
c=P*(1-P)*fr; _,G3=ph.T3(c,True); A=-m*np.sign(G3)*fr
vals=[ph.delta(t*A) for t in (-1,-.5,0,.5,1)]; co=np.polyfit([-1,-.5,0,.5,1],vals,4)
ts=np.linspace(-1,1,401); A=ts[np.polyval(co,ts).argmin()]*A
f=ph.delta(A); print('init',f,time.time()-t0,flush=True); step=0.5; it=0
while time.time()-t0<tlimit:
    f,G,a,b=ph.delta(A,True); D=-G*m*m
    D[(A>=m-1e-15)&(D>0)]=0; D[(A<=-m+1e-15)&(D<0)]=0
    sc=np.max(np.abs(D[fr])/m[fr]); D/=sc; best=(f,None,step)
    for s in (step*2,step,step/4):
        An=np.clip(A+s*D,-m,m); fn=ph.delta(An)
        if fn<best[0]: best=(fn,An,s)
    if best[1] is None:
        step/=8
        if step<1e-5: break
        continue
    f,A,step=best; it+=1
    print(it,f,'step',step,round(time.time()-t0),flush=True)
    np.save(out+'/A.npy',A)
print('FINAL',f,flush=True)
