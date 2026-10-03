"""Independent small-kernel/partition checks and sub-random nonstationary fixtures."""
from fractions import Fraction as Q
from itertools import product
from math import comb
import hashlib, json, signal, sys, time
from pathlib import Path
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('170s')))
signal.alarm(170)
start=time.monotonic()
out=Path('reports/lower-frontier-C-structural-001');out.mkdir(exist_ok=True)

def kernel_eval(h,p):
    return sum(Q(comb(4,k))*p**k*(1-p)**(4-k)*h[k] for k in range(5))
def kernel_roots(h,p):
    return [sum(Q(comb(3,k))*p**k*(1-p)**(3-k)*h[k+j] for k in range(4)) for j in (0,1)]
def audit(h,p):
    F=kernel_eval(h,p);r,s=kernel_roots(h,p)
    assert F==(1-p)*r+p*s
    V=(1-p)*(r-F)**2+p*(s-F)**2
    a=(1-p)*abs(r-F)+p*abs(s-F)
    details=[]
    for t in (Q(1,2),Q(2,3)):
        q=p*(1+t*(F-s));G=kernel_eval(h,q)
        c=4*t-3*t*t-2*t**3*a-t**4*a*a/2
        assert G<=F-c*V
        details.append({'t':str(t),'new_mass':str(q),'new_F':str(G),'decrease':str(F-G)})
    return {'mass':str(p),'F':str(F),'F_decimal':float(F),'R':[str(r),str(s)],'V':str(V),'V_decimal':float(V),'tilts':details}

# Symmetric four-variable kernels, not merely graph-derived kernels: independent
# test of every sign/remainder bound in the proof.
generic=[]
for h in product((Q(0),Q(1)),repeat=5):
    for p in (Q(1,10),Q(1,3),Q(1,2),Q(4,5)):
        generic.append(audit(h,p))

F0=Q(1013294255057839,33620705806123008)
d=Q(3973,7872)
T=Q(1,4)+3*(d-Q(1,2))**2
# 192 equal base classes plus one new fair-coin class, fair cross edges.
# h[k] is the conditional monochromatic K4 probability given k new vertices.
h=[F0,T/8,Q(1,32),Q(1,32),Q(1,32)]
near=[audit(h,Q(1,k)) for k in (10,100,1000,10000,1000000)]
assert all(Q(x['F'])<Q(1,32) and Q(x['V'])>0 for x in near)

def literal(A):
    n=len(A);R=[]
    for i in range(n):
        total=Q(0)
        for j,k,l in product(range(n),repeat=3):
            red=blue=Q(1)
            for v in (A[i][j],A[i][k],A[i][l],A[j][k],A[j][l],A[k][l]):
                red*=v;blue*=1-v
            total+=red+blue
        R.append(total/n**3)
    return sum(R)/n,R

# Recheck the color-swap partition formula by literal direct integration on
# independent small transitive rational bases (diagonals included).
swaps=[]
for n in (1,2,3,4,5):
    for z in (0,1,2):
        vals=[Q((min(i,n-i)+z)%5,4) for i in range(n)]
        A=[[vals[(i-j)%n] for j in range(n)] for i in range(n)]
        F,R=literal(A);assert len(set(R))==1
        p=sum(A[0])/n
        TT=Q(0)
        for i,j,k in product(range(n),repeat=3):
            TT+=A[i][j]*A[i][k]*A[j][k]+(1-A[i][j])*(1-A[i][k])*(1-A[j][k])
        TT/=n**3
        assert TT==Q(1,4)+3*(p-Q(1,2))**2
        B=[[A[i][j] if i<n and j<n else (1-A[i-n][j-n] if i>=n and j>=n else Q(1,2)) for j in range(2*n)] for i in range(2*n)]
        G,S=literal(B)
        predicted=F/8+TT/16+3*p*(1-p)/64
        assert G==predicted and len(set(S))==1
        degrees=[sum(row)/(2*n) for row in B]
        dv=sum((v-Q(1,2))**2 for v in degrees)/(2*n)
        assert dv==(p-Q(1,2))**2/4
        swaps.append({'n':n,'seed':z,'F':str(G),'root_variance':'0','degree_variance':str(dv)})

report={'generic_symmetric_kernel_tests':len(generic),'near_optimal_fixtures':near,
        'literal_swap_tests':swaps,'all_pass':True,'elapsed_s':time.monotonic()-start,
        'command':'python3 research/experiments/lower_frontier_C/structural_checks.py',
        'python':sys.version,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'timeout_s':170,'threads':1,'termination':'completed'}
(out/'report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ('near_optimal_fixtures','literal_swap_tests')},indent=2))
print('Near-optimal fixtures:',[(x['mass'],x['F_decimal'],x['V_decimal']) for x in near])
