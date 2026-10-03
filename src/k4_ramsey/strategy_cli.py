"""One Typer adapter for the common standalone strategy protocol."""

from collections.abc import Callable
from pathlib import Path
from typing import Annotated

import typer

from .schemas.strategies import StrategyRequest


def run_strategy(search: Callable[[StrategyRequest], None]) -> None:
    """Parse the shared CLI and pass a validated request to a search function."""
    app = typer.Typer(pretty_exceptions_enable=False)

    @app.command(help=search.__doc__)
    def run(
        input: Annotated[Path, typer.Option()],
        output: Annotated[Path, typer.Option()],
        config: Annotated[Path, typer.Option()],
        seed: Annotated[int, typer.Option()],
        seconds: Annotated[float, typer.Option()],
    ) -> None:
        search(
            StrategyRequest(
                input=input, output=output, config=config, seed=seed, seconds=seconds
            )
        )

    app()
