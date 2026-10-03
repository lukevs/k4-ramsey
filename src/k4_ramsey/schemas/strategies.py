"""Shared strategy script protocol and configuration models."""

from pathlib import Path
from typing import Annotated, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator

from .types import Budget, Natural, Positive


class StrategyRequest(BaseModel):
    """The common script protocol used by every maintained search strategy."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    input: Path
    output: Path
    config: Path
    seed: int
    seconds: Budget


class DescentConfig(BaseModel):
    """Sampled edge descent stops at a move or time budget."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    max_moves: Natural = 100000000
    checkpoint_moves: Positive = 50000


class ScanConfig(BaseModel):
    """Exhaustive single-edge scans, bounded by passes and elapsed time."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    max_passes: Positive = 1000000


class AnnealConfig(BaseModel):
    """Metropolis walk with a cooling cycle and optional restart from best."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    temperature: Budget = 12.0
    cycle_moves: Positive = 300000
    max_moves: Positive = 1000000000
    restart: bool = True


class CloneConfig(BaseModel):
    """Sample clone moves; zero moves is a valid replay."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    max_moves: Natural = 100000000
    pool_size: Positive = 8
    selection: Literal["random", "closest", "linear"] = "random"


class StarConfig(BaseModel):
    """Bound opposite-color shared-endpoint pair screening."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    per_color: Annotated[int, Field(ge=1, le=128)] = 16
    random_per_color: Annotated[int, Field(ge=0, le=128)] = 4
    max_rounds: Positive = 1000


class FastNeighborhoodConfig(BaseModel):
    """Cached strict descent, optionally including screened star escapes."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    mode: Literal["single", "star"] = "star"
    per_color: Annotated[int, Field(ge=1, le=128)] = 16
    max_moves: Positive = 100000
    checkpoint_moves: Positive = 100


class MatchingConfig(BaseModel):
    """Exact matching subproblems chosen from a sufficiently large edge pool."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    size: Annotated[int, Field(ge=1, le=24)] = 16
    pool_size: Positive = 256
    max_neighborhoods: Positive = 100000
    mode: Literal["random", "low_delta", "interaction", "pair"] = "interaction"

    @model_validator(mode="after")
    def validate_pool(self) -> Self:
        if self.pool_size < self.size:
            raise ValueError("pool_size must be >= size")
        return self


class CubicStarConfig(BaseModel):
    """Exact cubic star subproblems with bounded random leaf diversity."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    size: Annotated[int, Field(ge=3, le=20)] = 12
    random_per_color: Natural = 1
    max_neighborhoods: Positive = 100000

    @model_validator(mode="after")
    def validate_diversity(self) -> Self:
        if self.random_per_color > self.size // 2:
            raise ValueError("random_per_color must be <= size//2")
        return self


class TabuConfig(BaseModel):
    """Tabu expiry indices must fit the native signed-int buffer."""

    model_config = ConfigDict(strict=True, extra="forbid", populate_by_name=True)

    max_moves: Natural = 1000000000
    tenure: Natural = 40
    tenure_jitter: Natural = 40
    checkpoint_seconds: Annotated[float, Field(gt=0, le=60, allow_inf_nan=False)] = 1.0

    @model_validator(mode="after")
    def validate_expiry(self) -> Self:
        if self.max_moves + self.tenure + self.tenure_jitter + 1 >= 2**31:
            raise ValueError("expiry could overflow native signed int")
        return self
