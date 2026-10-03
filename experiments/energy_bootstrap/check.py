"""Independent stdlib-only check of branch certificates and motif coefficients.
Uses previously independently enumerated Gram coefficients, checks their binding
and PSD anew. No optimizer, numpy, or generator import.
"""
import json,hashlib,itertools as it,time,signal,sys
from pathlib import Path
from fractions import Fraction as F
sys.path.insert(0,str(Path('experiments/clebsch_bowl').resolve()))
from check_coupled_certificate import exact_ldl
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175s limit')));signal.alarm(175)
t0=time.monotonic();out=Path('reports/energy-bootstrap-001');basepath=Path('reports/global-coupled-pilot-003/full-certificate.json');base=json.loads(basepath.read_text());meta=json.loads(Path('reports/global-coupled-pilot-003/coefficient-metadata.json').read_text());cert=json.loads((out/'certificate.json').read_text());graphs=meta['graphs6'];orders=list(it.permutations(range(6)));pairs=list(it.combinations(range(6),2))
xs=[];zs=[];code_index={};sizes=[]
for gi,A in enumerate(graphs):
 x=z=0;orbit=set()
 for v in orders:
  l=sum(A[v[i]][v[j]] for i,j in ((0,1),(0,2),(1,2)))==1
  r=sum(A[v[i]][v[j]] for i,j in ((3,4),(3,5),(4,5)))==1
  x+=l;z+=l and r
  orbit.add(sum(A[v[i]][v[j]]<<k for k,(i,j) in enumerate(pairs)))
 xs.append(F(x,720));zs.append(F(z,720));sizes.append(len(orbit))
 for code in orbit:
  assert code not in code_index;code_index[code]=gi
assert len(code_index)==32768
# Analytic ER controls, including all-zero/one endpoints.
for p in [F(0),F(1,5),F(1,2),F(4,5),F(1)]:
 probs=[]
 for A,m in zip(graphs,sizes):
  e=sum(A[i][j] for i,j in pairs);probs.append(m*p**e*(1-p)**(15-e))
 expected=3*p*(1-p)**2
 assert sum(probs)==1 and sum(w*x for w,x in zip(probs,xs))==expected
 assert sum(w*z for w,z in zip(probs,zs))==expected**2
# Unequal two-class complete bipartite graphon, including repeated classes.
for p in [F(1,3),F(2,5)]:
 probs=[F(0)]*len(graphs)
 for bits in it.product((0,1),repeat=6):
  code=sum((bits[i]!=bits[j])<<k for k,(i,j) in enumerate(pairs));m=sum(bits);probs[code_index[code]]+=p**m*(1-p)**(6-m)
 # A complete bipartite triple never has exactly one edge.
 assert sum(probs)==1 and sum(w*x for w,x in zip(probs,xs))==0 and sum(w*z for w,z in zip(probs,zs))==0
# Unequal union-of-two-cliques: exactly-one-edge probability 3p(1-p).
for p in [F(1,3),F(2,5)]:
 probs=[F(0)]*len(graphs)
 for bits in it.product((0,1),repeat=6):
  code=sum((bits[i]==bits[j])<<k for k,(i,j) in enumerate(pairs));m=sum(bits);probs[code_index[code]]+=p**m*(1-p)**(6-m)
 expected=3*p*(1-p)
 assert sum(w*x for w,x in zip(probs,xs))==expected and sum(w*z for w,z in zip(probs,zs))==expected**2
scale=cert['scale'];endpoint=F(0);bounds=[]
for branch in cert['branches']:
 a,b=map(F,branch['interval']);assert a==endpoint and b>a;endpoint=b
 lam=F(branch['lambda_integer'],scale);assert lam>=0
 penalties=[F(0)]*len(graphs);seen=set()
 for block in branch['blocks']:
  idx=block['reference_block'];assert idx not in seen;seen.add(idx);B=base['blocks'][idx]['C_integer'];Q=block['Q_integer'];d=len(Q)
  assert all(Q[i][j]==Q[j][i] for i in range(d) for j in range(d));exact_ldl(Q)
  for g in range(len(graphs)):penalties[g]+=F(sum(Q[i][j]*B[g][i][j] for i in range(d) for j in range(d)),720*scale)
 assert len(seen)==19
 coefficients=[F(v,720)-pen-lam*((a+b)*x-z) for v,pen,x,z in zip(base['objective_numerators'],penalties,xs,zs)]
 bound=min(coefficients)+lam*a*b;assert bound==F(branch['bound']);bounds.append(bound)
assert endpoint==1 and min(bounds)==F(cert['bound'])
r={'bound':str(min(bounds)),'bound_decimal':float(min(bounds)),'branches':len(bounds),'coverage':'[0,1] exactly','PSD_matrices_checked':19*len(bounds),'independent_motif_enumeration':True,'labelled_graphs':len(code_index),'analytic_graphon_controls':9,'base_Gram_certificate_sha256':hashlib.sha256(basepath.read_bytes()).hexdigest(),'certificate_sha256':hashlib.sha256((out/'certificate.json').read_bytes()).hexdigest(),'checker_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'seconds':time.monotonic()-t0,'scope':'Exact rational branch certificate; universal graphon proof in research note. Existing Gram enumeration certificate reused.'}
(out/'independent-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
