"""Independent multiset derivative audit of every saved rooted density."""
from fractions import Fraction as Q
from itertools import combinations_with_replacement
from collections import Counter
from math import factorial,prod
from pathlib import Path
import json,hashlib,time,signal
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('170s')))
signal.alarm(170)
start=time.monotonic()
source=Path('reports/lower-frontier-C-exact-001/cases.json')
cases=json.loads(source.read_text());root_checks=0
for case in cases:
    A=case['matrix'];w=case['weights'];d=case['denominator'];n=len(w)
    accum=[0]*n
    for xs in combinations_with_replacement(range(n),4):
        counts=Counter(xs);mult=24//prod(factorial(x) for x in counts.values())
        red=blue=1
        for i in range(4):
            for j in range(i):
                a=A[xs[i]][xs[j]];red*=a;blue*=d-a
        term=mult*(red+blue)*prod(w[i] for i in xs)
        for i,k in counts.items():
            assert (term*k)%w[i]==0
            accum[i]+=term*k//w[i]
    roots=[Q(x,4*d**6*sum(w)**3) for x in accum]
    assert roots==list(map(Q,case['root_values'])),case['name']
    root_checks+=n
out=Path('reports/lower-frontier-C-audit-001');out.mkdir(exist_ok=True)
owned=[Path('research/notes/lower-frontier-C.md')]+sorted(Path('research/experiments/lower_frontier_C').glob('*.py'))
inputs=[Path('research/notes')/p for p in ['round4-P-paper-draft.md','round5-F4.md','global-lower-bound-transfer-audit.md','certificate-guided-upper-search.md','global-coupled-pilot.md']]
report={'all_pass':True,'graphons':len(cases),'root_values_independently_checked':root_checks,
 'method':'differentiate unnormalized unordered-multiset K4 polynomial with respect to each vertex mass',
 'elapsed_s':time.monotonic()-start,'command':'python3 research/experiments/lower_frontier_C/final_audit.py',
 'source_revision':'66b6eadbc3d67a025fce49c41e46f9f2c29127f9','timeout_s':170,'threads':1,'termination':'completed',
 'hashes':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in owned+inputs+[source]}}
(out/'audit.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='hashes'},indent=2))
