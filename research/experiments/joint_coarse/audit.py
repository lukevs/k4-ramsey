"""Independent generic ordered-index recount for the joint-coarse candidate."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[3]
CANDIDATE_DIR = ROOT / "reports/joint-coarse-001"
CHECKER_DIR = ROOT / "reports/association-scheme-phase-001"
OUT = ROOT / "reports/joint-coarse-audit-001"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    candidate_path = CANDIDATE_DIR / "graphon-candidate.json"
    prediction = json.loads((CANDIDATE_DIR / "report.json").read_text())
    candidate = json.loads(candidate_path.read_text())
    matrix = candidate["red_probability_numerators"]
    denominator = candidate["edge_probability_denominator"]
    order = len(matrix)
    assert order == 960 and denominator == 65536
    assert sha256(candidate_path) == prediction["candidate_sha256"]
    assert all(len(row) == order for row in matrix)
    assert all(0 <= value <= denominator for row in matrix for value in row)
    assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))

    OUT.mkdir(parents=True, exist_ok=False)
    checker = OUT / "ordered_graphon_u256"
    checker_source = OUT / "checker_snapshot.cpp"
    shutil.copy2(CHECKER_DIR / "ordered_graphon_u256", checker)
    shutil.copy2(CHECKER_DIR / "checker_snapshot.cpp", checker_source)
    payload = f"{order} {denominator}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix
    ) + "\n"
    recount_started = time.monotonic()
    red, blue, total = map(
        int,
        subprocess.check_output(
            [str(checker)], input=payload, text=True, timeout=180
        ).split(),
    )
    recount_seconds = time.monotonic() - recount_started
    normalization = order**4 * denominator**6
    assert total == prediction["numerator"]
    assert normalization == prediction["normalization"]
    density = Fraction(total, normalization)
    assert density == Fraction(prediction["density"])
    report = {
        "status": "independent_generic_ordered_recount_passed",
        "candidate": str(candidate_path.relative_to(ROOT)),
        "candidate_sha256": sha256(candidate_path),
        "checker_source_sha256": sha256(checker_source),
        "checker_binary_sha256": sha256(checker),
        "red": red,
        "blue": blue,
        "numerator": total,
        "normalization": normalization,
        "density": str(density),
        "decimal": float(density),
        "recount_seconds": recount_seconds,
        "total_seconds": time.monotonic() - started,
        "evidence": "Independent generic C++ U256 ordered-index recount of the serialized 960-class matrix; no search-model coefficients used",
        "limitations": "No Lean/kernel-only proof and no global p,h or graphon optimum claim",
    }
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, sort_keys=True))


if __name__ == "__main__":
    main()
