"""Exact adversarial tests for the rooted-K4 mass-tilt lemma; stdlib only."""
from fractions import Fraction as Q
from itertools import product, combinations
from math import prod, lcm
import hashlib, json, platform, random, signal, sys, time
from pathlib import Path

signal.signal(signal.SIGALRM, lambda *_: (_ for _ in ()).throw(TimeoutError('170s job limit')))
signal.alarm(170)
START = time.monotonic()
OUT = Path('reports/lower-frontier-C-exact-001')
PAIRS = list(combinations(range(4), 2))

def measure(A, den, weights):
    """All ordered quadruples, with repeats and diagonal entries."""
    n = len(A)
    M = sum(weights)
    root = [0] * n
    for xs in product(range(n), repeat=4):
        es = [A[xs[i]][xs[j]] for i,j in PAIRS]
        h = prod(es) + prod(den-v for v in es)
        root[xs[0]] += h*weights[xs[1]]*weights[xs[2]]*weights[xs[3]]
    R = [Q(x, den**6*M**3) for x in root]
    w = [Q(x,M) for x in weights]
    F = sum(a*b for a,b in zip(w,R))
    V = sum(a*(b-F)**2 for a,b in zip(w,R))
    return F,V,R,w

def independent_F(A, den, weights):
    """Unordered multiset sum with multinomial factors; separate counter."""
    from itertools import combinations_with_replacement
    from collections import Counter
    from math import factorial
    total = 0
    for xs in combinations_with_replacement(range(len(A)),4):
        m = 24 // prod(factorial(v) for v in Counter(xs).values())
        red = blue = 1
        for i in range(4):
            for j in range(i):
                red *= A[xs[i]][xs[j]]
                blue *= den-A[xs[i]][xs[j]]
        total += m*(red+blue)*prod(weights[i] for i in xs)
    return Q(total, den**6*sum(weights)**4)

def encode(x):
    return {'exact':str(x),'decimal':float(x)}

def check(name,A,den,weights):
    F,V,R,w=measure(A,den,weights)
    assert F == independent_F(A,den,weights)
    a=sum(wi*abs(ri-F) for wi,ri in zip(w,R))
    assert a*a<=V and a<=2*F*(1-F)
    details=[]
    for t in [Q(1,2),Q(2,3)]:
        new=[wi*(1+t*(F-ri)) for wi,ri in zip(w,R)]
        assert sum(new)==1 and min(new)>=0
        D=lcm(*(x.denominator for x in new))
        nums=[int(x*D) for x in new]
        G=independent_F(A,den,nums)
        coefficient=4*t-3*t*t-2*t**3*a-t**4*a*a/2
        assert G<=F-coefficient*V, (name,t,F,V,G,coefficient)
        if t==Q(1,2):
            assert coefficient>=Q(143,128)
        if F<=Q(1,32) and t==Q(2,3):
            assert coefficient>=LOW_COEFFICIENT
        details.append({'t':str(t),'tilted_F':encode(G),
                        'guaranteed_coefficient':encode(coefficient),
                        'decrease':encode(F-G)})
    degrees=[sum(w[j]*Q(A[i][j],den) for j in range(len(A))) for i in range(len(A))]
    p=sum(wi*d for wi,d in zip(w,degrees))
    dv=sum(wi*(d-p)**2 for wi,d in zip(w,degrees))
    return {'name':name,'matrix':A,'denominator':den,'weights':weights,
            'F':encode(F),'root_variance':encode(V),'degree_variance':encode(dv),
            'root_values':[str(x) for x in R],'tilts':details}

LOW_COEFFICIENT=Q(4,3)-Q(16,27)*Q(31,512)-Q(8,81)*Q(31,512)**2
records=[]
for a,b,c in product(range(5),repeat=3):
    for m in [1,2,3]:
        records.append(check(f'two-class-{a}-{b}-{c}-mass{m}',[[a,b],[b,c]],4,[m,4-m]))
rng=random.Random(9302026)
for n in range(1,7):
    for k in range(8):
        A=[[0]*n for _ in range(n)]
        for i in range(n):
            for j in range(i,n): A[i][j]=A[j][i]=rng.randrange(8)
        records.append(check(f'random-{n}-{k}',A,7,[rng.randrange(1,6) for _ in range(n)]))
for n in [3,4,5,6]:
    records.append(check(f'clique-{n}',[[int(i!=j) for j in range(n)] for i in range(n)],1,[1]*n))
    records.append(check(f'cycle-{n}',[[int((i-j)%n in (1,n-1)) for j in range(n)] for i in range(n)],1,list(range(1,n+1))))
S={1,2,4,8,15}
A=[[int(i^j in S) for j in range(16)] for i in range(16)]
records.append(check('clebsch-balanced',A,1,[1]*16))
records.append(check('clebsch-unequal',A,1,[1+(i%3) for i in range(16)]))

# Exact regular-base / color-swap construction: uses the established B192
# polynomial (p,h)=(32/41,22/41), not a new 384-class brute-force recount.
base_F=Q(1013294255057839,33620705806123008)
base_degree=Q(87,192)+Q(12,192)*Q(32,41)+Q(1,192)*Q(22,41)
base_T=Q(1,4)+3*(base_degree-Q(1,2))**2
swap_F=base_F/8+base_T/16+3*base_degree*(1-base_degree)/64
swap_V=(base_degree-Q(1,2))**2/4
assert swap_F<Q(1,32) and swap_V>0
L=Q(36226165105091,1260000000000000)
U=Q('0.030138887566497220')
summary={'tests':len(records),'all_exact_tests_pass':True,'seed':9302026,
 'universal_coefficient':encode(Q(143,128)),
 'sub_random_coefficient':encode(LOW_COEFFICIENT),
 'root_variance_cap_at_displayed_incumbent':encode((U-L)/LOW_COEFFICIENT),
 'color_swap_obstruction':{'base_F':encode(base_F),'base_degree':encode(base_degree),
                          'F':encode(swap_F),'degree_variance':encode(swap_V),'root_variance':'0'},
 'elapsed_s':time.monotonic()-START,'python':sys.version,'platform':platform.platform(),
 'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
 'command':'python3 research/experiments/lower_frontier_C/exact_tests.py',
 'timeout_s':170,'threads':1,'termination':'completed'}
(OUT/'cases.json').write_text(json.dumps(records,indent=2)+'\n')
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
