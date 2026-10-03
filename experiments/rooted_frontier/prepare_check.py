import itertools,json,struct,sys
from pathlib import Path
import numpy as np
p=Path('reports/rooted-frontier-001');r=int(sys.argv[1]);cuts=json.loads((p/f'screen-{r}.json').read_text())['cuts']
graphs=json.loads(Path('reports/energy-bootstrap-n8-001/graphs8.json').read_text())
pairs=list(itertools.combinations(range(5),2));ix={v:i for i,v in enumerate(pairs)};canonical=[]
for g in range(1024):
 variants=[]
 for free in itertools.permutations([2,3,4]):
  perm=(0,1)+free
  variants.append(sum(((g>>ix[tuple(sorted((perm[a],perm[b])))])&1)<<k for k,(a,b) in enumerate(pairs)))
 canonical.append(min(variants))
reps=[sorted(set(canonical[t::2])) for t in range(2)];assert len(reps[0])==len(reps[1])==120
lookup=[reps[g&1].index(canonical[g]) for g in range(1024)]
lines=[f'{len(graphs)} 120 {len(cuts)}',' '.join(map(str,graphs)),' '.join(map(str,lookup))]
for c in cuts:lines.append(str(c['type'])+' '+' '.join(map(str,c['vector'])))
(p/f'check-{r}.txt').write_text('\n'.join(lines)+'\n');np.load(p/f'cuts-{r}.npz')['coefficients'].tofile(p/f'check-{r}.bin')
