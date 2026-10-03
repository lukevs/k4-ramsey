# PatternBoost-style alternation on 0/1 Cayley graphs of F2^8 (bitstring over 255 nonzero elements).
import numpy as np, time, sys, json, os, argparse; sys.path.insert(0,os.path.dirname(os.path.abspath(__file__)))
from groups import *
ap=argparse.ArgumentParser(); ap.add_argument('--out'); ap.add_argument('--rounds',type=int,default=4)
ap.add_argument('--n0',type=int,default=96); ap.add_argument('--per',type=int,default=32); ap.add_argument('--K',type=int,default=48)
ap.add_argument('--steps',type=int,default=100); ap.add_argument('--seed',type=int,default=0); ap.add_argument('--group',default='F2^8')
ap.add_argument('--budget',type=float,default=540); ap.add_argument('--init_bank',default=None); ap.add_argument('--align',type=int,default=0)
a=ap.parse_args(); os.makedirs(a.out,exist_ok=True); T0=time.time()
if a.group=='F2^8': G=Group(*elementary(8),'F2^8')
elif a.group=='F2^7xC3r1': G=Group(*semidirect_f2_c3(7,1),'F2^7xC3r1')
G.activate(); m=G.m; tenure=max(3,m//12); rng=np.random.default_rng(a.seed)
log=open(os.path.join(a.out,'log.jsonl'),'w')
bank={}  # key bytes -> (tot, bits, arm, round)
calls=[0]
def repair(x, arm, rnd):
    calls[0]+=1; tot,b,ev=tabu(G,x,int(rng.integers(1<<60)),a.steps,tenure)
    k=b.tobytes()
    new = k not in bank
    if new: bank[k]=(tot,b,arm,rnd)
    return tot,b,new
def topK(K):
    items=sorted(bank.values(),key=lambda t:t[0]); out=[]; seen=set()
    for t in items:
        if t[0] in seen: continue   # value-dedupe as crude orbit-dedupe (automorphic copies share value)
        seen.add(t[0]); out.append(t)
        if len(out)>=K: break
    return out
def train_fvsbn(X, iters=400, lam=1e-2, lr=0.05):
    K,m=X.shape; Wt=np.zeros((m,m)); b=np.log((X.mean(0)+.02)/(1.02-X.mean(0))); mask=np.tril(np.ones((m,m)),-1)
    mW=np.zeros_like(Wt); vW=np.zeros_like(Wt); mb=np.zeros(m); vb=np.zeros(m)
    for t in range(1,iters+1):
        z=X@(Wt*mask).T+b; p=1/(1+np.exp(-z)); g=(p-X)/K
        gW=(g.T@X)*mask+lam*Wt; gb=g.sum(0)
        for P,gP,M,V in ((Wt,gW,mW,vW),(b,gb,mb,vb)):
            M*=.9; M+=.1*gP; V*=.999; V+=.001*gP*gP; P-=lr*(M/(1-.9**t))/(np.sqrt(V/(1-.999**t))+1e-8)
    nll=float(-(X*np.log(p+1e-12)+(1-X)*np.log(1-p+1e-12)).sum(1).mean())
    return Wt*mask,b,nll
def sample_fvsbn(Wt,b,N):
    X=np.zeros((N,len(b)))
    for i in range(len(b)):
        z=X@Wt[i]+b[i]; X[:,i]=rng.random(N)<1/(1+np.exp(-z))
    return X.astype(np.uint8)
K8=8; TRANS=[]
for i in range(K8):
    for j in range(K8):
        if i!=j: g=np.arange(256); TRANS.append(g ^ (((g>>j)&1)<<i))
TRANS=np.array(TRANS)
def to_set(bits): s=np.zeros(256,np.uint8); s[1:]=bits; return s
def align_one(x, ref, iters):
    # find A in GL(8,2) (product of transvections) with S_x o A close to ref; returns aligned bits (same graph up to iso)
    s=to_set(x); r=to_set(ref); cur=s.copy(); h=int((cur!=r).sum())
    for t in range(iters):
        T=TRANS[rng.integers(len(TRANS))]; cand=cur[T]; hc=int((cand!=r).sum())
        if hc<=h: cur,h=cand,hc
    return cur[1:].copy(), h
def align_bank(Bu, iters):
    ref=Bu[0]; out=[ref.copy()]
    for x in Bu[1:]:
        best=None
        for rep in range(3):
            y,h=align_one(x,ref,iters)
            if best is None or h<best[1]: best=(y,h)
        out.append(best[0])
    return np.array(out)
def ham_nn(X,B): return np.array([int(np.min((B!=x).sum(1))) for x in X])
def stats(v): v=np.array(v)/G.n**3; return dict(min=float(v.min()),mean=float(v.mean()),median=float(np.median(v)),q10=float(np.quantile(v,.1)))
# round 0
t=time.time(); r0=[]
for i in range(a.n0):
    x=(rng.random(m)<rng.uniform(.3,.7)).astype(np.uint8); r0.append(repair(x,'random',0)[0])
rec=dict(round=0,arm='random',n=a.n0,**stats(r0),secs=time.time()-t,bank=len(bank)); print(rec,flush=True); log.write(json.dumps(rec)+'\n')
rnd=0
while rnd<a.rounds and time.time()-T0<a.budget:
    rnd+=1; top=topK(a.K); B=np.array([t[1] for t in top]).astype(float); Bu=B.astype(np.uint8)
    if a.align:
        ta=time.time(); Bu=align_bank(Bu,a.align); B=Bu.astype(float)
        assert all(G.eval(x)==q[0] for x,q in zip(Bu[:5],top[:5]))
        print('aligned pairwise ham med', int(np.median([(Bu[i]!=Bu[j]).sum() for i in range(len(Bu)) for j in range(i)])), 'to ref med', int(np.median((Bu[1:]!=Bu[0]).sum(1))), 'secs %.1f'%(time.time()-ta), flush=True)
    else: ta=time.time()
    dens=B.mean(1); t=time.time(); Wt,bb,nll=train_fvsbn(B); ttrain=time.time()-ta
    Xm=sample_fvsbn(Wt,bb,a.per); hm=ham_nn(Xm,Bu); kmatch=max(1,int(np.median(hm)))
    pind=B.mean(0); Xp=(rng.random((a.per,m))<pind).astype(np.uint8)
    Xr=(rng.random((a.per,m))<rng.uniform(dens.min(),dens.max(),(a.per,1))).astype(np.uint8)
    Xb=Bu[rng.integers(len(Bu),size=a.per)].copy()
    for x in Xb: x[rng.choice(m,kmatch,replace=False)]^=1
    seedvals={nm:[G.eval(x) for x in X] for nm,X in (('model',Xm),('indep',Xp),('random',Xr),('perturb',Xb))}
    for nm,X in (('model',Xm),('indep',Xp),('random',Xr),('perturb',Xb)):
        t=time.time(); res=[repair(x,nm,rnd) for x in X]; vals=[r[0] for r in res]
        outs=np.array([r[1] for r in res]); dfar=ham_nn(outs,Bu)
        rec=dict(round=rnd,arm=nm,n=len(X),**stats(vals),vals=[int(v) for v in vals],seed_median=float(np.median(seedvals[nm])/G.n**3),new=int(sum(r[2] for r in res)),
                 beat_bank_best=int(sum(v<top[0][0] for v in vals)),beat_bank_med=int(sum(v<np.median([q[0] for q in top]) for v in vals)),
                 seed_ham_nn=float(np.median(ham_nn(X,Bu))),out_ham_nn=float(np.median(dfar)),secs=time.time()-t,
                 train_secs=ttrain if nm=='model' else 0.0, nll=nll if nm=='model' else None, kmatch=kmatch)
        print(rec,flush=True); log.write(json.dumps(rec)+'\n'); log.flush()
    bv=[q[0] for q in top]; print('bank top best %.10f  K-th %.10f  distinct values %d  bank dens %.3f-%.3f  pairwise ham med %d'%(bv[0]/G.n**3,bv[-1]/G.n**3,len(set(bv)),dens.min(),dens.max(),int(np.median([(Bu[i]!=Bu[j]).sum() for i in range(len(Bu)) for j in range(i)]))),flush=True)
best=min(bank.values(),key=lambda t:t[0])
json.dump(dict(group=G.name,tot=int(best[0]),den=G.n**3,value=best[0]/G.n**3,bits=best[1].tolist(),arm=best[2],round=best[3],calls=calls[0],secs=time.time()-T0),open(os.path.join(a.out,'best.json'),'w'))
np.save(os.path.join(a.out,'bank_bits.npy'),np.array([t[1] for t in sorted(bank.values(),key=lambda t:t[0])[:400]]))
print('BEST',best[0]/G.n**3,best[2],best[3],'calls',calls[0],'secs',time.time()-T0)
