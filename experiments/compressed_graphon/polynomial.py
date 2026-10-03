"""Exact degree-six polynomial and centered-kernel feasibility primitives.

The canonical convention is

    N(q) = base_numerator + sum_k coefficients[k] * q**k,

with ``coefficients[0] == 0`` and density ``N(q) / normalization``.  These
utilities evaluate supplied coefficients; they do not certify how a histogram
or motif counter derived them.
"""

from dataclasses import dataclass
from fractions import Fraction
import re
from typing import Iterable, Mapping, Sequence


def _exact_int(value: object, name: str = "value") -> int:
    """Accept exact integral representations and reject every lossy coercion."""
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an exact integer, not bool")
    if isinstance(value, int):
        return value
    if isinstance(value, Fraction):
        if value.denominator == 1:
            return value.numerator
        raise ValueError(f"{name} is not integral")
    if isinstance(value, str) and re.fullmatch(r"[+-]?[0-9]+", value):
        return int(value)
    raise TypeError(f"{name} must be an integer, integral Fraction, or decimal integer string")


def _as_fraction(value: int | Fraction) -> Fraction:
    if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
        raise TypeError("rational evaluation accepts only int or Fraction")
    return value if isinstance(value, Fraction) else Fraction(value)


def evaluate_coefficients(coefficients: Sequence[int | Fraction], q: int | Fraction) -> Fraction:
    """Evaluate low-to-high coefficients by exact Horner arithmetic."""
    x = _as_fraction(q)
    answer = Fraction(0)
    for coefficient in reversed(coefficients):
        answer = answer*x + _as_fraction(coefficient)
    return answer


def interpolate_integer_polynomial(
    points: Sequence[tuple[int, int]], *, max_degree: int = 6,
    degree_bound_proven: bool = False,
) -> tuple[int, ...]:
    """Return the unique integer power-basis polynomial through exact points.

    Raises when there are duplicate abscissae, too many points for the degree
    cap, or the interpolated polynomial does not have integer coefficients.
    """
    if not degree_bound_proven:
        raise ValueError("interpolation requires an external proof that degree <= max_degree")
    if not points:
        raise ValueError("at least one point is required")
    if len(points) > max_degree + 1:
        raise ValueError("too many points for degree cap")
    exact_points = [(_exact_int(x, "coordinate"), _exact_int(y, "sample")) for x, y in points]
    xs = [Fraction(x) for x, _ in exact_points]
    if len(set(xs)) != len(xs):
        raise ValueError("duplicate interpolation coordinate")
    divided = [Fraction(y) for _, y in exact_points]
    newton: list[Fraction] = []
    for degree in range(len(points)):
        newton.append(divided[0])
        divided = [
            (divided[i+1]-divided[i]) / (xs[i+degree+1]-xs[i])
            for i in range(len(divided)-1)
        ]
    power = [Fraction(0)]
    basis = [Fraction(1)]
    for degree, coefficient in enumerate(newton):
        if len(power) < len(basis):
            power.extend([Fraction(0)]*(len(basis)-len(power)))
        for i, value in enumerate(basis):
            power[i] += coefficient*value
        if degree+1 < len(newton):
            nxt = [Fraction(0)]*(len(basis)+1)
            for i, value in enumerate(basis):
                nxt[i] -= xs[degree]*value
                nxt[i+1] += value
            basis = nxt
    while len(power) > 1 and power[-1] == 0:
        power.pop()
    if any(value.denominator != 1 for value in power):
        raise ValueError("polynomial coefficients are not integral")
    return tuple(int(value) for value in power)


@dataclass(frozen=True)
class IntegerMinimum:
    value: int
    minimizers: tuple[int, ...]
    interval: tuple[int, int]
    evaluations: int


@dataclass(frozen=True)
class ExactPolynomial:
    """Canonical raw-numerator polynomial with a constant normalization."""

    base_numerator: int
    numerator_coefficients_low_to_high: tuple[int, ...]
    normalization_denominator: int
    amplitude_parameter: str = "q"
    feasible_integer_interval: tuple[int, int] | None = None
    base_order: int | None = None
    latent_order: int | None = None
    probability_denominator: int | None = None

    def __post_init__(self) -> None:
        coefficients = tuple(_exact_int(x, "coefficient") for x in self.numerator_coefficients_low_to_high)
        object.__setattr__(self, "numerator_coefficients_low_to_high", coefficients)
        object.__setattr__(self, "base_numerator", _exact_int(self.base_numerator, "base_numerator"))
        object.__setattr__(self, "normalization_denominator", _exact_int(self.normalization_denominator, "normalization_denominator"))
        if not 1 <= len(coefficients) <= 7:
            raise ValueError("polynomial degree must be at most six")
        if coefficients[0] != 0:
            raise ValueError("canonical delta polynomial must have zero constant term")
        if self.normalization_denominator <= 0:
            raise ValueError("normalization denominator must be positive")
        if self.feasible_integer_interval is not None:
            lo, hi = (_exact_int(self.feasible_integer_interval[0], "interval lower bound"),
                      _exact_int(self.feasible_integer_interval[1], "interval upper bound"))
            object.__setattr__(self, "feasible_integer_interval", (lo, hi))
            if lo > hi:
                raise ValueError("empty feasible interval")
        for name in ("base_order", "latent_order", "probability_denominator"):
            value = getattr(self, name)
            if value is not None:
                value = _exact_int(value, name)
                object.__setattr__(self, name, value)
                if value <= 0:
                    raise ValueError(f"{name} must be positive")

    @classmethod
    def from_total_coefficients(
        cls, total_coefficients_low_to_high: Sequence[int], normalization_denominator: int, **metadata
    ) -> "ExactPolynomial":
        """Adapt reports whose coefficient zero already equals the base."""
        if not total_coefficients_low_to_high:
            raise ValueError("missing coefficients")
        total = tuple(_exact_int(x, "total coefficient") for x in total_coefficients_low_to_high)
        return cls(total[0], (0, *total[1:]), normalization_denominator, **metadata)

    @classmethod
    def from_record(cls, record: Mapping[str, object]) -> "ExactPolynomial":
        expected = record.get("coefficient_convention")
        if expected != "N(q)=base_numerator+sum_k(c[k]*q^k), c[0]=0":
            raise ValueError("unknown coefficient convention")
        interval = record.get("feasible_integer_interval")
        return cls(
            base_numerator=_exact_int(record["base_numerator"], "base_numerator"),
            numerator_coefficients_low_to_high=tuple(
                _exact_int(x, "coefficient") for x in record["numerator_coefficients_low_to_high"]  # type: ignore[index]
            ),
            normalization_denominator=_exact_int(record["normalization_denominator"], "normalization_denominator"),
            amplitude_parameter=str(record.get("amplitude_parameter", "q")),
            feasible_integer_interval=None if interval is None else (_exact_int(interval[0]), _exact_int(interval[1])),  # type: ignore[index]
            base_order=None if record.get("base_order") is None else _exact_int(record["base_order"]),
            latent_order=None if record.get("latent_order") is None else _exact_int(record["latent_order"]),
            probability_denominator=None if record.get("probability_denominator") is None else _exact_int(record["probability_denominator"]),
        )

    def to_record(self) -> dict[str, object]:
        return {
            "schema": "compressed-graphon-polynomial-v1",
            "base_numerator": str(self.base_numerator),
            "numerator_coefficients_low_to_high": [str(x) for x in self.numerator_coefficients_low_to_high],
            "normalization_denominator": str(self.normalization_denominator),
            "amplitude_parameter": self.amplitude_parameter,
            "feasible_integer_interval": self.feasible_integer_interval,
            "base_order": self.base_order,
            "latent_order": self.latent_order,
            "probability_denominator": self.probability_denominator,
            "coefficient_convention": "N(q)=base_numerator+sum_k(c[k]*q^k), c[0]=0",
        }

    def delta_raw(self, q: int) -> int:
        coordinate = _exact_int(q, "coordinate")
        value = 0
        for coefficient in reversed(self.numerator_coefficients_low_to_high):
            value = value*coordinate + coefficient
        return value

    def raw(self, q: int) -> int:
        return self.base_numerator + self.delta_raw(q)

    def density(self, q: int) -> Fraction:
        return Fraction(self.raw(q), self.normalization_denominator)

    def minimize_integer(self, interval: tuple[int, int] | None = None) -> IntegerMinimum:
        """Rigorous exhaustive minimization on a finite integer interval."""
        use = interval if interval is not None else self.feasible_integer_interval
        if use is None:
            raise ValueError("no feasible integer interval supplied")
        lo, hi = (_exact_int(use[0], "interval lower bound"),
                  _exact_int(use[1], "interval upper bound"))
        if lo > hi:
            raise ValueError("empty interval")
        best_value: int | None = None
        minimizers: list[int] = []
        for q in range(lo, hi+1):
            value = self.raw(q)
            if best_value is None or value < best_value:
                best_value, minimizers = value, [q]
            elif value == best_value:
                minimizers.append(q)
        assert best_value is not None
        return IntegerMinimum(best_value, tuple(minimizers), (lo, hi), hi-lo+1)

    def additive_raw(self, coordinates: Iterable[int], *, mixed_terms_absent: bool = False) -> int:
        """Evaluate independent levels only after the caller asserts additivity.

        Centering alone does not imply absence of mixed-level motif terms, so
        the explicit flag prevents this helper from silently making that leap.
        """
        if not mixed_terms_absent:
            raise ValueError("multilevel additivity requires a separate no-mixed-terms argument")
        return self.base_numerator + sum(self.delta_raw(q) for q in coordinates)

    def additive_density(self, coordinates: Iterable[int], *, mixed_terms_absent: bool = False) -> Fraction:
        return Fraction(
            self.additive_raw(coordinates, mixed_terms_absent=mixed_terms_absent),
            self.normalization_denominator,
        )


def additive_raw(
    base_numerator: int,
    components: Iterable[tuple[Sequence[int], int]],
    *, mixed_terms_absent: bool = False,
) -> int:
    """Combine potentially different level polynomials under an explicit proof.

    Every coefficient sequence is a raw-numerator delta polynomial under the
    same external normalization and must have zero constant term.
    """
    if not mixed_terms_absent:
        raise ValueError("multilevel additivity requires a separate no-mixed-terms argument")
    answer = _exact_int(base_numerator, "base_numerator")
    for coefficients, coordinate in components:
        exact = tuple(_exact_int(x, "coefficient") for x in coefficients)
        if not 1 <= len(exact) <= 7 or exact[0] != 0:
            raise ValueError("each delta polynomial must have degree <=6 and zero constant")
        q = _exact_int(coordinate, "coordinate")
        value = 0
        for coefficient in reversed(exact):
            value = value*q + coefficient
        answer += value
    return answer


@dataclass(frozen=True)
class CenteredKernel:
    entries: tuple[tuple[int, ...], ...]

    def __post_init__(self) -> None:
        rows = tuple(tuple(_exact_int(x, "kernel entry") for x in row) for row in self.entries)
        object.__setattr__(self, "entries", rows)
        n = len(rows)
        if n == 0 or any(len(row) != n for row in rows):
            raise ValueError("kernel must be nonempty and square")
        if any(rows[i][j] != rows[j][i] for i in range(n) for j in range(n)):
            raise ValueError("kernel must be symmetric")
        if any(sum(row) != 0 for row in rows):
            raise ValueError("kernel must have zero uniform row sums")

    @property
    def order(self) -> int:
        return len(self.entries)

    def perturbation_range(self, coordinate: int) -> tuple[int, int]:
        q = _exact_int(coordinate, "coordinate")
        values = [q*x for row in self.entries for x in row]
        return min(values), max(values)


@dataclass(frozen=True)
class KernelLevel:
    kernel: CenteredKernel
    coordinate: int

    def __post_init__(self) -> None:
        if not isinstance(self.kernel, CenteredKernel):
            raise TypeError("kernel must be a CenteredKernel")
        object.__setattr__(self, "coordinate", _exact_int(self.coordinate, "coordinate"))


def probability_ranges(
    base_probability_numerators: Iterable[int], levels: Iterable[KernelLevel]
) -> tuple[tuple[int, int], ...]:
    """Exact fine-block ranges for the caller-supplied perturbed base values.

    The caller controls support semantics by passing exactly the base entries
    being perturbed; diagonal values may be included when diagonal support is
    intended. Independent latent levels have Cartesian-product extrema, hence
    their per-level minima and maxima add exactly.
    """
    materialized = tuple(levels)
    low_shift = high_shift = 0
    for level in materialized:
        lo, hi = level.kernel.perturbation_range(level.coordinate)
        low_shift += lo
        high_shift += hi
    return tuple((_exact_int(base, "base probability")+low_shift,
                  _exact_int(base, "base probability")+high_shift)
                 for base in base_probability_numerators)


def probabilities_feasible(
    base_probability_numerators: Iterable[int], probability_denominator: int,
    levels: Iterable[KernelLevel]
) -> bool:
    probability_denominator = _exact_int(probability_denominator, "probability denominator")
    if probability_denominator <= 0:
        raise ValueError("probability denominator must be positive")
    return all(
        0 <= lo <= hi <= probability_denominator
        for lo, hi in probability_ranges(base_probability_numerators, levels)
    )
