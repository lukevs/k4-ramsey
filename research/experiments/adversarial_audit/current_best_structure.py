"""Standalone structural audit of the frozen two-amplitude r=5 graphon.

This intentionally reads no optimization report and no claimed score.  It
reconstructs the serialized candidate from the independently frozen coarse
matrix, phase assignment, cyclic kernel, and amplitude.
"""

from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import time


ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
PHASES = ROOT / "reports/association-scheme-phase-two-amplitude-001/phase-assignment.json"
CANDIDATE = ROOT / "reports/association-scheme-phase-two-amplitude-001/graphon-candidate.json"
OUT = ROOT / "reports/current-best-structure-audit-001"

BASE_SHA256 = "e26e754168010c069da3e0b207a140f2c7cbbfc36cc0a6af06ef409db5024450"
PHASE_SHA256 = "226ab819da150c12b8152e2ac6a10acaf7d5dcff716199c42d8d42c68790011e"
CANDIDATE_SHA256 = "33df1d72c6e50a2ea0dc205f771ab8d3372b621b273cc53237072017ad4dda4d"
R = 5
Q = 65536
AMPLITUDES = {51064: -7236, 35015: -11671}


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kernel(x: int) -> int:
    return 3 if x % R in (1, 4) else -2


def main() -> None:
    started = time.monotonic()
    assert digest(BASE) == BASE_SHA256
    assert digest(PHASES) == PHASE_SHA256
    assert digest(CANDIDATE) == CANDIDATE_SHA256
    base_record = json.loads(BASE.read_text())
    candidate = json.loads(CANDIDATE.read_text())
    phases = {
        tuple(map(int, key.split(","))): int(value)
        for key, value in json.loads(PHASES.read_text()).items()
    }
    base = base_record["red_probability_numerators"]
    matrix = candidate["red_probability_numerators"]
    n = len(base)
    order = R * n
    assert n == 192 and order == 960
    assert base_record["edge_probability_denominator"] == Q
    assert candidate["schema"] == "rational-step-graphon-v1"
    assert candidate["edge_probability_denominator"] == Q
    assert candidate["block_weights"] == [1] * order
    assert len(matrix) == order and all(len(row) == order for row in matrix)

    fractional_edges = {
        (i, j)
        for i in range(n)
        for j in range(i + 1, n)
        if 0 < base[i][j] < Q
    }
    assert set(phases) == fractional_edges
    assert set(phases.values()) <= {-1, 0, 1, 2, 3, 4}

    mismatch_examples = []
    symmetry_failures = 0
    range_failures = 0
    diagonal_failures = 0
    value_counts: Counter[int] = Counter()
    for ia, row in enumerate(matrix):
        i, a = divmod(ia, R)
        for jb, value in enumerate(row):
            j, b = divmod(jb, R)
            if i != j and 0 < base[i][j] < Q:
                edge = (i, j) if i < j else (j, i)
                state = phases[edge]
            else:
                state = -1
            expected = base[i][j]
            if state >= 0:
                oriented = state if i < j else -state
                expected += AMPLITUDES[base[i][j]] * kernel(a - b - oriented)
            if value != expected and len(mismatch_examples) < 10:
                mismatch_examples.append([ia, jb, value, expected])
            symmetry_failures += value != matrix[jb][ia]
            range_failures += not 0 <= value <= Q
            diagonal_failures += ia == jb and value != 0
            value_counts[value] += 1
    assert not mismatch_examples
    assert symmetry_failures == range_failures == diagonal_failures == 0

    marginal_failures = []
    for i in range(n):
        for j in range(n):
            block_sum = sum(
                matrix[R * i + a][R * j + b]
                for a in range(R)
                for b in range(R)
            )
            expected = R * R * base[i][j]
            if block_sum != expected and len(marginal_failures) < 10:
                marginal_failures.append([i, j, block_sum, expected])
    assert not marginal_failures

    active_by_parent_value: Counter[int] = Counter()
    for edge, state in phases.items():
        if state >= 0:
            i, j = edge
            active_by_parent_value[base[i][j]] += 1
    active_values = sorted(active_by_parent_value)
    feasible_intervals = {}
    boundary_witnesses = []
    expected_intervals = {51064: (-7236, 4824), 35015: (-11671, 10173)}
    for value in active_values:
        feasible = [
            q
            for q in range(-Q, Q + 1)
            if 0 <= value - 2 * q <= Q and 0 <= value + 3 * q <= Q
        ]
        interval = (min(feasible), max(feasible))
        assert interval == expected_intervals[value]
        assert AMPLITUDES[value] == interval[0]
        witness = {
            "parent_probability": value,
            "selected_q": AMPLITUDES[value],
            "selected_fine_values": [
                value - 2 * AMPLITUDES[value],
                value + 3 * AMPLITUDES[value],
            ],
            "q_minus_one_fine_values": [
                value - 2 * (AMPLITUDES[value] - 1),
                value + 3 * (AMPLITUDES[value] - 1),
            ],
        }
        assert all(0 <= x <= Q for x in witness["selected_fine_values"])
        assert any(not 0 <= x <= Q for x in witness["q_minus_one_fine_values"])
        feasible_intervals[str(value)] = list(interval)
        boundary_witnesses.append(witness)

    report = {
        "schema": "current-best-structural-audit-v1",
        "status": "passed",
        "finished_at": datetime.now(timezone.utc).isoformat(),
        "candidate_sha256": digest(CANDIDATE),
        "base_sha256": digest(BASE),
        "phase_assignment_sha256": digest(PHASES),
        "construction": {
            "base_order": n,
            "fine_order": order,
            "types": R,
            "denominator": Q,
            "amplitudes_by_parent_probability": {
                str(k): v for k, v in sorted(AMPLITUDES.items())
            },
            "fractional_coarse_edges": len(fractional_edges),
            "active_edges": sum(state >= 0 for state in phases.values()),
            "inactive_edges": sum(state < 0 for state in phases.values()),
            "phase_histogram": {str(s): list(phases.values()).count(s) for s in range(-1, R)},
        },
        "checks": {
            "all_candidate_entries_reconstructed": True,
            "entries_checked": order * order,
            "mismatch_examples": mismatch_examples,
            "symmetry_failures": symmetry_failures,
            "range_failures": range_failures,
            "diagonal_failures": diagonal_failures,
            "all_coarse_marginals_checked": True,
            "coarse_blocks_checked": n * n,
            "marginal_failures": marginal_failures,
            "kernel_values": [kernel(x) for x in range(R)],
            "kernel_sum": sum(kernel(x) for x in range(R)),
            "candidate_value_counts": {str(k): v for k, v in sorted(value_counts.items())},
            "active_edges_by_parent_probability": {
                str(k): v for k, v in sorted(active_by_parent_value.items())
            },
            "exact_feasible_amplitude_intervals": feasible_intervals,
            "selected_amplitudes_are_lower_boundaries": True,
            "boundary_witnesses": boundary_witnesses,
            "normalization": order**4 * Q**6,
        },
        "evidence_scope": (
            "Independent structural reconstruction from frozen base, phases, kernel, and amplitude; "
            "reads no optimization report or supplied score and does not recount K4s."
        ),
        "source_sha256": digest(Path(__file__)),
        "seconds": time.monotonic() - started,
    }
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__), OUT / "source_snapshot.py")
    shutil.copy2(CANDIDATE, OUT / "candidate_snapshot.json")
    (OUT / "report.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
