"""Scale cross-check: principal submatrices of E5 candidates (whole fibres kept), counted
(a) via discovered Z2^k character expansion and (b) with the fibre structure ignored (k=0,
plain mixed-K4 engine on the full submatrix).  Exact equality required."""
import json, sys, time
import numpy as np
import zk_checker as z

out = {}
for name, path, m in (("depth1", "reports/round4-E5-depth1-001/graphon-candidate.json", 480),
                      ("depth2", "reports/round4-E5-depth2-001/graphon-candidate.json", 960)):
    d = json.load(open(path))
    Q = d["edge_probability_denominator"]
    W = np.array(d["red_probability_numerators"], dtype=np.int64)[:m, :m]
    res = {}
    for label, M in (("red", W), ("blue", Q - W)):
        t = time.time()
        basis, k = z.discover_group(M)
        _, n, F, _, _, mism = z.fourier_blocks(M, basis)
        assert mism == 0
        Dk, _ = z.exact_count(F, k)
        t1 = time.time() - t
        t = time.time()
        D0, _ = z.exact_count(M[None, :, :].astype(np.int64), 0)
        t2 = time.time() - t
        res[label] = {"k": k, "basis": basis, "n_base": n, "character": str(Dk), "plain": str(D0),
                      "match": Dk == D0, "t_char": t1, "t_plain": t2}
        print(name, label, res[label], flush=True)
    out[name] = {"path": path, "submatrix_order": m, **res}
json.dump(out, open(sys.argv[1], "w"), indent=1)
