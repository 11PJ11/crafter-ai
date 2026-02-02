"""Forge install CLI command.

This module provides the 'forge install' command for the crafter-ai CLI.
Displays pre-flight checks, prompts for confirmation, runs install service,
and displays release report.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from crafter_ai.installer.adapters.backup_adapter import FileSystemBackupAdapter
from crafter_ai.installer.adapters.pipx_adapter import SubprocessPipxAdapter
from crafter_ai.installer.checks.install_checks import create_install_check_registry
from crafter_ai.installer.cli.forge_build import forge_app
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult
from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.services.install_service import InstallService
from crafter_ai.installer.services.release_readiness_service import (
    ReleaseReadinessService,
)
from crafter_ai.installer.services.release_report_service import ReleaseReportService


console = Console()


def is_ci_mode() -> bool:
    """Check if running in CI environment.

    Returns:
        True if CI environment variable is set to 'true'.
    """
    return os.environ.get("CI", "").lower() == "true"


def find_latest_wheel(dist_dir: Path | None = None) -> Path | None:
    """Find the latest wheel file in dist directory.

    Args:
        dist_dir: Optional directory to search. Defaults to ./dist.

    Returns:
        Path to the latest wheel file, or None if not found.
    """
    search_dir = dist_dir or Path("dist")
    if not search_dir.exists():
        return None

    wheels = list(search_dir.glob("*.whl"))
    if not wheels:
        return None

    # Sort by modification time, newest first
    wheels.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return wheels[0]


def run_pre_flight_checks() -> list[CheckResult]:
    """Run pre-flight checks for installation.

    Returns:
        List of CheckResult from pre-flight checks.
    """
    registry = create_install_check_registry()
    check_executor = CheckExecutor(registry)
    return check_executor.run_all()


def display_pre_flight_results(results: list[CheckResult]) -> None:
    """Display pre-flight check results in a Rich table.

    Args:
        results: List of CheckResult objects to display.
    """
    table = Table(title="Pre-flight Checks", show_header=True)
    table.add_column("Check", style="cyan")
    table.add_column("Status", justify="center")
    table.add_column("Details")

    for check in results:
        status = "[green]OK[/green]" if check.passed else "[red]FAIL[/red]"
        table.add_row(check.name, status, check.message)

    console.print(table)
    console.print()


def display_header(wheel_path: Path) -> None:
    """Display FORGE: INSTALL header.

    Args:
        wheel_path: Path to the wheel being installed.
    """
    console.print()
    console.print(
        Panel(
            f"[bold cyan]FORGE: INSTALL[/bold cyan]\n\nWheel: {wheel_path.name}",
            title="Installation",
            border_style="cyan",
        )
    )
    console.print()


def display_failure(error_message: str) -> None:
    """Display installation failure message.

    Args:
        error_message: Error message to display.
    """
    console.print(
        Panel(
            f"[bold red]FORGE: INSTALL FAILED[/bold red]\n\n{error_message}",
            title="Installation Failed",
            border_style="red",
        )
    )
    console.print()


def create_install_service(skip_verification: bool = False) -> InstallService:
    """Factory function to create an InstallService with all dependencies.

    Args:
        skip_verification: If True, don't include health checker.

    Returns:
        Configured InstallService instance.
    """
    pipx_port = SubprocessPipxAdapter()
    backup_port = FileSystemBackupAdapter()
    registry = create_install_check_registry()
    check_executor = CheckExecutor(registry)
    release_readiness_service = ReleaseReadinessService()

    health_checker: HealthChecker | None = None
    if not skip_verification:
        health_checker = HealthChecker()

    return InstallService(
        pipx_port=pipx_port,
        backup_port=backup_port,
        check_executor=check_executor,
        release_readiness_service=release_readiness_service,
        health_checker=health_checker,
    )


@forge_app.command("install")
def install(
    wheel: Annotated[
        Path | None,
        typer.Option(
            "--wheel",
            help="Path to wheel file. If not provided, auto-detects latest in dist/.",
        ),
    ] = None,
    force: Annotated[
        bool,
        typer.Option(
            "--force",
            "-f",
            help="Force reinstall even if already installed.",
        ),
    ] = False,
    no_verify: Annotated[
        bool,
        typer.Option(
            "--no-verify",
            help="Skip post-install verification phase.",
        ),
    ] = False,
    no_prompt: Annotated[
        bool,
        typer.Option(
            "--no-prompt",
            help="Skip confirmation prompts (for CI environments).",
        ),
    ] = False,
) -> None:
    """Install crafter-ai from a wheel package.

    Runs pre-flight checks, installs via pipx, and verifies installation.
    If no --wheel is provided, auto-detects the latest wheel in dist/.
    """
    start_time = datetime.now()

    # Resolve wheel path
    wheel_path: Path | None = wheel
    if wheel_path is None:
        wheel_path = find_latest_wheel()
        if wheel_path is None:
            console.print(
                "[bold red]Error:[/bold red] No wheel file found in dist/. "
                "Run 'forge build' first or provide --wheel path."
            )
            raise typer.Exit(code=1)

    # Verify wheel exists
    if not wheel_path.exists():
        console.print(f"[bold red]Error:[/bold red] Wheel file not found: {wheel_path}")
        raise typer.Exit(code=1)

    # Display header
    display_header(wheel_path)

    # Run and display pre-flight checks
    pre_flight_results = run_pre_flight_checks()
    display_pre_flight_results(pre_flight_results)

    # Determine if we should prompt
    ci_mode = is_ci_mode()
    should_prompt = not ci_mode and not no_prompt

    # Prompt for confirmation
    if should_prompt:
        proceed = typer.confirm("Proceed with install?", default=True)
        if not proceed:
            console.print("[yellow]Install cancelled by user.[/yellow]")
            raise typer.Exit(code=0)

    # Create install service and run installation
    service = create_install_service(skip_verification=no_verify)
    install_result = service.install(wheel_path, force=force)

    if not install_result.success:
        display_failure(install_result.error_message or "Unknown error")
        raise typer.Exit(code=1)

    # Generate and display release report
    report_service = ReleaseReportService()
    release_report = report_service.generate(
        install_result=install_result,
        wheel_path=wheel_path,
        start_time=start_time,
        backup_path=None,  # Would come from install result in full implementation
    )

    formatted_report = report_service.format_console(release_report)
    console.print(formatted_report)

    raise typer.Exit(code=0)
