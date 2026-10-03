"""Exact degree-path contraction and old N5 moment witness audit. Stdlib only."""
from fractions import Fraction as F
from itertools import permutations, product, combinations
from pathlib import Path
import json, time, hashlib, platform, sys
START=time.monotonic()
OUT=Path('reports/lower-frontier-B-001'); OUT.mkdir(exist_ok=True)
# |W-1/2| <= 1/2 implies the 2x2 common-prefix matrix for functions (1,d).
# A00=1/4-E(d-1/2)^2 = p-s2.
# A01=1/4*p - E[(d-1/2)(Wd-p/2)] = (s2+p*p)/2 - P4.
# A11=1/4*s2 - E[(Wd-p/2)^2] = s2/4-P5+p*s2-p*p/4.
# Products in these formulas denote DISJOINT motifs when applied to moment vectors.
MOTIFS={'p':(2,[(0,1)]),'s2':(3,[(0,1),(1,2)]),
 'p2':(4,[(0,1),(2,3)]),'P4':(4,[(0,1),(1,2),(2,3)]),
 'P5':(5,[(0,1),(1,2),(2,3),(3,4)]),
 'p_s2':(5,[(0,1),(2,3),(3,4)])}
def entries(t):
 return [[t['p']-t['s2'],(t['s2']+t['p2'])/2-t['P4']],
 [(t['s2']+t['p2'])/2-t['P4'],t['s2']/4-t['P5']+t['p_s2']-t['p2']/4]]
def det(A):return A[0][0]*A[1][1]-A[0][1]**2
def hom(W,w,n,edges):
 total=F(0)
 for v in product(range(len(w)),repeat=n):
  val=F(1)
  for i in v:val*=w[i]
  for a,b in edges:val*=W[v[a]][v[b]]
  total+=val
 return total
def check(W,w):
 t={k:hom(W,w,*m) for k,m in MOTIFS.items()}
 A=entries(t); d=[sum(w[j]*W[i][j] for j in range(len(w))) for i in range(len(w))]
 f=[[F(1)]*len(w),d]
 Sf=[[sum(w[j]*(W[i][j]-F(1,2))*ff[j] for j in range(len(w))) for i in range(len(w))]for ff in f]
 B=[[sum(w[x]*(f[i][x]*f[j][x]/4-Sf[i][x]*Sf[j][x]) for x in range(len(w))) for j in range(2)]for i in range(2)]
 assert A==B and min(A[0][0],A[1][1],det(A))>=0
 return {'A':[[str(x) for x in row] for row in A],'det':str(det(A))}
cases=[]
for bits in range(8):
 W=[[F(bits&1),F((bits>>1)&1)],[F((bits>>1)&1),F((bits>>2)&1)]]
 for a in [F(1,4),F(1,2),F(3,4)]:
  cases.append(check(W,[a,1-a]))
cases.append(check([[F(1,3),F(2,5),F(1,7)],[F(2,5),F(4,5),F(2,3)],[F(1,7),F(2,3),F(3,4)]],[F(1,2),F(1,3),F(1,6)]))
meta_path=Path('reports/global-coupled-pilot-003/coefficient-metadata.json')
witness_path=Path('reports/global-coupled-pilot-003/baseline-feasible-witness.json')
meta=json.loads(meta_path.read_text()); witness=json.loads(witness_path.read_text())
y=[F(x,witness['denominator']) for x in witness['probability_numerators']]
graphs=meta['graphs6']; t={k:F(0) for k in MOTIFS}
for G,prob in zip(graphs,y):
 for key,(n,edges) in MOTIFS.items():
  maps=list(permutations(range(6),n)); count=sum(all(G[v[a]][v[b]] for a,b in edges) for v in maps)
  t[key]+=prob*F(count,len(maps))
A=entries(t)
result={'hypothesis':'B1','exact_graphon_cases':len(cases),'checks':cases,'old_witness_moments':{k:str(v)for k,v in t.items()},'old_witness_A':[[str(v)for v in row]for row in A],'old_witness_determinant':str(det(A)),'old_witness_excluded':min(A[0][0],A[1][1],det(A))<0,'seconds':time.monotonic()-START,'python':sys.version,'platform':platform.platform(),'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in [Path(__file__),meta_path,witness_path]},'command':'python3 experiments/lower_frontier_B/check_contraction.py','scope':'Exact rational checks; universal proof is in research note. No new global bound.'}
(OUT/'contraction.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps({k:v for k,v in result.items() if k not in ['checks','hashes']},indent=2))
