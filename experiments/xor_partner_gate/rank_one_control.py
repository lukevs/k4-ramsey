"""Reproducible bounded grid for equal-mass two-block rank-one XOR partners."""
import argparse
import hashlib
import itertools
import json
from pathlib import Path

from experiments.structural.profiles import CLASSES, EDGES

ROOT = Path(__file__).resolve().parents[2]
PROFILE = ROOT / "reports/xor-partner-e26-gate-005/report.json"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    if args.out.exists():
        raise FileExistsError(args.out)
    report = json.loads(PROFILE.read_text())
    denominator = report["profile_denominator"]
    g = [0.0] * 64
    for item, orbit in zip(report["unlabeled_profile"], CLASSES):
        for mask in orbit:
            g[mask] = item["numerator_total"] / len(orbit) / denominator

    def evaluate(p, a):
        total = mono = 0.0
        for signs in itertools.product((-1, 1), repeat=4):
            probabilities = [p + a*signs[i]*signs[j] for i, j in EDGES]
            for mask in range(64):
                probability = 1/16
                for bit, q in enumerate(probabilities):
                    probability *= q if mask >> bit & 1 else 1-q
                total += probability * (g[mask] + g[63 ^ mask])
                if mask in (0, 63):
                    mono += probability
        return total, mono

    best = None
    balanced = None
    trials = 0
    for ip in range(101):
        p = ip / 100
        radius = min(ip, 100-ip)
        for ia in range(-radius, radius+1):
            a = ia / 100
            value, mono = evaluate(p, a)
            trials += 1
            record = (value, p, a, mono)
            if best is None or record < best:
                best = record
            if ip == 50 and (balanced is None or record < balanced):
                balanced = record
    answer = {
        "schema": "xor-rank-one-two-block-control-v1",
        "family": "equal masses, W_H=p+a*s_x*s_y, integer p,a grid step 0.01, |a|<=min(p,1-p)",
        "trials": trials,
        "best": {"xor_density": best[0], "p": best[1], "a": best[2],
                 "partner_monochromatic_density": best[3]},
        "balanced_p_half_best": {"xor_density": balanced[0], "p": balanced[1],
                                 "a": balanced[2],
                                 "partner_monochromatic_density": balanced[3]},
        "parent_density": float(report["parent_monochromatic_density"].split("/")[0]) /
                          float(report["parent_monochromatic_density"].split("/")[1]),
        "scope": "floating bounded grid control; not continuous optimization or exact promotion evidence",
        "profile_report": str(PROFILE.relative_to(ROOT)),
        "profile_report_sha256": sha(PROFILE),
        "source_sha256": sha(Path(__file__)),
    }
    args.out.mkdir(parents=True)
    (args.out / "report.json").write_text(json.dumps(answer, indent=2) + "\n")
    print(json.dumps(answer, indent=2))


if __name__ == "__main__":
    main()
