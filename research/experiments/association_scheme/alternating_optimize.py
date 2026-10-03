"""Alternate exact phase/support sweeps with exact amplitude minimization."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from research.experiments.association_scheme.phase_optimize import (
    PhaseModel,
    feasible_interval,
    materialize,
    tiny_checks,
)


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE_PARENT = ROOT / "reports/literature-two-parameter-001"
CONTROL = ROOT / "reports/association-scheme-phase-001"
OUT = ROOT / "reports/association-scheme-phase-alternating-001"
MAX_ROUNDS = 16
MAX_SECONDS = 300
R = 5


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def objective_from_coefficients(coefficients, q):
    return sum(coefficients[d] * q**d for d in range(3, 7))


def exact_amplitude_minimum(base, denominator, model, states, coefficients):
    lo, hi = feasible_interval(base, denominator, model, states)
    best_q = min(
        range(lo, hi + 1),
        key=lambda q: (objective_from_coefficients(coefficients, q), q),
    )
    return best_q, objective_from_coefficients(coefficients, best_q), (lo, hi)


def one_sweep(model, states, q, deadline):
    """One deterministic strict coordinate sweep; ties retain current state."""
    states = list(states)
    start_objective, start_coefficients = model.objective(states, q)
    objective = start_objective
    moves = 0
    complete = True
    state_changes = {state: 0 for state in range(-1, 5)}
    for variable in range(len(states)):
        if time.monotonic() >= deadline:
            complete = False
            break
        affected = model.incident[variable]
        old_state = states[variable]
        old_local = sum(
            model.factor_coefficient(model.factors[index], states)
            * q ** model.factors[index][0]
            for index in affected
        )
        best_state, best_local = old_state, old_local
        for trial in (-1, 0, 1, 2, 3, 4):
            if trial == old_state:
                continue
            states[variable] = trial
            value = sum(
                model.factor_coefficient(model.factors[index], states)
                * q ** model.factors[index][0]
                for index in affected
            )
            if value < best_local:
                best_state, best_local = trial, value
        states[variable] = best_state
        if best_state != old_state:
            objective += best_local - old_local
            moves += 1
            state_changes[best_state] += 1
    checked, coefficients = model.objective(states, q)
    assert checked == objective
    assert objective <= start_objective
    return states, {
        "complete": complete,
        "moves": moves,
        "state_changes_by_destination": state_changes,
        "objective_before": start_objective,
        "objective_after": objective,
        "coefficients_before": start_coefficients,
        "coefficients_after": coefficients,
    }


def main():
    started = time.monotonic()
    prereg = json.loads((HERE / "alternating_preregistration.json").read_text())
    assert sha256(CONTROL / "phase-assignment.json") == prereg["parent_phase_assignment_sha256"]
    assert sha256(CONTROL / "graphon-candidate.json") == prereg["parent_candidate_sha256"]

    # Re-execute literal tiny objective/full-count checks before the full model.
    tests = tiny_checks()
    assert tests and all(row["predicted_raw"] == row["actual_raw"] for row in tests)
    base_candidate = json.loads((BASE_PARENT / "graphon-candidate.json").read_text())
    base_report = json.loads((BASE_PARENT / "report.json").read_text())
    control_report = json.loads((CONTROL / "report.json").read_text())
    assignment = json.loads((CONTROL / "phase-assignment.json").read_text())
    base = base_candidate["red_probability_numerators"]
    denominator = base_candidate["edge_probability_denominator"]
    model = PhaseModel(base, denominator)
    states = [assignment[f"{i},{j}"] for i, j in model.edge_list]
    q = prereg["initial_q"]
    control_objective, control_coefficients = model.objective(states, q)
    assert control_coefficients == {int(k): v for k, v in control_report["coefficients"].items()}
    assert control_objective == control_report["selected_delta_raw"]

    base_density = Fraction(base_report["density"])
    control_density = Fraction(control_report["actual_density"])
    normalization = (len(base) * R) ** 4 * denominator**6
    deadline = time.monotonic() + MAX_SECONDS
    rounds = []
    termination = "round_limit"
    for round_number in range(1, MAX_ROUNDS + 1):
        q_before = q
        states, phase_result = one_sweep(model, states, q_before, deadline)
        coefficients = phase_result["coefficients_after"]
        q, exact_objective, interval = exact_amplitude_minimum(
            base, denominator, model, states, coefficients
        )
        density = base_density + Fraction(exact_objective, normalization)
        contributions = {
            str(d): coefficients[d] * q**d for d in range(3, 7)
        }
        rounds.append({
            "round": round_number,
            "q_before": q_before,
            "q_after": q,
            "feasible_q": list(interval),
            "phase": phase_result,
            "objective_after_amplitude": exact_objective,
            "coefficients": coefficients,
            "contributions_at_q_after": contributions,
            "predicted_density": str(density),
            "predicted_decimal": float(density),
            "active_edges": sum(state >= 0 for state in states),
            "phase_histogram": {str(s): states.count(s) for s in range(-1, 5)},
        })
        if not phase_result["complete"]:
            termination = "time_limit_during_phase_sweep"
            break
        if phase_result["moves"] == 0 and q == q_before:
            termination = "exact_coordinate_and_amplitude_fixed_point"
            break
        if time.monotonic() >= deadline:
            termination = "time_limit_after_round"
            break

    final = rounds[-1]
    final_density = Fraction(final["predicted_density"])
    improved = final_density < control_density
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(HERE / "alternating_preregistration.json", OUT / "preregistration.json")
    phase_assignment = {
        f"{i},{j}": state for (i, j), state in zip(model.edge_list, states)
    }
    write_json(OUT / "phase-assignment.json", phase_assignment)
    report = {
        "schema": "association-scheme-alternating-phase-amplitude-v1",
        "status": "predicted_improvement_awaiting_compressed_recount" if improved else "completed_without_improvement",
        "hypothesis": "H-F2-01C alternating exact phase/support descent and amplitude reoptimization",
        "control": str(CONTROL.relative_to(ROOT)),
        "control_report_sha256": sha256(CONTROL / "report.json"),
        "control_candidate_sha256": sha256(CONTROL / "graphon-candidate.json"),
        "control_phase_assignment_sha256": sha256(CONTROL / "phase-assignment.json"),
        "control_density": str(control_density),
        "control_q": prereg["initial_q"],
        "variables": len(model.edge_list),
        "factor_count": len(model.factors),
        "rounds": rounds,
        "termination": termination,
        "final_q": q,
        "final_coefficients": final["coefficients"],
        "final_contributions": final["contributions_at_q_after"],
        "predicted_density": str(final_density),
        "predicted_decimal": float(final_density),
        "predicted_improvement_over_control": str(control_density - final_density),
        "active_edges": final["active_edges"],
        "phase_histogram": final["phase_histogram"],
        "tiny_exact_tests": tests,
        "phase_assignment_sha256": sha256(OUT / "phase-assignment.json"),
        "model_source_sha256": sha256(HERE / "phase_optimize.py"),
        "source_sha256": sha256(Path(__file__)),
        "optimization_seconds": time.monotonic() - started,
        "scope": "One continuation from the immutable phase-001 assignment; no restart, seed, kernel, novelty, record, or optimality claim.",
    }
    if improved:
        matrix = materialize(base, denominator, q, model.edge_index, states)
        order = len(matrix)
        assert order == 960
        assert all(0 <= value <= denominator for row in matrix for value in row)
        assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))
        for i in range(len(base)):
            for j in range(len(base)):
                assert sum(
                    matrix[R*i+a][R*j+b] for a in range(R) for b in range(R)
                ) == R*R*base[i][j]
        write_json(OUT / "graphon-candidate.json", {
            "schema": "rational-step-graphon-v1",
            "block_weights": [1] * order,
            "edge_probability_denominator": denominator,
            "red_probability_numerators": matrix,
        })
        report.update({
            "candidate_sha256": sha256(OUT / "graphon-candidate.json"),
            "refined_order": order,
            "normalization": normalization,
            "coarse_marginals_exactly_preserved": True,
        })
    write_json(OUT / "report.json", report)
    print(json.dumps({key: report[key] for key in (
        "status", "termination", "final_q", "predicted_density",
        "predicted_decimal", "predicted_improvement_over_control", "active_edges",
        "phase_histogram", "optimization_seconds",
    )}, indent=2))


if __name__ == "__main__":
    main()
