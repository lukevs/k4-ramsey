"""Seven-vertex optimizer-only cut E[R^2] <= U F; no solver or shared edits."""
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import json,random,hashlib,time,signal
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('170s')))
signal.alarm(170)
start=time.monotonic()
src=Path('reports/toolbox-extension-001/pentagon-portable.json')
data=json.loads(src.read_text())
# Rounded upward from the user-supplied independently checked upper bound.
# Its use is only an incumbent upper bound, never a claim that it is c4.
U=Q(30138888,1000000000)
out=Path('reports/lower-frontier-C-cut-001');out.mkdir(exist_ok=True)

def coefficients(edges):
    E={tuple(sorted(e)) for e in edges}
    def mono(xs):
        return len({tuple(sorted(e)) in E for e in combinations(xs,2)})==1
    good={tuple(xs):mono(xs) for xs in combinations(range(7),4)}
    fnum=sum(good.values())
    bnum=0
    for root in range(7):
        others=set(range(7))-{root}
        for A in combinations(sorted(others),3):
            B=others-set(A)
            bnum+=good[tuple(sorted((root,)+A))] and good[tuple(sorted((root,)+tuple(B)))]
    return Q(fnum,35),Q(bnum,140)

rows=[]
for idx,g in enumerate(data['graphs']):
    assert g[0]==7
    edges=dict(g[2])['edges']
    f,b=coefficients(edges)
    rows.append({'index':idx,'edges':edges,'F':str(f),'B':str(b),'B_minus_UF':str(b-U*f)})

# Independent permutation definition of B, plus explicit complement and
# relabeling checks on a bounded sample of the stored representatives.
rng=random.Random(930)
indices=rng.sample(range(len(rows)),20)+[0,len(rows)-1]
for idx in indices:
    row=rows[idx];E={tuple(e) for e in row['edges']}
    s=0
    def mono_direct(xs):
        vals=[tuple(sorted((xs[i],xs[j]))) in E for i in range(4) for j in range(i)]
        return all(vals) or not any(vals)
    for p in permutations(range(7)):
        s+=mono_direct(p[:4]) and mono_direct((p[0],)+p[4:])
    assert Q(s,5040)==Q(row['B'])
    p=list(range(7));rng.shuffle(p)
    assert coefficients([(p[a],p[b]) for a,b in E])==(Q(row['F']),Q(row['B']))
    comp=set(combinations(range(7),2))-E
    assert coefficients(comp)==(Q(row['F']),Q(row['B']))

report={'U':str(U),'scope':'necessary for a limiting global minimizer; NOT valid for every graphon',
        'coefficient_meaning':'sum y_H (B(H)-U F(H)) <= 0',
        'n':7,'rows':len(rows),'permutation_crosschecks':len(indices),'all_pass':True,
        'source_graphs':str(src),'source_graphs_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
        'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'elapsed_s':time.monotonic()-start,'timeout_s':170,'threads':1,'termination':'completed',
        'command':'python3 research/experiments/lower_frontier_C/export_stationarity_cut.py',
        'solver_test':'not run; no N7 primal vector located; no claimed lower-bound gain',
        'coefficients':rows}
(out/'cut.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='coefficients'},indent=2))
