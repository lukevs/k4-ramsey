"""Separate exact checker: explicit coarse/XOR convolution + Bareiss principal minors."""
import signal,time,os,json,hashlib,itertools
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
START=time.time()
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/assumption-symmetry_insertion-001'
source=ROOT/'reports/clebsch-size-coarse-002/weighted-k12.json';data=json.loads(source.read_text());N=data['red_probability_numerators'];Q=data['edge_probability_denominator'];cert=json.loads((OUT/'obstruction.json').read_text())
assert len(N)==192 and cert['input_sha256']==hashlib.sha256(source.read_bytes()).hexdigest()
for i,j in itertools.product(range(192),repeat=2):
 assert N[i][j]==N[j][i] and 0<=N[i][j]<=Q
 assert N[i][j]==N[(i//16)*16][(j//16)*16+((i%16)^(j%16))]
def det(B):
 A=[row[:] for row in B];previous=1
 for k in range(len(A)-1):
  pivot=A[k][k];assert pivot!=0
  for i in range(k+1,len(A)):
   for j in range(k+1,len(A)):
    numerator=A[i][j]*pivot-A[i][k]*A[k][j];assert numerator%previous==0;A[i][j]=numerator//previous
  previous=pivot
 return A[-1][-1]
reports={}
for eig,s in [(1,1),(-3,7)]:
 block=[]
 for a in range(12):
  row=[]
  for b in range(12):
   value=0
   for d in range(16):
    red=N[16*a][16*b+d];blue=Q-red
    convolution=0
    for c,z in itertools.product(range(12),range(16)):
     u=N[16*a][16*c+z];v=N[16*b][16*c+(z^d)]
     convolution+=red*u*v+blue*(Q-u)*(Q-v)
    value+=(-1)**((d&s).bit_count())*convolution
   row.append(value)
  block.append(row)
 assert block==cert['sectors'][str(eig)]['integer_hessian_block']
 minors=[det([r[:k] for r in block[:k]]) for k in range(1,13)];assert all(v>0 for v in minors)
 chars=cert['sectors'][str(eig)]['characters'];assert all(sum((-1)**((x&t).bit_count()) for x in [1,2,4,8,15])==eig for t in chars)
 triples=[list(t) for t in itertools.combinations(chars,3) if t[0]^t[1]^t[2]==0]
 assert triples==cert['sectors'][str(eig)]['xor_zero_distinct_triples']
 reports[str(eig)]={'leading_principal_minors':[str(x) for x in minors],'positive_definite_exact':True,'xor_zero_triples':triples}
assert reports['-3']['xor_zero_triples']==[]
# Certify that fixed-half -3 family cannot beat the exact base either.
f=json.loads((OUT/'finite-check.json').read_text());margin=Fraction(cert['R_half_exact'])-Fraction(f['base_F_exact']);assert margin>0
out={'independent_input_recompute':True,'exact_translation_check':True,'sectors':reports,'R_half_minus_base_exact':str(margin),'R_half_minus_base_float':float(margin),'seconds':time.time()-START,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'certificate_sha256':hashlib.sha256((OUT/'obstruction.json').read_bytes()).hexdigest(),'scope':'Exact rational matrix/character certificate with written translation-selection derivation. Not a formal proof assistant check; varying coarse means excluded.'}
(OUT/'obstruction-independent-check.json').write_text(json.dumps(out,indent=2)+'\n');print('PASS',time.time()-START,float(margin))
