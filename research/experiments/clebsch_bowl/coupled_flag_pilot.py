"""Small universal K4 flag SDPs: N=5, coupled N=6, full N=6 control.

All variables are induced unlabelled graph probabilities. Flag products use
disjoint extension vertices; no Clebsch or regularity assumption is imposed.
"""
import itertools as it
import math
import json
import hashlib
import time
from pathlib import Path
from functools import lru_cache

import numpy as np
import networkx as nx
import cvxpy as cp


def pairs(n):
    return list(it.combinations(range(n), 2))


def code(A, vertices):
    return sum(int(A[vertices[i], vertices[j]]) << b
               for b, (i, j) in enumerate(pairs(len(vertices))))


@lru_cache(None)
def canonical_bits(bits, n, roots=0):
    A = np.zeros((n, n), dtype=np.int8)
    for b, (i, j) in enumerate(pairs(n)):
        A[i, j] = A[j, i] = (bits >> b) & 1
    return min(code(A, tuple(range(roots))+p)
               for p in it.permutations(range(roots, n)))


def atlas(n):
    return [nx.to_numpy_array(g, dtype=np.int8) for g in nx.graph_atlas_g()
            if len(g) == n]


def objective(A):
    mono = sum(code(A, v) in (0, 63) for v in it.combinations(range(len(A)), 4))
    return mono / math.comb(len(A), 4)


def gram_coefficients(graphs, r):
    n = len(graphs[0])
    k = (n-r)//2
    assert r+2*k == n
    all_rows = []
    seen = {}
    # Conditional type is kept as one canonical *labelled* representative.
    # Ordered root sampling handles all its embeddings and automorphisms.
    for A in graphs:
        counts = {}
        for root in it.permutations(range(n), r):
            t = code(A, root)
            if t != canonical_bits(t, r):
                continue
            rem = tuple(v for v in range(n) if v not in root)
            for outside in it.combinations(rem, k):
                other = tuple(v for v in rem if v not in outside)
                f = canonical_bits(code(A, root+outside), r+k, r)
                g = canonical_bits(code(A, root+other), r+k, r)
                counts[t, f, g] = counts.get((t, f, g), 0)+1
                seen.setdefault(t, set()).update((f, g))
        all_rows.append(counts)
    denominator = math.factorial(n)//math.factorial(n-r)*math.comb(n-r, k)
    result = []
    for t, flags in sorted(seen.items()):
        flags = sorted(flags)
        index = {f: i for i, f in enumerate(flags)}
        C = np.zeros((len(graphs), len(flags), len(flags)))
        for h, counts in enumerate(all_rows):
            for (tt, f, g), value in counts.items():
                if tt == t:
                    C[h, index[f], index[g]] = value / denominator
        assert np.max(np.abs(C-C.transpose(0, 2, 1))) == 0
        result.append({"roots": r, "type": t, "flags": flags, "C": C})
    return result


def marginal(big, small):
    n = len(small[0])
    lookup = {canonical_bits(code(A, tuple(range(n))), n): i
              for i, A in enumerate(small)}
    P = np.zeros((len(small), len(big)))
    for j, A in enumerate(big):
        for v in it.combinations(range(n+1), n):
            P[lookup[canonical_bits(code(A, v), n)], j] += 1/(n+1)
    assert np.allclose(P.sum(axis=0), 1, atol=1e-15)
    return P


def random_graph_distribution(graphs):
    n = len(graphs[0])
    probabilities = []
    for A in graphs:
        G = nx.from_numpy_array(A)
        aut = sum(1 for _ in nx.algorithms.isomorphism.GraphMatcher(G, G).isomorphisms_iter())
        probabilities.append(math.factorial(n)/aut / 2**math.comb(n, 2))
    return np.array(probabilities)


def check_random_graph(blocks, distribution, n):
    worst = 0
    for block in blocks:
        r = block["roots"]
        size = (n+r)//2
        flags = block["flags"]
        q = np.zeros(len(flags))
        lookup = {f: i for i, f in enumerate(flags)}
        # Separate oracle: enumerate Bernoulli edges of ONE rooted flag.
        for bits in range(2**math.comb(size, 2)):
            B = np.zeros((size, size), dtype=np.int8)
            for b, (i, j) in enumerate(pairs(size)):
                B[i, j] = B[j, i] = (bits >> b) & 1
            if code(B, tuple(range(r))) == block["type"]:
                q[lookup[canonical_bits(bits, size, r)]] += 1/2**(math.comb(size, 2)-math.comb(r, 2))
        expected = np.outer(q, q)/2**math.comb(r, 2)
        actual = np.einsum("g,gij->ij", distribution, block["C"])
        worst = max(worst, float(np.max(np.abs(actual-expected))))
    assert worst < 1e-14, worst
    return worst


def solve(label, objective_vector, base_blocks, extra_blocks=(), P=None, certificate=None):
    v = cp.Variable(len(objective_vector))
    old = v if P is None else P@v
    constraints = [v >= 0, cp.sum(v) == 1]
    matrices = []
    for blocks, variable in ((base_blocks, old), (extra_blocks, v)):
        for block in blocks:
            C = block["C"]
            d = C.shape[1]
            M = cp.reshape(C.reshape((len(C), d*d)).T@variable, (d, d), order="C")
            constraints.append(M >> 0)
            matrices.append((C, variable))
    problem = cp.Problem(cp.Minimize(objective_vector@v), constraints)
    started = time.monotonic()
    problem.solve(solver="CLARABEL", tol_gap_abs=1e-9, tol_feas=1e-9,
                  tol_gap_rel=1e-9, max_iter=150, time_limit=120)
    if v.value is None:
        raise RuntimeError((label, problem.status))
    min_eigenvalue = min(float(np.linalg.eigvalsh(np.einsum("g,gij->ij", var.value, C))[0])
                        for C, var in matrices)
    record = {"label": label, "status": problem.status, "objective": float(problem.value),
              "seconds": time.monotonic()-started, "variables": len(v.value),
              "PSD_blocks": len(matrices), "minimum_probability": float(v.value.min()),
              "normalization_error": abs(float(v.value.sum())-1),
              "minimum_gram_eigenvalue": min_eigenvalue,
              "primal": v.value.tolist()}
    if certificate is not None:
        certificate["Q"] = [np.array(c.dual_value) for c in constraints[2:]]
        certificate["C"] = ([b["C"] if P is None else np.einsum("hg,hij->gij", P, b["C"])
                             for b in base_blocks]+[b["C"] for b in extra_blocks])
    print(json.dumps({k: x for k, x in record.items() if k != "primal"}), flush=True)
    return record


if __name__ == "__main__":
    start = time.monotonic()
    out = Path("reports/global-coupled-pilot-001")
    out.mkdir(exist_ok=True, parents=True)
    g5, g6 = atlas(5), atlas(6)
    assert (len(g5), len(g6)) == (34, 156)
    c5, c6 = np.array(list(map(objective, g5))), np.array(list(map(objective, g6)))
    b5 = sum((gram_coefficients(g5, r) for r in (1, 3)), [])
    b6 = sum((gram_coefficients(g6, r) for r in (0, 2, 4)), [])
    P = marginal(g6, g5)
    assert np.max(np.abs(c5@P-c6)) < 1e-14
    p5, p6 = random_graph_distribution(g5), random_graph_distribution(g6)
    assert abs(p5.sum()-1) < 1e-14 and abs(p6.sum()-1) < 1e-14
    assert np.max(np.abs(P@p6-p5)) < 1e-14
    assert abs(c5@p5-1/32) < 1e-14 and abs(c6@p6-1/32) < 1e-14
    checks = {"N5_ER_gram_error": check_random_graph(b5, p5, 5),
              "N6_ER_gram_error": check_random_graph(b6, p6, 6),
              "K4_marginal_error": float(np.max(np.abs(c5@P-c6))),
              "generation_seconds": time.monotonic()-start}
    print(json.dumps(checks), flush=True)
    runs = []
    runs.append(solve("full_N5", c5, b5))
    runs.append(solve("N6_nonnegative_extension_only", c6, b5, P=P))
    runs.append(solve("N6_coupled_edge_root_blocks", c6, b5,
                      [b for b in b6 if b["roots"] == 2], P=P))
    runs.append(solve("full_N6_plus_N5", c6, b5, b6, P=P))
    np.savez_compressed(out/"coefficients.npz", P=P, c5=c5, c6=c6,
                        graphs5=np.array(g5), graphs6=np.array(g6),
                        **{f"N5_{i}": b["C"] for i, b in enumerate(b5)},
                        **{f"N6_{i}": b["C"] for i, b in enumerate(b6)})
    report = {"hypothesis": "H-GC1", "checks": checks, "runs": runs,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "versions": {"numpy": np.__version__, "networkx": nx.__version__, "cvxpy": cp.__version__},
              "seconds": time.monotonic()-start, "rigorous_certificate": False,
              "improved_published_bound": False}
    (out/"result.json").write_text(json.dumps(report, indent=2)+"\n")
