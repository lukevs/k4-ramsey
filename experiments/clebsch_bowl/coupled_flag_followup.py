"""Ablations and rational dual rounding for the small coupled pilot."""
from fractions import Fraction as F
import json
from pathlib import Path
import time
import hashlib
import numpy as np
import coupled_flag_pilot as core


def exact_positive_definite(A):
    n = len(A)
    L = [[F(int(i == j)) for j in range(n)] for i in range(n)]
    D = []
    for j in range(n):
        pivot = F(int(A[j][j]))-sum(L[j][k]**2*D[k] for k in range(j))
        if pivot <= 0:
            return False
        D.append(pivot)
        for i in range(j+1, n):
            L[i][j] = (F(int(A[i][j]))-sum(L[i][k]*L[j][k]*D[k] for k in range(j)))/pivot
    return True


def certify(c, data, output):
    scale, denominator = 10**10, 720
    c_int = np.rint(c*denominator).astype(np.int64)
    assert np.max(np.abs(c_int/denominator-c)) < 1e-14
    penalties = [0]*len(c)
    blocks = []
    for Q, C in zip(data["Q"], data["C"]):
        R = np.rint((Q+Q.T)/2*scale).astype(np.int64)
        shift = max(1, int(np.ceil(-np.linalg.eigvalsh(R.astype(float))[0]))+2)
        while True:
            S = R+shift*np.eye(len(R), dtype=np.int64)
            if exact_positive_definite(S):
                break
            shift *= 2
        C_int = np.rint(C*denominator).astype(np.int64)
        assert np.max(np.abs(C_int/denominator-C)) < 1e-14
        for g in range(len(c)):
            penalties[g] += sum(int(S[i,j])*int(C_int[g,i,j])
                                for i in range(len(S)) for j in range(len(S)))
        blocks.append({"Q_integer": S.tolist(), "C_integer": C_int.tolist(),
                       "diagonal_shift_integer": shift})
    slacks = [int(c_int[g])*scale-penalties[g] for g in range(len(c))]
    lower = F(min(slacks), scale*denominator)
    result = {"Q_denominator": scale, "C_denominator": denominator,
              "objective_numerators": c_int.tolist(), "blocks": blocks,
              "bound": str(lower), "bound_decimal": float(lower),
              "minimum_slack_graph_index": int(np.argmin(slacks)),
              "scope": "Universal asymptotic K4 bound, conditional on coefficient tensors; check separately."}
    output.write_text(json.dumps(result)+"\n")
    return {"bound": str(lower), "bound_decimal": float(lower),
            "blocks": len(blocks), "certificate": str(output)}


if __name__ == "__main__":
    start = time.monotonic()
    out = Path("reports/global-coupled-pilot-002")
    out.mkdir(exist_ok=True, parents=True)
    g5, g6 = core.atlas(5), core.atlas(6)
    b5 = sum((core.gram_coefficients(g5, r) for r in (1,3)), [])
    b6 = sum((core.gram_coefficients(g6, r) for r in (0,2,4)), [])
    P = core.marginal(g6, g5)
    c = np.array(list(map(core.objective, g6)))
    groups = {}
    for b in b6:
        if b["roots"] == 4:
            t = b["type"]
            pair = tuple(sorted({t, core.canonical_bits(t^63,4)}))
            groups.setdefault(pair, []).append(b)
    runs = []
    for pair, blocks in groups.items():
        runs.append(core.solve("four_root_types_"+str(pair), c, b5, blocks, P=P))
    best_index = int(np.argmax([r["objective"] for r in runs]))
    best_pair = list(groups)[best_index]
    data = {}
    best = core.solve("best_sparse_for_certificate", c, b5, groups[best_pair], P=P, certificate=data)
    cert = certify(c, data, out/"sparse-certificate.json")
    # Save the exact block identity, enabling a separate coefficient checker.
    meta = {"base": [{k:b[k] for k in ("roots","type","flags")} for b in b5],
            "extra": [{k:b[k] for k in ("roots","type","flags")} for b in groups[best_pair]],
            "graphs6": np.array(g6).tolist()}
    (out/"coefficient-metadata.json").write_text(json.dumps(meta)+"\n")
    report = {"runs": runs, "selected_root_types": best_pair, "certificate": cert,
              "seconds": time.monotonic()-start,
              "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (out/"result.json").write_text(json.dumps(report, indent=2)+"\n")
    print(json.dumps(cert), flush=True)
