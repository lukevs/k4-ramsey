"""Strict, score-free construction data and byte-level supplement identities.

Historical count receipts remain legacy data; witness checks recombine their
exact integer fields without treating a recorded score as construction input.
"""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .types import Natural

Sha256 = Annotated[str, Field(pattern=r"^[0-9a-f]{64}$")]
ProbabilityNumerator = Annotated[int, Field(ge=0, le=65536)]


class PaperModel(BaseModel):
    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)


class BaseParameters(PaperModel):
    p_numerator: Literal[51064]
    h_numerator: Literal[35139]


class CompactWitness(PaperModel):
    schema_version: Literal["clebsch192-refinement20-v1"] = Field(alias="schema")
    denominator: Literal[65536]
    coarse_classes: Literal[192]
    fine_labels: Literal[20]
    base_parameters: BaseParameters
    original_candidate_sha256: Sha256
    canonical_to_original_coarse: list[Natural] = Field(min_length=192, max_length=192)
    block_index: list[Annotated[int, Field(ge=0, le=1248)]] = Field(
        min_length=36864, max_length=36864
    )
    blocks: list[list[ProbabilityNumerator]] = Field(min_length=1248, max_length=1248)

    @model_validator(mode="after")
    def validate_dimensions(self) -> Self:
        if sorted(self.canonical_to_original_coarse) != list(range(192)):
            raise ValueError("coarse class map must be a permutation")
        if any(len(block) != 400 for block in self.blocks):
            raise ValueError("each refinement block must be 20 by 20")
        return self


class FileIdentity(PaperModel):
    sha256: Sha256
    bytes: Natural


class ExportEvidence(PaperModel):
    original_matrix_entries_checked: Literal[14745600]
    mismatches: Literal[0]
    exporter_sha256: Sha256
    witness_checker_sha256: Sha256
    note: str


class SupplementManifest(PaperModel):
    schema_version: Literal["k4-paper-supplement-v1"] = Field(alias="schema")
    files: dict[str, FileIdentity]
    source_sha256: dict[str, Sha256]
    export: ExportEvidence

    @model_validator(mode="after")
    def validate_names(self) -> Self:
        if any(
            "/" in name or "\\" in name or name in {"", ".", ".."}
            for name in self.files
        ):
            raise ValueError("supplement filenames must be local basenames")
        return self


class FigureManifest(PaperModel):
    schema_version: Literal["k4-paper-figures-v1"] = Field(alias="schema")
    source_sha256: dict[str, Sha256]
    files: dict[str, FileIdentity]
    checks: list[str]
