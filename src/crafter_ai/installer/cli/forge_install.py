"""Forge install CLI command.

This module provides the 'forge install' command for the crafter-ai CLI.
Displays pre-flight checks, prompts for confirmation, runs install service,
and displays release report. Includes auto-chain build when no wheel found.
Supports multiple wheel selection when multiple wheels exist in dist/.
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.prompt import IntPrompt

from crafter_ai.installer.adapters.backup_adapter import FileSystemBackupAdapter
from crafter_ai.installer.adapters.build_adapter import SubprocessBuildAdapter
from crafter_ai.installer.adapters.git_adapter import SubprocessGitAdapter
from crafter_ai.installer.adapters.pipx_adapter import SubprocessPipxAdapter
from crafter_ai.installer.checks.build_checks import create_build_check_registry
from crafter_ai.installer.checks.install_checks import create_install_check_registry
from crafter_ai.installer.cli.forge_build import forge_app
from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
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
    registry = create_build_check_registry()
    check_executor = CheckExecutor(registry)
    build_port = SubprocessBuildAdapter()
    git_port = SubprocessGitAdapter()
    version_bump_service = VersionBumpService(git_port)
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
            f"[bold red]Build failed:[/bold red] {build_result.error_message}"
        )
        raise typer.Exit(code=1)

    console.print(
        f"[bold green]Build complete:[/bold green] {build_result.wheel_path}"
    )

    return build_result.wheel_path


def list_wheels_in_dist(dist_dir: Path | None = None) -> list[Path]:
    """List all wheel files in dist directory, sorted by modification time.

    Args:
        dist_dir: Optional directory to search. Defaults to ./dist.

    Returns:
        List of wheel paths, sorted by modification time (newest first).
        Empty list if directory doesn't exist or contains no wheels.
    """
    search_dir = dist_dir or Path("dist")
    if not search_dir.exists():
        return []

    wheels = list(search_dir.glob("*.whl"))
    if not wheels:
        return []

    # Sort by modification time, newest first
    wheels.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return wheels


def format_wheel_info(wheel_path: Path) -> str:
    """Format wheel information for display.

    Args:
        wheel_path: Path to the wheel file.

    Returns:
        Formatted string with wheel name, date, and size.
    """
    stat = wheel_path.stat()
    mtime = datetime.fromtimestamp(stat.st_mtime)
    date_str = mtime.strftime("%Y-%m-%d %H:%M")

    # Format size in human-readable format
    size_bytes = stat.st_size
    if size_bytes >= 1024 * 1024:
        size_str = f"{size_bytes / (1024 * 1024):.1f} MB"
    elif size_bytes >= 1024:
        size_str = f"{size_bytes / 1024:.1f} KB"
    else:
        size_str = f"{size_bytes} B"

    return f"{wheel_path.name} ({date_str}, {size_str})"


def prompt_wheel_selection(wheels: list[Path]) -> Path:
    """Prompt user to select a wheel from multiple options.

    Displays a numbered list of wheels and prompts for selection.
    In CI mode or with --no-prompt, auto-selects the newest wheel.

    Args:
        wheels: List of wheel paths (assumed sorted, newest first).

    Returns:
        Selected wheel path.

    Raises:
        typer.Exit: If selection is invalid after retries.
    """
    # Display numbered list
    console.print("\n[bold cyan]Multiple wheels found:[/bold cyan]\n")
    for i, wheel in enumerate(wheels, 1):
        info = format_wheel_info(wheel)
        console.print(f"  {i}. {info}")
    console.print()

    # Get user selection with validation
    while True:
        try:
            selection = IntPrompt.ask(
                f"Select wheel [1-{len(wheels)}]",
                default=1,
            )
            if 1 <= selection <= len(wheels):
                return wheels[selection - 1]
            console.print(
                f"[red]Invalid selection. Please enter a number between 1 and {len(wheels)}.[/red]"
            )
        except (ValueError, KeyboardInterrupt):
            console.print("[yellow]Selection cancelled.[/yellow]")
            raise typer.Exit(code=1)


def find_latest_wheel(dist_dir: Path | None = None) -> Path | None:
    """Find the latest wheel file in dist directory.

    Args:
        dist_dir: Optional directory to search. Defaults to ./dist.

    Returns:
        Path to the latest wheel file, or None if not found.
    """
    wheels = list_wheels_in_dist(dist_dir)
    return wheels[0] if wheels else None


def run_pre_flight_checks() -> list[CheckResult]:
    """Run pre-flight checks for installation.

    Returns:
        List of CheckResult from pre-flight checks.
    """
    registry = create_install_check_registry()
    check_executor = CheckExecutor(registry)
    return check_executor.run_all()


def display_pre_flight_results(results: list[CheckResult]) -> None:
    """Display pre-flight check results as streaming emoji list.

    Args:
        results: List of CheckResult objects to display.
    """
    console.print("  \U0001f50d Pre-flight checks")
    for check in results:
        if not check.passed and check.severity == CheckSeverity.BLOCKING:
            console.print(f"  \u274c {check.message}")
        elif not check.passed and check.severity == CheckSeverity.WARNING:
            console.print(f"  \u26a0\ufe0f  {check.message}")
        else:
            console.print(f"  \u2705 {check.message}")

    all_blocking_passed = all(
        check.passed for check in results if check.severity == CheckSeverity.BLOCKING
    )
    if all_blocking_passed:
        console.print("  \u2705 Pre-flight passed")


def get_blocking_failures(results: list[CheckResult]) -> list[CheckResult]:
    """Get all blocking failures from pre-flight check results.

    Args:
        results: List of CheckResult objects.

    Returns:
        List of CheckResult objects that failed with BLOCKING severity.
    """
    return [r for r in results if not r.passed and r.severity == CheckSeverity.BLOCKING]


def display_blocking_failures(failures: list[CheckResult]) -> None:
    """Display blocking failure summary with remediation hints.

    Args:
        failures: List of blocking CheckResult failures.
    """
    console.print("[bold red]Install blocked[/bold red]")
    console.print("The following blocking checks failed:")

    for failure in failures:
        console.print(f"  [red]{failure.name}:[/red] {failure.message}")
        if failure.remediation:
            console.print(f"    Fix: {failure.remediation}")

    console.print()


def display_header(wheel_path: Path) -> None:
    """Display install header with package emoji.

    Args:
        wheel_path: Path to the wheel being installed.
    """
    console.print()
    console.print("[bold]\U0001f4e6 Installing crafter-ai[/bold]")


def display_failure(error_message: str) -> None:
    """Display installation failure message.

    Args:
        error_message: Error message to display.
    """
    console.print(f"[bold red]Install failed:[/bold red] {error_message}")
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
        wheels = list_wheels_in_dist()
        if not wheels:
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
        elif len(wheels) == 1:
            # Single wheel: use it directly
            wheel_path = wheels[0]
        else:
            # Multiple wheels: selection logic
            ci_mode = is_ci_mode()
            if ci_mode or no_prompt:
                # Auto-select newest (first in sorted list)
                wheel_path = wheels[0]
                console.print(
                    f"[cyan]Auto-selected newest wheel:[/cyan] {wheel_path.name}"
                )
            else:
                # Prompt user to select
                wheel_path = prompt_wheel_selection(wheels)

    # Verify wheel exists
    if not wheel_path.exists():
        console.print(f"[bold red]Error:[/bold red] Wheel file not found: {wheel_path}")
        raise typer.Exit(code=1)

    # Display header
    display_header(wheel_path)

    # Run and display pre-flight checks
    pre_flight_results = run_pre_flight_checks()
    display_pre_flight_results(pre_flight_results)

    # Check for blocking failures - stop if any exist
    blocking_failures = get_blocking_failures(pre_flight_results)
    if blocking_failures:
        display_blocking_failures(blocking_failures)
        raise typer.Exit(code=1)

    # Determine if we should prompt
    ci_mode = is_ci_mode()
    should_prompt = not ci_mode and not no_prompt

    # Prompt for confirmation
    if should_prompt:
        proceed = typer.confirm("Proceed with install?", default=True)
        if not proceed:
            console.print("[yellow]Install cancelled by user.[/yellow]")
            raise typer.Exit(code=0)

    # Create install service and run installation with progress indicator
    service = create_install_service(skip_verification=no_verify)

    # Import InstallPhase for the progress callback
    from crafter_ai.installer.services.install_service import InstallPhase

    # Phase icons and descriptions for beautiful output
    phase_info = {
        InstallPhase.PREFLIGHT: ("🔍", "Pre-flight checks"),
        InstallPhase.READINESS: ("📋", "Validating wheel readiness"),
        InstallPhase.BACKUP: ("💾", "Creating backup"),
        InstallPhase.INSTALL: ("📦", "Installing via pipx"),
        InstallPhase.VERIFICATION: ("✅", "Verifying installation"),
    }

    console.print()  # Add spacing

    # Track current status for the spinner
    status_handle = console.status(
        "[cyan]⏳ Preparing installation...[/cyan]", spinner="dots"
    )
    status_handle.start()

    def on_progress(phase: InstallPhase, message: str) -> None:
        """Update the spinner with current phase information."""
        icon, phase_name = phase_info.get(phase, ("•", phase.value))
        status_handle.update(f"[cyan]{icon} {phase_name}:[/cyan] {message}")

    try:
        install_result = service.install(wheel_path, force=force, on_progress=on_progress)
    finally:
        status_handle.stop()

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
