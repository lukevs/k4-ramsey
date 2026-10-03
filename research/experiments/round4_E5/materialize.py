import numpy as np, sys, json, hashlib, os
sys.path.insert(0,'research/experiments/round4_E5')
from load import load
from exact import exact_delta
from phi import Phi
from fractions import Fraction
F0=Fraction(16900934504649027287619486865996291,560768060721761383881293603555770368)
Apath, outdir = sys.argv[1], sys.argv[2]
src = sys.argv[3] if len(sys.argv)>3 else None
if src:
    d=json.load(open(src)); Q=d['edge_probability_denominator']; N=np.array(d['red_probability_numerators'],dtype=np.int64)
    F0=Fraction(sys.argv[4])
else:
    N,Q,_=load()
A=np.load(Apath); M=np.minimum(N,Q-N)
a=np.rint(A*Q).astype(np.int64); a=np.clip(a,-M,M); a=np.triu(a,1); a=a+a.T
P=N/Q; ph=Phi(P); fl=ph.delta(a/Q)
d,S3,S4=exact_delta(N,Q,a)
F1=F0+d
print('float delta',fl,'exact delta',float(d),'F1',float(F1))
n=N.shape[0]; N2=np.zeros((2*n,2*n),dtype=np.int64)
for i,si in enumerate((1,-1)):
    for j,sj in enumerate((1,-1)): N2[i::2,j::2]=N+a*si*sj
assert (N2==N2.T).all() and N2.min()>=0 and N2.max()<=Q and (np.diag(N2)==0).all()
os.makedirs(outdir,exist_ok=True)
cand={'block_weights':[1]*(2*n),'edge_probability_denominator':int(Q),'red_probability_numerators':N2.tolist(),'schema':'rational-step-graphon-v1'}
p=os.path.join(outdir,'graphon-candidate.json')
with open(p,'w') as f: json.dump(cand,f,indent=2); f.write('\n')
sha=hashlib.sha256(open(p,'rb').read()).hexdigest()
np.save(os.path.join(outdir,'a_int.npy'),a)
rep={'candidate_sha256':sha,'parent_density':str(F0),'exact_delta':str(d),'S3':str(S3),'S4':str(S4),
     'predicted_density':str(F1),'predicted_decimal':float(F1),'float_delta':fl,'classes':2*n,'Q':int(Q),
     'construction':"W'((u,s),(v,t)) = W(u,v) + s*t*a(u,v)/Q, s,t in {+1,-1}; class index 2u+(s==-1)"}
json.dump(rep,open(os.path.join(outdir,'report.json'),'w'),indent=1)
print(json.dumps(rep,indent=1))
