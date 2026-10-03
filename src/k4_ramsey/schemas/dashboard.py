"""Read-only projections of historical reports; not new verification evidence.

Old reports omit fields required by today's writer. These projections validate
only the fields used by the display and deliberately ignore unrelated metadata.
"""

from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .types import Positive
from .verification import ExactValue


class ReportHeader(BaseModel):
    """Minimum metadata needed to display a historical experiment."""

    model_config = ConfigDict(strict=True, extra="ignore")
    status: str
    hypothesis: str
    started_at: str


class RecordedValue(ExactValue):
    """A historical exact value; its method and candidate hash are checked separately."""

    model_config = ConfigDict(strict=True, extra="ignore")


class WeightedSidecar(RecordedValue):
    """A separately versioned weighted result attached to its own experiment."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    schema_version: Literal["k4-weighted-verification-v1"] = Field(alias="schema")
    status: Literal["lean_native_checked_weighted_v1"]
    total_weight: Positive
    candidate: str
    candidate_sha256: str

    @model_validator(mode="after")
    def validate_normalization(self) -> Self:
        if self.denominator != self.total_weight**4:
            raise ValueError("weighted denominator must equal total weight⁴")
        return self
