"""Deterministic continuation from the preserved three-sweep boundary artifact."""

from fractions import Fraction
import json
from pathlib import Path
import shutil
import time

from experiments.association_scheme.per_edge_amplitude import (
    PhaseModel, coordinate_coefficients, distinct_oriented_kernels,
    exact_coordinate_minimum, full_objective, interval, materialize,
    objective_by_motif, tiny_oracles,
)
from experiments.association_scheme.per_edge_boundary_optimize import (
    ROOT, BASE_PARENT, PHASE_PARENT, CONTROL, R, Q, P_VALUE, H_OLD, H_ACTIVE,
    sha256, write_json,
)

START = ROOT / "reports/association-scheme-per-edge-boundary-001"
OUT = ROOT / "reports/association-scheme-per-edge-boundary-continuation-001"
MAX_SWEEPS, MAX_SECONDS = 10, 120


def main():
    started = time.monotonic()
    deadline = started + MAX_SECONDS
    tiny = tiny_oracles()
    original = json.loads((BASE_PARENT / "graphon-candidate.json").read_text())["red_probability_numerators"]
    assignment = json.loads((PHASE_PARENT / "phase-assignment.json").read_text())
    original_model = PhaseModel(original, Q)
    states = [assignment[f"{i},{j}"] for i, j in original_model.edge_list]
    base = [list(row) for row in original]
    for z, (i, j) in enumerate(original_model.edge_list):
        if states[z] >= 0 and original[i][j] == H_OLD:
            base[i][j] = base[j][i] = H_ACTIVE
    model = PhaseModel(base, Q)
    amplitude_record = json.loads((START / "per-edge-amplitudes.json").read_text())
    amplitudes = [0 if states[z] < 0 else amplitude_record[f"{i},{j}"]
                  for z, (i, j) in enumerate(model.edge_list)]
    reconstructed = materialize(base, Q, model, states, amplitudes)
    start_candidate = json.loads((START / "graphon-candidate.json").read_text())
    assert reconstructed == start_candidate["red_probability_numerators"]
    start_report = json.loads((START / "report.json").read_text())
    start_density = Fraction(start_report["predicted_density"])
    start_objective = full_objective(model, states, amplitudes)
    normalization = (len(base)*R)**4 * Q**6
    bounds = [interval(base[i][j], Q) for i, j in model.edge_list]
    sweeps = []
    complete = True
    for number in range(4, 4 + MAX_SWEEPS):
        changes = 0
        for variable in range(len(model.edge_list)):
            if states[variable] < 0:
                continue
            if time.monotonic() >= deadline:
                complete = False
                break
            coefficients, multiplicities, _ = coordinate_coefficients(model, states, amplitudes, variable)
            assert max(multiplicities, default=0) <= 4
            current = amplitudes[variable]
            best, best_value = exact_coordinate_minimum(coefficients, bounds[variable], current)
            current_value = sum(coefficients[k]*current**k for k in range(1, 5))
            if best_value < current_value:
                amplitudes[variable] = best
                changes += 1
        objective = full_objective(model, states, amplitudes)
        density = start_density + Fraction(objective-start_objective, normalization)
        sweeps.append({"sweep": number, "changes": changes, "exact_objective": objective,
                       "predicted_density": str(density), "predicted_decimal": float(density),
                       "nonzero_amplitudes": sum(x != 0 for x in amplitudes)})
        if not complete or changes == 0:
            break
    final_objective = full_objective(model, states, amplitudes)
    predicted = start_density + Fraction(final_objective-start_objective, normalization)
    improved = predicted < start_density
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    write_json(OUT / "per-edge-amplitudes.json", {
        f"{i},{j}": amplitudes[z] for z, (i,j) in enumerate(model.edge_list) if states[z] >= 0})
    report = {"schema": "association-scheme-per-edge-boundary-continuation-v1",
              "status": "predicted_improvement_awaiting_audit" if improved else "completed_without_candidate",
              "control": str(START.relative_to(ROOT)),
              "control_candidate_sha256": sha256(START / "graphon-candidate.json"),
              "control_density": str(start_density), "tiny_exact_tests": tiny,
              "sweeps": sweeps, "complete": complete,
              "termination": ("coordinate_fixed_point" if sweeps and sweeps[-1]["changes"] == 0 else
                              "time_limit" if not complete else "sweep_limit"),
              "predicted_density": str(predicted), "predicted_decimal": float(predicted),
              "predicted_improvement_over_control": str(start_density-predicted),
              "final_motif_contributions": objective_by_motif(model, states, amplitudes),
              "normalization": normalization, "total_seconds": time.monotonic()-started,
              "scope": "Deterministic exact continuation only; inherited phases/support/base fixed."}
    if improved:
        matrix = materialize(base, Q, model, states, amplitudes)
        write_json(OUT / "graphon-candidate.json", {"schema": "rational-step-graphon-v1",
                   "block_weights": [1]*len(matrix), "edge_probability_denominator": Q,
                   "red_probability_numerators": matrix})
        report.update({"candidate_sha256": sha256(OUT / "graphon-candidate.json"),
                       "refined_order": len(matrix),
                       "distinct_oriented_kernel_count": distinct_oriented_kernels(matrix, len(base))})
    write_json(OUT / "report.json", report)
    print(json.dumps({"status": report["status"], "termination": report["termination"],
          "sweeps": sweeps, "predicted_density": report["predicted_density"],
          "predicted_improvement_over_control": report["predicted_improvement_over_control"],
          "candidate_sha256": report.get("candidate_sha256"),
          "distinct_oriented_kernel_count": report.get("distinct_oriented_kernel_count"),
          "total_seconds": report["total_seconds"]}, indent=2))


if __name__ == "__main__":
    main()
