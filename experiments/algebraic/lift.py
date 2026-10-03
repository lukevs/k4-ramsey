"""Global permutation-voltage variants of the seed's discovered four-sheet lift."""
import argparse
from collections import Counter
from itertools import combinations, permutations, product
import json
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, certificate, load
from k4_ramsey.lab import write_json

PERMUTATIONS = tuple(permutations(range(4)))
KLEIN = tuple(tuple(i^a for i in range(4)) for a in range(4))
REGULAR_TWO = tuple(tuple(sum(1<<j for j in pair) for pair in row_pairs)
    for row_pairs in product(tuple(combinations(range(4),2)),repeat=4)
    if all(sum(j in pair for pair in row_pairs)==2 for j in range(4)))


def half_blocks(rows,fibers):
    result=[]
    for i,cell in enumerate(fibers):
        for j in range(i):
            pattern=tuple(sum((rows[u][v]=='1')<<b for b,v in enumerate(fibers[j])) for u in cell)
            if all(row.bit_count()==2 for row in pattern):
                if pattern not in REGULAR_TWO: raise ValueError('invalid degree-two block')
                result.append((i,j,pattern))
    return result


def materialize_half(rows,fibers,blocks,patterns):
    if len(blocks)!=len(patterns): raise ValueError('pattern length mismatch')
    result=[list(row) for row in rows]
    for (i,j,_),pattern in zip(blocks,patterns):
        pattern=tuple(pattern)
        if pattern not in REGULAR_TWO: raise ValueError('invalid degree-two pattern')
        for a,u in enumerate(fibers[i]):
            for b,v in enumerate(fibers[j]):
                result[u][v]=result[v][u]=str(pattern[a]>>b&1)
    return [''.join(row) for row in result]


def discover_fibers(rows, max_distance=26):
    bits=[int(row,2) for row in rows]
    remaining=set(range(len(rows)))
    fibers=[]
    while remaining:
        u=min(remaining)
        cell=sorted(v for v in remaining if (bits[u]^bits[v]).bit_count()<=max_distance)
        if len(cell)!=4 or any((bits[i]^bits[j]).bit_count()>max_distance for i in cell for j in cell):
            raise ValueError('distance threshold does not define four-vertex fibers')
        fibers.append(cell)
        remaining.difference_update(cell)
    return fibers


def decompose(rows,fibers):
    if sorted(v for cell in fibers for v in cell)!=list(range(len(rows))):
        raise ValueError('fibers must partition vertices')
    if any(len(cell)!=4 for cell in fibers):
        raise ValueError('all fibers must have order four')
    blocks=[]
    counts=Counter()
    for i,cell in enumerate(fibers):
        if any(rows[u][v]!='0' for u in cell for v in cell):
            raise ValueError('fibers must be independent sets')
        for j in range(i):
            other=fibers[j]
            matrix=[[int(rows[u][v]) for v in other] for u in cell]
            degrees=[sum(row) for row in matrix]
            columns=[sum(matrix[a][b] for a in range(4)) for b in range(4)]
            if len(set(degrees+columns))!=1:
                raise ValueError('inter-fiber block is not biregular')
            degree=degrees[0]
            counts[degree]+=1
            if degree==3:
                missing=tuple(row.index(0) for row in matrix)
                if sorted(missing)!=list(range(4)):
                    raise ValueError('missing edges must form a matching')
                blocks.append((i,j,missing))
    return blocks,dict(sorted(counts.items()))


def materialize(rows,fibers,blocks,voltages):
    if len(blocks)!=len(voltages):
        raise ValueError('voltage length mismatch')
    result=[list(row) for row in rows]
    for (i,j,_),voltage in zip(blocks,voltages):
        if tuple(sorted(voltage))!=(0,1,2,3):
            raise ValueError('voltage must be a permutation')
        for a,u in enumerate(fibers[i]):
            for b,v in enumerate(fibers[j]):
                result[u][v]=result[v][u]=str(int(voltage[a]!=b))
    return [''.join(row) for row in result]


def gauge_relabel(rows,fibers,gauges):
    order=list(range(len(rows)))
    for cell,gauge in zip(fibers,gauges):
        if tuple(sorted(gauge))!=(0,1,2,3):
            raise ValueError('gauge must be a permutation')
        for i,v in enumerate(cell):
            order[v]=cell[gauge[i]]
    return [''.join(rows[order[u]][order[v]] for v in range(len(rows)))
            for u in range(len(rows))]


def standardize_halves(rows,fibers):
    """Gauge disjoint two-K2,2 blue blocks to equality of sheet bit 1."""
    halves=half_blocks(rows,fibers)
    gauges=[None]*len(fibers)
    for i,j,pattern in halves:
        if gauges[i] is not None or gauges[j] is not None or len(set(pattern))!=2:
            raise ValueError('half blocks must form a matching of two-K2,2 blocks')
        first=[a for a in range(4) if pattern[a]==pattern[0]]
        rest=[a for a in range(4) if a not in first]
        blue=[b for b in range(4) if not (pattern[0]>>b&1)]
        red=[b for b in range(4) if pattern[0]>>b&1]
        gauges[i]=tuple(first+rest)
        gauges[j]=tuple(blue+red)
    if any(g is None for g in gauges): raise ValueError('half matching not perfect')
    changed=gauge_relabel(rows,fibers,gauges)
    if any(p!=(12,12,3,3) for _,_,p in half_blocks(changed,fibers)):
        raise RuntimeError('half normalization failed')
    return changed,gauges


def triangle_constraint_components(blocks,halves):
    mate={u:v for i,j,_ in halves for u,v in ((i,j),(j,i))}
    lookup={tuple(sorted((i,j))):e for e,(i,j,_) in enumerate(blocks)}
    adjacency=[set() for _ in blocks]
    for e,(i,j,_) in enumerate(blocks):
        for u,v in ((i,mate[j]),(mate[i],j)):
            other=lookup.get(tuple(sorted((u,v))))
            if other is not None: adjacency[e].add(other)
    colors={}
    components=[]
    for root in range(len(blocks)):
        if root in colors: continue
        colors[root]=0
        todo=[root]
        component=[]
        while todo:
            e=todo.pop()
            component.append(e)
            for f in adjacency[e]:
                if f not in colors: colors[f]=1-colors[e];todo.append(f)
                elif colors[f]==colors[e]: raise ValueError('odd triangle-constraint cycle')
        components.append(component)
    return components,colors,adjacency


def assignments(blocks,rng):
    original=[p for _,_,p in blocks]
    for index,twist in enumerate(PERMUTATIONS):
        if index:
            yield [tuple(twist[p[a]] for a in range(4)) for p in original],dict(family='global_left_twist',permutation=twist)
    for twist in PERMUTATIONS:
        yield [twist]*len(blocks),dict(family='constant_voltage',permutation=twist)
    for group,bank in [('S4',PERMUTATIONS),('V4',KLEIN)]:
        for probability in (0.01,0.05,0.25,1.0):
            for repetition in range(3):
                voltages=[rng.choice(bank) if rng.random()<probability else p for p in original]
                yield voltages,dict(family='random_voltage',group=group,
                    replace_probability=probability,repetition=repetition)


def main():
    p=argparse.ArgumentParser()
    for name in ('input','output','config'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--seconds',type=float,required=True)
    args=p.parse_args()
    config=json.loads(args.config.read_text())
    if set(config)-{'phase'} or config.get('phase',1) not in (1,2,3):
        raise ValueError('phase must be 1, 2 or 3')
    start=time.monotonic()
    rows=load(args.input)['red_rows']
    fibers=discover_fibers(rows)
    gauges=None
    if config.get('phase',1)==3:
        rows,gauges=standardize_halves(rows,fibers)
    blocks,block_counts=decompose(rows,fibers)
    halves=half_blocks(rows,fibers)
    write_json(args.output.parent/'quotient.json',dict(fibers=fibers,
        complement_matching_blocks=blocks,half_blocks=halves,block_counts=block_counts,gauges=gauges,
        convention='block(i,j,p), i>j: missing edge from fiber_i[a] to fiber_j[p[a]]'))
    graph=Graph(certificate(rows))
    initial=graph.counts()['numerator']
    graph.close()
    best=initial
    original_degrees=[row.count('1') for row in rows]
    write_json(args.output,certificate(rows))
    rng=random.Random(args.seed)
    controls=[]
    for _ in range(2):
        gauged=gauge_relabel(rows,fibers,[rng.choice(PERMUTATIONS) for _ in fibers])
        control=Graph(certificate(gauged))
        value=control.counts()['numerator']
        control.close()
        if value!=initial: raise RuntimeError('gauge changed objective')
        controls.append(value)
    seen={tuple(p for _,_,p in blocks)+tuple(p for _,_,p in halves)}
    records=[]
    complete=True
    def bank():
        original=[p for _,_,p in blocks]
        old_half=[p for _,_,p in halves]
        if config.get('phase',1)==1:
            for voltages,descriptor in assignments(blocks,rng):
                yield voltages,old_half,descriptor
        elif config.get('phase')==2:
            # A matched factorial comparison: same random voltages and patterns
            # in all four cells of a repetition, one cause changed at a time.
            for kind in ('two_K22','C8','all'):
                bank=[p for p in REGULAR_TWO if kind=='all' or
                      (len(set(p))==2)==(kind=='two_K22')]
                for repetition in range(6):
                    fresh=[rng.choice(PERMUTATIONS) for _ in blocks]
                    half=[rng.choice(bank) for _ in halves]
                    for change_voltage,change_half in ((False,True),(True,False),(True,True)):
                        yield fresh if change_voltage else original, half if change_half else old_half,dict(
                            family='matched_regular_block_randomization',half_kind=kind,
                            repetition=repetition,change_voltage=change_voltage,change_half=change_half)
        else:
            components,colors,adjacency=triangle_constraint_components(blocks,halves)
            write_json(args.output.parent/'constraints.json',dict(components=components,
                bipartite_colors=colors,adjacency=[sorted(ns) for ns in adjacency],
                constraints=sum(map(len,adjacency))//2,
                equation='x_e XOR x_f = 1 eliminates all blue D-D-H triangles'))
            for group in ('V4','D8'):
                for repetition in range(4):
                    roots=[rng.randrange(2) for _ in components]
                    second=[(rng.randrange(2),rng.randrange(2)) for _ in blocks]
                    for opposite in (False,True):
                        bits={e:roots[c]^(colors[e] if opposite else 0)
                              for c,component in enumerate(components) for e in component}
                        fresh=[]
                        for e in range(len(blocks)):
                            flips=second[e] if group=='D8' else (second[e][0],)*2
                            fresh.append(tuple(((a>>1)^bits[e])*2+((a&1)^flips[a>>1]) for a in range(4)))
                        yield fresh,old_half,dict(family='exact_triangle_constraints',group=group,
                            repetition=repetition,opposite=opposite)
    for voltages,half_patterns,descriptor in bank():
        if time.monotonic()>=start+args.seconds-1:
            complete=False
            break
        key=tuple(voltages)+tuple(half_patterns)
        if key in seen: continue
        seen.add(key)
        candidate=materialize(rows,fibers,blocks,voltages)
        candidate=materialize_half(candidate,fibers,halves,half_patterns)
        if [row.count('1') for row in candidate]!=original_degrees:
            raise RuntimeError('lift changed degrees')
        graph=Graph(certificate(candidate))
        counts=graph.counts()
        graph.close()
        value=counts['numerator']
        raw_path=None
        if config.get('phase')==3:
            raw_path=str(args.output.parent/f'raw-{len(records):02d}.json')
            write_json(raw_path,certificate(candidate))
        records.append(dict(**descriptor,numerator=value,delta=value-initial,counts=counts,
            voltages=voltages,half_patterns=half_patterns,
            changed_blocks=sum(p!=q for (_,_,p),q in zip(blocks,voltages)),
            changed_half_blocks=sum(p!=q for (_,_,p),q in zip(halves,half_patterns)),
            raw_path=raw_path,
            seconds=time.monotonic()-start))
        if value<best:
            best=value
            write_json(args.output,certificate(candidate))
    write_json(args.output.parent/'search.json',dict(numerator=best,initial_numerator=initial,
        attempted=len(records),gauge_controls=controls,records=records,
        seconds=time.monotonic()-start,termination='family_exhausted' if complete else 'time_limit',
        evidence='Exact native recount of materialized four-sheet lifts; retained output independently checked by runner',
        scope='Selected global voltage assignment bank; not full S4 lift optimization'))


if __name__=='__main__': main()
