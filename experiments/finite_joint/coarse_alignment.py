"""Coarse relative alignment of deterministic quotient support blocks."""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import random
import shutil
import subprocess
import time

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


PARENT = ROOT / "reports/literature-two-parameter-001"
QUOTIENT = ROOT / "reports/pilot-algebraic-lift-003/quotient.json"
OUT = ROOT / "reports/finite-joint-coarse-alignment-001"


def components(matrix, q):
    n = len(matrix)
    adjacency = [{j for j in range(n) if j != i and 0 < matrix[i][j] < q}
                 for i in range(n)]
    unseen = set(range(n))
    answer = []
    while unseen:
        root = min(unseen)
        todo = [root]
        unseen.remove(root)
        comp = []
        while todo:
            i = todo.pop()
            comp.append(i)
            fresh = adjacency[i] & unseen
            unseen.difference_update(fresh)
            todo.extend(fresh)
        answer.append(sorted(comp))
    return sorted(answer, key=lambda c: c[0])


def matching_permutation(edges, component):
    comp = set(component)
    mate = {}
    for a, b in edges:
        if a in comp or b in comp:
            if not (a in comp and b in comp):
                raise ValueError("matching crosses a fractional component")
            if a in mate or b in mate:
                raise ValueError("edges are not a matching")
            mate[a], mate[b] = b, a
    if set(mate) != comp:
        raise ValueError("matching is not perfect on component")
    return mate


def compose(left, right):
    return {v: left[right[v]] for v in right}


def random_involution(component, rng):
    order = list(component)
    rng.shuffle(order)
    return {order[i]: order[i ^ 1] for i in range(len(order))}


def relative_align(matrix, component, permutation):
    comp = set(component)
    result = [row[:] for row in matrix]
    for b in component:
        for x in range(len(matrix)):
            if x not in comp:
                result[b][x] = result[x][b] = matrix[permutation[b]][x]
    return result


def relabel_control(matrix, component, permutation):
    order = list(range(len(matrix)))
    for b in component:
        order[b] = permutation[b]
    return [[matrix[order[i]][order[j]] for j in range(len(matrix))]
            for i in range(len(matrix))]


def count(counter, matrix, q):
    payload = f"{len(matrix)} {q}\n" + "\n".join(" ".join(map(str, row)) for row in matrix) + "\n"
    red, blue, total = map(int, subprocess.check_output(
        [str(counter)], input=payload, text=True, timeout=40).split())
    return red, blue, total


def tiny_signed_identity():
    rng = random.Random(9272026)
    checks = []
    positional_edges = tuple(combinations(range(4), 2))
    adjacent_pairs = sum(1 for a, b in combinations(positional_edges, 2)
                         if len(set(a + b)) == 3)
    disjoint_pairs = 15 - adjacent_pairs
    assert (adjacent_pairs, disjoint_pairs) == (12, 3)
    for n in range(1, 6):
        q = 11
        p = [[0] * n for _ in range(n)]
        for i in range(n):
            for j in range(i + 1):
                p[i][j] = p[j][i] = rng.randrange(q + 1)
        direct = even = 0
        for vs in product(range(n), repeat=4):
            values = [p[vs[a]][vs[b]] for a, b in positional_edges]
            red = blue = 1
            u = [2 * x - q for x in values]
            for x in values:
                red *= x
                blue *= q - x
            direct += red + blue
            subtotal = 0
            for mask in range(64):
                if mask.bit_count() % 2 == 0:
                    term = q ** (6 - mask.bit_count())
                    for e in range(6):
                        if mask >> e & 1:
                            term *= u[e]
                    subtotal += term
            even += subtotal // 32
        assert direct == even
        checks.append({"n": n, "direct": direct, "signed_even_expansion": even})
    return checks


def main():
    start = time.monotonic()
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    candidate = json.loads((PARENT / "graphon-candidate.json").read_text())
    matrix = candidate["red_probability_numerators"]
    q = candidate["edge_probability_denominator"]
    n = len(matrix)
    comps = components(matrix, q)
    if [len(c) for c in comps] != [64, 64, 64]:
        raise RuntimeError("expected three fractional components of order64")
    if any(matrix[i][j] not in (0, q) for c in comps for i in c
           for j in range(n) if j not in set(c)):
        raise RuntimeError("cross-component block is not deterministic")

    quotient = json.loads(QUOTIENT.read_text())
    defect = {tuple(sorted((i, j))) for i, j, *_ in quotient["complement_matching_blocks"]}
    h_value = min(x for row in matrix for x in row if 0 < x < q)
    p_value = max(x for row in matrix for x in row if 0 < x < q)
    h_edges = [(i, j) for i in range(n) for j in range(i) if matrix[i][j] == h_value]
    p_edges = {(i, j) for i in range(n) for j in range(i) if matrix[i][j] == p_value}
    m_edges = [edge for edge in p_edges if tuple(sorted(edge)) not in defect]
    if (len(defect), len(h_edges), len(m_edges)) != (1056, 96, 96):
        raise RuntimeError("unexpected structural edge counts")

    counter = PARENT / "ordered_counter"
    if not counter.exists():
        raise FileNotFoundError(counter)
    parent_red, parent_blue, parent_total = count(counter, matrix, q)
    records = []
    rng = random.Random(92731)
    proposals = []
    for ci, comp in enumerate(comps):
        h = matching_permutation(h_edges, comp)
        m = matching_permutation(m_edges, comp)
        for name, pi in (("H", h), ("M", m), ("H_after_M", compose(h, m)),
                         ("M_after_H", compose(m, h))):
            proposals.append(("structural", ci, name, comp, pi))
        proposals.append(("random_control", ci, "random_involution", comp,
                          random_involution(comp, rng)))

    # One exact isomorphism control exercises the same permutation machinery
    # while relabeling the internal component as well.
    _, ci, name, comp, pi = proposals[0]
    iso = relabel_control(matrix, comp, pi)
    iso_red, iso_blue, iso_total = count(counter, iso, q)
    if iso_total != parent_total:
        raise RuntimeError("isomorphism control changed the objective")

    best = (parent_total, matrix, {"family": "parent"}, parent_red, parent_blue)
    base_rows = [sum(row) for row in matrix]
    for family, ci, name, comp, pi in proposals:
        changed = relative_align(matrix, comp, pi)
        rows = [sum(row) for row in changed]
        red, blue, total = count(counter, changed, q)
        descriptor = {"family": family, "component": ci, "permutation": name,
                      "moved_vertices": sum(pi[v] != v for v in comp),
                      "changed_unordered_blocks": sum(
                          matrix[i][j] != changed[i][j] for i in range(n) for j in range(i)),
                      "row_sums_preserved": rows == base_rows,
                      "numerator": total, "delta": total - parent_total,
                      "red": red, "blue": blue,
                      "seconds": time.monotonic() - start}
        records.append(descriptor)
        if total < best[0]:
            best = (total, changed, descriptor, red, blue)

    best_total, best_matrix, best_descriptor, best_red, best_blue = best
    output = dict(candidate, red_probability_numerators=best_matrix)
    write_json(OUT / "graphon-candidate.json", output)
    candidate_hash = hashlib.sha256((OUT / "graphon-candidate.json").read_bytes()).hexdigest()
    denominator = n ** 4 * q ** 6
    report = {
        "hypothesis": "H-FJ-005",
        "parent": str(PARENT),
        "parent_sha256": hashlib.sha256((PARENT / "graphon-candidate.json").read_bytes()).hexdigest(),
        "parent_numerator": parent_total,
        "parent_density": str(Fraction(parent_total, denominator)),
        "best_descriptor": best_descriptor,
        "numerator": best_total,
        "denominator": denominator,
        "density": str(Fraction(best_total, denominator)),
        "decimal": float(Fraction(best_total, denominator)),
        "delta": best_total - parent_total,
        "red": best_red,
        "blue": best_blue,
        "records": records,
        "components": comps,
        "structural_counts": {"defect": len(defect), "H": len(h_edges), "M": len(m_edges)},
        "tiny_signed_identity": tiny_signed_identity(),
        "isomorphism_control": {"component": ci, "permutation": name,
                                "numerator": iso_total, "matches_parent": True},
        "candidate_sha256": candidate_hash,
        "counter_sha256": hashlib.sha256(counter.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "seconds": time.monotonic() - start,
        "evidence": "Exact existing C++128 direct ordered-index recount per candidate; no Lean recount of retained macro candidate",
        "scope": "Fixed p,h and 15 relative-alignment permutations; not arbitrary support optimization"
    }
    write_json(OUT / "report.json", report)
    print(json.dumps({k: report[k] for k in ("numerator", "density", "decimal", "delta", "best_descriptor", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
