"""Controlled N6 -> N7 pentagon-root extension; run under external timeout."""
import sys, json, time, hashlib, multiprocessing as mp
from pathlib import Path
from itertools import combinations

# The fork uses cpu_count()-1 in some table-generation paths.
# Keep that pool to one worker, and constrain BLAS/OpenMP in the launcher.
mp.cpu_count = lambda: 2
mode = sys.argv[1]
out = Path(sys.argv[2])
out.mkdir(parents=True, exist_ok=True)
start = time.monotonic()
GraphTheory.reset()
try:
    objective = GraphTheory(4, edges=list(combinations(range(4), 2))) + GraphTheory(4, edges=[])
    old = [(ns, typ, 7) for ns, typ, _ in GraphTheory._get_relevant_ftypes(6)]
    new = GraphTheory._get_relevant_ftypes(7)
    pentagon = GraphTheory(5, edges=[(0,1),(1,2),(2,3),(3,4),(4,0)])
    ptype = pentagon.subflag([], ftype_points=list(range(5)))
    if mode == 'extension':
        selected = old
    elif mode in ('pentagon', 'pentagon_exact'):
        selected = old + [(6, ptype, 7)]
    elif mode == 'five_roots':
        selected = old + [d for d in new if d[0] == 6]
    elif mode == 'pentagon_neighbors':
        path_edges=[(0,1),(1,2),(2,3),(3,4)]
        complement_edges=[e for e in combinations(range(5),2) if e not in path_edges]
        types=[ptype]+[GraphTheory(5,edges=es).subflag([],ftype_points=list(range(5)))
                        for es in (path_edges,complement_edges)]
        selected=old+[(6,t,7) for t in types]
    elif mode in ('full', 'full_exact'):
        selected = old + new
    else:
        raise ValueError(mode)
    exact = mode.endswith('_exact')
    print('EXPERIMENT', mode, 'types', len(selected), flush=True)
    value = GraphTheory.optimize(objective, 7, maximize=False,
        specific_ftype=selected, exact=exact, construction=False,
        precision=1e-9, maxiter=150, denom=10**10,
        file=str(out/(mode+'.pickle')))
    result = dict(mode=mode, value=str(value), decimal=float(value),
        seconds=time.monotonic()-start, types=len(selected), exact_rounding=exact,
        source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())
    (out/(mode+'.json')).write_text(json.dumps(result, indent=2)+'\n')
    print('RESULT', json.dumps(result), flush=True)
finally:
    GraphTheory.reset()
