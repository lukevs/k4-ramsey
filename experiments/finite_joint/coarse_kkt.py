"""Box-KKT diagnostic on the retained 192-class two-parameter graphon."""
import collections
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


def main():
    start = time.monotonic()
    out = ROOT / "reports/finite-joint-coarse-kkt-001"
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, out / "source_snapshot.py")
    parent = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
    data = json.loads(parent.read_text())
    q = data["edge_probability_denominator"]
    matrix = data["red_probability_numerators"]
    n = len(matrix)
    binary = ROOT / "reports/literature-graphon-gradient-001/gradient"
    payload = str(n) + "\n" + "\n".join(
        " ".join(str(x / q) for x in row) for row in matrix) + "\n"
    text = subprocess.check_output([str(binary)], input=payload, text=True, timeout=30)
    records = []
    groups = collections.defaultdict(list)
    violations = []
    fractional_nonzero = []
    for line in text.splitlines():
        i, j, gradient = line.split()
        i, j, gradient = int(i), int(j), float(gradient)
        if i == j:
            continue
        value = matrix[i][j]
        record = {"i": i, "j": j, "numerator": value,
                  "probability": value / q, "gradient": gradient}
        records.append(record)
        groups[(value, round(gradient, 8))].append((i, j))
        if (value == 0 and gradient < -1e-8) or (value == q and gradient > 1e-8):
            violations.append(record)
        if 0 < value < q and abs(gradient) > 1e-8:
            fractional_nonzero.append(record)
    summary = [{"numerator": value, "gradient": gradient, "count": len(edges),
                "sample_edges": edges[:5]}
               for (value, gradient), edges in sorted(groups.items())]
    report = {
        "hypothesis": "H-FJ-006-box-KKT",
        "parent": str(parent),
        "parent_sha256": hashlib.sha256(parent.read_bytes()).hexdigest(),
        "n": n,
        "denominator": q,
        "offdiagonal_coordinates": len(records),
        "boundary_violations": len(violations),
        "fractional_nonstationary": len(fractional_nonzero),
        "groups": summary,
        "strongest_boundary_violations": sorted(violations, key=lambda r: -abs(r["gradient"]))[:50],
        "strongest_fractional_gradients": sorted(fractional_nonzero, key=lambda r: -abs(r["gradient"]))[:50],
        "seconds": time.monotonic() - start,
        "evidence": "Double-precision analytic derivative diagnostic on the exact rational parent; proposal guide only",
        "gradient_binary_sha256": hashlib.sha256(binary.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    }
    write_json(out / "gradients.json", records)
    write_json(out / "report.json", report)
    print(json.dumps({k: report[k] for k in ("boundary_violations", "fractional_nonstationary", "groups", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
