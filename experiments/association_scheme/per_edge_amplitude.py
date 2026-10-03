"""Exact per-edge amplitude diagnostic and one conditional coordinate sweep."""

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from experiments.association_scheme.phase_optimize import PhaseModel, literal_counts


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
BASE_PARENT = ROOT / "reports/literature-two-parameter-001"
CONTROL = ROOT / "reports/association-scheme-phase-two-amplitude-001"
OUT = ROOT / "reports/association-scheme-per-edge-amplitude-001"
R, P_VALUE, H_VALUE = 5, 51064, 35015
MAX_SECONDS = 150


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kernel(x):
    return 3 if x % R in (1, 4) else -2


def interval(value, denominator):
    valid = [q for q in range(-denominator, denominator + 1)
             if 0 <= value - 2*q <= denominator and 0 <= value + 3*q <= denominator]
    return min(valid), max(valid)


def coordinate_coefficients(model, states, amplitudes, variable):
    coefficients = [0, 0, 0, 0, 0]
    multiplicity_counts = defaultdict(int)
    motif_counts = defaultdict(int)
    for factor_index in model.incident[variable]:
        factor = model.factors[factor_index]
        base = model.factor_coefficient(factor, states)
        if base == 0:
            continue
        degree, signature, _ = factor
        multiplicity = sum(other == variable for other, _ in signature)
        assert 1 <= multiplicity <= 4
        product_other = 1
        for other, _ in signature:
            if other != variable:
                product_other *= amplitudes[other]
        coefficients[multiplicity] += base * product_other
        multiplicity_counts[multiplicity] += 1
        motif_counts[degree] += 1
    return coefficients, dict(multiplicity_counts), dict(motif_counts)


def evaluate_coordinate(coefficients, x):
    return (((coefficients[4]*x + coefficients[3])*x + coefficients[2])*x
            + coefficients[1])*x


def exact_coordinate_minimum(coefficients, bounds, current):
    lo, hi = bounds
    best_x, best_value = current, evaluate_coordinate(coefficients, current)
    for x in range(lo, hi + 1):
        value = evaluate_coordinate(coefficients, x)
        if value < best_value:
            best_x, best_value = x, value
    return best_x, best_value


def full_objective(model, states, amplitudes):
    total = 0
    for factor in model.factors:
        base = model.factor_coefficient(factor, states)
        if base == 0:
            continue
        product_amplitude = 1
        for variable, _ in factor[1]:
            product_amplitude *= amplitudes[variable]
        total += base * product_amplitude
    return total


def objective_by_motif(model, states, amplitudes):
    """Exact contributions by surviving K4 expansion motif."""
    names = {3: "triangle", 4: "C4", 5: "diamond", 6: "K4"}
    answer = {names[degree]: 0 for degree in names}
    for factor in model.factors:
        degree = factor[0]
        base = model.factor_coefficient(factor, states)
        if base == 0:
            continue
        product_amplitude = 1
        for variable, _ in factor[1]:
            product_amplitude *= amplitudes[variable]
        answer[names[degree]] += base * product_amplitude
    return answer


def materialize(base, denominator, model, states, amplitudes):
    n = len(base)
    matrix = []
    for ia in range(R*n):
        i, a = divmod(ia, R)
        row = []
        for jb in range(R*n):
            j, b = divmod(jb, R)
            value = base[i][j]
            if i != j and 0 < value < denominator:
                edge = (i, j) if i < j else (j, i)
                variable = model.edge_index[edge]
                state = states[variable]
                if state >= 0:
                    phase = state if i < j else -state
                    value += amplitudes[variable] * kernel(a-b-phase)
            row.append(value)
        matrix.append(row)
    return matrix


def tiny_oracles():
    results = []
    # Sole edge: 2+2 equality patterns force fourth powers of one amplitude.
    denominator = 50
    base = [[0, 35], [35, 0]]
    model = PhaseModel(base, denominator)
    states = [1]
    amplitudes = [-7]
    coefficients, multiplicities, _ = coordinate_coefficients(model, states, amplitudes, 0)
    assert multiplicities.get(4, 0) > 0 and coefficients[4] != 0
    base_raw = literal_counts(base, denominator)[2]
    bounds = interval(35, denominator)
    for x in range(bounds[0], bounds[1] + 1):
        matrix = materialize(base, denominator, model, states, [x])
        predicted = base_raw*R**4 + evaluate_coordinate(coefficients, x)
        actual = literal_counts(matrix, denominator)[2]
        assert predicted == actual
    results.append({"fixture": "sole_edge_repeated_2plus2", "bounds": bounds,
                    "coefficients": coefficients, "multiplicity_counts": multiplicities})

    # Mixed values, phases and an inactive edge.
    base = [[0, 35, 20], [35, 0, 35], [20, 35, 0]]
    model = PhaseModel(base, denominator)
    states = [1, -1, 3]
    amplitudes = [-7, 0, -5]
    base_raw = literal_counts(base, denominator)[2]
    delta = full_objective(model, states, amplitudes)
    actual = literal_counts(materialize(base, denominator, model, states, amplitudes), denominator)[2]
    assert actual == base_raw*R**4 + delta
    for variable in (0, 2):
        coefficients, multiplicities, _ = coordinate_coefficients(
            model, states, amplitudes, variable
        )
        value = base[model.edge_list[variable][0]][model.edge_list[variable][1]]
        bounds = interval(value, denominator)
        for x in (bounds[0], amplitudes[variable], 0, bounds[1]):
            trial = list(amplitudes); trial[variable] = x
            actual = literal_counts(materialize(base, denominator, model, states, trial), denominator)[2]
            unchanged = delta - evaluate_coordinate(coefficients, amplitudes[variable])
            predicted = base_raw*R**4 + unchanged + evaluate_coordinate(coefficients, x)
            assert actual == predicted
        results.append({"fixture": "mixed_with_inactive", "variable": variable,
                        "bounds": bounds, "coefficients": coefficients,
                        "multiplicity_counts": multiplicities})
    return results


def distinct_oriented_kernels(matrix, base_order):
    kernels = set()
    for i in range(base_order):
        for j in range(base_order):
            kernels.add(tuple(
                matrix[R*i+a][R*j+b] for a in range(R) for b in range(R)
            ))
    return len(kernels)


def main():
    started = time.monotonic()
    deadline = started + MAX_SECONDS
    prereg = json.loads((HERE / "per_edge_amplitude_preregistration.json").read_text())
    assert sha256(CONTROL / "graphon-candidate.json") == prereg["parent_candidate_sha256"]
    assert sha256(CONTROL / "phase-assignment.json") == prereg["parent_phase_assignment_sha256"]
    tests = tiny_oracles()
    base_candidate = json.loads((BASE_PARENT / "graphon-candidate.json").read_text())
    base_report = json.loads((BASE_PARENT / "report.json").read_text())
    control_report = json.loads((CONTROL / "report.json").read_text())
    assignment = json.loads((CONTROL / "phase-assignment.json").read_text())
    base = base_candidate["red_probability_numerators"]
    denominator = base_candidate["edge_probability_denominator"]
    model = PhaseModel(base, denominator)
    states = [assignment[f"{i},{j}"] for i, j in model.edge_list]
    amplitudes = [
        0 if states[index] < 0 else (-7236 if base[i][j] == P_VALUE else -11671)
        for index, (i, j) in enumerate(model.edge_list)
    ]
    bounds_by_kind = {P_VALUE: interval(P_VALUE, denominator),
                      H_VALUE: interval(H_VALUE, denominator)}
    parent_delta = full_objective(model, states, amplitudes)
    parent_motif_contributions = objective_by_motif(model, states, amplitudes)
    assert parent_delta == control_report["rounds"][-1]["exact_delta"]

    screen_started = time.monotonic()
    screen = []
    max_multiplicity = 0
    for variable, (i, j) in enumerate(model.edge_list):
        if states[variable] < 0:
            continue
        coefficients, multiplicities, motifs = coordinate_coefficients(
            model, states, amplitudes, variable
        )
        max_multiplicity = max(max_multiplicity, *(multiplicities or {0: 0}))
        current = amplitudes[variable]
        bounds = bounds_by_kind[base[i][j]]
        best, best_value = exact_coordinate_minimum(coefficients, bounds, current)
        current_value = evaluate_coordinate(coefficients, current)
        screen.append({"variable": variable, "edge": [i, j],
                       "kind": "p" if base[i][j] == P_VALUE else "h",
                       "current": current, "bounds": list(bounds),
                       "coefficients": coefficients,
                       "current_local": current_value, "best": best,
                       "best_local": best_value, "delta": best_value-current_value,
                       "inward_one_step_delta": evaluate_coordinate(coefficients, current+1)-current_value,
                       "multiplicity_counts": multiplicities, "motif_counts": motifs})
    screen_seconds = time.monotonic()-screen_started
    improving = [row for row in screen if row["delta"] < 0]
    assert len(screen) == sum(state >= 0 for state in states) == 976
    assert max_multiplicity <= 4

    sweep = []
    sweep_complete = True
    sweep_started = time.monotonic()
    if improving:
        for variable, (i, j) in enumerate(model.edge_list):
            if states[variable] < 0:
                continue
            if time.monotonic() >= deadline:
                sweep_complete = False
                break
            coefficients, _, _ = coordinate_coefficients(model, states, amplitudes, variable)
            current = amplitudes[variable]
            best, best_value = exact_coordinate_minimum(
                coefficients, bounds_by_kind[base[i][j]], current
            )
            current_value = evaluate_coordinate(coefficients, current)
            if best_value < current_value:
                amplitudes[variable] = best
                sweep.append({"variable": variable, "edge": [i, j],
                              "kind": "p" if base[i][j] == P_VALUE else "h",
                              "before": current, "after": best,
                              "exact_delta": best_value-current_value})
    sweep_seconds = time.monotonic()-sweep_started
    final_delta = full_objective(model, states, amplitudes)
    final_motif_contributions = objective_by_motif(model, states, amplitudes)
    motif_contribution_changes = {
        name: final_motif_contributions[name] - parent_motif_contributions[name]
        for name in parent_motif_contributions
    }
    assert final_delta <= parent_delta
    base_density = Fraction(base_report["density"])
    normalization = (len(base)*R)**4 * denominator**6
    predicted = base_density + Fraction(final_delta, normalization)
    control_density = Fraction(control_report["predicted_density"])
    improved = sweep_complete and predicted < control_density

    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(HERE / "per_edge_amplitude_preregistration.json", OUT / "preregistration.json")
    write_json(OUT / "matched-screen.json", screen)
    write_json(OUT / "per-edge-amplitudes.json", {
        f"{i},{j}": amplitudes[index]
        for index, (i, j) in enumerate(model.edge_list) if states[index] >= 0
    })
    report = {"schema": "association-scheme-per-edge-amplitude-v1",
              "status": "predicted_improvement_awaiting_audit" if improved else "completed_without_candidate",
              "hypothesis": "H-F2-01E active edges are not individually optimized at shared class amplitudes",
              "control": str(CONTROL.relative_to(ROOT)),
              "control_candidate_sha256": sha256(CONTROL / "graphon-candidate.json"),
              "control_density": str(control_density), "active_variables_screened": len(screen),
              "matched_improving_variables": len(improving),
              "matched_best_delta": min((row["delta"] for row in screen), default=0),
              "matched_screen_seconds": screen_seconds, "max_repeated_variable_multiplicity": max_multiplicity,
              "conditional_sweep_admitted": bool(improving), "conditional_sweep_complete": sweep_complete,
              "conditional_sweep_changes": len(sweep), "conditional_sweep": sweep,
              "conditional_sweep_seconds": sweep_seconds, "parent_delta": parent_delta,
              "final_delta": final_delta,
              "parent_motif_contributions": parent_motif_contributions,
              "final_motif_contributions": final_motif_contributions,
              "motif_contribution_changes": motif_contribution_changes,
              "predicted_density": str(predicted),
              "predicted_decimal": float(predicted),
              "predicted_improvement_over_control": str(control_density-predicted),
              "tiny_exact_tests": tests,
              "amplitudes_sha256": sha256(OUT / "per-edge-amplitudes.json"),
              "source_sha256": sha256(Path(__file__)), "total_seconds": time.monotonic()-started,
              "scope": "One matched coordinate diagnostic plus one conditional lexicographic sweep on immutable33df; fixed phase/support/means/kernel, no restart or global-optimality claim."}
    if improved:
        matrix = materialize(base, denominator, model, states, amplitudes)
        order = len(matrix)
        assert all(0 <= value <= denominator for row in matrix for value in row)
        assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))
        write_json(OUT / "graphon-candidate.json", {"schema": "rational-step-graphon-v1",
                   "block_weights": [1]*order, "edge_probability_denominator": denominator,
                   "red_probability_numerators": matrix})
        report.update({"candidate_sha256": sha256(OUT / "graphon-candidate.json"),
                       "refined_order": order, "normalization": normalization,
                       "distinct_oriented_kernel_count": distinct_oriented_kernels(matrix, len(base)),
                       "coarse_marginals_exactly_preserved": True})
    write_json(OUT / "report.json", report)
    print(json.dumps({key: report.get(key) for key in ("status", "matched_improving_variables",
          "matched_best_delta", "conditional_sweep_changes", "predicted_density",
          "predicted_decimal", "predicted_improvement_over_control",
          "distinct_oriented_kernel_count", "total_seconds")}, indent=2))


if __name__ == "__main__":
    main()
