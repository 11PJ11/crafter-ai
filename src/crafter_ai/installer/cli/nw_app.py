"""nw CLI command group for crafter-ai nWave operations.

This module provides the 'nw' command group that aggregates:
- nw setup: Post-install agent configuration
- nw doctor: Health check diagnostics
- nw version: Version information
- nw rollback: Restore from backup
"""

import typer

from crafter_ai.installer.cli.nw_doctor import doctor
from crafter_ai.installer.cli.nw_rollback import rollback
from crafter_ai.installer.cli.nw_setup import setup
from crafter_ai.installer.cli.nw_version import version


# Create the nw command group
nw_app = typer.Typer(
    name="nw",
    help="nWave framework management commands.",
    no_args_is_help=True,
)


# Register subcommands
nw_app.command(name="setup")(setup)
nw_app.command(name="doctor")(doctor)
nw_app.command(name="version")(version)
nw_app.command(name="rollback")(rollback)
