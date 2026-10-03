"""Exact rational restricted obstruction at q=1/2, fixed coarse means."""
import signal,time,os,json,hashlib,itertools
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
START=time.time()
from pathlib import Path
from fractions import Fraction as F
import numpy as np
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/assumption-symmetry_insertion-001';SOURCE=ROOT/'reports/clebsch-size-coarse-002/weighted-k12.json'
def dump(name,d):
 p=OUT/name;t=p.with_suffix('.tmp');t.write_text(json.dumps(d,indent=2)+'\n');t.replace(p)
dump('obstruction-active.json',{'pid':os.getpid(),'start':START,'deadline':START+175})
d=json.loads(SOURCE.read_text());N=np.array(d['red_probability_numerators'],dtype=object);Q=d['edge_probability_denominator'];n=len(N)
chi=np.array([[(-1)**((x&s).bit_count()) for s in range(16)] for x in range(16)],dtype=object)
eig=[sum(int(chi[x,s]) for x in [1,2,4,8,15]) for s in range(16)]
assert np.array_equal(chi.T@chi,16*np.eye(16,dtype=object))
# Prove input translation symmetry and hence selection rule, with exact integer equality.
for a,b,x,y in itertools.product(range(12),range(12),range(16),range(16)):
 assert N[a*16+x,b*16+y]==N[a*16,b*16+(x^y)]
# H(1/2) =3/(n^3 Q^3) [N*(N@N)+(Q-N)*((Q-N)@(Q-N))].
M=Q-N;K=N*(N@N)+M*(M@M)
blocks={}
for s in range(16):
 B=[[sum(int(chi[z,s])*int(K[a*16,b*16+z]) for z in range(16)) for b in range(12)] for a in range(12)]
 blocks[s]=B
for ev in [1,-3]:
 ids=[s for s in range(16) if eig[s]==ev]
 assert all(blocks[s]==blocks[ids[0]] for s in ids)

def ldl(B):
 k=len(B);L=[[F(int(i==j)) for j in range(k)] for i in range(k)];D=[]
 for j in range(k):
  dj=F(B[j][j])-sum(L[j][t]**2*D[t] for t in range(j));assert dj>0;D.append(dj)
  for i in range(j+1,k):L[i][j]=(F(B[i][j])-sum(L[i][t]*L[j][t]*D[t] for t in range(j)))/dj
 assert all(sum(L[i][t]*D[t]*L[j][t] for t in range(k))==B[i][j] for i in range(k) for j in range(k))
 return {'L':[[str(x) for x in row] for row in L],'D':[str(x) for x in D]}
cert={}
for ev in [1,-3]:
 ids=[s for s in range(16) if eig[s]==ev];triples=[list(t) for t in itertools.combinations(ids,3) if t[0]^t[1]^t[2]==0]
 cert[str(ev)]={'characters':ids,'xor_zero_distinct_triples':triples,'integer_hessian_block':blocks[ids[0]],'ldl':ldl(blocks[ids[0]])}
assert cert['-3']['xor_zero_distinct_triples']==[]
# R(1/2): each rooted triangle term has attachment product1/8; exact integer trace of N^3+M^3.
rhalf=F(sum(int(K[i,j]) for i in range(n) for j in range(n)),8*n**3*Q**3)
# The sum K equals sum_ijk N_ij N_ik N_jk plus complement, as required.
dump('obstruction.json',{'claim':'For equal-mass frozen B192 and q(a,x)=1/2+sum_{s in {7,11,13,14,15}} v[a,s] chi_s(x), R(q)>=R(1/2), equality only v=0. Admissible profiles are a subset. No statement with varying coarse means or mixed +1 modes.','reason':'translation selection rule kills linear and cubic terms; exact rational positive-definite Hessian blocks certify the remaining quadratic','normalization':'blocks act on normalized chi/4; H block =3*integer_block/(192^3 Q^3)','Q':Q,'n':n,'R_half_exact':str(rhalf),'R_half_float':float(rhalf),'sectors':cert,'translation_exact':True,'character_orthogonality_exact':True,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'seconds':time.time()-START,'evidence':'exact rational restricted algebra certificate; separately check LDL and selection rule; not Lean/formally kernel certified'})
dump('obstruction-active.json',{'pid':None,'stage':'completed','end':time.time()});print('DONE',time.time()-START,float(rhalf),flush=True)
