import signal,time,os
signal.signal(signal.SIGALRM,signal.SIG_DFL);signal.alarm(175)
START=time.time()
import sys,json,hashlib,math
from pathlib import Path
from fractions import Fraction as Fr
import numpy as np
from scipy.optimize import minimize
sys.path.insert(0,str(Path(__file__).resolve().parents[3]))
import research.experiments.assumption_symmetry_insertion.pilot as p
signal.alarm(max(1,175-int(time.time()-START)))
p.dump('finite-active.json',{'pid':os.getpid(),'start':START,'deadline':START+175})
F=p.density(p.W,p.m)
rows=json.loads((p.OUT/'runs.json').read_text())+json.loads((p.OUT/'boundary-runs.json').read_text())
selected=[min([r for r in rows if r['label']==label],key=lambda r:r['R']) for label in sorted(set(r['label'] for r in rows))]
finite=[]
for r in selected:
 q=np.array(r['q']); candidates=[]
 for e0 in [.001,.03,.15,.5]:
  opt=minimize(lambda x:p.poly(x[0],p.coeff(q,x[1],F)),[e0,.5],method='Nelder-Mead',bounds=[(0,1),(0,1)],options={'maxiter':300,'xatol':1e-10,'fatol':1e-16})
  candidates.append({'e':float(opt.x[0]),'d':float(opt.x[1]),'F':float(opt.fun),'success':bool(opt.success)})
 forced=[]
 for e in [.000001,.001,.01,.05,.2,.5]:
  opt=minimize(lambda x:p.poly(e,p.coeff(q,x[0],F)),[.5],method='Nelder-Mead',bounds=[(0,1)],options={'maxiter':150,'xatol':1e-10,'fatol':1e-16})
  forced.append({'e':e,'d':float(opt.x[0]),'delta':float(opt.fun-F)})
 finite.append({'label':r['label'],'seed':r['seed'],'best':min(candidates,key=lambda z:z['F']),'forced_positive_mass':forced})
p.dump('finite-runs.json',finite)
# Independently evaluate a real, genuinely new profile at positive mass .01 after rationalization.
best=min(rows,key=lambda r:r['R']);T=10**9;qnum=np.rint(np.array(best['q'])*T).astype(np.int64);q=qnum/T
selectedfinite=next(r for r in finite if r['label']==best['label'])
dnum=round(next(r for r in selectedfinite['forced_positive_mass'] if r['e']==.01)['d']*T);d=dnum/T;e=.01
V,w=p.materialize(q,d,e);val=p.density(V,w);polyval=p.poly(e,p.coeff(q,d,F))
assert abs(val-polyval)<1e-12
Q=int(p.D['edge_probability_denominator']);common=math.lcm(Q,T);N=np.array(p.D['red_probability_numerators'],dtype=object);n=len(N)
NN=np.empty((n+1,n+1),dtype=object);NN[:-1,:-1]=N*(common//Q);NN[-1,:-1]=NN[:-1,-1]=qnum.astype(object)*(common//T);NN[-1,-1]=dnum*(common//T)
witness={'format':'rational-step-graphon-v1','edge_probability_denominator':common,'red_probability_numerators':NN.tolist(),'block_weights':[str(Fr(99,100*n))]*n+['1/100'],'note':'Positive-mass negative-result witness; not an improving candidate.'}
p.dump('checked-positive-mass-witness.json',witness)
# Exact rooted evaluator by weighted integer matrix contraction. Translation verified separately.
def exactroot(qi,den):
 total=0
 for A,z in [(N,np.array(qi,dtype=object)),(Q-N,den-np.array(qi,dtype=object))]:
  B=(A*z)@A
  total+=sum(int(z[i])*int(z[j])*int(A[i,j])*int(B[i,j]) for i in range(n) for j in range(n))
 return Fr(total,n**3*Q**3*den**3)
base_roots=[exactroot(N[a*16],Q) for a in range(12)];Fexact=sum(base_roots)/12
Rexact=exactroot(qnum,T)
# Exact finite-mass coefficient terms with 2,3,4 occurrences of the new label.
r2=Fr(0);r3=Fr(0)
for A,z,dd in [(N,qnum.astype(object),Fr(dnum,T)),(Q-N,T-qnum.astype(object),1-Fr(dnum,T))]:
 v=z*z
 r2+=dd*Fr(sum(int(v[i])*int(A[i,j])*int(v[j]) for i in range(n) for j in range(n)),n*n*Q*T**4)
 r3+=dd**3*Fr(sum(int(x)**3 for x in z),n*T**3)
cc=[Fexact,Rexact,r2,r3,Fr(dnum,T)**6+(1-Fr(dnum,T))**6];ee=Fr(1,100)
exactval=sum(k*ee**i*(1-ee)**(4-i)*cc[i] for i,k in enumerate([1,4,6,4,1]))
assert abs(float(exactval)-val)<1e-12
p.dump('finite-check.json',{'base_F_exact':str(Fexact),'base_roots_exact_equal':len(set(base_roots))==1,'base_F_float':float(Fexact),'profile':best['label'],'seed':best['seed'],'q_numerators':qnum.tolist(),'q_denominator':T,'d_numerator':dnum,'d_denominator':T,'mass':'1/100','R_exact':str(Rexact),'R_minus_F_exact':str(Rexact-Fexact),'coefficients_exact':[str(x) for x in cc],'finite_F_exact':str(exactval),'finite_delta_exact':str(exactval-Fexact),'finite_delta_float':float(exactval-Fexact),'separate_all_root_density':val,'polynomial_error':abs(val-polyval),'exact_vs_all_root_error':abs(float(exactval)-val),'nearest_old_row_rms':float(np.sqrt(np.mean((p.W-q)**2,axis=1)).min()),'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'pilot_sha256':hashlib.sha256(Path(p.__file__).read_bytes()).hexdigest(),'seconds':time.time()-START,'evidence':'exact rational relative recount using input translation symmetry; independent all-root float recount; not formal kernel certification'})
p.dump('finite-active.json',{'pid':None,'stage':'completed','end':time.time()});print('DONE',time.time()-START,float(Rexact-Fexact),float(exactval-Fexact),flush=True)
