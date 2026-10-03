"""Exact small portfolio of alternative 192-by-four quotients of the 768 seed."""
from collections import defaultdict
from fractions import Fraction
import hashlib
import json
import math
from pathlib import Path
import random
import shutil
import subprocess
import time

from experiments.algebraic.lift import discover_fibers, decompose, half_blocks
from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


Q = 65536


class Counter:
    def __init__(self, binary, classes, parameter_count):
        self.p = subprocess.Popen([str(binary)], stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, text=True)
        self.p.stdin.write(f"{len(classes)} {parameter_count}\n" +
                           "\n".join(" ".join(map(str, row)) for row in classes) + "\n")
        self.p.stdin.flush()

    def __call__(self, denominator, parameters):
        self.p.stdin.write(" ".join(map(str, [denominator, *parameters])) + "\n")
        self.p.stdin.flush()
        return int(self.p.stdout.readline())

    def close(self):
        self.p.stdin.close()
        self.p.wait(timeout=10)


def unique_classes(n):
    classes = [[-1] * n for _ in range(n)]
    coords = []
    for i in range(n):
        for j in range(i + 1):
            c = len(coords)
            coords.append((i, j))
            classes[i][j] = classes[j][i] = c
    return classes, coords


def direct_numerator(matrix, denominator):
    """Slow tiny ordered-index oracle."""
    n = len(matrix)
    answer = 0
    for color in range(2):
        p = matrix if color == 0 else [[denominator - x for x in row] for row in matrix]
        for i in range(n):
            for j in range(n):
                for k in range(n):
                    for l in range(n):
                        answer += (p[i][j] * p[i][k] * p[i][l] *
                                   p[j][k] * p[j][l] * p[k][l])
    return answer


def matrix_to_parameters(matrix, coords):
    return [matrix[i][j] for i, j in coords]


def parameters_to_matrix(parameters, coords, n):
    matrix = [[0] * n for _ in range(n)]
    for x, (i, j) in zip(parameters, coords):
        matrix[i][j] = matrix[j][i] = x
    return matrix


def block_average(rows, partition):
    n = len(partition)
    matrix = [[0] * n for _ in range(n)]
    for i, left in enumerate(partition):
        for j in range(i + 1):
            right = partition[j]
            count = sum(rows[u][v] == "1" for u in left for v in right)
            x = count * (Q // 16)
            matrix[i][j] = matrix[j][i] = x
    return matrix


def half_regroupings(rows, fibers, halves):
    red, blue = [], []
    for i, j, pattern in halves:
        left, right = fibers[i], fibers[j]
        groups = defaultdict(list)
        for a, mask in enumerate(pattern):
            groups[mask].append(a)
        if sorted(map(len, groups.values())) != [2, 2]:
            raise RuntimeError("degree-two block is not two K2,2 components")
        masks = sorted(groups)
        a0 = [left[a] for a in groups[masks[0]]]
        a1 = [left[a] for a in groups[masks[1]]]
        b0 = [right[b] for b in range(4) if masks[0] >> b & 1]
        b1 = [right[b] for b in range(4) if not (masks[0] >> b & 1)]
        if set(b0) != {right[b] for b in range(4) if not (masks[1] >> b & 1)}:
            raise RuntimeError("unexpected K2,2 complement pattern")
        red.extend((sorted(a0 + b0), sorted(a1 + b1)))
        blue.extend((sorted(a0 + b1), sorted(a1 + b0)))
    return red, blue


def defect_graph(blocks, count):
    adjacency = [set() for _ in range(count)]
    lookup = {}
    for i, j, missing in blocks:
        adjacency[i].add(j)
        adjacency[j].add(i)
        lookup[(i, j)] = missing
    return adjacency, lookup


def deterministic_perfect_matching(adjacency, salt):
    unmatched = set(range(len(adjacency)))
    result = []

    def rank(u, v):
        return ((u + 1) * 0x9E3779B1 ^ (v + 3) * 0x85EBCA77 ^ salt * 0xC2B2AE3D) & 0xffffffff

    def search():
        if not unmatched:
            return True
        possible = [(sum(v in unmatched for v in adjacency[u]), u) for u in unmatched]
        _, u = min(possible)
        neighbors = sorted((v for v in adjacency[u] if v in unmatched),
                           key=lambda v: (rank(u, v), v))
        unmatched.remove(u)
        for v in neighbors:
            unmatched.remove(v)
            result.append((u, v))
            if search():
                return True
            result.pop()
            unmatched.add(v)
        unmatched.add(u)
        return False

    if not search():
        raise RuntimeError("defect graph matching search failed")
    return sorted(tuple(sorted(edge)) for edge in result)


def defect_regrouping(fibers, matching, lookup, pairing_index):
    pairings = (((0, 1), (2, 3)), ((0, 2), (1, 3)), ((0, 3), (1, 2)))
    result = []
    for a, b in matching:
        i, j = max(a, b), min(a, b)
        missing = lookup[(i, j)]
        edges = [(fibers[i][s], fibers[j][missing[s]]) for s in range(4)]
        for x, y in pairings[pairing_index]:
            result.append(sorted(edges[x] + edges[y]))
    return result


def random_local_regrouping(fibers, halves, seed):
    rng = random.Random(seed)
    result = []
    for i, j, _ in halves:
        left, right = list(fibers[i]), list(fibers[j])
        rng.shuffle(left)
        rng.shuffle(right)
        if rng.randrange(2):
            right = right[2:] + right[:2]
        result.extend((sorted(left[:2] + right[:2]),
                       sorted(left[2:] + right[2:])))
    return result


def global_random_partition(order, seed):
    vertices = list(range(order))
    random.Random(seed).shuffle(vertices)
    return [sorted(vertices[i:i + 4]) for i in range(0, order, 4)]


def validate_partition(partition, order):
    if len(partition) != order // 4 or any(len(cell) != 4 for cell in partition):
        raise RuntimeError("partition shape mismatch")
    if sorted(v for cell in partition for v in cell) != list(range(order)):
        raise RuntimeError("partition does not cover vertices exactly")


def gradients(binary, parameters, coords, n):
    matrix = parameters_to_matrix(parameters, coords, n)
    payload = str(n) + "\n" + "\n".join(
        " ".join(str(x / Q) for x in row) for row in matrix) + "\n"
    output = subprocess.check_output([str(binary)], input=payload, text=True, timeout=30)
    result = []
    for expected, line in zip(coords, output.splitlines()):
        i, j, value = line.split()
        if (int(i), int(j)) != expected:
            raise RuntimeError("gradient coordinate order mismatch")
        result.append(float(value))
    if len(result) != len(coords):
        raise RuntimeError("gradient length mismatch")
    return result


def optimize(name, start, counter, gradient_binary, coords, n, deadline):
    current = list(start)
    value = counter(Q, current)
    initial = value
    m = [0.0] * len(current)
    v = [0.0] * len(current)
    history = [{"iteration": 0, "numerator": value}]
    for iteration in range(1, 11):
        if time.monotonic() >= deadline:
            break
        g = gradients(gradient_binary, current, coords, n)
        for e, ge in enumerate(g):
            m[e] = .9 * m[e] + .1 * ge
            v[e] = .999 * v[e] + .001 * ge * ge
        mscale, vscale = 1 - .9 ** iteration, 1 - .999 ** iteration
        direction = [(me / mscale) / (math.sqrt(ve / vscale) + 1e-12)
                     for me, ve in zip(m, v)]
        options = [(value, 0, current)]
        for step in (.0005, .001, .002, .005, .01, .02):
            trial = [min(Q, max(0, round(x - step * Q * d)))
                     for x, d in zip(current, direction)]
            options.append((counter(Q, trial), step, trial))
        chosen_value, chosen_step, chosen = min(options, key=lambda x: (x[0], x[1]))
        history.append({"iteration": iteration, "numerator": chosen_value,
                        "delta_from_start": chosen_value - initial,
                        "step": chosen_step,
                        "boundary_coordinates": sum(x in (0, Q) for x in chosen)})
        if chosen_value >= value:
            break
        current, value = chosen, chosen_value
    return current, value, initial, history


def ordered_recount(binary, matrix):
    payload = f"{len(matrix)} {Q}\n" + "\n".join(
        " ".join(map(str, row)) for row in matrix) + "\n"
    return tuple(map(int, subprocess.check_output(
        [str(binary)], input=payload, text=True, timeout=40).split()))


def main():
    started = time.monotonic()
    deadline = started + 285
    out = ROOT / "reports/quotient-portfolio-002"
    out.mkdir(parents=True, exist_ok=False)
    shutil.copy2(__file__, out / "source_snapshot.py")
    shutil.copy2(ROOT / "experiments/quotient_portfolio/preregistration.json",
                 out / "preregistration.json")
    source = ROOT / "data/published_cayley_768.json"
    rows = json.loads(source.read_text())["red_rows"]
    fibers = discover_fibers(rows)
    blocks, block_counts = decompose(rows, fibers)
    halves = half_blocks(rows, fibers)
    adjacency, lookup = defect_graph(blocks, len(fibers))
    red, blue = half_regroupings(rows, fibers, halves)

    matchings = [deterministic_perfect_matching(adjacency, salt) for salt in (1, 2, 3)]
    if len({tuple(m) for m in matchings}) != 3:
        raise RuntimeError("defect matching controls were not distinct")
    bank = [
        ("original_four_sheet", fibers, "control"),
        ("degree2_red_K22", red, "structured"),
        ("degree2_blue_K22", blue, "structured"),
    ]
    bank += [(f"degree3_matching_{i}", defect_regrouping(
        fibers, matching, lookup, i), "structured")
             for i, matching in enumerate(matchings)]
    bank += [
        ("random_local_2plus2", random_local_regrouping(fibers, halves, 0x51A7), "control"),
        ("random_global_four", global_random_partition(len(rows), 0x51A7), "control"),
    ]
    for _, partition, _ in bank:
        validate_partition(partition, len(rows))

    class_binary = ROOT / "reports/literature-class-graphon-001/counter"
    gradient_binary = ROOT / "reports/literature-graphon-gradient-001/gradient"
    ordered_binary = ROOT / "reports/literature-two-parameter-001/ordered_counter"

    # Tiny oracle: exact class counter equals a literal ordered four-loop sum.
    tiny = [[0, 1, 2, 3], [1, 4, 0, 2], [2, 0, 3, 1], [3, 2, 1, 4]]
    tiny_classes, tiny_coords = unique_classes(4)
    tiny_counter = Counter(class_binary, tiny_classes, len(tiny_coords))
    tiny_count = tiny_counter(5, matrix_to_parameters(tiny, tiny_coords))
    tiny_counter.close()
    tiny_direct = direct_numerator(tiny, 5)
    if tiny_count != tiny_direct:
        raise RuntimeError("tiny partition counter oracle mismatch")

    classes, coords = unique_classes(192)
    counter = Counter(class_binary, classes, len(coords))
    denominator = Q ** 6 * 192 ** 4
    # Frozen parent reproduction using the same all-coordinate class counter.
    parent_path = ROOT / "reports/literature-two-parameter-001/graphon-candidate.json"
    parent = json.loads(parent_path.read_text())["red_probability_numerators"]
    parent_count = counter(Q, matrix_to_parameters(parent, coords))
    parent_expected = Fraction(json.loads(
        (ROOT / "reports/literature-two-parameter-001/report.json").read_text())["density"])
    if Fraction(parent_count, denominator) != parent_expected:
        raise RuntimeError("frozen parent reproduction failed")

    records = []
    best = None
    for name, partition, kind in bank:
        if time.monotonic() >= deadline:
            break
        average = block_average(rows, partition)
        start_parameters = matrix_to_parameters(average, coords)
        parameters, value, initial, history = optimize(
            name, start_parameters, counter, gradient_binary, coords, 192, deadline)
        matrix = parameters_to_matrix(parameters, coords, 192)
        red_count, blue_count, ordered = ordered_recount(ordered_binary, matrix)
        if ordered != value:
            raise RuntimeError(f"independent recount mismatch for {name}")
        record = {
            "name": name, "kind": kind, "initial_numerator": initial,
            "numerator": value, "delta_optimization": value - initial,
            "density": str(Fraction(value, denominator)),
            "decimal": float(Fraction(value, denominator)),
            "iterations": len(history) - 1, "history": history,
            "ordered_red": red_count, "ordered_blue": blue_count,
            "partition_sha256": hashlib.sha256(json.dumps(partition).encode()).hexdigest(),
            "matrix_sha256": hashlib.sha256(json.dumps(matrix).encode()).hexdigest(),
        }
        records.append(record)
        write_json(out / f"{name}-partition.json", partition)
        write_json(out / f"{name}-matrix.json", matrix)
        if best is None or value < best[0]:
            best = (value, name, matrix)
    counter.close()
    if best is None:
        raise RuntimeError("deadline expired before first portfolio member")
    best_value, best_name, best_matrix = best
    candidate = {
        "schema": "rational-step-graphon-v1",
        "block_weights": [1] * 192,
        "red_probability_numerators": best_matrix,
        "edge_probability_denominator": Q,
    }
    write_json(out / "graphon-candidate.json", candidate)
    report = {
        "hypothesis": "H-QP-001 alternative intrinsic four-vertex quotients",
        "source": str(source), "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
        "members_planned": len(bank), "members_completed": len(records),
        "block_counts": block_counts, "tiny_oracle": {"class": tiny_count, "direct": tiny_direct},
        "parent_reproduction": {"numerator": parent_count, "density": str(parent_expected)},
        "records": records, "best_name": best_name, "numerator": best_value,
        "denominator": denominator, "density": str(Fraction(best_value, denominator)),
        "decimal": float(Fraction(best_value, denominator)),
        "candidate_sha256": hashlib.sha256((out / "graphon-candidate.json").read_bytes()).hexdigest(),
        "seconds": time.monotonic() - started,
        "evidence": "Tiny literal oracle; exact C++128 all-coordinate search counts; every retained member independently recounted by direct ordered-index C++128",
        "scope": "Eight equal-size-four partitions and at most10 matched projected-Adam iterations; a negative does not exclude other partitions or optimizer budgets",
    }
    write_json(out / "report.json", report)
    print(json.dumps({k: report[k] for k in (
        "members_completed", "best_name", "numerator", "density", "decimal", "seconds")}, indent=2))


if __name__ == "__main__":
    main()
