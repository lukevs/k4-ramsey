import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,signal,itertools as it,math
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path('research/experiments/clebsch_bowl').resolve()))
import coupled_flag_pilot as core
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175 seconds')))
signal.alarm(175);start=time.monotonic();out=Path('reports/edge-optimality-001')
z=np.load('reports/global-coupled-pilot-001/coefficients.npz');graphs=z['graphs6'];P=z['P'];c=z['c6']
base=[{'C':np.einsum('hg,hij->gij',P,z[k])} for k in sorted(z.files) if k.startswith('N5_')]+[{'C':z[k]} for k in sorted(z.files) if k.startswith('N6_')]
edge=np.load(out/'coefficients.npz')['counts']/720
# Vertex optimality: R=F<=U, so E[(U-R)ff^T] PSD, f=(1-d,d).
# Six distinct vertices: root, three clique extensions, two flag extensions.
U=3767361/125000000
flag=np.zeros((len(graphs),2,2),dtype=np.int64);clique=flag.copy()
for gi,A in enumerate(graphs):
 for x,a,b,c0,s,t in it.permutations(range(6)):
  i=int(A[x,s]);j=int(A[x,t]);flag[gi,i,j]+=1
  bits=[A[u,v] for u,v in it.combinations((x,a,b,c0),2)]
  clique[gi,i,j]+=int(all(bits) or not any(bits))
C=(U*flag-clique)/720
assert np.max(abs(C-C.transpose(0,2,1)))==0
np.savez_compressed(out/'vertex-coefficients.npz',flag=flag,clique=clique)
screen={}
for name in ['control','edges']:
 y=np.array(json.loads((out/(name+'-result.json')).read_text())['primal'])
 screen[name]=np.linalg.eigvalsh(np.einsum('g,gij->ij',y,C)).tolist()
print('VERTEX_SCREEN',json.dumps(screen),flush=True)
runs=[]
for name,blocks in [('vertex',base+[{'C':C}]),('both',base+[{'C':b} for b in edge]+[{'C':C}])]:
 run=core.solve(name,z['c6'],blocks);runs.append(run)
 (out/(name+'-result.json')).write_text(json.dumps(run,indent=2)+'\n')
(out/'vertex-summary.json').write_text(json.dumps({'screen':screen,'runs':runs,'seconds':time.monotonic()-start},indent=2)+'\n')
