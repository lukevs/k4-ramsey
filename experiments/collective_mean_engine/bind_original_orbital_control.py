"""Bind the original parent to the same 24-orbital relation matrix."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


EXPECTED = "515776850799050572477656236153/17113283103081096920205493272576"


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--softened-config", type=Path, required=True)
    parser.add_argument("--audit", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    config = json.loads(args.softened_config.read_text())
    audit = json.loads(args.audit.read_text())
    config["probability_numerators"] = audit["parent_probability_numerators"]
    config["constraint_group_ids"] = [-1] * config["relation_count"]
    config["expected_parent_fraction"] = EXPECTED
    config["consumer_scope"] = "Frozen original parent in the same 24 symmetric orbital coordinates."
    args.out.write_text(json.dumps(config, indent=2, sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
