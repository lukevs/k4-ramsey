"""Exact deterministic Seidel-cut screen on the current 192 coarse marginal."""

from collections import deque
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import subprocess
import time

from research.experiments.compressed_graphon.polynomial import ExactPolynomial, interpolate_integer_polynomial


ROOT = Path(__file__).resolve().parents[3]
PARENT = ROOT / "reports/joint-coarse-boundary-face-001/graphon-candidate.json"
QUOTIENT = ROOT / "reports/pilot-algebraic-lift-001/quotient.json"
CHECKER = ROOT / "reports/association-scheme-phase-001/ordered_graphon_u256"
OUT = ROOT / "reports/latent-precision-seidel-switch-001"
Q = 65536


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def raw(matrix, denominator=Q):
    payload = f"{len(matrix)} {denominator}\n" + "\n".join(" ".join(map(str, row)) for row in matrix) + "\n"
    return int(subprocess.check_output([str(CHECKER)], input=payload, text=True, timeout=30).split()[2])


def switch(matrix, cut, denominator=Q):
    chosen = set(cut)
    return [[denominator - value if (i in chosen) != (j in chosen) else value
             for j, value in enumerate(row)] for i, row in enumerate(matrix)]


def literal(matrix, denominator):
    n = len(matrix)
    total = 0
    for a in range(n):
        for b in range(n):
            for c in range(n):
                for d in range(n):
                    labels = (a, b, c, d)
                    red = blue = 1
                    for i, j in ((0,1),(0,2),(0,3),(1,2),(1,3),(2,3)):
                        p = matrix[labels[i]][labels[j]]
                        red *= p
                        blue *= denominator - p
                    total += red + blue
    return total


def components(adjacency):
    unseen = set(range(len(adjacency)))
    answer = []
    while unseen:
        root = min(unseen); unseen.remove(root); todo = deque([root]); cell = []
        while todo:
            u = todo.popleft(); cell.append(u)
            for v in adjacency[u]:
                if v in unseen: unseen.remove(v); todo.append(v)
        answer.append(sorted(cell))
    return sorted(answer, key=lambda x: (len(x), x))


def main():
    started = time.monotonic()
    fine = json.loads(PARENT.read_text())["red_probability_numerators"]
    assert len(fine) == 960
    base = []
    for i in range(192):
        row = []
        for j in range(192):
            block_sum = sum(fine[5*i+a][5*j+b] for a in range(5) for b in range(5))
            assert block_sum % 25 == 0
            row.append(block_sum // 25)
        base.append(row)
    quotient = json.loads(QUOTIENT.read_text())
    defect = [set() for _ in range(192)]
    halves = []
    for i, j, _ in quotient["complement_matching_blocks"]:
        defect[i].add(j); defect[j].add(i)
    for i in range(192):
        for j in range(i):
            block = fine[5*i:5*i+5]
            # The quotient's 96 half edges are recovered from its own exact list below.
    # The lift quotient is immutable and explicitly stores the matching in the phase-3 copy.
    phase3 = json.loads((ROOT / "reports/pilot-algebraic-lift-003/quotient.json").read_text())
    halves = [(i, j) for i, j, _ in phase3["half_blocks"]]
    cells = components(defect)
    assert [len(c) for c in cells] == [64, 64, 64] and len(halves) == 96
    matching_side = {min(i, j) for i, j in halves}

    tiny = [[0,3,7,2],[3,0,5,9],[7,5,0,4],[2,9,4,0]]
    tiny_cut = {0,2}
    tiny_switched = switch(tiny, tiny_cut, 11)
    tiny_check = {"before": literal(tiny,11), "after": literal(tiny_switched,11)}
    assert switch(tiny_switched,tiny_cut,11) == tiny
    assert raw(tiny,11) == tiny_check["before"]
    assert raw(tiny_switched,11) == tiny_check["after"]

    baseline = raw(base)
    cuts = [(f"defect_component_{i}", set(cell)) for i, cell in enumerate(cells)]
    cuts.append(("half_matching_lower_index_side", matching_side))
    records = []
    best = (baseline, "empty", set())
    for name, cut in cuts:
        value = raw(switch(base, cut))
        records.append({"name": name, "size": len(cut), "raw": value, "delta": value-baseline})
        if value < best[0]: best = (value, name, cut)

    # One exact best-improvement coarse-vertex pass from the best structural cut.
    greedy_start = best
    candidates = []
    for vertex in range(192):
        cut = set(greedy_start[2]); cut.symmetric_difference_update({vertex})
        value = raw(switch(base, cut))
        candidates.append((value, vertex, cut))
    value, vertex, cut = min(candidates, key=lambda x: x[0])
    greedy = {"start": greedy_start[1], "flipped_vertex": vertex, "raw": value,
              "delta_from_baseline": value-baseline, "delta_from_start": value-greedy_start[0]}
    if value < best[0]: best = (value, f"{greedy_start[1]}+flip_{vertex}", cut)

    line = None
    if best[0] < baseline:
        switched = switch(base, best[2])
        points = []
        denominator = Q * Q
        for t in range(7):
            matrix = [[Q*base[i][j] + t*(switched[i][j]-base[i][j]) for j in range(192)] for i in range(192)]
            points.append((t, raw(matrix, denominator)))
        coefficients = interpolate_integer_polynomial(points, max_degree=6, degree_bound_proven=True)
        normalization = 192**4 * denominator**6
        polynomial = ExactPolynomial.from_total_coefficients(coefficients, normalization,
            feasible_integer_interval=(0,Q), base_order=192, latent_order=1,
            probability_denominator=denominator)
        minimum = polynomial.minimize_integer()
        t = minimum.minimizers[0]
        matrix = [[Q*base[i][j] + t*(switched[i][j]-base[i][j]) for j in range(192)] for i in range(192)]
        assert raw(matrix, denominator) == minimum.value
        line = {"coefficients_low_to_high": list(coefficients), "selected_t": t,
                "raw": minimum.value, "normalization": normalization,
                "density": str(Fraction(minimum.value, normalization)),
                "decimal": float(Fraction(minimum.value, normalization))}

    OUT.mkdir(parents=True, exist_ok=False)
    report = {"schema":"coarse-seidel-switch-v1", "status":"screen_complete",
        "hypothesis":"Deterministic Seidel switching of the current 192 coarse marginal exposes a noncentered structural direction",
        "parent":str(PARENT.relative_to(ROOT)), "parent_sha256":sha256(PARENT),
        "coarse_baseline_raw":baseline, "coarse_normalization":192**4*Q**6,
        "coarse_baseline_density":str(Fraction(baseline,192**4*Q**6)),
        "cuts":records, "greedy_one_vertex_pass":greedy,
        "best_endpoint":{"name":best[1],"size":len(best[2]),"raw":best[0],"delta":best[0]-baseline},
        "convex_line":line, "tiny_exact_oracle":tiny_check,
        "seconds":time.monotonic()-started,
        "decision":"advance" if line is not None else "retire tested cuts: no negative exact endpoint signal",
        "scope":"Four intrinsic cuts and one exact best-improvement vertex pass; not all Seidel cuts. Screen is on the verified candidate's 192 coarse marginal, without its fine phase kernel."}
    (OUT/"report.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("decision","best_endpoint","convex_line","seconds")},sort_keys=True))


if __name__ == "__main__": main()
