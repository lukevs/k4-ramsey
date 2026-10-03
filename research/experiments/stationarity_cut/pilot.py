import sys,json,time,pickle,multiprocessing as mp
from pathlib import Path
from itertools import combinations
from sage.all import *
mp.cpu_count=lambda:2
mode=sys.argv[1]; out=Path(sys.argv[2]); out.mkdir(parents=True,exist_ok=True)
start=time.monotonic(); GraphTheory.reset()
try:
    data=json.loads(Path('cut.json').read_text())
    objective=GraphTheory(4,edges=list(combinations(range(4),2)))+GraphTheory(4,edges=[])
    old=[(ns,typ,7) for ns,typ,_ in GraphTheory._get_relevant_ftypes(6)]
    typ=GraphTheory(5,edges=[(0,1),(1,2),(2,3),(3,4),(4,0)]).subflag([],ftype_points=list(range(5)))
    selected=old+[(6,typ,7)]
    positive=sum((-QQ(row['B_minus_UF']))*GraphTheory(7,edges=row['edges']) for row in data['coefficients'])
    value=GraphTheory.optimize(objective,7,maximize=False,specific_ftype=selected,
        positives=[positive] if mode=='cut' else None,exact=False,construction=False,
        precision=1e-9,maxiter=150,file=str(out/(mode+'.pickle')))
    c=pickle.loads((out/(mode+'.pickle')).read_bytes())
    expected={tuple(sorted(tuple(sorted(e)) for e in row['edges'])):row for row in data['coefficients']}
    rows=[]
    for g in c['base flags']:
        es=tuple(sorted(tuple(sorted(e)) for name,edges in g[2] if name=='edges' for e in edges))
        rows.append(expected[es])
    y=list(map(float,c['phi vectors'][0]))
    violation=sum(v*float(QQ(r['B_minus_UF'])) for v,r in zip(y,rows))
    result=dict(mode=mode,value=float(value),seconds=time.monotonic()-start,
        cut_violation_B_minus_UF=violation,mass=sum(y),min_moment=min(y),
        moment_objective=sum(v*float(QQ(r['F'])) for v,r in zip(y,rows)),
        multipliers=list(map(float,c['e vector'])),moments=y)
    (out/(mode+'.json')).write_text(json.dumps(result,indent=2)+'\n')
    print('RESULT',json.dumps({k:v for k,v in result.items() if k!='moments'}),flush=True)
finally: GraphTheory.reset()
