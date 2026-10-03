import os
for key in ['VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']: os.environ[key]='1'
import numpy as np
from scipy.optimize import minimize
import itertools as it, json, time, signal, hashlib, platform, sys
from pathlib import Path
signal.signal(signal.SIGALRM, lambda *args: (_ for _ in ()).throw(TimeoutError('180s hard job limit')))
signal.alarm(178)
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'reports/clebsch-size-coarse-001'
PAIRS=list(it.combinations(range(4),2)); TYPES='ZXPH'
T=np.array([[TYPES.index(x) for x in row] for row in json.load(open(ROOT/'experiments/round4_E11/rule.json'))['types']])
C={0,1,2,4,8,15}; start=time.time()

def coefficients():
    xyz=np.array(list(it.product(range(16),repeat=3))); pts=np.column_stack([np.zeros(len(xyz),int),xyz])
    dif=np.array([pts[:,i]^pts[:,j] for i,j in PAIRS]).T
    cats=np.where(dif==0,0,np.where(np.isin(dif,list(C)),1,2))
    patterns,counts=np.unique(cats,axis=0,return_counts=True)
    coeff=np.zeros((4096,2,7,7))
    for idx,sig in enumerate(it.product(range(4),repeat=6)):
        sig=np.array(sig)[None,:]
        for col in range(2):
            if col==0:
                valid=np.all(np.where(sig==0,patterns==2,np.where(sig==3,patterns!=2,patterns!=2)),axis=1)
            else:
                valid=np.all(np.where(sig==0,patterns!=2,np.where(sig==1,patterns==2,np.where(sig==3,patterns!=1,True))),axis=1)
            a=np.sum((sig==2)&(patterns!=2),axis=1)
            b=np.sum((sig==3)&(patterns==0),axis=1)
            np.add.at(coeff[idx,col],(a[valid],b[valid]),counts[valid]/4096)
    return coeff,len(patterns)

def basis(p,h):
    out=[]; dp=[]; dh=[]
    for col in range(2):
        u,v=(p,h) if col==0 else (1-p,1-h); sign=1 if col==0 else -1
        pu=u**np.arange(7); pv=v**np.arange(7)
        du=np.r_[0,np.arange(1,7)*u**np.arange(6)]*sign
        dv=np.r_[0,np.arange(1,7)*v**np.arange(6)]*sign
        out.append(np.outer(pu,pv)); dp.append(np.outer(du,pv)); dh.append(np.outer(pu,dv))
    return [np.array(z).reshape(-1) for z in (out,dp,dh)]

class Model:
    def __init__(self,t,co):
        self.t=t; self.k=len(t)
        self.ix=np.array(list(it.combinations_with_replacement(range(self.k),4)))
        mult=np.array([24/np.prod([__import__('math').factorial(list(x).count(a)) for a in set(x)]) for x in self.ix])
        sig=np.zeros(len(self.ix),int)
        for i,j in PAIRS: sig=4*sig+t[self.ix[:,i],self.ix[:,j]]
        self.co=co.reshape(4096,-1)[sig]*mult[:,None]
    def fg(self,x):
        w=x[:self.k]; b,dp,dh=basis(*x[-2:]); val=self.co@b
        a=w[self.ix]; prod=np.prod(a,axis=1); f=prod@val
        g=np.zeros(self.k+2)
        for j in range(4): np.add.at(g,self.ix[:,j],val*np.prod(np.delete(a,j,axis=1),axis=1))
        g[-2]=prod@(self.co@dp); g[-1]=prod@(self.co@dh)
        return float(f),g

def matrix(t,p,h,q=16):
    d=np.arange(q)[:,None]^np.arange(q)[None,:]; c=np.isin(d,list(C))
    gs=np.array([~c,c,p*c,np.where(d==0,h,c)]).astype(float)
    return gs[t].transpose(0,2,1,3).reshape(len(t)*q,-1)

def direct(U,w):
    # Full root and full second index, weighted triangle common-neighbor sum.
    total=0.
    for V in (U,1-U):
        for a in range(len(V)):
            z=V[a][None,:]*V*w[None,:]
            total+=w[a]*np.sum((w*V[a])*np.einsum('ij,ij->i',z@V,z))
    return float(total)

def literal(U,w):
    total=0.
    for ids in it.product(range(len(U)),repeat=4):
        edges=[U[ids[a],ids[b]] for a,b in PAIRS]
        total+=np.prod(w[list(ids)])*(np.prod(edges)+np.prod(1-np.array(edges)))
    return float(total)

def fit(name,t,co,free,seed=0,x0=None):
    model=Model(t,co); k=len(t)
    if x0 is None: x0=np.r_[np.ones(k)/k,.779181,.534265]
    if free and seed:
        rng=np.random.default_rng(seed); x0=x0.copy(); x0[:k]*=rng.uniform(.65,1.35,k); x0[:k]/=sum(x0[:k])
    if free:
        f=lambda x: (model.fg(x)[0]*1e4,model.fg(x)[1]*1e4)
        r=minimize(f,x0,jac=True,method='SLSQP',bounds=[(0,1)]*(k+2),constraints={'type':'eq','fun':lambda x:sum(x[:k])-1,'jac':lambda x:np.r_[np.ones(k),0,0]},options={'ftol':1e-11,'maxiter':150})
        x=r.x
    else:
        f=lambda ph: (model.fg(np.r_[x0[:k],ph])[0]*1e4,model.fg(np.r_[x0[:k],ph])[1][-2:]*1e4)
        r=minimize(f,x0[-2:],jac=True,method='L-BFGS-B',bounds=[(0,1)]*2,options={'ftol':1e-14,'gtol':1e-9,'maxiter':100})
        x=np.r_[x0[:k],r.x]
    row={'name':name,'k':k,'free':free,'seed':seed,'F':model.fg(x)[0],'x':x.tolist(),'types':t.tolist(),'success':bool(r.success),'message':str(r.message),'nit':int(r.nit)}
    print(json.dumps({key:row[key] for key in ['name','k','free','F','success','nit']}),flush=True)
    return row

def main():
    co,npat=coefficients(); np.save(OUT/'coefficients.npy',co)
    checks={}; rng=np.random.default_rng(704)
    for n in [2,3,5]:
        U=rng.uniform(0,1,(n,n)); U=(U+U.T)/2; w=rng.dirichlet(np.ones(n))
        checks['tiny_'+str(n)]=abs(direct(U,w)-literal(U,w))
    # Coarse polynomial against full-root 32-state count; includes nonzero H diagonals.
    tiny=np.array([[3,2],[2,0]]); xx=np.array([.37,.63,.71,.43])
    checks['polynomial_32']=abs(Model(tiny,co).fg(xx)[0]-direct(matrix(tiny,*xx[-2:]),np.repeat(xx[:2]/16,16)))
    base=fit('parent12',T,co,False); x=np.array(base['x']); mod=Model(T,co)
    checks['parent_full_root']=abs(mod.fg(x)[0]-direct(matrix(T,*x[-2:]),np.repeat(x[:12]/16,16)))
    ids=list(range(12))+[0]; dup=T[np.ix_(ids,ids)]; xd=np.r_[x[:12],x[0]/2,x[-2:]]; xd[0]/=2
    checks['duplicate_split']=abs(Model(dup,co).fg(xd)[0]-mod.fg(x)[0])
    # Analytic gradient versus finite differences and projected mass Hessian.
    eps=1e-5; g=mod.fg(x)[1]; eye=np.eye(14)
    checks['gradient_max_error']=max(abs((mod.fg(x+eps*e)[0]-mod.fg(x-eps*e)[0])/(2*eps)-g[i]) for i,e in enumerate(eye))
    H=np.column_stack([(mod.fg(x+eps*e)[1][:12]-mod.fg(x-eps*e)[1][:12])/(2*eps) for e in eye[:12]])
    Q=np.linalg.qr(np.vstack([np.eye(11),-np.ones(11)]))[0]
    checks['mass_hessian_eigenvalues']=np.linalg.eigvalsh(Q.T@H@Q).tolist(); checks['mass_gradient_range']=float(np.ptp(g[:12]))
    assert max(v for key,v in checks.items() if key not in ['mass_hessian_eigenvalues','mass_gradient_range'])<1e-8, checks
    print('CHECKS',json.dumps(checks),flush=True)
    json.dump(checks,open(OUT/'checks.json','w'),indent=2)
    rows=[base]
    cases=[('parent12',T,None),('delete0',T[1:,1:],None)]
    # Three pair deletions distinguished by removed-pair type (H,P,X).
    for label in [1,2,3]:
        j=next(j for j in range(1,12) if T[0,j]==label); ids=[i for i in range(12) if i not in [0,j]]
        cases.append(('delete0_'+str(j)+'_'+TYPES[label],T[np.ix_(ids,ids)],None))
    cases.append(('duplicate_control',dup,xd))
    # New copy row differs from copy0 in its connection to the original copy, all intradiagonals Z.
    for label in [1,2,3]:
        td=dup.copy(); td[0,12]=td[12,0]=label
        cases.append(('duplicate0_cross_'+TYPES[label],td,xd))
    ids=list(range(12))+[0,3]; td=T[np.ix_(ids,ids)].copy(); td[0,12]=td[12,0]=3; td[3,13]=td[13,3]=3
    x14=np.r_[x[:12],x[0]/2,x[3]/2,x[-2:]]; x14[[0,3]]/=2
    cases.append(('duplicate_H_pair_cross_H',td,x14))
    for name,t,initial in cases:
        if name!='parent12': rows.append(fit(name,t,co,False))
        rows.append(fit(name,t,co,True,seed=704,x0=initial))
        json.dump(rows,open(OUT/'runs.json','w'),indent=2)
    best=min(rows,key=lambda r:r['F'])
    checks['best_full_root']=abs(best['F']-direct(matrix(np.array(best['types']),*best['x'][-2:]),np.repeat(np.array(best['x'][:-2])/16,16)))
    json.dump(checks,open(OUT/'checks.json','w'),indent=2)
    if best['F']<base['F']-1e-12: json.dump(best,open(OUT/'candidate.json','w'),indent=2)
    meta={'seconds':time.time()-start,'python':sys.version,'numpy':np.__version__,'platform':platform.platform(),'pattern_count':npat,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'rule_sha256':hashlib.sha256((ROOT/'experiments/round4_E11/rule.json').read_bytes()).hexdigest(),'thread_env':{k:os.environ[k] for k in ['VECLIB_MAXIMUM_THREADS','OPENBLAS_NUM_THREADS','OMP_NUM_THREADS']},'termination':'completed','best':best['F']}
    json.dump(meta,open(OUT/'meta.json','w'),indent=2); print('DONE',json.dumps(meta),flush=True)
if __name__=='__main__':main()
