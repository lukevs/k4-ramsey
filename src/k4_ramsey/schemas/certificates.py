"""Binary graph certificates: part weights, adjacency, and blue loops."""

from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class WeightedCertificate(BaseModel):
    """1–1024 vertices, weights 1–65535, symmetric red rows, blue diagonal."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    schema_version: Literal["weighted-two-color-blowup-v1"] = Field(alias="schema")
    weights: list[Annotated[int, Field(ge=1, le=65535)]]
    red_rows: list[str] = Field(min_length=1, max_length=1024)

    @model_validator(mode="after")
    def validate_graph(self) -> Self:
        n = len(self.red_rows)
        if len(self.weights) != n:
            raise ValueError("weights and rows must be equal-length arrays")
        if any(len(row) != n or set(row) - {"0", "1"} for row in self.red_rows):
            raise ValueError("invalid square binary matrix")
        if any(self.red_rows[i][i] != "0" for i in range(n)):
            raise ValueError("backend requires blue diagonal")
        if any(
            self.red_rows[i][j] != self.red_rows[j][i]
            for i in range(n)
            for j in range(i)
        ):
            raise ValueError("asymmetric matrix")
        return self


class UnitCertificate(WeightedCertificate):
    """A weighted certificate whose parts all have size one."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    @model_validator(mode="after")
    def validate_unit_weights(self) -> Self:
        if any(weight != 1 for weight in self.weights):
            raise ValueError("backend requires unit integer weights")
        return self
