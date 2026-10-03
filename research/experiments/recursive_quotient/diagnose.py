"""Exact equality-type diagnosis for the immutable H-TR3-1 report."""
from fractions import Fraction
import hashlib
import json
from pathlib import Path

from k4_ramsey.engine import ROOT
from k4_ramsey.lab import write_json


SOURCE = ROOT / "reports/recursive-quotient-first-difference-001/report.json"
OUT = ROOT / "reports/recursive-quotient-first-difference-diagnostic-001"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def diagnose(result):
    b, q = result["B"], result["Q"]
    answer = {}
    for color in ("red", "blue"):
        s1, s2, s3, s4, triangle, paired, clique4 = result["colors"][color]["terms"]
        t2 = Fraction(result["colors"][color]["T2"])
        t3 = Fraction(result["colors"][color]["T3"])
        t4 = Fraction(result["colors"][color]["T4"])
        if color == "red":
            deltas = {
                "1111": Fraction(0),
                "211": 6 * t2 * Fraction(paired, q**5 * b**4),
                "22": 3 * t2**2 * Fraction(s4, q**4 * b**4),
                "31": 4 * t3 * Fraction(s3, q**3 * b**4),
                "4": Fraction(t4, b**3),
            }
            ordinary = Fraction(clique4, q**6 * b**4)
        else:
            deltas = {
                "1111": Fraction(0),
                "211": 6 * (t2 - 1) * Fraction(paired, q**5 * b**4),
                "22": 3 * (t2**2 - 1) * Fraction(s4, q**4 * b**4),
                "31": 4 * (t3 - 1) * Fraction(s3, q**3 * b**4),
                "4": Fraction(t4 - 1, b**3),
            }
            ordinary = (Fraction(clique4, q**6) +
                        6 * Fraction(paired, q**5) +
                        3 * Fraction(s4, q**4) +
                        4 * Fraction(s3, q**3) + b) / b**4
        delta = sum(deltas.values(), Fraction())
        if ordinary + delta != t4:
            raise RuntimeError(f"{color} equality-type reconstruction failed")
        answer[color] = {
            "ordinary_T4": str(ordinary), "nested_T4": str(t4),
            "delta": str(delta), "delta_decimal": float(delta),
            "delta_by_equality_type": {key: str(value) for key, value in deltas.items()},
            "delta_decimal_by_equality_type": {key: float(value) for key, value in deltas.items()},
        }
    total = Fraction(answer["red"]["delta"]) + Fraction(answer["blue"]["delta"])
    if total != Fraction(result["delta_nested_minus_ordinary"]):
        raise RuntimeError("total equality-type reconstruction failed")
    return {
        "directory": result["directory"], "B": b, "Q": q,
        "colors": answer, "total_delta": str(total),
        "total_delta_decimal": float(total),
        "exact_reconstruction": "pass",
    }


def main():
    source = json.loads(SOURCE.read_text())
    report = {
        "hypothesis": source["hypothesis"],
        "source_report": str(SOURCE), "source_report_sha256": sha256(SOURCE),
        "results": [diagnose(result) for result in source["results"]],
        "interpretation": "1111 is unchanged. Red repeated-label types are new positive penalties; blue repeated-label types are negative gains. Type4 includes the all-equal recursive contraction.",
        "scope": "Exact decomposition of the already computed homogeneous recurrence; no new search or candidate",
    }
    OUT.mkdir(parents=True, exist_ok=False)
    write_json(OUT / "report.json", report)
    print(json.dumps({"results": [{"directory": x["directory"],
                                    "total_delta_decimal": x["total_delta_decimal"],
                                    "red": x["colors"]["red"]["delta_decimal_by_equality_type"],
                                    "blue": x["colors"]["blue"]["delta_decimal_by_equality_type"]}
                                   for x in report["results"]]}, indent=2))


if __name__ == "__main__":
    main()
