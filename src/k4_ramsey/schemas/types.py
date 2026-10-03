"""Scalar domains shared by the Pydantic data definitions."""

from typing import Annotated

from pydantic import Field

Natural = Annotated[int, Field(ge=0)]
Positive = Annotated[int, Field(gt=0)]
Seconds = Annotated[float, Field(ge=0, allow_inf_nan=False)]
Budget = Annotated[float, Field(gt=0, allow_inf_nan=False)]
