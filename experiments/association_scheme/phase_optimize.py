"""One preregistered exact-factor coordinate run for cyclic r=5 phases/support."""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import time


ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
PARENT = ROOT / "reports/literature-two-parameter-001"
CONTROL = ROOT / "reports/association-scheme-r5-001"
OUT = ROOT / "reports/association-scheme-phase-001"
CPP = HERE / "ordered_graphon_u256.cpp"
R = 5
Q_CONTROL = -2611
MAX_SWEEPS = 8
MAX_SECONDS = 180
EDGES = ((0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3))
MOTIFS = {
    3: ((0, 1), (0, 2), (1, 2)),
    4: ((0, 1), (1, 2), (2, 3), (0, 3)),
    5: tuple(edge for edge in EDGES if edge != (0, 1)),
    6: EDGES,
}


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def kernel(x):
    return 3 if x % R in (1, 4) else -2


class PhaseModel:
    def __init__(self, p, denominator):
        self.p = p
        self.denominator = denominator
        self.n = len(p)
        self.edge_list = [
            (i, j)
            for i in range(self.n)
            for j in range(i + 1, self.n)
            if 0 < p[i][j] < denominator
        ]
        self.edge_index = {edge: index for index, edge in enumerate(self.edge_list)}
        self.neighbors = [set() for _ in range(self.n)]
        for i, j in self.edge_list:
            self.neighbors[i].add(j)
            self.neighbors[j].add(i)
        self.moment_cache = {}
        self.factors = self._build_factors()
        self.incident = [[] for _ in self.edge_list]
        for factor_index, factor in enumerate(self.factors):
            for variable in set(item[0] for item in factor[1]):
                self.incident[variable].append(factor_index)

    def signed_variable(self, i, j):
        assert i != j
        edge = (i, j) if i < j else (j, i)
        return self.edge_index[edge], (1 if i < j else -1)

    def signature(self, vertices, selected):
        return tuple(self.signed_variable(vertices[u], vertices[v]) for u, v in selected)

    def _build_factors(self):
        aggregate = defaultdict(int)
        p, qden, n, nbr = self.p, self.denominator, self.n, self.neighbors

        # Triangle factor, compressed over the fourth coarse position.
        for i in range(n):
            for j in nbr[i]:
                if j <= i:
                    continue
                for k in nbr[i] & nbr[j]:
                    if k <= j:
                        continue
                    weight = 24 * sum(
                        p[i][l] * p[j][l] * p[k][l]
                        - (qden - p[i][l]) * (qden - p[j][l]) * (qden - p[k][l])
                        for l in range(n)
                    )
                    aggregate[(3, self.signature((i, j, k, 0), MOTIFS[3]))] += weight

        # One canonical C4 times its three labeled choices.
        for i in range(n):
            for j in nbr[i]:
                for k in nbr[j]:
                    for l in nbr[k] & nbr[i]:
                        weight = 3 * (
                            p[i][k] * p[j][l]
                            + (qden - p[i][k]) * (qden - p[j][l])
                        )
                        aggregate[(4, self.signature((i, j, k, l), MOTIFS[4]))] += weight

        # One canonical missing edge times six choices.
        for i in range(n):
            for j in range(n):
                common = nbr[i] & nbr[j]
                for k in common:
                    for l in common & nbr[k]:
                        weight = 6 * (2 * p[i][j] - qden)
                        aggregate[(5, self.signature((i, j, k, l), MOTIFS[5]))] += weight

        # Full K4, with equal red and blue contributions.
        for i in range(n):
            for j in nbr[i]:
                common = nbr[i] & nbr[j]
                for k in common:
                    for l in common & nbr[k]:
                        aggregate[(6, self.signature((i, j, k, l), MOTIFS[6]))] += 2

        return [
            (degree, signature, weight)
            for (degree, signature), weight in aggregate.items()
            if weight
        ]

    def moment(self, degree, phases):
        key = (degree, phases)
        answer = self.moment_cache.get(key)
        if answer is not None:
            return answer
        answer = 0
        for types in product(range(R), repeat=4):
            term = 1
            for (u, v), phase_value in zip(MOTIFS[degree], phases):
                term *= kernel(types[u] - types[v] - phase_value)
            answer += term
        self.moment_cache[key] = answer
        return answer

    def factor_coefficient(self, factor, states):
        degree, signature, weight = factor
        phases = []
        for variable, sign in signature:
            state = states[variable]
            if state < 0:
                return 0
            phases.append((sign * state) % R)
        return weight * self.moment(degree, tuple(phases))

    def coefficients(self, states):
        answer = {degree: 0 for degree in range(3, 7)}
        for factor in self.factors:
            answer[factor[0]] += self.factor_coefficient(factor, states)
        return answer

    def objective(self, states, q):
        coefficients = self.coefficients(states)
        return sum(coefficients[d] * q**d for d in range(3, 7)), coefficients

    def coordinate_descent(self, states, q, deadline):
        states = list(states)
        history = []
        objective, coefficients = self.objective(states, q)
        history.append({"sweep": 0, "objective": objective, "moves": 0,
                        "active": sum(state >= 0 for state in states),
                        "coefficients": coefficients})
        for sweep in range(1, MAX_SWEEPS + 1):
            moves = 0
            for variable in range(len(states)):
                if time.monotonic() >= deadline:
                    history.append({"sweep": sweep, "objective": objective,
                                    "moves": moves, "terminated": "time_limit",
                                    "active": sum(state >= 0 for state in states)})
                    return states, history
                affected = self.incident[variable]
                old_state = states[variable]
                old_local = sum(
                    self.factor_coefficient(self.factors[index], states)
                    * q ** self.factors[index][0]
                    for index in affected
                )
                best_state, best_local = old_state, old_local
                for trial in (-1, 0, 1, 2, 3, 4):
                    if trial == old_state:
                        continue
                    states[variable] = trial
                    value = sum(
                        self.factor_coefficient(self.factors[index], states)
                        * q ** self.factors[index][0]
                        for index in affected
                    )
                    if value < best_local:
                        best_state, best_local = trial, value
                states[variable] = best_state
                if best_state != old_state:
                    objective += best_local - old_local
                    moves += 1
            checked, coefficients = self.objective(states, q)
            assert checked == objective
            history.append({"sweep": sweep, "objective": objective, "moves": moves,
                            "active": sum(state >= 0 for state in states),
                            "coefficients": coefficients})
            if moves == 0:
                break
        return states, history


def materialize(base, denominator, q, edge_index, states):
    n = len(base)
    matrix = []
    for ia in range(R * n):
        i, a = divmod(ia, R)
        row = []
        for jb in range(R * n):
            j, b = divmod(jb, R)
            value = base[i][j]
            if i != j and 0 < value < denominator:
                edge = (i, j) if i < j else (j, i)
                state = states[edge_index[edge]]
                if state >= 0:
                    oriented = state if i < j else -state
                    value += q * kernel(a - b - oriented)
            row.append(value)
        matrix.append(row)
    return matrix


def literal_counts(matrix, denominator):
    red_answer = blue_answer = 0
    for vertices in product(range(len(matrix)), repeat=4):
        red = blue = 1
        for u, v in EDGES:
            value = matrix[vertices[u]][vertices[v]]
            red *= value
            blue *= denominator - value
        red_answer += red
        blue_answer += blue
    return red_answer, blue_answer, red_answer + blue_answer


def tiny_checks():
    fixtures = [
        ([[0, 4, 5], [4, 0, 6], [5, 6, 0]], 10),
        ([[0, 4, 7, 5], [4, 0, 6, 3], [7, 6, 0, 4], [5, 3, 4, 0]], 10),
    ]
    results = []
    for base, denominator in fixtures:
        model = PhaseModel(base, denominator)
        assignments = [
            [1] * len(model.edge_list),
            [(-1 if index % 3 == 0 else index % 5) for index in range(len(model.edge_list))],
        ]
        base_raw = literal_counts(base, denominator)[2]
        for q in (-1, 1):
            for states in assignments:
                matrix = materialize(base, denominator, q, model.edge_index, states)
                if not all(0 <= x <= denominator for row in matrix for x in row):
                    continue
                objective, coefficients = model.objective(states, q)
                actual = literal_counts(matrix, denominator)[2]
                predicted = base_raw * R**4 + objective
                assert actual == predicted
                results.append({"base_order": len(base), "q": q,
                                "states": states, "coefficients": coefficients,
                                "predicted_raw": predicted, "actual_raw": actual,
                                "repeated_coarse_indices_included": True})
    return results


def feasible_interval(base, denominator, model, states):
    active_values = {
        base[i][j]
        for (i, j), state in zip(model.edge_list, states)
        if state >= 0
    }
    if not active_values:
        return 0, 0
    lo, hi = -denominator, denominator
    for value in active_values:
        valid = [q for q in range(-denominator, denominator + 1)
                 if 0 <= value - 2*q <= denominator
                 and 0 <= value + 3*q <= denominator]
        lo, hi = max(lo, min(valid)), min(hi, max(valid))
    return lo, hi


def checker_payload(matrix, denominator):
    return f"{len(matrix)} {denominator}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix
    ) + "\n"


def main():
    start = time.monotonic()
    prereg = json.loads((HERE / "phase_preregistration.json").read_text())
    tests = tiny_checks()
    parent_bytes = (PARENT / "graphon-candidate.json").read_bytes()
    parent = json.loads(parent_bytes)
    parent_report = json.loads((PARENT / "report.json").read_text())
    control_report = json.loads((CONTROL / "report.json").read_text())
    base = parent["red_probability_numerators"]
    denominator = parent["edge_probability_denominator"]
    assert len(base) == 192 and denominator == 65536
    assert prereg["optimization_q"] == Q_CONTROL

    model = PhaseModel(base, denominator)
    assert len(model.edge_list) == 1248
    control_states = [1] * len(model.edge_list)
    control_objective, control_coefficients = model.objective(control_states, Q_CONTROL)
    coefficient_control = json.loads(
        (ROOT / "reports/association-scheme-coefficients-001/report.json").read_text()
    )
    expected_coefficients = {
        int(key): value for key, value in coefficient_control["raw_polynomial_coefficients"].items()
    }
    assert control_coefficients == expected_coefficients
    assert control_objective == coefficient_control["selected_delta_raw"]

    optimize_start = time.monotonic()
    states, history = model.coordinate_descent(
        control_states, Q_CONTROL, optimize_start + MAX_SECONDS
    )
    optimize_seconds = time.monotonic() - optimize_start
    coefficients = model.coefficients(states)
    lo, hi = feasible_interval(base, denominator, model, states)
    delta_by_q = {
        q: sum(coefficients[d] * q**d for d in range(3, 7))
        for q in range(lo, hi + 1)
    }
    selected_q = min(delta_by_q, key=lambda q: (delta_by_q[q], q))
    selected_delta = delta_by_q[selected_q]
    parent_density = Fraction(parent_report["density"])
    order = R * len(base)
    normalization = order**4 * denominator**6
    predicted = parent_density + Fraction(selected_delta, normalization)
    control_density = Fraction(control_report["actual_density"])
    admit = predicted < control_density

    OUT.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, OUT / "source_snapshot.py")
    shutil.copy2(CPP, OUT / "checker_snapshot.cpp")
    shutil.copy2(HERE / "phase_preregistration.json", OUT / "preregistration.json")
    phase_assignment = {
        f"{i},{j}": state
        for (i, j), state in zip(model.edge_list, states)
    }
    write_json(OUT / "phase-assignment.json", phase_assignment)
    preliminary = {
        "schema": "association-scheme-phase-optimization-v1",
        "status": "predicted_candidate" if admit else "completed_without_recount",
        "hypothesis": "H-F2-01B exact cyclic phase/support Max-CSP",
        "parent": str(PARENT.relative_to(ROOT)),
        "parent_candidate_sha256": hashlib.sha256(parent_bytes).hexdigest(),
        "control": str(CONTROL.relative_to(ROOT)),
        "control_candidate_sha256": sha256(CONTROL / "graphon-candidate.json"),
        "variables": len(model.edge_list),
        "states_per_variable": 6,
        "factor_count": len(model.factors),
        "factor_counts_by_degree": {str(d): sum(f[0] == d for f in model.factors) for d in range(3, 7)},
        "control_q": Q_CONTROL,
        "control_coefficients": control_coefficients,
        "control_objective": control_objective,
        "history": history,
        "optimization_seconds": optimize_seconds,
        "active_edges": sum(state >= 0 for state in states),
        "inactive_edges": sum(state < 0 for state in states),
        "phase_histogram": {str(s): states.count(s) for s in range(-1, 5)},
        "coefficients": coefficients,
        "feasible_q": [lo, hi],
        "selected_q": selected_q,
        "selected_epsilon": str(Fraction(selected_q, denominator)),
        "selected_delta_raw": selected_delta,
        "predicted_density": str(predicted),
        "predicted_decimal": float(predicted),
        "control_density": str(control_density),
        "predicted_improvement_over_control": str(control_density - predicted),
        "admitted_recount": admit,
        "tiny_exact_tests": tests,
        "micro_moment_cache_entries": len(model.moment_cache),
        "phase_assignment_sha256": sha256(OUT / "phase-assignment.json"),
        "source_sha256": sha256(Path(__file__)),
        "scope": "One deterministic coordinate run from the sign(j-i) control; no restart, seed, kernel sweep, record or optimality claim.",
    }
    write_json(OUT / "optimization.json", preliminary)
    if not admit:
        print(json.dumps({k: preliminary[k] for k in ("status", "predicted_density", "active_edges", "history")}, indent=2))
        return

    matrix = materialize(base, denominator, selected_q, model.edge_index, states)
    assert all(0 <= x <= denominator for row in matrix for x in row)
    assert all(matrix[i][j] == matrix[j][i] for i in range(order) for j in range(order))
    for i in range(len(base)):
        for j in range(len(base)):
            assert sum(matrix[R*i+a][R*j+b] for a in range(R) for b in range(R)) == R*R*base[i][j]
    write_json(OUT / "graphon-candidate.json", {
        "schema": "rational-step-graphon-v1",
        "block_weights": [1] * order,
        "edge_probability_denominator": denominator,
        "red_probability_numerators": matrix,
    })

    binary = OUT / "ordered_graphon_u256"
    compile_command = ["c++", "-O3", "-std=c++17", str(CPP), "-o", str(binary)]
    subprocess.run(compile_command, check=True, timeout=60)
    tiny_matrix = materialize(
        [[0, 4, 5], [4, 0, 6], [5, 6, 0]], 10, -1,
        PhaseModel([[0, 4, 5], [4, 0, 6], [5, 6, 0]], 10).edge_index,
        [1, -1, 3],
    )
    tiny_expected = literal_counts(tiny_matrix, 10)
    tiny_actual = tuple(map(int, subprocess.check_output(
        [str(binary)], input=checker_payload(tiny_matrix, 10), text=True, timeout=30
    ).split()))
    assert tiny_actual == tiny_expected

    run_start = time.monotonic()
    red, blue, total = map(int, subprocess.check_output(
        [str(binary)], input=checker_payload(matrix, denominator), text=True, timeout=600
    ).split())
    run_seconds = time.monotonic() - run_start
    actual = Fraction(total, normalization)
    assert actual == predicted
    preliminary.update({
        "status": "independent_generic_ordered_recount_passed",
        "red": red,
        "blue": blue,
        "numerator": total,
        "normalization": normalization,
        "actual_density": str(actual),
        "actual_decimal": float(actual),
        "actual_improvement_over_control": str(control_density - actual),
        "candidate_sha256": sha256(OUT / "graphon-candidate.json"),
        "checker_source_sha256": sha256(CPP),
        "checker_binary_sha256": sha256(binary),
        "compile_command": compile_command,
        "run_command": [str(binary)],
        "run_seconds": run_seconds,
        "total_seconds": time.monotonic() - start,
        "tiny_checker_expected": tiny_expected,
        "tiny_checker_actual": tiny_actual,
        "coarse_marginals_exactly_preserved": True,
        "machine": platform.platform(),
        "evidence": "Exact motif-factor optimization and prediction followed by a generic direct ordered-index U256 recount of the explicit 960-step matrix.",
    })
    write_json(OUT / "report.json", preliminary)
    print(json.dumps({k: preliminary[k] for k in ("status", "actual_density", "actual_decimal", "actual_improvement_over_control", "active_edges", "phase_histogram", "run_seconds", "total_seconds")}, indent=2))


if __name__ == "__main__":
    main()
