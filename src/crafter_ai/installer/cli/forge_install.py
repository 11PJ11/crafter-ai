"""Forge install CLI command.

This module provides the 'forge install' command for the crafter-ai CLI.
Displays pre-flight checks, prompts for confirmation, runs install service,
and displays release report. Includes auto-chain build when no wheel found.
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
from crafter_ai.installer.adapters.build_adapter import SubprocessBuildAdapter
from crafter_ai.installer.adapters.pipx_adapter import SubprocessPipxAdapter
from crafter_ai.installer.checks.install_checks import create_install_check_registry
from crafter_ai.installer.cli.forge_build import forge_app
from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult
from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.services.build_service import BuildService
from crafter_ai.installer.services.install_service import InstallService
from crafter_ai.installer.services.release_readiness_service import (
    ReleaseReadinessService,
)
from crafter_ai.installer.services.release_report_service import ReleaseReportService
from crafter_ai.installer.services.version_bump_service import VersionBumpService
from crafter_ai.installer.services.wheel_validation_service import (
    WheelValidationService,
)


console = Console()


def is_ci_mode() -> bool:
    """Check if running in CI environment.

    Returns:
        True if CI environment variable is set to 'true'.
    """
    return os.environ.get("CI", "").lower() == "true"


def create_build_service() -> BuildService:
    """Factory function to create a BuildService with all dependencies.

    Returns:
        Configured BuildService instance.
    """
    check_executor = CheckExecutor()
    build_port = SubprocessBuildAdapter()
    version_bump_service = VersionBumpService()
    wheel_validation_service = WheelValidationService()
    artifact_registry = ArtifactRegistry()

    return BuildService(
        check_executor=check_executor,
        build_port=build_port,
        version_bump_service=version_bump_service,
        wheel_validation_service=wheel_validation_service,
        artifact_registry=artifact_registry,
    )


def run_auto_chain_build(no_prompt: bool) -> Path | None:
    """Run auto-chain build when no wheel is found.

    Prompts user (unless in CI mode or --no-prompt) to build first.
    If user agrees or running non-interactively, executes build.

    Args:
        no_prompt: If True, skip prompts and auto-build.

    Returns:
        Path to built wheel if successful, None if build failed or user declined.

    Raises:
        typer.Exit: If user declines build or build fails.
    """
    ci_mode = is_ci_mode()
    should_prompt = not ci_mode and not no_prompt

    if should_prompt:
        proceed = typer.confirm("No wheel found. Build first?", default=True)
        if not proceed:
            console.print("[yellow]Run forge build first[/yellow]")
            raise typer.Exit(code=1)
    else:
        console.print("[cyan]No wheel found. Auto-building...[/cyan]")

    # Execute build
    from crafter_ai import __version__

    current_version = __version__
    output_dir = Path("dist")
    output_dir.mkdir(exist_ok=True)

    build_service = create_build_service()
    build_result = build_service.execute(
        current_version=current_version,
        output_dir=output_dir,
    )

    if not build_result.success:
        console.print(
            Panel(
                f"[bold red]Build failed:[/bold red] {build_result.error_message}",
                title="Build Failed",
                border_style="red",
            )
        )
        raise typer.Exit(code=1)

    console.print(
        Panel(
            f"[bold green]Build complete:[/bold green] {build_result.wheel_path}",
            title="Build Success",
            border_style="green",
        )
    )

    return build_result.wheel_path


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
    If no wheel exists, offers to build first (auto-chain).
    """
    start_time = datetime.now()

    # Resolve wheel path
    wheel_path: Path | None = wheel
    if wheel_path is None:
        wheel_path = find_latest_wheel()
        if wheel_path is None:
            # Auto-chain: offer to build first
            wheel_path = run_auto_chain_build(no_prompt)
            # After build, find the newly created wheel
            if wheel_path is None:
                wheel_path = find_latest_wheel()
            if wheel_path is None:
                console.print(
                    "[bold red]Error:[/bold red] Build succeeded but no wheel found."
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
