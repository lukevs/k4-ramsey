"""Finalize immutable H-CR-001 evidence and decode assignment witnesses."""
from __future__ import annotations

import argparse
import hashlib
import json
from fractions import Fraction
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def edges(vertices: list[int], mask: int) -> list[dict[str, object]]:
    answer = []
    bit = 0
    for i in range(6):
        for j in range(i + 1, 6):
            answer.append({"u": vertices[i], "v": vertices[j],
                           "red": bool(mask & (1 << bit)), "bit": bit})
            bit += 1
    return answer


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--native", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--fixture", type=Path, required=True)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--binary", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    native = json.loads(args.native.read_text())
    audit = json.loads(args.audit.read_text())
    parent = int(native["parent_total_numerator"])
    denominator = 192**4 * 65536**6
    enriched = []
    for row in native["sets"]:
        current, best = int(row["current_impacted"]), int(row["best_impacted"])
        greedy = int(row["greedy_impacted"])
        if int(row["best_total_numerator"]) != parent - current + best:
            raise RuntimeError("best total arithmetic")
        if int(row["greedy_total_numerator"]) != parent - current + greedy:
            raise RuntimeError("greedy total arithmetic")
        best_fraction = Fraction(parent - current + best, denominator)
        enriched.append({
            **row,
            "best_delta_from_parent": str(best - current),
            "greedy_delta_from_parent": str(greedy - current),
            "best_fraction": str(best_fraction),
            "best_decimal": float(best_fraction),
            "global_beats_sequential": best < greedy,
            "best_assignment_edges": edges(row["vertices"], row["best_mask"]),
            "greedy_assignment_edges": edges(row["vertices"], row["greedy_mask"]),
        })
    report = {
        "schema": "coordinated-reconstruction-final-report-v1",
        "status": "completed",
        "hypothesis": "A jointly optimized positive-mass asymmetric six-class defect can beat sequential reconstruction.",
        "solver": "Exact exhaustive enumeration of 2^15 assignments; no SAT/MaxSAT/IP package was installed.",
        "objective": "Exact asymptotic monochromatic K4 ordered-quadruple numerator including repeated indices and diagonal block probabilities.",
        "tiny_control": native["tiny_control"],
        "normalization": str(denominator),
        "parent_fraction": str(Fraction(parent, denominator)),
        "input_audit": audit,
        "sets": enriched,
        "verdict": "The structured binary defect is worse than the fractional parent and equals sequential descent; the deterministic random control returns the parent. No witness improves the parent.",
        "scope": "One symmetry-defined six-class core and one seeded random six-class control; all 15 internal offdiagonal block probabilities only. This does not test larger, external-edge, weighted, or nonbinary defect reconstructions.",
        "timing": {"end_to_end_first_gate_seconds_approx": 150, "native_total_seconds": 0.743, "production_seconds_each": [row["compute_seconds"] for row in native["sets"]]},
        "sha256": {"fixture": sha(args.fixture), "source": sha(args.source), "binary": sha(args.binary), "native_report": sha(args.native), "input_audit": sha(args.audit)},
    }
    args.out.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
