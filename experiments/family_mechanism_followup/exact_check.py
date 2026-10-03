"""Integer version of the independent endpoint-multiplicity relative counter."""
import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import signal,time,json,sys,itertools
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(170)
import numpy as np
from pathlib import Path
from fractions import Fraction
start=time.monotonic();OUT=Path('reports/family-mechanism-followup-001')

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

rng=np.random.default_rng(92);fixtures=[]
for n in (2,3,5):
    Q=17;N=rng.integers(0,Q+1,(n,n));N=np.triu(N)+np.triu(N,1).T;V=N.copy();V[0,1]=V[1,0]=7
    expected=direct(V,Q)-direct(N,Q);observed=change(N,Q,0,1,7);assert expected==observed
    fixtures.append(dict(n=n,numerator=expected))
sys.path.insert(0,'experiments/round4_E5');from load import load
N,Q,w=load();a=np.load('reports/round4-E5-depth1-001/a_int.npy');n=len(N)
M=np.empty((2*n,2*n),dtype=np.int64)
for s in range(2):
    for t in range(2):M[s::2,t::2]=N+(-1)**(s+t)*a
patch=json.loads((OUT/'checked-patch.json').read_text());u,v=patch['edge'];rows=[]
for ctrl in patch['controls']:
    V=M.copy();num=0
    for s in range(2):
        for t in range(2):
            i,j=2*u+s,2*v+t;z=ctrl['parent_numerator']+(-1)**(s+t)*ctrl['amplitude_numerator']
            assert 0<=z<=Q
            if z!=V[i,j]:num+=change(V,Q,i,j,z)
            V[i,j]=V[j,i]=z
    delta=Fraction(num,(2*n)**4*Q**6)
    assert abs(float(delta)-ctrl['delta'])<1e-20
    row=dict(name=ctrl['name'],exact_delta=str(delta),decimal=float(delta));rows.append(row);print(json.dumps(row),flush=True)
F0=Fraction(json.loads(Path('reports/round4-E5-depth1-001/report.json').read_text())['predicted_density'])
result=dict(fixtures=fixtures,rows=rows,joint_density_conditional_on_saved_baseline=str(F0+Fraction(rows[-1]['exact_delta'])),seconds=time.monotonic()-start,scope='Independent exact relative recount on real 1920-class matrix. Saved baseline reused; not a fresh full recount or promotion.')
(OUT/'exact-check.json').write_text(json.dumps(result,indent=2)+'\n')
