"""Per-edge exact amplitude descent on the immutable b93 boundary-face parent."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from experiments.association_scheme.per_edge_amplitude import (
    PhaseModel, coordinate_coefficients, distinct_oriented_kernels,
    exact_coordinate_minimum, full_objective, interval, materialize,
    objective_by_motif, tiny_oracles,
)

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE_PARENT = ROOT / "reports/literature-two-parameter-001"
PHASE_PARENT = ROOT / "reports/association-scheme-phase-two-amplitude-001"
CONTROL = ROOT / "reports/joint-coarse-boundary-face-001"
OUT = ROOT / "reports/association-scheme-per-edge-boundary-001"
R, Q = 5, 65536
P_VALUE, H_OLD, H_ACTIVE = 51064, 35015, 35139
QP, QH = -7236, -11713
MAX_SWEEPS, MAX_SECONDS = 3, 60


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def main():
    started = time.monotonic()
    deadline = started + MAX_SECONDS
    prereg_path = HERE / "per_edge_boundary_preregistration.json"
    prereg = json.loads(prereg_path.read_text())
    assert sha256(CONTROL / "graphon-candidate.json") == prereg["parent_candidate_sha256"]
    assert sha256(PHASE_PARENT / "phase-assignment.json") == prereg["phase_assignment_sha256"]
    tiny = tiny_oracles()

    base_record = json.loads((BASE_PARENT / "graphon-candidate.json").read_text())
    original = base_record["red_probability_numerators"]
    assignment = json.loads((PHASE_PARENT / "phase-assignment.json").read_text())
    original_model = PhaseModel(original, Q)
    states = [assignment[f"{i},{j}"] for i, j in original_model.edge_list]

    # The mask is inherited from 33df. Reclassification depends only on the old
    # coarse value and fixed state, never on a newly materialized fine entry.
    base = [list(row) for row in original]
    for variable, (i, j) in enumerate(original_model.edge_list):
        if states[variable] >= 0 and original[i][j] == H_OLD:
            base[i][j] = base[j][i] = H_ACTIVE
    model = PhaseModel(base, Q)
    assert model.edge_list == original_model.edge_list
    amplitudes = [
        0 if states[z] < 0 else (QP if original[i][j] == P_VALUE else QH)
        for z, (i, j) in enumerate(model.edge_list)
    ]
    # This reconstruction is the semantic gate for the combined parent.
    reconstructed = materialize(base, Q, model, states, amplitudes)
    parent_record = json.loads((CONTROL / "graphon-candidate.json").read_text())
    assert reconstructed == parent_record["red_probability_numerators"]

    parent_density = Fraction(json.loads((CONTROL / "report.json").read_text())["density"])
    parent_objective = full_objective(model, states, amplitudes)
    parent_motifs = objective_by_motif(model, states, amplitudes)
    bounds = [interval(base[i][j], Q) for i, j in model.edge_list]
    assert bounds[0]  # bounds are explicit per edge after the face move

    rounds = []
    complete = True
    for sweep_number in range(1, MAX_SWEEPS + 1):
        changes = []
        for variable, (i, j) in enumerate(model.edge_list):
            if states[variable] < 0:
                continue
            if time.monotonic() >= deadline:
                complete = False
                break
            coefficients, multiplicities, motifs = coordinate_coefficients(
                model, states, amplitudes, variable
            )
            assert max(multiplicities, default=0) <= 4
            current = amplitudes[variable]
            best, best_value = exact_coordinate_minimum(coefficients, bounds[variable], current)
            current_value = sum(coefficients[k] * current**k for k in range(1, 5))
            if best_value < current_value:
                amplitudes[variable] = best
                changes.append({"variable": variable, "edge": [i, j],
                                "before": current, "after": best,
                                "exact_delta": best_value-current_value,
                                "multiplicity_counts": multiplicities,
                                "motif_counts": motifs})
        objective = full_objective(model, states, amplitudes)
        rounds.append({"sweep": sweep_number, "changes": len(changes),
                       "exact_objective": objective, "moves": changes})
        if not complete or not changes:
            break

    final_objective = full_objective(model, states, amplitudes)
    final_motifs = objective_by_motif(model, states, amplitudes)
    normalization = (len(base)*R)**4 * Q**6
    predicted = parent_density + Fraction(final_objective-parent_objective, normalization)
    improved = complete and predicted < parent_density
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(prereg_path, OUT / "preregistration.json")
    write_json(OUT / "per-edge-amplitudes.json", {
        f"{i},{j}": amplitudes[z]
        for z, (i, j) in enumerate(model.edge_list) if states[z] >= 0
    })
    report = {
        "schema": "association-scheme-per-edge-boundary-v1",
        "status": "predicted_improvement_awaiting_audit" if improved else "completed_without_candidate",
        "hypothesis": prereg["hypothesis"], "control": str(CONTROL.relative_to(ROOT)),
        "control_candidate_sha256": prereg["parent_candidate_sha256"],
        "control_density": str(parent_density), "active_variables": sum(s >= 0 for s in states),
        "coarse_rebuild": {"active_p": P_VALUE, "active_h": H_ACTIVE,
                           "inactive_h": H_OLD, "q_p": QP, "q_h": QH},
        "feasible_intervals": {"p": list(interval(P_VALUE, Q)),
                               "active_h": list(interval(H_ACTIVE, Q))},
        "tiny_exact_tests": tiny, "rounds": rounds, "complete": complete,
        "parent_objective": parent_objective, "final_objective": final_objective,
        "parent_motif_contributions": parent_motifs,
        "final_motif_contributions": final_motifs,
        "motif_contribution_changes": {k: final_motifs[k]-parent_motifs[k] for k in parent_motifs},
        "predicted_density": str(predicted), "predicted_decimal": float(predicted),
        "predicted_improvement_over_control": str(parent_density-predicted),
        "normalization": normalization, "total_seconds": time.monotonic()-started,
        "scope": "Fixed inherited phase/support; exact per-edge amplitude descent only; no optimality claim."
    }
    if improved:
        matrix = materialize(base, Q, model, states, amplitudes)
        assert all(0 <= x <= Q for row in matrix for x in row)
        write_json(OUT / "graphon-candidate.json", {
            "schema": "rational-step-graphon-v1", "block_weights": [1]*len(matrix),
            "edge_probability_denominator": Q, "red_probability_numerators": matrix})
        report.update({"candidate_sha256": sha256(OUT / "graphon-candidate.json"),
                       "refined_order": len(matrix),
                       "distinct_oriented_kernel_count": distinct_oriented_kernels(matrix, len(base))})
    write_json(OUT / "report.json", report)
    print(json.dumps({
        "status": report["status"],
        "rounds": [{"sweep": row["sweep"], "changes": row["changes"]}
                   for row in rounds],
        "predicted_density": report["predicted_density"],
        "predicted_decimal": report["predicted_decimal"],
        "predicted_improvement_over_control": report["predicted_improvement_over_control"],
        "candidate_sha256": report.get("candidate_sha256"),
        "distinct_oriented_kernel_count": report.get("distinct_oriented_kernel_count"),
        "total_seconds": report["total_seconds"],
    }, indent=2))


if __name__ == "__main__":
    main()
