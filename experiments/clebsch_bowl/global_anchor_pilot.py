"""Exact finite checks for a universal six-root / ten-vertex square."""
from fractions import Fraction as F
from itertools import product, combinations
import hashlib
import json
from pathlib import Path
import time

ROOT_EDGES = {(0, 1), (1, 2), (2, 3), (3, 4), (0, 4)}
A = (1, 1, 1, 1, 1, -5)


def anchor(U, r):
    out = F(1)
    for i, j in combinations(range(6), 2):
        p = U[r[i]][r[j]]
        out *= p if (i, j) in ROOT_EDGES else 1-p
    return out


def grouped(U, w):
    """Integrate extension vertices first, then assemble a 3x3 Gram matrix."""
    n = len(w)
    M = [[F(0) for _ in range(3)] for _ in range(3)]
    for r in product(range(n), repeat=6):
        weight = anchor(U, r)
        for v in r:
            weight *= w[v]
        psi = [sum(A[i]*U[r[i]][z] for i in range(6)) for z in range(n)]
        mean = sum(w[z]*psi[z] for z in range(n))
        red = sum(w[z]*w[t]*U[z][t]*psi[z]*psi[t]
                  for z in range(n) for t in range(n))
        features = (F(1), mean**2, red)
        for i in range(3):
            for j in range(3):
                M[i][j] += weight*features[i]*features[j]
    return M


def direct(U, w):
    """Literal ten independent latent draws, signed-edge expansion of f^2."""
    total = F(0)
    for vertices in product(range(len(w)), repeat=10):
        weight = F(1)
        for v in vertices:
            weight *= w[v]
        # Independently encode the five cycle edges and ten nonedges.
        for i in range(6):
            for j in range(i+1, 6):
                edge = U[vertices[i]][vertices[j]]
                cycle = i < 5 and j < 5 and (j-i == 1 or (i == 0 and j == 4))
                weight *= edge if cycle else 1-edge
        contrast = []
        for z in range(6, 10):
            contrast.append(sum(U[vertices[i]][vertices[z]] for i in range(5))
                            -5*U[vertices[5]][vertices[z]])
        total += (weight*U[vertices[6]][vertices[7]]
                  *U[vertices[8]][vertices[9]]
                  *contrast[0]*contrast[1]*contrast[2]*contrast[3])
    return total


def determinant(M):
    n = len(M)
    if n == 1:
        return M[0][0]
    return sum((-1)**j*M[0][j]*determinant(
        [[M[i][k] for k in range(n) if k != j] for i in range(1, n)])
        for j in range(n))


def highest_term():
    # Top term of the induced anchor is K6 with sign (-1)^10 = +1.
    # Identify K6 with two triangles attached at the same core vertex.
    coefficient = 0
    hits = 0
    for attachments in product(range(6), repeat=4):
        edges = set(combinations(range(6), 2)) | {(6, 7), (8, 9)}
        c = 1
        for outside, inside in enumerate(attachments, start=6):
            edges.add((inside, outside))
            c *= A[inside]
        degrees = [sum(v in e for e in edges) for v in range(10)]
        if sorted(degrees) == [2, 2, 2, 2, 5, 5, 5, 5, 5, 9]:
            coefficient += c
            hits += 1
    assert hits == 6 and coefficient == 630
    return {"vertices": 10, "edges": 21, "coefficient": coefficient,
            "attachment_assignments_checked": 6**4, "matching_terms": hits}


def free_completion():
    # If the new ten-vertex moments are unconstrained, a Gram block alone
    # never cuts off any (a,b,c) with a>0: complete it as vv^T/a.
    examples = []
    for a, b, c in [(F(1, 8), F(-3), F(2)),
                    (F(1, 100), F(1, 7), F(-5, 11))]:
        v = (a, b, c)
        M = [[x*y/a for y in v] for x in v]
        assert M[0] == list(v)
        assert all(determinant([[M[i][j] for j in ids] for i in ids]) >= 0
                   for k in (1, 2, 3) for ids in combinations(range(3), k))
        examples.append([[str(x) for x in row] for row in M])
    return {"formula": "M = (a,b,c)(a,b,c)^T / a, a>0",
            "examples": examples, "isolated_block_can_strengthen": False,
            "qualification": "Only when all three lower-block entries are free."}


if __name__ == "__main__":
    start = time.monotonic()
    fixtures = [
        ([[F(1, 2)]], [F(1)]),
        ([[F(1, 3), F(2, 3)], [F(2, 3), F(1, 4)]], [F(1, 3), F(2, 3)]),
        ([[F(1), F(0)], [F(0), F(0)]], [F(1, 4), F(3, 4)]),
        ([[F(0), F(1)], [F(1), F(0)]], [F(2, 5), F(3, 5)]),
    ]
    rows = []
    for U, w in fixtures:
        M = grouped(U, w)
        literal = direct(U, w)
        assert literal == M[2][2]
        minors = [determinant([[M[i][j] for j in ids] for i in ids])
                  for k in (1, 2, 3) for ids in combinations(range(3), k)]
        assert min(minors) >= 0
        rows.append({"matrix": [[str(x) for x in row] for row in U],
                     "weights": list(map(str, w)),
                     "gram": [[str(x) for x in row] for row in M],
                     "direct_ten_vertex_square": str(literal),
                     "exact_agreement": True, "all_principal_minors_nonnegative": True})
    print(json.dumps({"hypothesis": "H-GA1", "arithmetic": "exact rational",
                      "highest_order_term": highest_term(), "fixtures": rows,
                      "free_moment_completion": free_completion(),
                      "seconds": time.monotonic()-start,
                      "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      "global_SDP_nonredundancy_proved": False,
                      "lower_bound_improved": False}, indent=2))
