"""Read-only exact structure probe for the fixed final Lean witness."""
import hashlib
import json
from pathlib import Path
import time

import numpy as np


def main():
    start = time.monotonic()
    path = Path("reports/round4-E5-depth2-001/graphon-candidate.json")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    assert digest == "05302cbc635e939cc41f4ba019cdcba80199b0b83563100bac0b1a0d9fff1a29"
    data = json.loads(raw)
    q = data["edge_probability_denominator"]
    a = np.array(data["red_probability_numerators"], dtype=np.int64)
    assert a.shape == (3840, 3840)
    assert data["block_weights"] == [1] * 3840
    blocks = a.reshape(192, 20, 192, 20).transpose(0, 2, 1, 3)
    row_sums = blocks.sum(axis=3)
    assert np.all(row_sums == row_sums[:, :, :1])
    assert np.all(row_sums % 20 == 0)
    base = row_sums[:, :, 0] // 20
    d = blocks - base[:, :, None, None]
    support = np.any(d != 0, axis=(2, 3)).astype(np.int64)
    paths = support @ support
    report = {
        "hypothesis": "LF1", "candidate_sha256": digest,
        "Q": q, "block_means": np.unique(base).tolist(),
        "symmetric": bool(np.array_equal(a, a.T)),
        "in_probability_range": bool(a.min() >= 0 and a.max() <= q),
        "zero_row_means": bool(np.all(d.sum(axis=3) == 0)),
        "zero_column_means": bool(np.all(d.sum(axis=2) == 0)),
        "support_degrees": np.unique(support.sum(axis=1), return_counts=True)[0].tolist(),
        "support_edges": int(support.sum() // 2),
        "triangle_orderings": int((paths * support).sum()),
        "cycle4_orderings_with_repeats": int((paths * paths).sum()),
        "diamond_orderings_with_repeats": int((paths * paths * support).sum()),
        "k4_orderings": sum(int(support[np.ix_(np.flatnonzero(support[i] * support[j]),
                                                np.flatnonzero(support[i] * support[j]))].sum())
                            for i in range(192) for j in np.flatnonzero(support[i])),
        "centered_nonzero_entries": int(np.count_nonzero(d)),
        "elapsed_seconds": time.monotonic() - start,
        "decision": "pursue exact centered-block contraction"}
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
