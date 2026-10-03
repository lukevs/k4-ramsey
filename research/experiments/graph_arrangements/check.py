import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS'):os.environ[k]='1'
from pathlib import Path
import json,sys,time,itertools as it
import numpy as np
sys.path.insert(0,str(Path('research/experiments/round5_C1').resolve()))
from base import base,Fval
from family import F
start=time.monotonic();out=Path('reports/graph-arrangements-001');mixed=json.loads((out/'mixed-summary.json').read_text());p=.779180833031354;h=.5342651880306992;W,typ,cls=base(p,h);fr=(W>0)&(W<1);rng=np.random.default_rng(930)
D=[]
for _ in range(2):
 A=rng.uniform(-.1,.1,(3,3));A=(A+A.T)/2;D.append(A-A.mean(0)[None,:]-A.mean(1)[:,None]+A.mean())
positions={3:[(0,1),(1,2),(2,0)],4:[(0,1),(1,2),(2,3),(3,0)],5:[(0,1),(0,2),(1,2),(0,3),(1,3)],6:[(0,1),(0,2),(1,2),(0,3),(1,3),(2,3)]}
terms=np.zeros(4)
for entry in mixed['coarse_words']:
 r=entry['degree'];word=entry['word'];v=0
 for xs in it.product(range(3),repeat=4):
  q=1
  for t,(a,b) in zip(word,positions[r]):q*=D[t][xs[a],xs[b]]
  v+=q
 terms[r-3]+=entry['coefficient']*v/81
full=np.kron(W,np.ones((3,3)))+np.kron(fr&(typ=='P'),D[0])+np.kron(fr&(typ=='H'),D[1]);assert full.min()>=0 and full.max()<=1
reps=[(16*s)*3+a for s in range(12) for a in range(3)];direct=F(full,reps,[16]*len(reps));pred=Fval(W)+sum(terms);assert abs(direct-pred)<2e-14
# All-root direct recount of the best standalone rounded candidate.
summary=json.loads((out/'summary.json').read_text());best=min(summary['runs'],key=lambda r:r['rounded_decimal']);folder=out/best['tag'];cfg=json.loads((folder/'config.json').read_text());native=json.loads((folder/'native.json').read_text());matrix=np.array(native['rounded_probabilities'])[np.array(cfg['relation_ids'])]/cfg['q'];recount=F(matrix,list(range(len(matrix))),[1]*len(matrix));assert abs(recount-native['rounded_decimal'])<2e-14
# Validate exact tuple census mass and one-vertex marginals for all latent relation tables.
graphs=json.loads((out/'graphs.json').read_text());counts={}
for name,g in graphs.items():
 n=len(g['adjacency']);k=sum(g['adjacency'][0]);tab=np.array([list(map(int,l.split())) for l in (out/(name+'-patterns.txt')).read_text().splitlines()]);assert int(tab[:,1].sum())==n**4
 for pos in range(6):
  for relation,expect in [(0,n-1-k),(1,k),(2,1)]:assert int(tab[tab[:,0]//3**pos%3==relation,1].sum())==n**3*expect
 counts[name]={'ordered_tuple_mass':int(tab[:,1].sum()),'patterns':len(tab),'all_six_marginals_exact':True}
r={'mixed576_direct':direct,'mixed576_expansion':pred,'mixed_error':abs(direct-pred),'mixed_terms':terms.tolist(),'standalone_tag':best['tag'],'standalone_direct':recount,'standalone_engine':native['rounded_decimal'],'pattern_checks':counts,'seconds':time.monotonic()-start,'scope':'Independent floating direct recount on576-class asymmetric-P/H validation fixture and100-class standalone; exact integer latent mass/marginal checks. Large latent lifts not fully materialized or exact-certified.'}
(out/'independent-check.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
