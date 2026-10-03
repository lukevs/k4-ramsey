import itertools,json,struct
from pathlib import Path
import numpy as np
p=Path('reports/rooted-frontier-001');V=np.load(p/'projection-vectors.npy')
with open(p/'projection.bin','rb') as f:
 n,k=struct.unpack('ii',f.read(8));B=np.fromfile(f,dtype=np.int64).reshape(n,2,k,k)
graphs=json.loads(Path('reports/energy-bootstrap-n8-001/graphs8.json').read_text())
# Reuse the independently generated labelled-flag lookup, not event generator.
lookup=(p/'check-0.txt').read_text().splitlines()[2]
lines=[];coeff=[]
for t in range(2):
 for i in range(k):
  lines.append(str(t)+' '+' '.join(map(str,V[t,:,i])));coeff.append(B[:,t,i,i])
 for i,j in itertools.combinations(range(k),2):
  lines.append(str(t)+' '+' '.join(map(str,V[t,:,i]+V[t,:,j])));coeff.append(B[:,t,i,i]+B[:,t,j,j]+2*B[:,t,i,j])
assert np.array_equal(B,B.transpose(0,1,3,2))
(p/'check-projection.txt').write_text('\n'.join([f'{n} 120 {len(lines)}',' '.join(map(str,graphs)),lookup]+lines)+'\n')
np.array(coeff,dtype=np.int64).tofile(p/'check-projection.bin')
