"""Exact active-block coarse/amplitude optimization on clipped probability faces."""

from collections import defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import time

from research.experiments.association_scheme.phase_optimize import PhaseModel, R, literal_counts
from research.experiments.association_scheme.two_amplitude_optimize import materialize
from research.experiments.compressed_graphon.polynomial import ExactPolynomial, interpolate_integer_polynomial


ROOT = Path(__file__).resolve().parents[3]
BASE_PARENT = ROOT / "reports/literature-two-parameter-001"
CONTROL = ROOT / "reports/association-scheme-phase-two-amplitude-001"
OUT = ROOT / "reports/joint-coarse-boundary-face-001"
CHECKER = ROOT / "reports/association-scheme-phase-001/ordered_graphon_u256"
Q = 65536
P0, H0 = 51064, 35015
QP0, QH0 = -7236, -11671


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class FixedKindsObjective:
    """Two-amplitude factor evaluator with kinds fixed from the original base."""

    def __init__(self, model, kind_by_edge):
        self.model = model
        self.kind = [kind_by_edge[edge] for edge in model.edge_list]
        self.exponents = []
        for _, signature, _ in model.factors:
            p_count = sum(self.kind[variable] == 0 for variable, _ in signature)
            self.exponents.append((p_count, len(signature) - p_count))

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


def checker_payload(matrix, denominator):
    return f"{len(matrix)} {denominator}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix
    ) + "\n"


def direct_coarse_raw(matrix):
    return int(
        subprocess.check_output(
            [str(CHECKER)], input=checker_payload(matrix, Q), text=True, timeout=30
        ).split()[2]
    )


def tiny_affine_oracle():
    denominator = 20
    p0, h0 = 13, 8
    base = [[0, p0, h0, p0], [p0, 0, h0, p0], [h0, h0, 0, p0], [p0, p0, p0, 0]]
    original = PhaseModel(base, denominator)
    states = [(-1 if index % 4 == 0 else index % 5) for index in range(len(original.edge_list))]
    assignment = {edge: state for edge, state in zip(original.edge_list, states)}
    kinds = {edge: 0 if base[edge[0]][edge[1]] == p0 else 1 for edge in original.edge_list}
    changed = [row[:] for row in base]
    for edge, state in assignment.items():
        if state < 0:
            continue
        i, j = edge
        changed[i][j] = changed[j][i] = 12 if kinds[edge] == 0 else 9
    model = PhaseModel(changed, denominator)
    changed_states = [assignment[edge] for edge in model.edge_list]
    objective = FixedKindsObjective(model, kinds)
    qp, qh = -2, -1
    delta, coefficients = objective.objective(changed_states, qp, qh)
    refined = materialize(changed, denominator, qp, qh, model, objective, changed_states)
    predicted = literal_counts(changed, denominator)[2] * R**4 + delta
    actual = literal_counts(refined, denominator)[2]
    assert predicted == actual
    return {
        "predicted": predicted,
        "actual": actual,
        "inactive_edges_retained_original_means": True,
        "coefficients": {f"{a},{b}": value for (a, b), value in sorted(coefficients.items())},
    }


def main():
    started = time.monotonic()
    tiny = tiny_affine_oracle()
    base_record = json.loads((BASE_PARENT / "graphon-candidate.json").read_text())
    base = base_record["red_probability_numerators"]
    assignment = {
        tuple(map(int, key.split(","))): int(value)
        for key, value in json.loads((CONTROL / "phase-assignment.json").read_text()).items()
    }
    n = len(base)
    order = R * n
    normalization = order**4 * Q**6
    kind_by_edge = {
        (i, j): 0 if base[i][j] == P0 else 1
        for i in range(n)
        for j in range(i + 1, n)
        if 0 < base[i][j] < Q
    }
    assert len(kind_by_edge) == 1248
    cache = {}
    timings = []

    def parameters(residual, tp, th):
        qp = QP0 - tp
        qh = QH0 - th
        active_p = P0 - 2 * tp
        active_h = (35013 + residual) + 3 * th
        return active_p, active_h, qp, qh

    def changed_base(residual, tp, th):
        active_p, active_h, _, _ = parameters(residual, tp, th)
        changed = [row[:] for row in base]
        for edge, state in assignment.items():
            if state < 0:
                continue
            i, j = edge
            changed[i][j] = changed[j][i] = active_p if kind_by_edge[edge] == 0 else active_h
        return changed

    def evaluate(residual, tp, th):
        key = (residual, tp, th)
        if key in cache:
            return cache[key]
        tick = time.monotonic()
        active_p, active_h, qp, qh = parameters(residual, tp, th)
        changed = changed_base(residual, tp, th)
        model = PhaseModel(changed, Q)
        states = [assignment[edge] for edge in model.edge_list]
        objective = FixedKindsObjective(model, kind_by_edge)
        delta, coefficients = objective.objective(states, qp, qh)
        raw = direct_coarse_raw(changed) * R**4 + delta
        cache[key] = (raw, coefficients)
        timings.append({"residual": residual, "t_p": tp, "t_h": th,
                        "active_p": active_p, "active_h": active_h,
                        "q_p": qp, "q_h": qh,
                        "seconds": time.monotonic() - tick})
        return cache[key]

    # Exact admissible face ranges. The clipped cell remains Q for p and the
    # requested residue r for h; the opposite cells move by five units/step.
    tp_interval = (0, (P0 + 3 * QP0) // 5)  # (29356)//5 = 5871
    assert tp_interval == (0, 5871)

    face_records = []
    global_best = None
    for residual in (2, 0, 1):
        th_interval = (0, (Q - (residual - 5 * QH0)) // 5)
        assert th_interval[1] == (1435 if residual == 2 else 1436)
        start_raw = evaluate(residual, 0, 0)[0]
        unit = {
            "p": evaluate(residual, 1, 0)[0] - start_raw,
            "h": evaluate(residual, 0, 1)[0] - start_raw,
        }
        tp = th = 0
        lines = []

        def optimize_coordinate(tp_value, th_value, coordinate):
            interval = tp_interval if coordinate == "p" else th_interval
            points = []
            for value in range(7):
                a, b = (value, th_value) if coordinate == "p" else (tp_value, value)
                points.append((value, evaluate(residual, a, b)[0]))
            coefficients = interpolate_integer_polynomial(
                points, max_degree=6, degree_bound_proven=True
            )
            polynomial = ExactPolynomial.from_total_coefficients(
                coefficients, normalization, feasible_integer_interval=interval,
                base_order=n, latent_order=R, probability_denominator=Q,
            )
            minimum = polynomial.minimize_integer()
            selected = minimum.minimizers[0]
            pair = (selected, th_value) if coordinate == "p" else (tp_value, selected)
            actual = evaluate(residual, *pair)[0]
            assert actual == minimum.value
            lines.append({"coordinate": coordinate, "fixed_before": [tp_value, th_value],
                          "coefficients_low_to_high": list(coefficients),
                          "interval": list(interval), "selected": selected,
                          "selected_pair": list(pair), "raw": actual})
            return pair

        # All three residue faces are exact, but only admit full line descent
        # if the face start or a unit inward direction beats the r=2 control.
        control_raw = evaluate(2, 0, 0)[0]
        admitted = start_raw < control_raw or min(unit.values()) < 0 or residual == 2
        if admitted:
            for _ in range(3):
                before = (tp, th)
                tp, th = optimize_coordinate(tp, th, "p")
                tp, th = optimize_coordinate(tp, th, "h")
                if (tp, th) == before:
                    break
        raw, coefficients = evaluate(residual, tp, th)
        face = {"residual": residual, "admitted": admitted, "start_raw": start_raw,
                "unit_deltas": unit, "selected_t": [tp, th],
                "selected_parameters": list(parameters(residual, tp, th)),
                "raw": raw, "density": str(Fraction(raw, normalization)),
                "decimal": float(Fraction(raw, normalization)),
                "lines": lines,
                "phase_coefficients": {f"{a},{b}": value for (a, b), value in sorted(coefficients.items())}}
        face_records.append(face)
        if global_best is None or (raw, residual) < (global_best[0], global_best[1]):
            global_best = (raw, residual, tp, th, coefficients)

    best_raw, residual, tp, th, best_coefficients = global_best
    control_raw = evaluate(2, 0, 0)[0]
    changed = changed_base(residual, tp, th)
    model = PhaseModel(changed, Q)
    states = [assignment[edge] for edge in model.edge_list]
    objective = FixedKindsObjective(model, kind_by_edge)
    active_p, active_h, qp, qh = parameters(residual, tp, th)
    matrix = materialize(changed, Q, qp, qh, model, objective, states)
    assert all(0 <= value <= Q for row in matrix for value in row)
    assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))
    # Inactive blocks must remain byte-for-byte at their original coarse means.
    for edge, state in assignment.items():
        i, j = edge
        expected = base[i][j] if state < 0 else active_p if kind_by_edge[edge] == 0 else active_h
        assert sum(matrix[R * i + a][R * j + b] for a in range(R) for b in range(R)) == R * R * expected

    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__), OUT / "source_snapshot.py")
    write_json(OUT / "graphon-candidate.json", {
        "schema": "rational-step-graphon-v1", "block_weights": [1] * order,
        "edge_probability_denominator": Q, "red_probability_numerators": matrix,
    })
    density = Fraction(best_raw, normalization)
    report = {
        "schema": "joint-active-boundary-face-v1",
        "status": "exact_model_candidate_awaiting_independent_recount",
        "hypothesis": "Co-adjust active-block coarse means and p/h amplitudes along clipped probability faces",
        "control": str(CONTROL.relative_to(ROOT)),
        "control_candidate_sha256": sha256(CONTROL / "graphon-candidate.json"),
        "control_phase_assignment_sha256": sha256(CONTROL / "phase-assignment.json"),
        "face_parameterization": {
            "p": "q_p=-7236-t_p, active_p=51064-2*t_p, so active_p-2*q_p=65536",
            "h": "q_h=-11671-t_h, active_h=35013+r+3*t_h, so active_h+3*q_h=r",
            "inactive": "all inactive fractional blocks retain original p=51064 or h=35015",
        },
        "face_records": face_records,
        "selected_residual": residual,
        "selected_t": [tp, th],
        "selected_parameters": {"active_p": active_p, "active_h": active_h,
                                "q_p": qp, "q_h": qh},
        "inactive_parameters": {"p": P0, "h": H0},
        "numerator": best_raw, "normalization": normalization,
        "density": str(density), "decimal": float(density),
        "raw_improvement_over_control": control_raw - best_raw,
        "improvement_over_control": str(Fraction(control_raw - best_raw, normalization)),
        "candidate_sha256": sha256(OUT / "graphon-candidate.json"),
        "source_sha256": sha256(Path(__file__)),
        "tiny_affine_oracle": tiny,
        "evaluations": len(cache), "timings": timings,
        "seconds": time.monotonic() - started,
        "evidence": "Exact direct coarse C++ recount plus recomputed typed phase polynomial on every sample; tiny literal refined oracle; serialized candidate range/symmetry/inactive-mean checks; independent promotion recount pending",
        "scope": "Fixed phase/support assignment; three clipped residual faces and three alternating exact coordinate sweeps; no global graphon or phase optimum claim.",
    }
    write_json(OUT / "report.json", report)
    print(json.dumps({key: report[key] for key in ("status", "selected_residual", "selected_t", "selected_parameters", "density", "decimal", "raw_improvement_over_control", "evaluations", "seconds")}, sort_keys=True))


if __name__ == "__main__":
    main()
