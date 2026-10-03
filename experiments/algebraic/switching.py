"""Macroscopic Seidel switches from spectral cuts, with exact graph recounts.

The exported graph, not the spectral surrogate, determines the objective.
This script is self-contained so the lab snapshots all strategy source.
"""
import argparse
import json
import math
from pathlib import Path
import random
import time

from k4_ramsey.engine import Graph, certificate, load
from k4_ramsey.lab import write_json


def switch(rows, cut):
    """A'ij = Aij XOR cut_i XOR cut_j; blue diagonal is preserved."""
    if len(cut) != len(rows) or any(x not in (0, 1) for x in cut):
        raise ValueError('cut must be binary and match graph order')
    return [''.join(str(int(c) ^ cut[i] ^ cut[j]) for j, c in enumerate(row))
            for i, row in enumerate(rows)]


def canonical_cut(cut):
    # Complementary vertex sets produce the same switch.
    return tuple(x ^ cut[0] for x in cut)


def spectral_vectors(rows, rng, count, iterations, deadline):
    """Deflated power iteration for large-|eigenvalue| Seidel directions.

    Project away the constant vector; on this regular seed its orthogonal
    complement is invariant. For nonregular inputs this is compressed-matrix
    power iteration, still a valid heuristic cut generator.
    """
    n = len(rows)
    neighbors = [[j for j,c in enumerate(row) if c == '1'] for row in rows]
    basis = [[1 / math.sqrt(n)] * n]
    for _ in range(count):
        v = [rng.gauss(0, 1) for _ in range(n)]
        for iteration in range(iterations + 1):
            for _pass in range(2):
                for q in basis:
                    dot = sum(a*b for a,b in zip(v,q))
                    v = [a-dot*b for a,b in zip(v,q)]
            norm = math.sqrt(sum(x*x for x in v))
            if norm < 1e-12:
                break
            v = [x/norm for x in v]
            if iteration == iterations or time.monotonic() >= deadline:
                break
            total = sum(v)
            v = [total-v[i]-2*sum(v[j] for j in ns) for i,ns in enumerate(neighbors)]
        basis.append(v)
        total = sum(v)
        sv = [total-v[i]-2*sum(v[j] for j in ns) for i,ns in enumerate(neighbors)]
        rayleigh = sum(x*y for x,y in zip(v,sv))
        residual = math.sqrt(sum((y-rayleigh*x)**2 for x,y in zip(v,sv)))
        yield v, dict(rayleigh=rayleigh, residual=residual, iterations=iteration)
        if time.monotonic() >= deadline:
            return


def candidate_cuts(rows, rng, config, deadline):
    n = len(rows)
    for vertex in config.get('neighborhood_vertices', [0,1,2,3]):
        if vertex < n:
            yield [int(x) for x in rows[vertex]], dict(family='neighborhood', vertex=vertex)
    for index in range(config.get('random_controls', 8)):
        yield [rng.randrange(2) for _ in rows], dict(family='random_balanced_in_expectation', index=index)
    spectral = []
    for index,(v,diagnostic) in enumerate(spectral_vectors(rows,rng,
            config.get('spectral_vectors',8),config.get('iterations',48),deadline)):
        ranking = sorted(range(n), key=lambda i: (v[i], i))
        for eighths in config.get('quantiles',[1,2,3,4,5,6,7]):
            chosen = set(ranking[:n*eighths//8])
            cut = [int(i in chosen) for i in range(n)]
            if eighths == 4:
                spectral.append(cut)
            yield cut, dict(family='spectral_quantile', vector=index,
                            eighths=eighths, **diagnostic)
    for i, first in enumerate(spectral):
        for j in range(i):
            yield [a^b for a,b in zip(first,spectral[j])], dict(family='spectral_xor',first=i,second=j)


def main():
    p = argparse.ArgumentParser()
    for name in ('input','output','config'):
        p.add_argument('--'+name,type=Path,required=True)
    p.add_argument('--seed',type=int,required=True)
    p.add_argument('--seconds',type=float,required=True)
    args = p.parse_args()
    config = json.loads(args.config.read_text())
    allowed = {'neighborhood_vertices','random_controls','spectral_vectors','iterations','quantiles'}
    if set(config)-allowed:
        raise ValueError('unknown config key')
    for name in ('random_controls','spectral_vectors','iterations'):
        if name in config and (type(config[name]) is not int or config[name]<0):
            raise ValueError(name+' must be a nonnegative integer')
    for name, minimum, maximum in [('neighborhood_vertices',0,None),('quantiles',1,7)]:
        if name in config and (not isinstance(config[name],list) or any(
            type(x) is not int or x<minimum or (maximum is not None and x>maximum)
            for x in config[name])):
            raise ValueError('invalid '+name)
    start = time.monotonic()
    rows = load(args.input)['red_rows']
    initial_graph = Graph(certificate(rows))
    initial = initial_graph.counts()['numerator']
    initial_graph.close()
    best = initial
    best_cut = [0]*len(rows)
    write_json(args.output, certificate(rows))
    records = []
    seen = {canonical_cut(best_cut)}
    complete = True
    for cut, descriptor in candidate_cuts(rows,random.Random(args.seed),config,start+args.seconds-1):
        if time.monotonic() >= start+args.seconds-0.5:
            complete = False
            break
        key = canonical_cut(cut)
        if key in seen:
            continue
        seen.add(key)
        transformed = switch(rows,cut)
        graph = Graph(certificate(transformed))
        counts = graph.counts()
        graph.close()
        value = counts['numerator']
        records.append(dict(**descriptor,cut=''.join(map(str,cut)),cut_size=sum(cut),
            numerator=value,delta=value-initial,counts=counts,seconds=time.monotonic()-start))
        if value < best:
            best, best_cut = value, cut
            write_json(args.output,certificate(transformed))
    write_json(args.output.parent/'search.json',dict(numerator=best,initial_numerator=initial,
        attempted=len(records),best_cut=best_cut,seconds=time.monotonic()-start,
        termination='family_exhausted' if complete and time.monotonic()<start+args.seconds-1 else 'time_limit',records=records,
        evidence='Exact native recount per materialized cut; only output independently checked by runner.',
        scope='Selected cuts of one Seidel switching orbit, not exhaustive orbit optimization.'))


if __name__ == '__main__':
    main()
