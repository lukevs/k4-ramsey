"""Independent stdlib-only certificate check; no optimizer or search imports.

Rebuild coefficients by averaging all 720 vertex orderings. Verify coverage
of all 32768 labelled six-vertex graphs by relabelling the supplied list.
"""
from fractions import Fraction as F
from itertools import permutations, combinations
from functools import lru_cache
from pathlib import Path
import json
import hashlib
import time
import sys


def edge_pairs(n):
    return list(combinations(range(n), 2))


def read_bits(bits, n, order):
    lookup = {pair:b for b,pair in enumerate(edge_pairs(n))}
    ans = 0
    for new_bit, (i,j) in enumerate(edge_pairs(len(order))):
        old_pair = tuple(sorted((order[i],order[j])))
        ans |= ((bits >> lookup[old_pair]) & 1) << new_bit
    return ans


@lru_cache(None)
def rooted_representative(bits, n, r):
    return min(read_bits(bits,n,tuple(range(r))+tail)
               for tail in permutations(range(r,n)))


def exact_ldl(A):
    n = len(A)
    L = [[F(i == j) for j in range(n)] for i in range(n)]
    pivots = []
    for j in range(n):
        pivot = F(A[j][j])-sum(L[j][k]**2*pivots[k] for k in range(j))
        assert pivot > 0, (j,pivot)
        pivots.append(pivot)
        for i in range(j+1,n):
            L[i][j] = (F(A[i][j])-sum(L[i][k]*L[j][k]*pivots[k] for k in range(j)))/pivot
    return min(pivots)


if __name__ == "__main__":
    start = time.monotonic()
    folder = Path(sys.argv[1]) if len(sys.argv)>1 else Path("reports/global-coupled-pilot-003")
    cert_path = folder/"full-certificate.json"
    cert = json.loads(cert_path.read_text())
    meta = json.loads((folder/"coefficient-metadata.json").read_text())
    specs = [(5,b) for b in meta["base"]]+[(6,b) for b in meta["extra"]]
    assert len(specs) == len(cert["blocks"])
    groups = {}
    for index,(n,b) in enumerate(specs):
        groups.setdefault((n,b["roots"]),{})[b["type"]] = (index,{f:i for i,f in enumerate(b["flags"])})
    @lru_cache(None)
    def contributions(bits):
        entries = []
        for (n,r),mapping in groups.items():
            t = read_bits(bits,6,tuple(range(r)))
            if t not in mapping:
                continue
            k = (n-r)//2
            index,flags = mapping[t]
            left = tuple(range(r+k))
            right = tuple(range(r))+tuple(range(r+k,r+2*k))
            a = rooted_representative(read_bits(bits,6,left),r+k,r)
            b = rooted_representative(read_bits(bits,6,right),r+k,r)
            entries.append((index,flags[a],flags[b]))
        return entries
    orders = list(permutations(range(6)))
    transforms = []
    lookup = {p:i for i,p in enumerate(edge_pairs(6))}
    for order in orders:
        transforms.append([lookup[tuple(sorted((order[i],order[j])))] for i,j in edge_pairs(6)])
    covered = set()
    numerators = []
    assert cert["C_denominator"] == 720
    for g,A in enumerate(meta["graphs6"]):
        assert len(A) == 6 and all(A[i][i] == 0 for i in range(6))
        assert all(A[i][j] in (0,1) and A[i][j] == A[j][i] for i,j in edge_pairs(6))
        bits = sum(A[i][j]<<b for b,(i,j) in enumerate(edge_pairs(6)))
        counts = [[[0 for _ in b["flags"]] for _ in b["flags"]] for _,b in specs]
        orbit = set()
        for transform in transforms:
            permuted = sum(((bits>>old)&1)<<new for new,old in enumerate(transform))
            orbit.add(permuted)
            for index,i,j in contributions(permuted):
                counts[index][i][j] += 1
        assert not orbit.intersection(covered), "Duplicate isomorphism class"
        covered.update(orbit)
        mono = sum(read_bits(bits,6,v) in (0,63) for v in combinations(range(6),4))
        c_int = mono*48  # 720 / choose(6,4).
        assert c_int == cert["objective_numerators"][g]
        penalty = 0
        for b,count in zip(cert["blocks"],counts):
            assert count == b["C_integer"][g], (g,"coefficient mismatch")
            Q = b["Q_integer"]
            penalty += sum(Q[i][j]*count[i][j] for i in range(len(Q)) for j in range(len(Q)))
        numerators.append(c_int*cert["Q_denominator"]-penalty)
    assert covered == set(range(2**15))
    for block in cert["blocks"]:
        Q = block["Q_integer"]
        assert all(Q[i][j] == Q[j][i] for i in range(len(Q)) for j in range(len(Q)))
        exact_ldl(Q)
    bound = F(min(numerators),720*cert["Q_denominator"])
    assert bound == F(cert["bound"])
    witness_path = folder/"baseline-feasible-witness.json"
    baseline = None
    if witness_path.exists():
        witness = json.loads(witness_path.read_text())
        z = witness["probability_numerators"]
        denominator = witness["denominator"]
        assert len(z) == len(meta["graphs6"]) and min(z) >= 0 and sum(z) == denominator
        for block in cert["blocks"][:len(meta["base"])]:
            C = block["C_integer"]
            d = len(C[0])
            M = [[sum(z[g]*C[g][i][j] for g in range(len(z))) for j in range(d)] for i in range(d)]
            exact_ldl(M)
        baseline = F(sum(z[g]*cert["objective_numerators"][g] for g in range(len(z))),720*denominator)
        assert baseline < bound
    result = {"bound":str(bound),"bound_decimal":float(bound),
              "labelled_graphs_covered":len(covered),"isomorphism_classes":len(meta["graphs6"]),
              "exact_coefficient_blocks_checked":len(specs),"all_Q_exact_positive_definite":True,
              "all_coefficient_slacks_nonnegative":True,
              "old_level_feasible_objective":str(baseline) if baseline is not None else None,
              "strict_strengthening_exactly_checked":baseline is not None,
              "seconds":time.monotonic()-start,
              "certificate_sha256":hashlib.sha256(cert_path.read_bytes()).hexdigest(),
              "checker_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "scope":"Exact finite coefficient identity and PSD; asymptotic flag-square argument in research note."}
    receipt = "independent-check-with-baseline.json" if baseline is not None else "independent-check.json"
    (folder/receipt).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result,indent=2))
