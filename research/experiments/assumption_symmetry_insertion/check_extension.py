import signal,time,json,itertools,hashlib,sys
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
from pathlib import Path
from fractions import Fraction as F
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));OUT=ROOT/'reports/assumption-symmetry_insertion-001'
from research.experiments.clebsch_bowl.audit_weighted import density
source=json.loads((ROOT/'reports/clebsch-size-coarse-002/weighted-k12.json').read_text());N=source['red_probability_numerators'];Q=source['edge_probability_denominator'];n=len(N);d=json.loads((OUT/'coarse-extension.json').read_text());v=d['integer_direction'];B=[]
for a in range(12):
 row=[]
 for b in range(12):
  zsum=0
  for z in range(16):
   red=N[a*16][b*16+z];ss=0
   for c,x in itertools.product(range(12),range(16)):
    u=N[a*16][c*16+x];w=N[b*16][c*16+(x^z)]
    ss+=99*red*u*w+(Q-red)*(Q-u)*(Q-w)
   zsum+=(-1)**((z&7).bit_count())*ss
  row.append(zsum)
 B.append(row)
quad=sum(v[a]*B[a][b]*v[b] for a in range(12) for b in range(12));assert str(quad)==d['exact_quadratic_numerator'] and quad<0
alpha=F(1,50);q=[F(99,100)+alpha*F(v[a],10**6)*(-1)**((x&7).bit_count()) for a,x in itertools.product(range(12),range(16))];assert all(0<=x<=1 for x in q)
# direction coefficients use unnormalized chi; Hessian certificate used chi/4.
# Thus delta=1/2 *16 *alpha^2 *6*quad/(100*n^3 Q^3 10^12).
delta=48*alpha**2*F(quad,100*n**3*Q**3*10**12)
W=np.array(N,float)/Q
# Independent direct triple sum contraction for q and q0, no pilot import.
def root(z):
 ans=0
 for A,y in [(W,z),(1-W,1-z)]:
  C=A*np.sqrt(y[:,None]*y[None,:]);ans+=np.trace(C@C@C)/n**3
 return float(ans)
qf=np.array([float(x) for x in q]);observed=root(qf)-root(np.full(n,.99));assert abs(observed-float(delta))<1e-13
result={'alpha_exact':str(alpha),'q_exact':[str(x) for x in q],'delta_exact':str(delta),'delta_float':float(delta),'independent_triangle_trace_delta':observed,'exact_vs_float_error':abs(observed-float(delta)),'base_root':root(np.full(n,.99)),'perturbed_root':root(qf),'exact_integer_convolution_recomputed':True,'admissible_exact':True,'scope':'Counterexample to extending fixed-half PSD claim to all coarse means; no gain against B192','source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(OUT/'coarse-extension-independent-check.json').write_text(json.dumps(result,indent=2)+'\n');print('PASS',float(delta),observed)
