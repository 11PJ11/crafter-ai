"""nw rollback CLI command for manual backup restoration.

This module provides the 'nw rollback' command that allows users to:
1. List available backups
2. Restore a specific backup (interactive or non-interactive)
3. Run health checks after restore

Follows hexagonal architecture - uses RollbackService, not direct adapters.
"""

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from crafter_ai.installer.adapters.backup_adapter import FileSystemBackupAdapter
from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.services.rollback_service import RollbackService


# Exit codes
EXIT_SUCCESS = 0
EXIT_NO_BACKUPS = 1
EXIT_RESTORE_FAILED = 2

# Status indicators for Rich output
CHECKMARK = "[green]✓[/green]"
CROSS = "[red]✗[/red]"
WARNING = "[yellow]⚠[/yellow]"

# Status indicators for CI mode
CI_CHECKMARK = "[OK]"
CI_CROSS = "[FAIL]"
CI_WARNING = "[WARN]"


def _is_ci_mode(ci_flag: bool = False) -> bool:
    """Check if running in CI mode.

    CI mode is detected via:
    1. --ci flag passed to command
    2. CI environment variable set to 'true' or '1'

    Args:
        ci_flag: Whether --ci flag was passed.

    Returns:
        True if in CI mode, False otherwise.
    """
    if ci_flag:
        return True
    ci_value = os.environ.get("CI", "").lower()
    return ci_value in ("true", "1")


def _get_health_indicator(status: HealthStatus | None, ci_mode: bool) -> str:
    """Get the health status indicator.

    Args:
        status: The health status to display.
        ci_mode: Whether to use CI mode (plain text) indicators.

    Returns:
        String indicator for the health status.
    """
    if status is None:
        return CI_WARNING if ci_mode else WARNING

    if ci_mode:
        indicators = {
            HealthStatus.HEALTHY: CI_CHECKMARK,
            HealthStatus.DEGRADED: CI_WARNING,
            HealthStatus.UNHEALTHY: CI_CROSS,
        }
    else:
        indicators = {
            HealthStatus.HEALTHY: CHECKMARK,
            HealthStatus.DEGRADED: WARNING,
            HealthStatus.UNHEALTHY: CROSS,
        }
    return indicators.get(status, CI_CROSS if ci_mode else CROSS)


def create_rollback_service() -> RollbackService:
    """Factory function to create RollbackService with dependencies.

    Returns:
        Configured RollbackService instance.
    """
    nwave_path = Path.home() / ".claude"
    backup_port = FileSystemBackupAdapter(nwave_path)
    health_checker = HealthChecker(nwave_path)
    return RollbackService(backup_port, health_checker, nwave_path)


def rollback(
    backup: Annotated[
        Path | None,
        typer.Option(
            "--backup",
            "-b",
            help="Specify backup path directly (non-interactive mode).",
        ),
    ] = None,
    ci: Annotated[
        bool,
        typer.Option(
            "--ci",
            help="Force CI mode (plain text output, no prompts).",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Auto-confirm restore without prompting.",
        ),
    ] = False,
) -> None:
    """Restore nWave from a backup.

    The rollback command allows you to restore your nWave installation
    from a previous backup. This is useful if an update caused issues.

    Without --backup, lists available backups for selection.
    With --backup, restores the specified backup directly.

    Exit codes:
        0: Success
        1: No backups available
        2: Restore failed
    """
    ci_mode = _is_ci_mode(ci)
    console = Console()

    # Create service via factory
    service = create_rollback_service()

    # Get available backups
    backups = service.list_available_backups()

    # Handle no backups case
    if not backups:
        if ci_mode:
            print("Error: No backups available.")
            print("Suggestion: Run 'crafter-ai install' to reinstall.")
        else:
            console.print("[red]Error:[/red] No backups available.")
            console.print(
                "[dim]Suggestion: Run 'crafter-ai install' to reinstall.[/dim]"
            )
        raise typer.Exit(code=EXIT_NO_BACKUPS)

    # Determine which backup to restore
    backup_path: Path
    if backup is not None:
        # Non-interactive mode: use specified backup
        backup_path = backup
    # List backups
    elif ci_mode:
        print("Available backups:")
        for i, b in enumerate(backups, 1):
            timestamp_str = b.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            print(f"  {i}. {b.path} ({timestamp_str})")
        # In CI mode without --backup, just list and exit with no backups to select
        print("")
        print("Use --backup to specify a backup path in CI mode.")
        raise typer.Exit(code=EXIT_NO_BACKUPS)
    else:
        console.print("[bold]Available backups:[/bold]")
        console.print()
        for i, b in enumerate(backups, 1):
            timestamp_str = b.timestamp.strftime("%Y-%m-%d %H:%M:%S")
            size_kb = b.size_bytes / 1024
            console.print(
                f"  {i}. [cyan]{b.path.name}[/cyan] - {timestamp_str} ({size_kb:.1f} KB)"
            )
        console.print()

        # Interactive selection
        try:
            from rich.prompt import IntPrompt

            selection = IntPrompt.ask(
                "Select backup to restore (number)",
                choices=[str(i) for i in range(1, len(backups) + 1)],
            )
            backup_path = backups[selection - 1].path
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Cancelled.[/yellow]")
            raise typer.Exit(code=EXIT_NO_BACKUPS)

    # Confirm restore (unless --yes or CI mode)
    if not yes and not ci_mode:
        from rich.prompt import Confirm

        if not Confirm.ask(f"Restore from [cyan]{backup_path.name}[/cyan]?"):
            console.print("[yellow]Cancelled.[/yellow]")
            raise typer.Exit(code=EXIT_NO_BACKUPS)

    # Perform restore
    if ci_mode:
        print(f"Restoring from {backup_path}...")
    else:
        console.print(f"Restoring from [cyan]{backup_path}[/cyan]...")

    result = service.manual_rollback(backup_path)

    if not result.success:
        error_msg = result.error_message or "Unknown error"
        if ci_mode:
            print(f"Error: Restore failed - {error_msg}")
        else:
            console.print(f"[red]Error:[/red] Restore failed - {error_msg}")
        raise typer.Exit(code=EXIT_RESTORE_FAILED)

    # Success - show confirmation and health status
    health_indicator = _get_health_indicator(result.health_status, ci_mode)

    if ci_mode:
        print("Restore complete successfully.")
        if result.health_status:
            health_text = result.health_status.value
            print(f"Health check: {health_indicator} {health_text}")
    else:
        console.print("[green]Restore complete successfully.[/green]")
        if result.health_status:
            health_text = result.health_status.value.title()
            console.print(f"Health check: {health_indicator} {health_text}")
