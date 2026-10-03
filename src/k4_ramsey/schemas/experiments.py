"""Requests, lifecycle states, subprocess outcomes, and untrusted claims."""

from pathlib import Path
from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, JsonValue, model_validator

from .types import Budget, Natural, Positive, Seconds
from .verification import Verification


class ExperimentRequest(BaseModel):
    """One isolated run; the total budget must leave time for verification."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    out: Path
    input_path: Path
    strategy: Path
    hypothesis: str
    prediction: str
    seed: int = 0
    seconds: Budget = 10.0
    timeout: Budget = 40.0
    config: dict[str, JsonValue] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_run(self) -> Self:
        if self.timeout <= self.seconds:
            raise ValueError(
                "timeout must exceed search seconds to leave verification time"
            )
        if not self.hypothesis.strip() or not self.prediction.strip():
            raise ValueError("hypothesis and prediction are required")
        # JsonValue admits nonfinite Python floats; our artifact format does not.
        import json

        json.dumps(self.config, allow_nan=False)
        return self


class ProcessResult(BaseModel):
    """Outcome of a reaped process tree, including an unstarted timeout."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    status: Literal["completed", "failed", "timeout"]
    returncode: int | None = None
    seconds: Seconds
    pid: Positive | None = None


class SearchMetrics(BaseModel):
    """An untrusted optional count claim plus strategy-specific diagnostics."""

    model_config = ConfigDict(strict=True, extra="allow")
    numerator: Natural | None = None
    __pydantic_extra__: dict[str, JsonValue] = Field(init=False)


class ExperimentReport(BaseModel):
    """A run's lifecycle record. Only a completed, recounted run has evidence.

    Failure/timeout/interruption can retain a baseline and unverified search
    diagnostics, but cannot acquire a candidate verification or checked label.
    """

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    schema_version: Literal["k4-experiment-v1"] = Field(
        default="k4-experiment-v1", alias="schema"
    )
    status: Literal[
        "preparing",
        "searching",
        "verifying",
        "completed",
        "failed",
        "timeout",
        "interrupted",
    ] = "preparing"
    hypothesis: str
    prediction: str
    seed: int
    search_seconds: Budget
    timeout_seconds: Budget
    started_at: str
    source_input: str
    strategy: str
    python: str
    platform: str
    evidence: Literal["unverified", "lean_native_checked"] = "unverified"
    official_autolab_report: Literal[False] = False
    source_hashes: dict[str, str] = Field(default_factory=dict)
    strategy_sha256: str | None = None
    input_sha256: str | None = None
    baseline: Verification | None = None
    setup_seconds: Seconds | None = None
    command: list[str] | None = None
    process: ProcessResult | None = None
    search_reported: dict[str, JsonValue] | None = None
    verification: Verification | None = None
    candidate_sha256: str | None = None
    improvement: int | None = None
    gap_to_mckay: str | None = None
    beats_mckay: bool | None = None
    interpretation: str | None = None
    error: str | None = None
    total_seconds: Seconds | None = None

    @model_validator(mode="after")
    def validate_evidence_state(self) -> Self:
        if self.status == "completed" and self.evidence != "lean_native_checked":
            raise ValueError("completed runs require checked candidate evidence")
        if self.evidence == "lean_native_checked":
            if (
                self.status != "completed"
                or self.verification is None
                or self.candidate_sha256 is None
            ):
                raise ValueError(
                    "checked evidence requires a completed, recounted candidate"
                )
        elif self.verification is not None:
            raise ValueError("unverified runs cannot contain candidate verification")
        return self
