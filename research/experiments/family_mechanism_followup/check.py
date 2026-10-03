"""Independent sequential single-edge recount; no LocalPatch code in oracle.

Group tuples by endpoint multiplicities (r,s), with both positive.
The (1,1) group leaves two arbitrary external indices. The (2,1)/(1,2)
groups leave one. The remaining (3,1)/(1,3)/(2,2) groups leave none.
This gives an exact degree-four edge polynomial including diagonal terms.
"""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import signal,time,json,sys,itertools,math
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(170)
from pathlib import Path
import numpy as np
from fractions import Fraction
start=time.monotonic();OUT=Path('reports/family-mechanism-followup-001')

def edge_delta(W,a,b,new):
    n=len(W);idx=np.array([i for i in range(n) if i!=a and i!=b]);total=np.longdouble(0)
    for color in (0,1):
        X=W if color==0 else 1-W
        old=np.longdouble(X[a,b]);z=np.longdouble(new if color==0 else 1-new)
        aa=np.longdouble(X[a,a]);bb=np.longdouble(X[b,b])
        va=X[a,idx].astype(np.longdouble);vb=X[b,idx].astype(np.longdouble);v=va*vb
        # Row-wise long-double accumulation avoids search's einsum contraction.
        C=sum(v[i]*np.dot(X[k,idx].astype(np.longdouble),v) for i,k in enumerate(idx))
        C2=aa*np.dot(va*va,vb)+bb*np.dot(va,vb*vb)
        total+=12*(z-old)*C+12*(z*z-old*old)*C2+4*(z**3-old**3)*(aa**3+bb**3)+6*(z**4-old**4)*aa*bb
    return total/np.longdouble(n)**4

def oracle(W):
    n=len(W);total=np.longdouble(0)
    for indices in itertools.product(range(n),repeat=4):
        v=np.array([W[indices[i],indices[j]] for i,j in itertools.combinations(range(4),2)],dtype=np.longdouble)
        total+=np.prod(v)+np.prod(1-v)
    return total/n**4

rng=np.random.default_rng(732);fixtures=[]
for n in (3,5):
    W=rng.random((n,n));W=(W+W.T)/2;V=W.copy();V[0,1]=V[1,0]=.173
    actual=oracle(V)-oracle(W);pred=edge_delta(W,0,1,.173)
    print('tiny',n,float(actual),float(pred),float(abs(actual-pred)),flush=True)
    assert abs(actual-pred)<2e-14
    fixtures.append(dict(n=n,error=float(abs(actual-pred))))

sys.path.insert(0,'research/experiments/round4_E5');from load import load
N,Q,w=load();a=np.load('reports/round4-E5-depth1-001/a_int.npy');n=len(N)
# Materialize directly without importing split() from the search.
W=np.empty((2*n,2*n))
for s in range(2):
    for t in range(2):W[s::2,t::2]=(N+((-1)**(s+t))*a)/Q
screen=json.loads((OUT/'screen.json').read_text());best=min(screen['rows'],key=lambda r:r['controls']['joint']['delta'])
u,v=best['edge'];records=[]
from local_patch import LocalPatch,directions
dp,da=directions();S=[2*u,2*u+1,2*v,2*v+1];model=LocalPatch(W,np.ones(2*n)/(2*n),S)
for name,item in best['controls'].items():
    np_=int(round(N[u,v]+Q*item['x'][0]));na=int(round(a[u,v]+Q*item['x'][1]));na=max(-min(np_,Q-np_),min(min(np_,Q-np_),na))
    V=W.copy();change=np.longdouble(0)
    for s in range(2):
        for t in range(2):
            i,j=2*u+s,2*v+t;z=(np_+(-1)**(s+t)*na)/Q
            assert 0<=z<=1
            change+=edge_delta(V,i,j,z);V[i,j]=V[j,i]=z
    prediction=model.evaluate(V[np.ix_(S,S)])[0]
    assert abs(float(change)-prediction)<1e-20
    records.append(dict(name=name,parent_numerator=np_,amplitude_numerator=na,delta=float(change),local_prediction=prediction,disagreement=abs(float(change)-prediction)))
    print(json.dumps(records[-1]),flush=True)
first=Fraction(json.loads(Path('reports/round4-E5-depth1-001/report.json').read_text())['predicted_density'])
patch=dict(schema='rational-single-parent-edge-patch-v1',parent='reports/association-scheme-per-edge-boundary-continuation-001/graphon-candidate.json',amplitudes='reports/round4-E5-depth1-001/a_int.npy',edge=[u,v],denominator=int(Q),controls=records,construction='Replace symmetric parent/amplitude entries at edge, then W_lift[2i+s,2j+t]=(Nij+(-1)^(s+t)*aij)/Q',baseline=float(first),joint_density=float(first)+records[-1]['delta'],status='Independently numerically recounted relative patch; no exact or full count, no promotion')
(OUT/'checked-patch.json').write_text(json.dumps(patch,indent=2)+'\n')
(OUT/'check.json').write_text(json.dumps(dict(fixtures=fixtures,records=records,seconds=time.monotonic()-start,numpy=np.__version__,python=sys.version,precision=str(np.finfo(np.longdouble)),scope='Long-double endpoint-multiplicity oracle on full real 1920-class matrix; relative changes only'),indent=2)+'\n')
