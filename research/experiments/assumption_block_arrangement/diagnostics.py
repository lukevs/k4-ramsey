# Recover nonisomorphic basin witness from the fixed-seed trajectory; no new search family.
import os
for key in ['OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','VECLIB_MAXIMUM_THREADS']:os.environ[key]='1'
from pathlib import Path
source=Path(__file__).with_name('search.py')
exec(compile(source.read_text().split('# Every coarse root')[0],str(source),'exec'))
def isomorphism(A,B):
 colorsA=[tuple(np.bincount(row,minlength=4)) for row in A];colorsB=[tuple(np.bincount(row,minlength=4)) for row in B]
 candidates=[[b for b in range(12) if colorsA[a]==colorsB[b] and A[a,a]==B[b,b]] for a in range(12)]
 order=sorted(range(12),key=lambda a:len(candidates[a]));mapping={};used=set()
 def visit(i):
  if i==12:return dict(mapping)
  a=order[i]
  for b in candidates[a]:
   if b not in used and all(A[a,c]==B[b,d] for c,d in mapping.items()):
    mapping[a]=b;used.add(b);r=visit(i+1)
    if r is not None:return r
    del mapping[a];used.remove(b)
  return None
 return visit(0)
prior=json.load(open(OUT/'destroy_rebuild.json'))['strongest_changed'];mapping=isomorphism(T,np.array(prior['types']))
rng=np.random.default_rng(120012);best=None;rows=[];deadline=time.time()+25
for trial in range(700):
 if time.time()>deadline-1:break
 t=T.copy();rowsel=rng.choice(12,size=int(rng.integers(3,6)),replace=False)
 for a,b in edges:
  if a in rowsel or b in rowsel:
   if rng.random()<.45:t[a,b]=t[b,a]=int(rng.integers(4))
 t,f,n=descend(t,100,deadline);iso=isomorphism(T,t) is not None
 rows.append({'trial':trial+1,'F':f,'iso_parent':iso,'repair_moves':n})
 if not iso and (best is None or f<best['F']):best={'F':f,'types':t.tolist(),'ph':ph.tolist(),'trial':trial+1}
if best:
 val,pp=polish(np.array(best['types']),ph);best.update(F_polished=val,ph_polished=pp.tolist());save('best-nonisomorphic-types.json',best)
save('isomorphism-diagnostics.json',{'tied_endpoint_mapping':mapping,'rows':rows,'nonisomorphic_count':sum(not x['iso_parent'] for x in rows),'seconds':time.time()-start,'source_sha256':sha(Path(__file__)),'dependency_sha256':sha(source),'seed':120012,'termination':'completed','command':'OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 uv run --offline --with numpy --with scipy python research/experiments/assumption_block_arrangement/diagnostics.py'})
print('PID',os.getpid(),'tied_mapping',mapping,'best_noniso',best,'trials',len(rows),'seconds',time.time()-start,flush=True)
