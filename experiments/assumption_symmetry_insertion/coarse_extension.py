"""Adversarial check: does fixed-half -3 obstruction extend to varying coarse means?"""
import signal,time,os
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
START=time.time()
import sys,json,hashlib,itertools
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
import experiments.assumption_symmetry_insertion.pilot as p
signal.alarm(max(1,175-int(time.time()-START)))
p.dump('coarse-extension-active.json',{'pid':os.getpid(),'start':START,'deadline':START+175})
N=np.array(p.D['red_probability_numerators'],dtype=object);Q=p.D['edge_probability_denominator'];M=Q-N;n=len(N);s=7
chi=np.array([(-1)**((x&s).bit_count()) for x in range(16)])
red=[];blue=[]
for c in range(12):
 for A,out in [(N,red),(M,blue)]:
  K=A*(A[:,16*c:16*(c+1)]@A[16*c:16*(c+1),:])
  B=np.array([[sum(int(chi[z])*int(K[16*a,16*b+z]) for z in range(16)) for b in range(12)] for a in range(12)],dtype=object)
  out.append(B)
base=sum(blue);directions=[a-b for a,b in zip(red,blue)];scale=6/(n**3*Q**3)
BF=np.asarray(base,float)*scale;DF=np.array([np.asarray(a,float)*scale for a in directions]);best=(float('inf'),None)
for bits in itertools.product([0,1],repeat=12):
 H=BF+np.einsum('c,cij->ij',bits,DF);lo=float(np.linalg.eigvalsh(H)[0])
 if lo<best[0]:best=(lo,list(bits))
out={'corners':4096,'minimum_corner_eigenvalue':best[0],'corner':best[1],'seconds':time.time()-START}
if best[0]<-1e-12:
 # Pull into interior; exact negative quadratic form if still negative.
 means=(1+98*np.array(best[1]))/100;H=BF+np.einsum('c,cij->ij',means,DF);ev,vec=np.linalg.eigh(H);v=np.rint(vec[:,0]*10**6).astype(np.int64)
 B100=100*base+sum(int(1+98*b)*D for b,D in zip(best[1],directions));vv=v.astype(object);quadratic=int(vv@B100@vv)
 out.update(interior_means=means.tolist(),interior_min_eigenvalue=float(ev[0]),integer_direction=v.tolist(),exact_quadratic_numerator=str(quadratic),exact_quadratic_denominator=str(100*n**3*Q**3*10**12),quadratic_prefactor=6)
 if quadratic<0:
  direction=np.outer(v/10**6,chi).ravel();alpha=.009/max(abs(direction));q0=np.repeat(means,16);q=q0+alpha*direction
  assert q.min()>=0 and q.max()<=1
  delta=p.rooted(q)[0]-p.rooted(q0)[0]
  out.update(feasible_alpha=alpha,numerical_root_delta=delta,base_root=p.rooted(q0)[0],perturbed_root=p.rooted(q)[0],q=q.tolist(),interpretation='The fixed-half obstruction does not extend to every interior coarse mean: explicit feasible -3 perturbation lowers its coarse-constant root. This does not beat B192.')
  assert delta<0
else:out['interpretation']='All4096 corner blocks numerically PSD; exact universal verification not performed.'
out.update(source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),seconds=time.time()-START)
p.dump('coarse-extension.json',out);p.dump('coarse-extension-active.json',{'pid':None,'stage':'completed','end':time.time()});print(json.dumps({k:v for k,v in out.items() if k not in ['q','integer_direction','exact_quadratic_denominator']}),flush=True)
