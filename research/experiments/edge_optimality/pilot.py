import os
for k in ('OPENBLAS_NUM_THREADS','OMP_NUM_THREADS','MKL_NUM_THREADS'):os.environ[k]='1'
import sys,json,time,signal,itertools as it,math
from pathlib import Path
import numpy as np
import cvxpy as cp
sys.path.insert(0,str(Path('research/experiments/clebsch_bowl').resolve()))
import coupled_flag_pilot as core
import coupled_flag_followup as rounding
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('175 second limit')))
signal.alarm(175);start=time.monotonic()
out=Path('reports/edge-optimality-001');z=np.load('reports/global-coupled-pilot-001/coefficients.npz')
graphs=z['graphs6'];N=len(graphs);P=z['P'];c=z['c6'];pairs=list(it.combinations(range(6),2));perms=list(it.permutations(range(6)))
base=[{'C':np.einsum('hg,hij->gij',P,z[k])} for k in sorted(z.files) if k.startswith('N5_')]
base += [{'C':z[k]} for k in sorted(z.files) if k.startswith('N6_')]
counts=np.zeros((2,N,4,4),dtype=np.int64);lookup={}
for gi,A in enumerate(graphs):
 for v in perms:
  x,y,a,b,s,t=v
  es=[int(A[x,a]),int(A[y,a]),int(A[x,b]),int(A[y,b]),int(A[a,b])]
  D=int(all(es))-int(not any(es));edge=int(A[x,y]);i=int(A[x,s])+2*int(A[y,s]);j=int(A[x,t])+2*int(A[y,t])
  counts[0,gi,i,j] += -edge*D
  counts[1,gi,i,j] += (1-edge)*D
  bits=sum(int(A[v[a],v[b]])<<k for k,(a,b) in enumerate(pairs));lookup[bits]=gi
assert len(lookup)==32768
assert np.array_equal(counts,counts.transpose(0,1,3,2))
extra=[{'C':co/720} for co in counts]
np.savez_compressed(out/'coefficients.npz',counts=counts,graphs=graphs)
# Marginalize saved N7 moments independently through deleting each vertex.
rows=json.loads(Path('reports/lower-frontier-C-cut-001/cut.json').read_text())['coefficients']
screens={}
for name in ('control','cut'):
 y=json.loads(Path(f'reports/stationarity-cut-001/{name}.json').read_text())['moments'];q=np.zeros(N)
 for row,w in zip(rows,y):
  E={tuple(sorted(e)) for e in row['edges']}
  for vs in it.combinations(range(7),6):
   bits=sum(int(tuple(sorted((vs[a],vs[b]))) in E)<<k for k,(a,b) in enumerate(pairs));q[lookup[bits]]+=w/7
 screens[name]={'eigenvalues':[np.linalg.eigvalsh(np.einsum('g,gij->ij',q,b['C'])).tolist() for b in extra], 'objective':float(c@q)}
print('SCREENS',json.dumps(screens),flush=True)
(out/'screen.json').write_text(json.dumps(screens,indent=2)+'\n')
runs=[]
for name,bs in [('control',base),('edges',base+extra)]:
 cert={};run=core.solve(name,c,bs,certificate=cert);runs.append(run)
 receipt=rounding.certify(c,cert,out/(name+'-certificate.json'))
 print('EXACT_ROUNDING_PROPOSAL',json.dumps(receipt),flush=True)
 (out/(name+'-result.json')).write_text(json.dumps(run,indent=2)+'\n')
(out/'result.json').write_text(json.dumps({'runs':runs,'seconds':time.monotonic()-start,'scope':'Numerical solve and search-side exact rounding; coefficients need independent audit'},indent=2)+'\n')
