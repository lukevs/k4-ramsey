"""Alternate exact phase/support descent with p/h-specific amplitudes."""

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from research.experiments.association_scheme.phase_optimize import PhaseModel, literal_counts


ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
BASE_PARENT = ROOT / "reports/literature-two-parameter-001"
CONTROL = ROOT / "reports/association-scheme-phase-alternating-001"
OUT = ROOT / "reports/association-scheme-phase-two-amplitude-001"
R = 5
P_VALUE, H_VALUE = 51064, 35015
MAX_ROUNDS, MAX_AMPLITUDE_CYCLES, MAX_SECONDS = 16, 8, 300


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kernel(x):
    return 3 if x % R in (1, 4) else -2


def feasible_interval(value, denominator):
    valid = [q for q in range(-denominator, denominator + 1)
             if 0 <= value - 2*q <= denominator and 0 <= value + 3*q <= denominator]
    return min(valid), max(valid)


class TwoAmplitudeObjective:
    def __init__(self, model, p_value, h_value):
        self.model = model
        self.kind = []
        for i, j in model.edge_list:
            value = model.p[i][j]
            if value == p_value:
                self.kind.append(0)
            elif value == h_value:
                self.kind.append(1)
            else:
                raise ValueError(f"unexpected fractional value {value}")
        self.exponents = []
        for _, signature, _ in model.factors:
            p_count = sum(self.kind[variable] == 0 for variable, _ in signature)
            self.exponents.append((p_count, len(signature) - p_count))

    def factor_value(self, index, states, qp, qh):
        base = self.model.factor_coefficient(self.model.factors[index], states)
        a, b = self.exponents[index]
        return base * qp**a * qh**b

    def coefficients(self, states):
        answer = defaultdict(int)
        for index, factor in enumerate(self.model.factors):
            value = self.model.factor_coefficient(factor, states)
            if value:
                answer[self.exponents[index]] += value
        return dict(answer)

    @staticmethod
    def evaluate(coefficients, qp, qh):
        return sum(value * qp**a * qh**b for (a, b), value in coefficients.items())

    def objective(self, states, qp, qh):
        coefficients = self.coefficients(states)
        return self.evaluate(coefficients, qp, qh), coefficients


def one_phase_sweep(objective, states, qp, qh, deadline):
    model = objective.model
    states = list(states)
    start, before = objective.objective(states, qp, qh)
    value = start
    moves = 0
    complete = True
    for variable in range(len(states)):
        if time.monotonic() >= deadline:
            complete = False
            break
        affected = model.incident[variable]
        old_state = states[variable]
        old_local = sum(objective.factor_value(index, states, qp, qh) for index in affected)
        best_state, best_local = old_state, old_local
        for trial in (-1, 0, 1, 2, 3, 4):
            if trial == old_state:
                continue
            states[variable] = trial
            trial_value = sum(objective.factor_value(index, states, qp, qh) for index in affected)
            if trial_value < best_local:
                best_state, best_local = trial, trial_value
        states[variable] = best_state
        if best_state != old_state:
            value += best_local - old_local
            moves += 1
    checked, after = objective.objective(states, qp, qh)
    assert checked == value and value <= start
    return states, {"complete": complete, "moves": moves,
                    "objective_before": start, "objective_after": value,
                    "coefficients_before": encode_coefficients(before),
                    "coefficients_after": encode_coefficients(after)}


def optimize_amplitudes(objective, coefficients, qp, qh, p_interval, h_interval):
    history = []
    for cycle in range(1, MAX_AMPLITUDE_CYCLES + 1):
        before = (qp, qh)
        qp = min(range(p_interval[0], p_interval[1] + 1),
                 key=lambda x: (objective.evaluate(coefficients, x, qh), x))
        qh = min(range(h_interval[0], h_interval[1] + 1),
                 key=lambda x: (objective.evaluate(coefficients, qp, x), x))
        history.append({"cycle": cycle, "before": list(before), "after": [qp, qh],
                        "objective": objective.evaluate(coefficients, qp, qh)})
        if (qp, qh) == before:
            break
    return qp, qh, history


def encode_coefficients(coefficients):
    return {f"{a},{b}": value for (a, b), value in sorted(coefficients.items())}


def materialize(base, denominator, qp, qh, model, objective, states):
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
                    oriented = state if i < j else -state
                    q = qp if objective.kind[variable] == 0 else qh
                    value += q * kernel(a - b - oriented)
            row.append(value)
        matrix.append(row)
    return matrix


def tiny_oracle():
    denominator = 10
    base = [[0, 7, 4, 7], [7, 0, 4, 7], [4, 4, 0, 7], [7, 7, 7, 0]]
    model = PhaseModel(base, denominator)
    objective = TwoAmplitudeObjective(model, 7, 4)
    states = [(-1 if index % 4 == 0 else index % 5) for index in range(len(model.edge_list))]
    base_raw = literal_counts(base, denominator)[2]
    results = []
    for qp, qh in ((-1, 1), (1, -1), (0, 1)):
        matrix = materialize(base, denominator, qp, qh, model, objective, states)
        assert all(0 <= x <= denominator for row in matrix for x in row)
        delta, coefficients = objective.objective(states, qp, qh)
        predicted = base_raw * R**4 + delta
        actual = literal_counts(matrix, denominator)[2]
        assert predicted == actual
        results.append({"qp": qp, "qh": qh, "predicted_raw": predicted,
                        "actual_raw": actual, "coefficients": encode_coefficients(coefficients),
                        "repeated_coarse_indices_included": True})
    return results


def main():
    started = time.monotonic()
    prereg = json.loads((HERE / "two_amplitude_preregistration.json").read_text())
    assert sha256(CONTROL / "graphon-candidate.json") == prereg["parent_candidate_sha256"]
    assert sha256(CONTROL / "phase-assignment.json") == prereg["parent_phase_assignment_sha256"]
    tiny = tiny_oracle()
    base_candidate = json.loads((BASE_PARENT / "graphon-candidate.json").read_text())
    base_report = json.loads((BASE_PARENT / "report.json").read_text())
    control_report = json.loads((CONTROL / "report.json").read_text())
    assignment = json.loads((CONTROL / "phase-assignment.json").read_text())
    base = base_candidate["red_probability_numerators"]
    denominator = base_candidate["edge_probability_denominator"]
    model = PhaseModel(base, denominator)
    objective = TwoAmplitudeObjective(model, P_VALUE, H_VALUE)
    states = [assignment[f"{i},{j}"] for i, j in model.edge_list]
    qp = qh = prereg["initial_amplitudes"]["q_p"]
    p_interval = feasible_interval(P_VALUE, denominator)
    h_interval = feasible_interval(H_VALUE, denominator)
    assert list(p_interval) == prereg["feasible_intervals"]["q_p"]
    assert list(h_interval) == prereg["feasible_intervals"]["q_h"]

    control_value, control_bivariate = objective.objective(states, qp, qh)
    assert control_value == control_report["rounds"][-1]["objective_after_amplitude"]
    collapsed = {degree: 0 for degree in range(3, 7)}
    for (a, b), value in control_bivariate.items():
        collapsed[a+b] += value
    assert collapsed == {int(k): v for k, v in control_report["final_coefficients"].items()}

    base_density = Fraction(base_report["density"])
    control_density = Fraction(control_report["predicted_density"])
    normalization = (len(base)*R)**4 * denominator**6
    deadline = time.monotonic() + MAX_SECONDS
    rounds = []
    termination = "round_limit"
    for round_number in range(1, MAX_ROUNDS + 1):
        before = (qp, qh)
        states, phase = one_phase_sweep(objective, states, qp, qh, deadline)
        coefficients = objective.coefficients(states)
        qp, qh, amplitude_history = optimize_amplitudes(
            objective, coefficients, qp, qh, p_interval, h_interval
        )
        exact_delta = objective.evaluate(coefficients, qp, qh)
        density = base_density + Fraction(exact_delta, normalization)
        contributions = {
            f"{a},{b}": value * qp**a * qh**b
            for (a, b), value in sorted(coefficients.items())
        }
        rounds.append({"round": round_number, "amplitudes_before": list(before),
                       "amplitudes_after": [qp, qh], "phase": phase,
                       "amplitude_history": amplitude_history,
                       "coefficients": encode_coefficients(coefficients),
                       "contributions": contributions, "exact_delta": exact_delta,
                       "predicted_density": str(density), "predicted_decimal": float(density),
                       "active_edges": sum(s >= 0 for s in states),
                       "active_p_edges": sum(s >= 0 and objective.kind[i] == 0 for i, s in enumerate(states)),
                       "active_h_edges": sum(s >= 0 and objective.kind[i] == 1 for i, s in enumerate(states))})
        if not phase["complete"]:
            termination = "time_limit_during_phase_sweep"
            break
        if phase["moves"] == 0 and (qp, qh) == before:
            termination = "exact_phase_and_coordinate_amplitude_fixed_point"
            break
        if time.monotonic() >= deadline:
            termination = "time_limit_after_round"
            break

    final = rounds[-1]
    predicted = Fraction(final["predicted_density"])
    improved = predicted < control_density
    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(HERE / "two_amplitude_preregistration.json", OUT / "preregistration.json")
    write_json(OUT / "phase-assignment.json", {
        f"{i},{j}": state for (i, j), state in zip(model.edge_list, states)
    })
    report = {"schema": "association-scheme-two-amplitude-v1",
              "status": "predicted_improvement_awaiting_compressed_recount" if improved else "completed_without_improvement",
              "hypothesis": "H-F2-01D split p/h amplitudes remove the global active constraint",
              "control": str(CONTROL.relative_to(ROOT)),
              "control_candidate_sha256": sha256(CONTROL / "graphon-candidate.json"),
              "control_phase_assignment_sha256": sha256(CONTROL / "phase-assignment.json"),
              "control_density": str(control_density), "control_amplitudes": [-7236, -7236],
              "feasible_intervals": {"q_p": list(p_interval), "q_h": list(h_interval)},
              "rounds": rounds, "termination": termination,
              "final_amplitudes": {"q_p": qp, "q_h": qh},
              "final_coefficients": final["coefficients"],
              "final_contributions": final["contributions"],
              "predicted_density": str(predicted), "predicted_decimal": float(predicted),
              "predicted_improvement_over_control": str(control_density-predicted),
              "active_edges": final["active_edges"], "active_p_edges": final["active_p_edges"],
              "active_h_edges": final["active_h_edges"], "tiny_exact_tests": tiny,
              "phase_assignment_sha256": sha256(OUT / "phase-assignment.json"),
              "model_source_sha256": sha256(HERE / "phase_optimize.py"),
              "source_sha256": sha256(Path(__file__)),
              "optimization_seconds": time.monotonic()-started,
              "scope": "One continuation from immutable d93 parent; fixed Z5 kernel, no restart, seed, novelty, record, or global-optimality claim."}
    if improved:
        matrix = materialize(base, denominator, qp, qh, model, objective, states)
        order = len(matrix)
        assert order == 960
        assert all(0 <= x <= denominator for row in matrix for x in row)
        assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))
        for i in range(len(base)):
            for j in range(len(base)):
                assert sum(matrix[R*i+a][R*j+b] for a in range(R) for b in range(R)) == R*R*base[i][j]
        write_json(OUT / "graphon-candidate.json", {"schema": "rational-step-graphon-v1",
                   "block_weights": [1]*order, "edge_probability_denominator": denominator,
                   "red_probability_numerators": matrix})
        report.update({"candidate_sha256": sha256(OUT / "graphon-candidate.json"),
                       "refined_order": order, "normalization": normalization,
                       "coarse_marginals_exactly_preserved": True})
    write_json(OUT / "report.json", report)
    print(json.dumps({key: report[key] for key in ("status", "termination", "final_amplitudes",
          "predicted_density", "predicted_decimal", "predicted_improvement_over_control",
          "active_edges", "active_p_edges", "active_h_edges", "optimization_seconds")}, indent=2))


if __name__ == "__main__":
    main()
