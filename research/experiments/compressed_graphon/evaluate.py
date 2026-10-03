"""CLI for exact evaluation/minimization of canonical polynomial records."""

import argparse
import json
from pathlib import Path
import time

from .polynomial import ExactPolynomial


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("record", type=Path)
    parser.add_argument("--q", type=int)
    parser.add_argument("--minimize", action="store_true")
    args = parser.parse_args()
    load_start = time.monotonic()
    polynomial = ExactPolynomial.from_record(json.loads(args.record.read_text()))
    load_seconds = time.monotonic()-load_start
    output: dict[str, object] = {"load_seconds": load_seconds}
    evaluation_start = time.monotonic()
    if args.q is not None:
        output.update(q=args.q, raw_numerator=str(polynomial.raw(args.q)), density=str(polynomial.density(args.q)))
    if args.minimize:
        result = polynomial.minimize_integer()
        output["minimum"] = {
            "raw_numerator": str(result.value), "minimizers": result.minimizers,
            "interval": result.interval, "evaluations": result.evaluations,
        }
    output["evaluation_seconds"] = time.monotonic()-evaluation_start
    print(json.dumps(output, indent=2))


if __name__ == "__main__":
    main()
