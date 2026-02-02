"""nw setup CLI command for post-install agent configuration.

This module provides the 'nw setup' command that configures Claude AI
agent directories for both user-level (~/.claude/) and project-level
(.claude/) configurations.
"""

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from crafter_ai.installer.adapters.filesystem_adapter import RealFileSystemAdapter
from crafter_ai.installer.services.celebration_service import CelebrationService
from crafter_ai.installer.services.setup_service import SetupResult, SetupService


# Create console for output
console = Console()


def _display_setup_result(
    result: SetupResult,
    context: str,
    celebration: CelebrationService,
) -> None:
    """Display setup result with appropriate formatting.

    Args:
        result: The setup result to display.
        context: Context string (e.g., "Global config" or "Project config").
        celebration: CelebrationService for display.
    """
    if result.success:
        if result.created_paths:
            console.print(
                f"\n[green]{CelebrationService.CHECKMARK}[/green] {context} setup complete!"
            )
            for path in result.created_paths:
                console.print(f"  [dim]Created:[/dim] {path}")
        else:
            console.print(
                f"\n[cyan]i[/cyan] {context} already configured (no changes needed)"
            )
    else:
        console.print(
            f"\n[red]{CelebrationService.CROSS}[/red] {context} setup failed!"
        )
        for error in result.errors:
            console.print(f"  [red]Error:[/red] {error}")


def _display_ci_result(result: SetupResult, context: str, file: object) -> None:
    """Display setup result in CI mode.

    Args:
        result: The setup result to display.
        context: Context string.
        file: Output file (stdout or custom).
    """
    import sys

    output = file if file is not None else sys.stdout

    if result.success:
        if result.created_paths:
            print(f"[OK] {context} setup complete!", file=output)
            for path in result.created_paths:
                print(f"  Created: {path}", file=output)
        else:
            print(f"[INFO] {context} already configured", file=output)
    else:
        print(f"[FAIL] {context} setup failed!", file=output)
        for error in result.errors:
            print(f"  Error: {error}", file=output)


def setup(
    global_config: Annotated[
        bool,
        typer.Option(
            "--global",
            "-g",
            help="Setup ~/.claude/ (user-level config only).",
        ),
    ] = False,
    project_config: Annotated[
        bool,
        typer.Option(
            "--project",
            "-p",
            help="Setup .claude/ (project-level config only).",
        ),
    ] = False,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Overwrite existing configuration files.",
        ),
    ] = False,
) -> None:
    """Configure Claude AI agent directories.

    Sets up the directory structure required for Claude Code to function
    properly, including user-level (~/.claude/) and project-level (.claude/)
    configurations.

    By default, sets up both global and project configs.
    Use --global or --project to setup only one.
    """
    # Determine what to setup
    # If neither flag is set, do both
    do_global = global_config or (not global_config and not project_config)
    do_project = project_config or (not global_config and not project_config)

    # Create dependencies
    filesystem = RealFileSystemAdapter()
    service = SetupService(filesystem)
    celebration = CelebrationService(console=console)

    # Detect CI mode
    ci_mode = os.environ.get("CI", "").lower() in ("true", "1")

    # Determine paths
    home_dir = Path.home()
    project_dir = Path.cwd()

    # Track overall success
    all_success = True

    # Display header
    if ci_mode:
        print("=" * 60)
        print("nWave Setup - Claude AI Agent Configuration")
        print("=" * 60)
    else:
        console.print(
            "\n[bold cyan]nWave Setup[/bold cyan] - Claude AI Agent Configuration\n"
        )

    # Setup global config
    if do_global:
        result = service.setup_claude_config(home_dir, force=force)
        if ci_mode:
            _display_ci_result(result, "Global config", None)
        else:
            _display_setup_result(result, "Global config", celebration)
        if not result.success:
            all_success = False

    # Setup project config
    if do_project:
        result = service.setup_project_config(project_dir, force=force)
        if ci_mode:
            _display_ci_result(result, "Project config", None)
        else:
            _display_setup_result(result, "Project config", celebration)
        if not result.success:
            all_success = False

    # Final message
    if ci_mode:
        print("")
        if all_success:
            print("[OK] Setup complete!")
        else:
            print("[FAIL] Setup completed with errors")
    else:
        console.print()
        if all_success:
            console.print("[bold green]Setup complete![/bold green]")
            console.print("\n[dim]Run 'nw doctor' to verify your installation.[/dim]")
        else:
            console.print("[bold red]Setup completed with errors.[/bold red]")
            console.print("\n[dim]Check the errors above and try again.[/dim]")

    # Exit with appropriate code
    if not all_success:
        raise typer.Exit(code=1)
