"""Bounded exact heterogeneous-recursion screens; outside fixed Lean scope."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time
from fractions import Fraction
from itertools import product

from research.experiments.structural.new_profiles import limiting_profiles
from research.experiments.structural.profiles import graph_from_mask, mono, profile, xor_graph, xor_profiles


def descriptor(rules):
    return [{"rows": list(rows), "children": list(children)} for rows, children in rules]


def experiment(seed=20260927):
    started = time.monotonic()
    rng = random.Random(seed)
    k3 = graph_from_mask(3, 7)
    k4 = graph_from_mask(4, 63)
    matching = ["0100", "1000", "0001", "0010"]
    xor_base = xor_profiles(profile(k4), profile(matching))
    q9 = xor_graph(k3, k3)
    best = None
    mechanism_best = None
    trials = improves_controls = 0
    records = []
    uniform_cache = {}

    def evaluate(rules, family):
        nonlocal best, mechanism_best, trials, improves_controls
        result = limiting_profiles(rules)
        for kind in range(2):
            value = mono(xor_profiles(xor_base, result[kind][4]))
            uniform_values = []
            for outer, _ in rules:
                key = tuple(outer)
                if key not in uniform_cache:
                    uniform = limiting_profiles([(outer, [0]*len(outer)), (outer, [1]*len(outer))])
                    uniform_cache[key] = mono(xor_profiles(xor_base, uniform[0][4]))
                uniform_values.append(uniform_cache[key])
            control = min(uniform_values)
            trials += 1
            improved = value < control
            improves_controls += improved
            record = {"family": family, "root_type": kind, "density": str(value),
                      "uniform_controls": [str(x) for x in uniform_values],
                      "improvement_over_better_control": str(control-value),
                      "rules": descriptor(rules)}
            if best is None or value < Fraction(best["density"]):
                best = record
                records.append({"trial": trials, "density": str(value), "family": family})
            if improved and (mechanism_best is None or control-value >
                             Fraction(mechanism_best["improvement_over_better_control"])):
                mechanism_best = record

    # Exhaust all two-type order-three rules (4 unlabeled cores ×8 child labels each).
    small = [graph_from_mask(3, mask) for mask in (0, 1, 3, 7)]
    rules3 = [(rows, assignment) for rows in small for assignment in product(range(2), repeat=3)]
    for a in rules3:
        for b in rules3:
            evaluate([a, b], "all_two_type_order3_rules")
    order3_seconds = time.monotonic()-started
    # A distinct, historically competitive core: Q9 against one-edge perturbations.
    # Child labels are heterogeneous and may differ between the two rule types.
    perturbations = []
    for color in "01":
        u, v = next((u, v) for u in range(9) for v in range(u+1, 9) if q9[u][v] == color)
        changed = [list(row) for row in q9]
        changed[u][v] = changed[v][u] = "1" if color == "0" else "0"
        perturbations.append(["".join(row) for row in changed])
    for changed in perturbations:
        for attempt in range(64):
            if attempt < 9:
                children0 = [int(i == attempt) for i in range(9)]
                children1 = [0]*9
            else:
                children0 = [rng.randrange(2) for _ in range(9)]
                children1 = [rng.randrange(2) for _ in range(9)]
            evaluate([(q9, children0), (changed, children1)], "q9_and_one_edge_perturbation")
    return {"schema": "heterogeneous-recursion-screen-v1", "seed": seed,
            "evidence": "exact rational profile screen; not independently Lean checked",
            "objective": "K4+blueK4 density of K4 XOR M4 XOR root recursive profile",
            "prediction": "Heterogeneous child types beat both corresponding homogeneous recursive controls",
            "trials_counting_both_root_types": trials, "trials_improving_both_controls": improves_controls,
            "best": best, "largest_mechanism_gain": mechanism_best, "progress": records,
            "order3_seconds": order3_seconds, "seconds": time.monotonic()-started,
            "source_hashes": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                              [Path(__file__), Path(__file__).with_name("new_profiles.py"),
                               Path(__file__).with_name("profiles.py")]}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result = experiment()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
