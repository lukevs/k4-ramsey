"""Finite correlated block rounding of an independently discovered graphon shift."""
import argparse
from itertools import permutations
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph,certificate,load
from k4_ramsey.lab import write_json


def main():
    p=argparse.ArgumentParser()
    for name in ('input','output','config'):p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--seconds',type=float,required=True);p.add_argument('--seed',type=int,required=True)
    args=p.parse_args()
    config=json.loads(args.config.read_text())
    rows=load(args.input)['red_rows'];fibers=config['fibers'];classes=config['classes']
    params=config['parameters'];den=config['denominator']
    if sorted(v for cell in fibers for v in cell)!=list(range(len(rows))):raise ValueError('bad partition')
    for i in range(len(fibers)):
        for j in range(i):
            kind=classes[i][j]
            if kind!=classes[j][i]:raise ValueError('asymmetric class matrix')
            expected={0:4,1:3,2:3,3:3,4:2,5:4}.get(kind)
            if expected is not None and any(sum(rows[u][v]=='1' for v in fibers[j])!=expected for u in fibers[i]):
                raise ValueError('class matrix does not match input block degrees')
    graph=Graph(certificate(rows));initial=graph.counts()['numerator'];graph.close()
    start=time.monotonic();rng=random.Random(args.seed);best=initial;records=[]
    write_json(args.output,certificate(rows))
    perms=list(permutations(range(4)))
    for repetition in range(4):
        draws={(i,j):(rng.randrange(den),rng.choice(perms))
               for i in range(len(fibers)) for j in range(i) if classes[i][j]>=0}
        for all_classes in (False,True):
            result=[list(row) for row in rows];changed=[]
            for (i,j),(draw,perm) in draws.items():
                kind=classes[i][j]
                if not all_classes and kind!=5:continue
                target=None
                if kind==5 and draw<4*(den-params[kind]):target=3
                elif kind in (1,2,3) and draw<4*params[kind]-3*den:target=4
                elif kind==4 and draw<4*params[kind]-2*den:target=3
                if target is None:continue
                for a,u in enumerate(fibers[i]):
                    for b,v in enumerate(fibers[j]):
                        result[u][v]=result[v][u]=str(int(target==4 or perm[a]!=b))
                changed.append((i,j,kind,target))
            data=certificate([''.join(row) for row in result])
            graph=Graph(data);counts=graph.counts();graph.close();value=counts['numerator']
            path=args.output.parent/f'raw-{len(records):02d}.json';write_json(path,data)
            records.append(dict(group='graphon_mean_shift' if all_classes else 'class5_only',opposite=all_classes,
                repetition=repetition,numerator=value,delta=value-initial,counts=counts,changed_blocks=changed,
                raw_path=str(path),seconds=time.monotonic()-start))
            if value<best:best=value;write_json(args.output,data)
    write_json(args.output.parent/'search.json',dict(numerator=best,initial_numerator=initial,
        records=records,attempted=len(records),seconds=time.monotonic()-start,
        evidence='Exact finite unit-weight recount; graphon probability only motivates correlated rounding',
        termination='predeclared_bank_exhausted'))


if __name__=='__main__':main()
