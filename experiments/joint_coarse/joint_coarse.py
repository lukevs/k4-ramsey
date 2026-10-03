"""Exact coordinate reoptimization of coarse p,h for a fixed phase assignment."""

from fractions import Fraction
import hashlib
import json
from pathlib import Path
import shutil
import time

from experiments.association_scheme.phase_optimize import PhaseModel, R, materialize
from experiments.compressed_graphon.polynomial import (
    ExactPolynomial,
    interpolate_integer_polynomial,
)


ROOT = Path(__file__).resolve().parents[2]
PARENT = ROOT / "reports/association-scheme-phase-001"
COARSE_PARENT = ROOT / "reports/literature-two-parameter-001"
OUT = ROOT / "reports/joint-coarse-001"
Q = 65536
FIXED_Q = -5496
P0 = 51064
H0 = 35015


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_probabilities(base, p_value, h_value):
    return [
        [p_value if value == P0 else h_value if value == H0 else value for value in row]
        for row in base
    ]


def coarse_raw(profile, p_value, h_value):
    answer = 0
    for color, p_power, h_power, count in profile:
        p = p_value if color == 0 else Q - p_value
        h = h_value if color == 0 else Q - h_value
        answer += count * p**p_power * h**h_power * Q ** (6 - p_power - h_power)
    return answer


def states_for(model, assignment):
    return [assignment[f"{i},{j}"] for i, j in model.edge_list]


def main():
    started = time.monotonic()
    base_record = json.loads((COARSE_PARENT / "graphon-candidate.json").read_text())
    coarse_report = json.loads((COARSE_PARENT / "report.json").read_text())
    parent_report = json.loads((PARENT / "report.json").read_text())
    assignment = {
        key: int(value)
        for key, value in json.loads((PARENT / "phase-assignment.json").read_text()).items()
    }
    base = base_record["red_probability_numerators"]
    profile = coarse_report["profile"]
    n = len(base)
    order = R * n
    normalization = order**4 * Q**6
    cache = {}
    timings = []

    def evaluate(p_value, h_value):
        key = (p_value, h_value)
        if key in cache:
            return cache[key]
        tick = time.monotonic()
        changed = replace_probabilities(base, p_value, h_value)
        model = PhaseModel(changed, Q)
        states = states_for(model, assignment)
        coefficients = model.coefficients(states)
        phase_delta = sum(coefficients[degree] * FIXED_Q**degree for degree in range(3, 7))
        raw = coarse_raw(profile, p_value, h_value) * R**4 + phase_delta
        cache[key] = (raw, coefficients)
        timings.append({"p": p_value, "h": h_value, "seconds": time.monotonic() - tick})
        return cache[key]

    center_raw, center_coefficients = evaluate(P0, H0)
    assert center_raw == parent_report["numerator"]
    neighbors = {
        "p_minus": evaluate(P0 - 1, H0)[0],
        "p_plus": evaluate(P0 + 1, H0)[0],
        "h_minus": evaluate(P0, H0 - 1)[0],
        "h_plus": evaluate(P0, H0 + 1)[0],
    }
    gradient_gate = {
        "center": center_raw,
        "neighbor_deltas": {name: value - center_raw for name, value in neighbors.items()},
        "central_difference_twice_gradient": {
            "p": neighbors["p_plus"] - neighbors["p_minus"],
            "h": neighbors["h_plus"] - neighbors["h_minus"],
        },
        "negative_neighbor_exists": min(neighbors.values()) < center_raw,
    }

    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(Path(__file__), OUT / "source_snapshot.py")
    if not gradient_gate["negative_neighbor_exists"]:
        write_json(
            OUT / "report.json",
            {
                "status": "retired_no_negative_unit_direction",
                "gradient_gate": gradient_gate,
                "evaluations": len(cache),
                "timings": timings,
                "seconds": time.monotonic() - started,
            },
        )
        print(json.dumps(gradient_gate, sort_keys=True))
        return

    # With q fixed, active kernel values are 3 and -2. Both p and h have
    # active edges, so these are the exact integer intervals preserving every
    # micro-probability and the unchanged fractional-support combinatorics.
    low = -3 * FIXED_Q
    high = Q + 2 * FIXED_Q
    assert (low, high) == (16488, 54544)

    line_records = []

    def optimize_coordinate(p_value, h_value, coordinate):
        anchor = p_value if coordinate == "p" else h_value
        sample_values = [anchor + offset for offset in range(-3, 4)]
        assert low <= min(sample_values) and max(sample_values) <= high
        points = []
        for value in sample_values:
            p_trial, h_trial = (value, h_value) if coordinate == "p" else (p_value, value)
            points.append((value, evaluate(p_trial, h_trial)[0]))
        total_coefficients = interpolate_integer_polynomial(
            points, max_degree=6, degree_bound_proven=True
        )
        polynomial = ExactPolynomial.from_total_coefficients(
            total_coefficients,
            normalization,
            feasible_integer_interval=(low, high),
            base_order=n,
            latent_order=R,
            probability_denominator=Q,
        )
        minimum = polynomial.minimize_integer()
        selected = minimum.minimizers[0]
        selected_pair = (selected, h_value) if coordinate == "p" else (p_value, selected)
        actual, _ = evaluate(*selected_pair)
        assert actual == minimum.value
        record = {
            "coordinate": coordinate,
            "fixed_pair_before": [p_value, h_value],
            "sample_values": sample_values,
            "total_coefficients_low_to_high": list(total_coefficients),
            "feasible_interval": [low, high],
            "selected": selected,
            "selected_pair": list(selected_pair),
            "selected_raw": actual,
            "improvement": evaluate(p_value, h_value)[0] - actual,
            "integer_evaluations": minimum.evaluations,
        }
        line_records.append(record)
        return selected_pair

    p_value, h_value = P0, H0
    # Exact degree-six coordinate lines, alternated to a fixed point or a short
    # three-sweep cap. This is a joint two-variable reoptimization, not a grid.
    for _ in range(3):
        before = (p_value, h_value)
        p_value, h_value = optimize_coordinate(p_value, h_value, "p")
        p_value, h_value = optimize_coordinate(p_value, h_value, "h")
        if (p_value, h_value) == before:
            break

    final_raw, final_coefficients = evaluate(p_value, h_value)
    changed_base = replace_probabilities(base, p_value, h_value)
    final_model = PhaseModel(changed_base, Q)
    final_states = states_for(final_model, assignment)
    matrix = materialize(
        changed_base, Q, FIXED_Q, final_model.edge_index, final_states
    )
    assert len(matrix) == order
    assert all(0 <= value <= Q for row in matrix for value in row)
    assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))
    for i in range(n):
        for j in range(n):
            assert sum(matrix[R * i + a][R * j + b] for a in range(R) for b in range(R)) == R * R * changed_base[i][j]

    write_json(
        OUT / "graphon-candidate.json",
        {
            "schema": "rational-step-graphon-v1",
            "block_weights": [1] * order,
            "edge_probability_denominator": Q,
            "red_probability_numerators": matrix,
        },
    )
    density = Fraction(final_raw, normalization)
    parent_density = Fraction(center_raw, normalization)
    report = {
        "schema": "joint-coarse-fixed-phase-v1",
        "status": "exact_model_candidate_awaiting_independent_recount",
        "hypothesis": "Reoptimize coarse p,h jointly under the fixed phase/support assignment",
        "parent": str(PARENT.relative_to(ROOT)),
        "parent_candidate_sha256": sha256(PARENT / "graphon-candidate.json"),
        "phase_assignment_sha256": sha256(PARENT / "phase-assignment.json"),
        "fixed_phase_q": FIXED_Q,
        "original_parameters": [P0, H0],
        "selected_parameters": [p_value, h_value],
        "gradient_gate": gradient_gate,
        "line_optimizations": line_records,
        "coarse_profile_source": str(COARSE_PARENT.relative_to(ROOT)),
        "coarse_profile_sha256": sha256(COARSE_PARENT / "report.json"),
        "parent_phase_coefficients_recomputed": center_coefficients,
        "selected_phase_coefficients": final_coefficients,
        "numerator": final_raw,
        "normalization": normalization,
        "density": str(density),
        "decimal": float(density),
        "improvement_over_parent": str(parent_density - density),
        "raw_improvement_over_parent": center_raw - final_raw,
        "candidate_sha256": sha256(OUT / "graphon-candidate.json"),
        "source_sha256": sha256(Path(__file__)),
        "evaluations": len(cache),
        "timings": timings,
        "seconds": time.monotonic() - started,
        "evidence": "Exact coarse profile plus recomputed fixed-phase motif polynomial; candidate materialized and range/symmetry/marginals checked; independent ordered/Lean recount pending",
        "scope": "Three alternating exact coordinate-line sweeps in p,h with q and the phase/support assignment fixed; no global two-variable optimum claim.",
    }
    write_json(OUT / "report.json", report)
    print(
        json.dumps(
            {key: report[key] for key in ("status", "selected_parameters", "density", "decimal", "raw_improvement_over_parent", "evaluations", "seconds")},
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
