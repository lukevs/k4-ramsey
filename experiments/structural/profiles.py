"""Exact labeled repetitive four-vertex profiles; no external dependencies.

Pattern bit k encodes EDGES[k]. Vertices are sampled WITH replacement.
XOR graphs use edgewise XOR, including their (blue) diagonal entries.
This is search arithmetic, not the independent Lean checker.
"""
from fractions import Fraction
from itertools import combinations, permutations, product

EDGES = tuple(combinations(range(4), 2))


def validate(rows):
    n = len(rows)
    if not n or any(len(row) != n or set(row) - set("01") for row in rows):
        raise ValueError("expected nonempty square binary rows")
    if any(rows[i][i] != "0" for i in range(n)):
        raise ValueError("only blue diagonals supported")
    if any(rows[i][j] != rows[j][i] for i in range(n) for j in range(i)):
        raise ValueError("rows must be symmetric")


def profile(rows):
    validate(rows)
    result = [0] * 64
    a = [[int(x) for x in row] for row in rows]
    for i, j, k, l in product(range(len(rows)), repeat=4):
        mask = (a[i][j] | a[i][k] << 1 | a[i][l] << 2 |
                a[j][k] << 3 | a[j][l] << 4 | a[k][l] << 5)
        result[mask] += 1
    return tuple(result)


def transform(values):
    """Unnormalized Walsh-Hadamard transform: transform(transform(v)) = 64*v."""
    if len(values) != 64:
        raise ValueError("expected 64 pattern coordinates")
    out = list(values)
    width = 1
    while width < 64:
        for start in range(0, 64, width * 2):
            for j in range(start, start + width):
                a, b = out[j], out[j + width]
                out[j], out[j + width] = a + b, a - b
        width *= 2
    return tuple(out)


def xor_profiles(a, b):
    values = transform(tuple(x * y for x, y in zip(transform(a), transform(b))))
    return tuple(Fraction(x, 64) for x in values)


def mono(values):
    return Fraction(values[0] + values[63], sum(values))


def xor_graph(a, b):
    validate(a)
    validate(b)
    vertices = tuple(product(range(len(a)), range(len(b))))
    return ["".join(str(int(a[i][k]) ^ int(b[j][l])) for k, l in vertices)
            for i, j in vertices]


def compose_graph(a, b):
    validate(a)
    validate(b)
    vertices = tuple(product(range(len(a)), range(len(b))))
    return ["".join(b[j][l] if i == k else a[i][k] for k, l in vertices)
            for i, j in vertices]


def composition_terms(outer):
    """Counts of (internal-edge mask, fixed outer-edge mask) among outer tuples."""
    validate(outer)
    terms = {}
    for vs in product(range(len(outer)), repeat=4):
        inside = fixed = 0
        for bit, (i, j) in enumerate(EDGES):
            if vs[i] == vs[j]:
                inside |= 1 << bit
            elif outer[vs[i]][vs[j]] == "1":
                fixed |= 1 << bit
        key = inside, fixed
        terms[key] = terms.get(key, 0) + 1
    return terms


def compose_profile(terms, inner):
    result = [0] * 64
    for (inside, fixed), count in terms.items():
        for mask, value in enumerate(inner):
            result[(mask & inside) | fixed] += count * value
    return tuple(result)


def relabel(mask, permutation):
    result = 0
    lookup = {edge: bit for bit, edge in enumerate(EDGES)}
    for bit, (i, j) in enumerate(EDGES):
        edge = tuple(sorted((permutation[i], permutation[j])))
        if mask >> lookup[edge] & 1:
            result |= 1 << bit
    return result


ORBITS = {}
for _mask in range(64):
    _representative = min(relabel(_mask, p) for p in permutations(range(4)))
    ORBITS.setdefault(_representative, []).append(_mask)
CLASSES = tuple(tuple(v) for v in ORBITS.values())


def nested_limit(outer):
    """Solve the 11-class stationary profile exactly; reject degenerate kernels.

    For |outer| > 1, first differing coordinates of independent infinite words
    define the nested blow-up. Probability of a shared prefix decays to zero.
    Thus the stationary profile equals this construction's limiting profile.
    """
    if len(outer) < 2:
        raise ValueError("nested core must have at least two vertices")
    terms = composition_terms(outer)
    denominator = len(outer) ** 4
    columns = []
    for orbit in CLASSES:
        p = [Fraction(int(mask in orbit), len(orbit)) for mask in range(64)]
        q = compose_profile(terms, p)
        columns.append([sum(q[mask] for mask in target) / denominator
                        for target in CLASSES])
    m = len(CLASSES)
    equations = [[columns[j][i] - int(i == j) for j in range(m)] + [Fraction(0)]
                 for i in range(m - 1)]
    equations.append([Fraction(1)] * m + [Fraction(1)])
    for col in range(m):
        pivot = next((i for i in range(col, m) if equations[i][col]), None)
        if pivot is None:
            raise ValueError("stationary kernel is not uniquely solved")
        equations[col], equations[pivot] = equations[pivot], equations[col]
        divisor = equations[col][col]
        equations[col] = [x / divisor for x in equations[col]]
        for row in range(m):
            if row != col:
                factor = equations[row][col]
                equations[row] = [a - factor * b for a, b in
                                  zip(equations[row], equations[col])]
    result = [Fraction(0)] * 64
    for row, orbit in enumerate(CLASSES):
        for mask in orbit:
            result[mask] = equations[row][-1] / len(orbit)
    composed = compose_profile(terms, result)
    assert all(x >= 0 for x in result) and sum(result) == 1
    assert all(x * denominator == y for x, y in zip(result, composed))
    return tuple(result)


def graph_from_mask(n, mask):
    rows = [["0"] * n for _ in range(n)]
    for bit, (i, j) in enumerate(combinations(range(n), 2)):
        rows[i][j] = rows[j][i] = str(mask >> bit & 1)
    return ["".join(row) for row in rows]
