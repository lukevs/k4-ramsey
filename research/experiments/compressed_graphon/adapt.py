"""Print a canonical polynomial record adapted from an existing report."""

import argparse
import json
from pathlib import Path
import time

from .adapters import adapt_degree_map_report, adapt_total_coefficients_report


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", required=True, choices=("total-coefficients", "degree-map"))
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--parent-report", type=Path)
    parser.add_argument("--base-order", required=True, type=int)
    parser.add_argument("--latent-order", required=True, type=int)
    parser.add_argument("--probability-denominator", required=True, type=int)
    args = parser.parse_args()
    started = time.monotonic()
    report = json.loads(args.report.read_text())
    common = dict(source_path=str(args.report), base_order=args.base_order,
                  latent_order=args.latent_order,
                  probability_denominator=args.probability_denominator)
    if args.kind == "total-coefficients":
        record = adapt_total_coefficients_report(report, **common)
    else:
        if args.parent_report is None:
            parser.error("--parent-report is required for degree-map")
        parent = json.loads(args.parent_report.read_text())
        record = adapt_degree_map_report(
            report, parent, parent_path=str(args.parent_report), **common,
        )
    record["adapter_generation_seconds"] = time.monotonic()-started
    print(json.dumps(record, indent=2))


if __name__ == "__main__":
    main()
