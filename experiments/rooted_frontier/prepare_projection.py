import json
from pathlib import Path
import numpy as np
p=Path('reports/rooted-frontier-001');vectors=[]
for typ in range(2):
 v=[]
 for r in [0,1]:
  cuts=json.loads((p/f'screen-{r}.json').read_text())['cuts'];v.extend([c['vector'] for c in cuts if c['type']==typ][:8])
 vectors.append(np.rint(np.array(v).T/100).astype(np.int64))
V=np.array(vectors);assert V.shape==(2,120,16)
(p/'projection-input.txt').write_text('16\n'+' '.join(map(str,V.ravel()))+'\n');np.save(p/'projection-vectors.npy',V)
