def main() -> None:
    """The project command is an alias of the Typer experiment interface."""
    from .lab import main as lab_main

    lab_main()
