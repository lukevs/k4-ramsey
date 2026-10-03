import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[key]='1'
import json,time,signal,itertools,hashlib,sys
from pathlib import Path
from fractions import Fraction
import numpy as np
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
ROOT=Path(__file__).resolve().parents[2];OUT=ROOT/'reports/assumption-block_arrangement-001';start=time.time()
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def recount(W,w):
 # Independently organized pair-root sum: z_c=w_c W_ac W_bc.
 # Sum a<=b with exact ordered-pair multiplicity; c,d unrestricted.
 total=0.
 for U in (W,1-W):
  for a in range(len(U)):
   for b in range(a,len(U)):
    z=w*U[a]*U[b]
    total+=(1 if a==b else 2)*w[a]*w[b]*U[a,b]*float(z@(U@z))
 return total
rng=np.random.default_rng(74102);fixtures=[]
for n in (2,3,4):
 M=rng.integers(0,8,(n,n));M=np.triu(M)+np.triu(M,1).T; masses=np.arange(1,n+1); w=masses/sum(masses);exact=Fraction()
 for ids in itertools.product(range(n),repeat=4):
  red=blue=Fraction(1);wt=Fraction(1)
  for i in ids:wt*=Fraction(int(masses[i]),int(sum(masses)))
  for i,j in itertools.combinations(ids,2):red*=Fraction(int(M[i,j]),7);blue*=1-Fraction(int(M[i,j]),7)
  exact+=wt*(red+blue)
 got=recount(M/7,w);assert abs(got-float(exact))<1e-14
 fixtures.append({'n':n,'exact':str(exact),'float':got})
base=json.load(open(OUT/'local.json'));rule=base['types'];Q=10**12;results=[]
cases=[('baseline',base),('type-nonisomorphic',json.load(open(OUT/'best-nonisomorphic-types.json'))),('shift-nonzero-holonomy',json.load(open(OUT/'best-shift-changed.json')))]
for name,row in cases:
 t=row.get('types',rule);s=row.get('shifts',np.zeros((12,12),int).tolist());ph=row.get('ph_polished',row['ph']);p,h=[round(x*Q) for x in ph]
 W=np.zeros((192,192),np.int64)
 for a in range(192):
  for b in range(192):
   i,x=divmod(a,16);j,y=divmod(b,16);d=x^y^s[i][j];inside=d in (0,1,2,4,8,15);typ=t[i][j]
   W[a,b]=[Q*(not inside),Q*inside,p*inside,h if d==0 else Q*inside][typ]
 assert np.array_equal(W,W.T) and W.min()>=0 and W.max()<=Q
 artifact={'schema':'rational-step-graphon-v1','edge_probability_denominator':Q,'red_probability_numerators':W.tolist(),'block_weights':['1/192']*192,'construction':{'types':t,'shifts':s,'p_numerator':p,'h_numerator':h},'evidence':'floating independent pair-root recount; no exact promotion audit'}
 path=OUT/(name+'-witness.json');path.write_text(json.dumps(artifact))
 loaded=json.loads(path.read_text());weights=np.array([float(Fraction(w)) for w in loaded['block_weights']]);assert sum(Fraction(w) for w in loaded['block_weights'])==1
 got=recount(np.array(loaded['red_probability_numerators'])/Q,weights);expected=row.get('F_polished',row['F']);assert abs(got-expected)<1e-11
 results.append({'name':name,'path':str(path.relative_to(ROOT)),'sha256':sha(path),'recount':got,'search_value':expected,'difference':got-expected,'edge_denominator':Q,'weight_sum':'1','classes':192})
 print(name,got,'delta',got-expected,flush=True)
report={'results':results,'tiny_exact_fixtures':fixtures,'seconds':time.time()-start,'pid':os.getpid(),'source_sha256':sha(Path(__file__)),'command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python experiments/assumption_block_arrangement/audit.py','scope':'independent float64 pair-root count from serialized rational witnesses, all repeats, diagonal probabilities, normalized weights; no exact full witness or parent promotion audit','termination':'completed'}
(OUT/'independent-check.json').write_text(json.dumps(report,indent=2))
