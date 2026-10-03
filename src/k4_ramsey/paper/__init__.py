"""Paper commands: validate frozen evidence, export source tables, draw figures.

The justfile owns LaTeX builds. These commands never search for new witnesses.
"""

from pathlib import Path
from typing import Annotated

import typer

app = typer.Typer(help=__doc__, no_args_is_help=True, pretty_exceptions_enable=False)


def main() -> None:
    app()


@app.command("check")
def check_command(
    matrix: Annotated[
        Path | None, typer.Option(help="Expand to a new matrix file.")
    ] = None,
    original_order: Annotated[
        bool, typer.Option(help="Use the archived audit order.")
    ] = False,
) -> None:
    """Validate the witness and receipts; do not recount clique density."""
    from .witness import check

    check(matrix, original_order)


@app.command("export")
def export_command(
    workflow: Annotated[
        Path | None, typer.Option(help="Research skill snapshot.")
    ] = None,
) -> None:
    """Regenerate supplement files from Lean tables and archived research reports."""
    from .export import export

    export(workflow)


@app.command("figures")
def figures_command() -> None:
    """Draw manuscript figures from checked construction data."""
    from .figures import render

    render()
