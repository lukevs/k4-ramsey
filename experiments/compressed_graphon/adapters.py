"""Adapters from existing exact reports to the canonical polynomial schema."""

from fractions import Fraction
from typing import Any, Mapping

from .polynomial import ExactPolynomial, _exact_int


def adapt_total_coefficients_report(
    report: Mapping[str, Any], *, source_path: str, base_order: int,
    latent_order: int, probability_denominator: int,
) -> dict[str, object]:
    """Adapt a report where coefficient zero is already the base numerator."""
    total = report["numerator_coefficients_low_to_high"]
    polynomial = ExactPolynomial.from_total_coefficients(
        total, _exact_int(report["normalization"], "normalization"),
        feasible_integer_interval=tuple(report["feasible_q"]),
        base_order=base_order, latent_order=latent_order,
        probability_denominator=probability_denominator,
    )
    record = polynomial.to_record()
    record["provenance"] = {
        "adapter": "total-coefficients-report-v1", "source_path": source_path,
        "candidate_sha256": report.get("candidate_sha256"),
        "counter_sha256": report.get("counter_sha256"),
        "coefficient_evidence": report.get("evidence"),
    }
    return record


def adapt_degree_map_report(
    report: Mapping[str, Any], parent_report: Mapping[str, Any], *,
    source_path: str, parent_path: str, base_order: int,
    latent_order: int, probability_denominator: int,
) -> dict[str, object]:
    """Adapt a degree->coefficient report using its parent's exact density."""
    normalization = _exact_int(report["normalization"], "normalization")
    base = Fraction(str(parent_report["density"]))*normalization
    if base.denominator != 1:
        raise ValueError("parent density is incompatible with report normalization")
    coefficients = [0]*7
    for degree, value in report["coefficients"].items():
        k = _exact_int(degree, "degree")
        if not 0 <= k <= 6:
            raise ValueError("coefficient degree exceeds six")
        coefficients[k] = _exact_int(value, "coefficient")
    polynomial = ExactPolynomial(
        int(base), tuple(coefficients), normalization,
        feasible_integer_interval=tuple(report["feasible_q"]),
        base_order=base_order, latent_order=latent_order,
        probability_denominator=probability_denominator,
    )
    selected = report.get("selected_q")
    numerator = report.get("numerator")
    if selected is not None and numerator is not None:
        if polynomial.raw(_exact_int(selected, "selected_q")) != _exact_int(numerator, "numerator"):
            raise ValueError("canonical polynomial disagrees with selected raw recount")
    record = polynomial.to_record()
    record["provenance"] = {
        "adapter": "degree-map-report-v1", "source_path": source_path,
        "parent_path": parent_path, "candidate_sha256": report.get("candidate_sha256"),
        "checker_binary_sha256": report.get("checker_binary_sha256"),
        "coefficient_evidence": report.get("evidence"),
    }
    return record
