"""Bind the frozen softened-orbital baseline and release all orbital means."""
from __future__ import annotations

import argparse
import json
from fractions import Fraction
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--control", type=Path, required=True)
    parser.add_argument("--report", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.control.read_text())
    report = json.loads(args.report.read_text())
    if report["constraint_dimension"] != 0 or report["parent_numerator"] != report["rounded_numerator"]:
        raise RuntimeError("frozen control mismatch")
    expected = Fraction(int(report["parent_numerator"]), int(report["parent_denominator"]))
    config["constraint_group_ids"] = [-2] * config["relation_count"]
    config["expected_parent_fraction"] = str(expected)
    config["consumer_scope"] = "Single delta=1/8 softened start with all symmetric orbital means free."
    args.out.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
