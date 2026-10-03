"""Independent integer six-edge products on categorized internal translations.
No imported search evaluator or cached coefficient table. Type-only witnesses.
"""
import signal,time,json,hashlib,itertools,math,os
from collections import Counter
from fractions import Fraction
from pathlib import Path
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'reports/assumption-block_arrangement-001';start=time.time();pairs=list(itertools.combinations(range(4),2));C={0,1,2,4,8,15}
patterns=Counter()
for xyz in itertools.product(range(16),repeat=3):
 x=(0,)+xyz
 patterns[tuple(0 if x[a]==x[b] else 1 if x[a]^x[b] in C else 2 for a,b in pairs)]+=1
results=[]
for name in ['baseline','type-nonisomorphic']:
 path=OUT/(name+'-witness.json');obj=json.loads(path.read_text());Q=obj['edge_probability_denominator'];c=obj['construction'];T=c['types'];p=c['p_numerator'];h=c['h_numerator'];vals=[[0,0,Q],[Q,Q,0],[p,p,0],[h,Q,0]]
 # Bind the abstract types to EVERY serialized matrix entry before counting.
 W=obj['red_probability_numerators'];assert obj['block_weights']==['1/192']*192
 for a in range(192):
  for b in range(192):
   i,x=divmod(a,16);j,y=divmod(b,16);d=x^y;cat=0 if d==0 else 1 if d in C else 2
   assert W[a][b]==vals[T[i][j]][cat]
 total=0;cache={}
 for ids in itertools.combinations_with_replacement(range(12),4):
  sig=tuple(T[ids[a]][ids[b]] for a,b in pairs)
  if sig not in cache:
   subtotal=0
   for cats,count in patterns.items():
    red=blue=1
    for typ,cat in zip(sig,cats):
     v=vals[typ][cat];red*=v;blue*=Q-v
    subtotal+=count*(red+blue)
   cache[sig]=subtotal
  mult=24//math.prod(math.factorial(v) for v in Counter(ids).values());total+=mult*cache[sig]
 f=Fraction(total,12**4*16**3*Q**6)
 row={'name':name,'witness_sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'exact':str(f),'decimal_float':float(f),'unique_signatures':len(cache)};results.append(row);print(row,flush=True)
report={'results':results,'seconds':time.time()-start,'pid':os.getpid(),'pattern_count':len(patterns),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'scope':'Exact integer six-edge products; translation reduction independently enumerated; sorted coarse tuples with exact multiplicities; all192x192 serialized entries checked; repeated labels and diagonal probabilities included. Parent audit still separate.','command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python research/experiments/assumption_block_arrangement/exact_types.py','termination':'completed'}
(OUT/'exact-types-check.json').write_text(json.dumps(report,indent=2))
