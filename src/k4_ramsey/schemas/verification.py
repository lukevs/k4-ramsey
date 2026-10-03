"""Exact count and independent compiled-Lean evidence contracts."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .types import Natural, Positive, Seconds


class Counts(BaseModel):
    """Unordered subgraph counts and the ordered monochromatic numerator."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    red_edges: Natural
    blue_triangles: Natural
    red_k4: Natural
    blue_k4: Natural
    numerator: Natural


class ExactValue(BaseModel):
    """An exact probability represented without floating-point rounding."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    numerator: Natural
    denominator: Positive

    @model_validator(mode="after")
    def validate_probability(self) -> Self:
        if self.numerator > self.denominator:
            raise ValueError("numerator exceeds denominator")
        return self


class Verification(ExactValue, Counts):
    """Unit-weight compiled Lean recount, not a kernel-only bound proof."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    status: Literal["lean_native_checked"] = "lean_native_checked"
    n: Annotated[int, Field(ge=1, le=1024)]
    density: str
    seconds: Seconds
    checker_binary_sha256: str
    trust: str = "Compiled Lean execution; not a kernel-only proof of c4 bound"

    @model_validator(mode="after")
    def validate_normalization(self) -> Self:
        if self.denominator != self.n**4:
            raise ValueError("denominator must equal order⁴")
        check_density(self.numerator, self.denominator, self.density)
        return self


class WeightedVerification(ExactValue):
    """Separate weighted recount contract; never unit-search evidence."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    schema_version: Literal["k4-weighted-verification-v1"] = Field(
        default="k4-weighted-verification-v1", alias="schema"
    )
    status: Literal["lean_native_checked_weighted_v1"] = (
        "lean_native_checked_weighted_v1"
    )
    n: Annotated[int, Field(ge=1, le=1024)]
    total_weight: Positive
    density: str
    seconds: Seconds
    checker_binary_sha256: str
    source_hashes: dict[str, str]
    scope: str = "Positive integer weights <=65535; order<=1024; symmetric binary graph; blue diagonals."
    trust: str = "Independent compiled Lean full weighted recount; not a kernel-only proof of the general counting identity or asymptotic bound."
    candidate: str | None = None
    candidate_sha256: str | None = None

    @model_validator(mode="after")
    def validate_normalization(self) -> Self:
        if self.denominator != self.total_weight**4:
            raise ValueError("denominator must equal total weight⁴")
        check_density(self.numerator, self.denominator, self.density)
        return self


def check_density(numerator: int, denominator: int, density: str) -> None:
    """Reject a display fraction that contradicts the exact count."""
    from fractions import Fraction

    if Fraction(density) != Fraction(numerator, denominator):
        raise ValueError("density disagrees with exact count")
