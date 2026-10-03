"""Exact profiles of two-type, vertex-dependent recursive graph constructions.

Each rule has a fixed simple outer graph and a child type for every vertex.
Cross-block edges use the outer graph; inside a block recurse using its child
type. Equal masses at each branching level; no fractional edge probabilities.
"""
from collections import Counter
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product

from experiments.structural.profiles import validate


def checked_rules(rules):
    if len(rules) != 2:
        raise ValueError("exactly two recursive types required")
    result = []
    for rows, children in rules:
        validate(rows)
        if len(rows) < 2 or len(children) != len(rows) or any(c not in (0, 1) for c in children):
            raise ValueError("invalid recursive rule")
        result.append((tuple(rows), tuple(children)))
    return tuple(result)


@lru_cache(maxsize=4096)
def recipes(rows, children, t):
    """Compress outer tuples by fixed cross edges and typed repeated groups."""
    edges = tuple(combinations(range(t), 2))
    count = Counter()
    for vs in product(range(len(rows)), repeat=t):
        groups = {}
        fixed = 0
        for pos, v in enumerate(vs):
            groups.setdefault(v, []).append(pos)
        for bit, (i, j) in enumerate(edges):
            if vs[i] != vs[j] and rows[vs[i]][vs[j]] == "1":
                fixed |= 1 << bit
        repeated = tuple((children[v], tuple(positions)) for v, positions in groups.items()
                         if len(positions) > 1)
        count[(fixed, repeated)] += 1
    return tuple(count.items())


@lru_cache(maxsize=256)
def embedded_masks(t, positions):
    lookup = {edge: i for i, edge in enumerate(combinations(range(t), 2))}
    inside = list(combinations(positions, 2))
    return tuple(sum(((mask >> i) & 1) << lookup[edge] for i, edge in enumerate(inside))
                 for mask in range(1 << len(inside)))


def contract(rule, t, profiles, *, exclude_same=False):
    rows, children = rule
    result = [Fraction(0)] * (1 << (t * (t - 1) // 2))
    for (fixed, groups), multiplicity in recipes(rows, children, t):
        if exclude_same and len(groups) == 1 and len(groups[0][1]) == t:
            continue
        states = [(fixed, Fraction(multiplicity, len(rows)**t))]
        for kind, positions in groups:
            p = profiles[kind][len(positions)]
            embeddings = embedded_masks(t, positions)
            states = [(mask | embedded, value * probability)
                      for mask, value in states
                      for embedded, probability in zip(embeddings, p) if probability]
        for mask, value in states:
            result[mask] += value
    return tuple(result)


def finite_profiles(rules, depth):
    rules = checked_rules(rules)
    if type(depth) is not int or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    profiles = [{t: (Fraction(1),) + (Fraction(0),) * ((1 << (t*(t-1)//2))-1)
                 for t in range(1, 5)} for _ in rules]
    for _ in range(depth):
        profiles = [{t: contract(rule, t, profiles) for t in range(1, 5)} for rule in rules]
    return profiles


def limiting_profiles(rules):
    """Solve bottom-up; only all-in-one-block terms involve order-t unknowns."""
    rules = checked_rules(rules)
    profiles = [{1: (Fraction(1),)} for _ in rules]
    for t in range(2, 5):
        matrix = [[Fraction(int(i == j)) - Fraction(rule[1].count(j), len(rule[0])**t)
                   for j in range(2)] for i, rule in enumerate(rules)]
        (a, b), (c, d) = matrix
        determinant = a*d-b*c
        assert determinant
        rhs = [contract(rule, t, profiles, exclude_same=True) for rule in rules]
        profiles[0][t] = tuple((d*x-b*y)/determinant for x, y in zip(*rhs))
        profiles[1][t] = tuple((a*y-c*x)/determinant for x, y in zip(*rhs))
        for kind in range(2):
            assert sum(profiles[kind][t]) == 1
            assert all(x >= 0 for x in profiles[kind][t])
        # Check all coordinates of the defining equations, not just the objective.
        assert all(contract(rule, t, profiles) == profiles[kind][t]
                   for kind, rule in enumerate(rules))
    return profiles


def explicit_expand(rules, kind, depth):
    """Tiny oracle materialization for equal-order rules; each block equal size."""
    rules = checked_rules(rules)
    if len(rules[0][0]) != len(rules[1][0]):
        raise ValueError("explicit unweighted expansion requires equal rule orders")
    if depth == 0:
        return ["0"]
    rows, children = rules[kind]
    inner = [explicit_expand(rules, c, depth-1) for c in children]
    m = len(inner[0])
    return ["".join(inner[u][i][j] if u == v else rows[u][v]
                    for v in range(len(rows)) for j in range(m))
            for u in range(len(rows)) for i in range(m)]
