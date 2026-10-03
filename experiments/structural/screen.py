"""Bounded deterministic exact-profile construction screen (not Lean evidence)."""
import argparse
import hashlib
import json
import time
from fractions import Fraction
from itertools import combinations_with_replacement
from pathlib import Path

from experiments.structural.profiles import (
    compose_graph, graph_from_mask, mono, nested_limit, profile, transform,
    xor_graph, xor_profiles,
)


def factors(n):
    unique = {}
    for mask in range(1 << (n * (n - 1) // 2)):
        rows = graph_from_mask(n, mask)
        p = profile(rows)
        unique.setdefault(p, {"n": n, "mask": mask, "rows": rows, "profile": p})
    return list(unique.values())


def run():
    started = time.monotonic()
    f3, f4 = factors(3), factors(4)
    unique16 = {}
    for a in f4:
        for b in f4:
            for operation in (xor_graph, compose_graph):
                rows = operation(a["rows"], b["rows"])
                p = profile(rows)
                unique16.setdefault(p, {"operation": operation.__name__,
                                        "a": a["mask"], "b": b["mask"], "profile": p})
    f16 = list(unique16.values())
    even = [i for i in range(64) if i.bit_count() % 2 == 0]
    spectra = [[transform(f["profile"])[i] for i in even] for f in f16]
    best = None
    trials = 0
    for small in f3:
        sp = [transform(small["profile"])[i] for i in even]
        for a, b in combinations_with_replacement(range(len(f16)), 2):
            numerator32 = sum(x*y*z for x, y, z in zip(sp, spectra[a], spectra[b]))
            assert numerator32 % 32 == 0
            numerator = numerator32 // 32
            trials += 1
            if best is None or numerator < best["numerator"]:
                best = {"numerator": numerator, "denominator": 768**4,
                        "density": str(Fraction(numerator, 768**4)),
                        "factors": [{"n": 3, "mask": small["mask"]}] +
                        [{k: v for k, v in f16[i].items() if k != "profile"}
                         for i in (a, b)]}
    finite_seconds = time.monotonic() - started
    # Broader, infinite-order diagnostic: not admissible to our fixed Lean checker.
    recursive_best = None
    recursive_trials = 0
    for core in factors(5):
        limit = nested_limit(core["rows"])
        for a, b in combinations_with_replacement(range(len(f4)), 2):
            result = xor_profiles(xor_profiles(f4[a]["profile"], f4[b]["profile"]), limit)
            value = mono(result)
            recursive_trials += 1
            if recursive_best is None or value < Fraction(recursive_best["density"]):
                recursive_best = {"density": str(value), "core_order": 5,
                                  "core_mask": core["mask"] ,
                                  "xor_factor_masks": [f4[a]["mask"], f4[b]["mask"]]}
    return {"schema": "k4-structural-screen-v1", "evidence": "exact Python profile arithmetic",
            "hypothesis": "Small XOR/composition factors provide competitive alternative constructions",
            "finite_scope": "XOR of one order3 factor and two order16 factors; each order16 is XOR or composition of two order4 graphs",
            "finite_factor_counts": {"order3": len(f3), "order4": len(f4), "order16": len(f16)},
            "finite_trials": trials, "finite_best": best, "finite_seconds": finite_seconds,
            "recursive_scope": "XOR of two order4 factors and a nested order5 core; outside current fixed-order Lean scope",
            "recursive_trials": recursive_trials, "recursive_best": recursive_best,
            "seconds": time.monotonic() - started,
            "code_hashes": {str(p): hashlib.sha256(p.read_bytes()).hexdigest()
                            for p in (Path(__file__), Path(__file__).with_name("profiles.py"))}}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    result = run()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x") as f:
        json.dump(result, f, indent=2)
        f.write("\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
