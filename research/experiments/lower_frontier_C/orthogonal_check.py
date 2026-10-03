"""Sharper proof check; reads frozen cases and independently recounts a unit tilt."""
from fractions import Fraction as Q
from itertools import combinations_with_replacement, product
from collections import Counter
from math import factorial, prod, lcm, sqrt
import hashlib,json,signal,time,sys
from pathlib import Path
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('170s')))
signal.alarm(170)
start=time.monotonic()
out=Path('reports/lower-frontier-C-orthogonal-001');out.mkdir(exist_ok=True)
inp=Path('reports/lower-frontier-C-exact-001/cases.json')
cases=json.loads(inp.read_text())
checks=[]
for c in cases:
    A=c['matrix'];den=c['denominator'];n=len(A)
    R=list(map(Q,c['root_values']));F=Q(c['F']['exact']);V=Q(c['root_variance']['exact'])
    M=sum(c['weights']);w=[Q(x,M) for x in c['weights']]
    assert V<=F*(1-F)/4
    q=[wi*(1+F-ri) for wi,ri in zip(w,R)]
    assert sum(q)==1 and min(q)>=0
    D=lcm(*(x.denominator for x in q));nums=[int(x*D) for x in q]
    total=0
    for xs in combinations_with_replacement(range(n),4):
        mult=24//prod(factorial(v) for v in Counter(xs).values())
        red=blue=1
        for i in range(4):
            for j in range(i):
                e=A[xs[i]][xs[j]];red*=e;blue*=den-e
        total+=mult*(red+blue)*prod(nums[i] for i in xs)
    G=Q(total,den**6*D**4)
    excess=G-F+4*V
    if excess>0:
        assert excess**2<=V**2*(F*(1-F)-4*V)*(6+4*V+V**2)
        assert excess**2<=6*F*(1-F)*V**2
    assert G<=F-Q(11,4)*V
    if F<=Q(1,32): assert G<=F-Q(7,2)*V
    checks.append({'name':c['name'],'F':str(F),'V':str(V),'tilted_F':str(G)})

# Standalone symmetric-kernel test, with no graph-count implementation shared.
from math import comb
def value(h,p,m):return sum(comb(m,k)*p**k*(1-p)**(m-k)*h[k] for k in range(m+1))
generic_count=0
for h in product((Q(0),Q(1)),repeat=5):
    for p in (Q(1,10),Q(1,3),Q(1,2),Q(4,5)):
        F=value(h,p,4);r=value(h[:4],p,3);s=value(h[1:],p,3)
        V=(1-p)*(r-F)**2+p*(s-F)**2
        G=value(h,p*(1+F-s),4)
        E=G-F+4*V
        assert V<=F*(1-F)/4
        if E>0:assert E*E<=V*V*(F*(1-F)-4*V)*(6+4*V+V*V)
        generic_count+=1

prior=Path('reports/lower-frontier-C-structural-001/report.json')
near=[]
F0=Q(1013294255057839,33620705806123008);d=Q(3973,7872)
h=[F0,(Q(1,4)+3*(d-Q(1,2))**2)/8,Q(1,32),Q(1,32),Q(1,32)]
for c in json.loads(prior.read_text())['near_optimal_fixtures']:
    p=Q(c['mass']);F=Q(c['F']);V=Q(c['V']);r,s=map(Q,c['R'])
    G=value(h,p*(1+F-s),4);E=G-F+4*V
    if E>0:assert E*E<=6*F*(1-F)*V*V
    assert G<=F-Q(7,2)*V
    near.append({'mass':str(p),'F':str(F),'V':str(V),'tilted_F':str(G),
                 'decrease_over_variance':float((F-G)/V)})
L=Q(36226165105091,1260000000000000);U=Q('0.030138887566497220')
report={'all_pass':True,'graphon_tests':len(checks),'symmetric_kernel_tests':generic_count,
        'nonstationary_sub_random_tests':near,'sub_random_coefficient':4-sqrt(186)/32,
        'root_variance_cap_at_displayed_incumbent':float(U-L)/(4-sqrt(6*float(U*(1-U)))),
        'rational_safe_coefficient':'7/2','rational_safe_variance_cap':str((U-L)*Q(2,7)),
        'elapsed_s':time.monotonic()-start,'command':'python3 research/experiments/lower_frontier_C/orthogonal_check.py',
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'case_sha256':hashlib.sha256(inp.read_bytes()).hexdigest(),
        'structural_sha256':hashlib.sha256(prior.read_bytes()).hexdigest(),
        'python':sys.version,'timeout_s':170,'threads':1,'termination':'completed'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
(out/'cases.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='nonstationary_sub_random_tests'},indent=2))
print('Near-fixture decrease/variance:',[x['decrease_over_variance'] for x in near])
