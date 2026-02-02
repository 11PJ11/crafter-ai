"""
CLI entry point for crafter-ai installer.

This module provides the main Typer application for the CLI.
"""

import typer

from crafter_ai import __version__
from crafter_ai.installer.cli.forge_build import forge_app
from crafter_ai.installer.cli.install_nwave import install_nwave
from crafter_ai.installer.cli.nw_app import nw_app


app = typer.Typer(
    name="crafter-ai",
    help="Modern CLI installer for crafter-ai with rich terminal UI.",
    no_args_is_help=True,
    add_completion=True,
)


def version_callback(value: bool) -> None:
    """Display version and exit."""
    if value:
        typer.echo(f"crafter-ai version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: bool = typer.Option(
        False,
        "--version",
        "-v",
        help="Show version and exit.",
        callback=version_callback,
        is_eager=True,
    ),
) -> None:
    """
    crafter-ai: Modern CLI installer with rich terminal UI.

    A professional installer featuring cross-platform support,
    rich terminal output, and comprehensive error handling.
    """
    pass


# Register forge subcommand group
app.add_typer(forge_app, name="forge")

# Register nw subcommand group (setup, doctor, version)
app.add_typer(nw_app, name="nw")

# Register install-nwave command
app.command("install-nwave")(install_nwave)


if __name__ == "__main__":
    app()
