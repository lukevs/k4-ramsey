import os
os.environ['OPENBLAS_NUM_THREADS']='1'
from pathlib import Path
from fractions import Fraction as Q
import json,time
import numpy as np
from scipy.linalg import qr
import sympy as s
start=time.monotonic();out=Path('reports/compressed-consistency-001');z=np.load('reports/global-coupled-pilot-001/coefficients.npz');w=json.loads(Path('reports/global-coupled-pilot-003/baseline-feasible-witness.json').read_text());D=np.rint(6*z['P']).astype(int)
p=[sum(Q(int(D[i,j])*int(w['probability_numerators'][j]),6*w['denominator']) for j in range(156)) for i in range(34)]
def pd(M):
 n=len(M);L=[[Q(i==j) for j in range(n)] for i in range(n)];piv=[]
 for j in range(n):
  v=M[j][j]-sum(L[j][k]**2*piv[k] for k in range(j));assert v>0;piv.append(v)
  for i in range(j+1,n):L[i][j]=(M[i][j]-sum(L[i][k]*L[j][k]*piv[k] for k in range(j)))/v
 return min(piv)
reports=[]
for mode in ('edge','edge_k4','root_degree'):
 a=np.load(out/(mode+'-coefficients.npz'));B=a['Cs_integer'];L=a['rowmaps_integer'];n=B.shape[1]
 A=[list(map(int,row)) for row in a['T_integer']];b=[6*sum(Q(int(v))*p[i] for i,v in enumerate(row)) for row in a['C']]
 A.append([1]*n);b.append(Q(1))
 for k in range(2):
  A.extend(B[k].sum(axis=2).T.tolist());b.extend(6*sum(Q(int(v))*p[i] for i,v in enumerate(row)) for row in L[k])
 A=np.array(A,dtype=np.int64);rank=np.linalg.matrix_rank(A);ri=qr(A.T.astype(float),pivoting=True,mode='economic')[2][:rank];ci=qr(A[ri].astype(float),pivoting=True,mode='economic')[2][:rank]
 data=json.loads((out/('degree-result.json' if mode=='root_degree' else 'result.json')).read_text());run=next(r for r in data['runs'] if r['mode']==mode and r['fixed_witness'])
 q=[Q(round(v*10**12),10**12) for v in run['q']]
 residual=[b[i]-sum(Q(int(v))*q[j] for j,v in enumerate(A[i])) for i in ri]
 delta=s.Matrix(A[np.ix_(ri,ci)].tolist()).inv()*s.Matrix([s.Rational(v.numerator,v.denominator) for v in residual])
 for j,v in zip(ci,delta):q[j]+=Q(int(v.p),int(v.q))
 assert min(q)>0
 for row,rhs in zip(A,b):assert sum(Q(int(v))*q[j] for j,v in enumerate(row))==rhs
 piv=[]
 for k in range(2):
  d=B.shape[2];M=[[sum(q[g]*int(B[k,g,i,j]) for g in range(n)) for j in range(d)] for i in range(d)];piv.append(str(pd(M)))
 r={'mode':mode,'probabilities':[str(v) for v in q],'p5':[str(v) for v in p],'equality_rank':int(rank),'minimum_probability':str(min(q)),'exact_positive_definite_pivots':piv,'all_equalities_exact':True}
 (out/(mode+'-exact-extension.json')).write_text(json.dumps(r,indent=2)+'\n');reports.append({k:v for k,v in r.items() if k not in ('probabilities','p5')})
result={'extensions':reports,'seconds':time.monotonic()-start,'interpretation':'Each tested compressed system admits the exact old N5-feasible witness. This does not prove equal optimal values.'};(out/'exact-extension-check.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
