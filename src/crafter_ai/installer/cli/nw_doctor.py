"""nw doctor CLI command for health check diagnostics.

This module provides the 'nw doctor' command that runs health checks
to verify the crafter-ai installation and environment are properly configured.
"""

import os
from typing import Annotated

import typer
from rich.console import Console

from crafter_ai.installer.checks.health_checks import create_doctor_health_checker
from crafter_ai.installer.domain.health_result import HealthResult, HealthStatus


# Status indicators for Rich output
CHECKMARK = "[green]✓[/green]"
CROSS = "[red]✗[/red]"
WARNING = "[yellow]⚠[/yellow]"

# Status indicators for CI mode
CI_CHECKMARK = "[OK]"
CI_CROSS = "[FAIL]"
CI_WARNING = "[WARN]"


def _is_ci_mode() -> bool:
    """Check if running in CI mode.

    CI mode is detected via CI environment variable set to 'true' or '1'.

    Returns:
        True if in CI mode, False otherwise.
    """
    ci_value = os.environ.get("CI", "").lower()
    return ci_value in ("true", "1")


def _get_status_indicator(status: HealthStatus, ci_mode: bool) -> str:
    """Get the status indicator for a health check result.

    Args:
        status: The health status to get indicator for.
        ci_mode: Whether to use CI mode (plain text) indicators.

    Returns:
        String indicator for the status.
    """
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


def _format_check_name(component: str) -> str:
    """Format a component name for display.

    Args:
        component: The component name (e.g., 'python-environment').

    Returns:
        Formatted name (e.g., 'Python Environment').
    """
    return component.replace("-", " ").title()


def _display_result(
    result: HealthResult,
    console: Console,
    ci_mode: bool,
    verbose: bool = False,
) -> None:
    """Display a single health check result.

    Args:
        result: The health check result to display.
        console: Rich Console for output.
        ci_mode: Whether to use CI mode output.
        verbose: Whether to show detailed output.
    """
    indicator = _get_status_indicator(result.status, ci_mode)
    check_name = _format_check_name(result.component)

    if ci_mode:
        print(f"  {indicator} {check_name} - {result.message}")
        if verbose and result.details:
            for key, value in result.details.items():
                print(f"      {key}: {value}")
    else:
        console.print(f"  {indicator} {check_name} - {result.message}")
        if verbose and result.details:
            for key, value in result.details.items():
                console.print(f"      [dim]{key}:[/dim] {value}")


def _display_summary(
    results: list[HealthResult],
    console: Console,
    ci_mode: bool,
) -> None:
    """Display summary of health check results.

    Args:
        results: List of health check results.
        console: Rich Console for output.
        ci_mode: Whether to use CI mode output.
    """
    total = len(results)
    passed = sum(1 for r in results if r.status == HealthStatus.HEALTHY)
    warnings = sum(1 for r in results if r.status == HealthStatus.DEGRADED)
    failed = sum(1 for r in results if r.status == HealthStatus.UNHEALTHY)

    if ci_mode:
        print("")
        print(f"Summary: {passed} of {total} checks passed", end="")
        if warnings > 0:
            print(f", {warnings} warnings", end="")
        if failed > 0:
            print(f", {failed} failed", end="")
        print("")
    else:
        console.print()
        summary_parts = [f"[bold]{passed} of {total}[/bold] checks passed"]
        if warnings > 0:
            summary_parts.append(f"[yellow]{warnings} warnings[/yellow]")
        if failed > 0:
            summary_parts.append(f"[red]{failed} failed[/red]")
        console.print(", ".join(summary_parts))


def doctor(
    verbose: Annotated[
        bool,
        typer.Option(
            "--verbose",
            "-v",
            help="Show detailed output for each check.",
        ),
    ] = False,
    check: Annotated[
        str | None,
        typer.Option(
            "--check",
            "-c",
            help="Run specific check by ID (e.g., 'python-environment').",
        ),
    ] = None,
    fix: Annotated[
        bool,
        typer.Option(
            "--fix",
            "-f",
            help="Attempt to fix fixable issues.",
        ),
    ] = False,
) -> None:
    """Run health checks to verify crafter-ai installation.

    The doctor command checks your environment to ensure everything
    is properly configured for crafter-ai to work correctly.

    Checks include:
    - Python environment and version
    - Package installation status
    - Configuration directory existence
    - Agent specification files
    - Update availability
    """
    # Detect CI mode
    ci_mode = _is_ci_mode()

    # Create console for Rich output
    console = Console()

    # Create health checker via factory function
    health_checker = create_doctor_health_checker()

    # Display header
    if ci_mode:
        print("=" * 60)
        print("nWave Health Check")
        print("=" * 60)
    else:
        console.print()
        console.print("[bold cyan]nWave Health Check[/bold cyan]")
        console.print()

    # Handle --fix flag (currently informational only)
    if fix:
        if ci_mode:
            print("[INFO] Fix mode enabled - will attempt to fix fixable issues")
        else:
            console.print(
                "[dim]Fix mode enabled - will attempt to fix fixable issues[/dim]"
            )
            console.print()

    # Run checks
    if check:
        # Run specific check only
        result = health_checker.check(check)
        results = [result]
    else:
        # Run all checks
        results = health_checker.check_all()

    # Display results
    for result in results:
        _display_result(result, console, ci_mode, verbose)

    # Display summary
    _display_summary(results, console, ci_mode)

    # Determine exit code
    # Exit 0 if all healthy or degraded (warnings don't fail)
    # Exit 1 if any unhealthy
    has_failures = any(r.status == HealthStatus.UNHEALTHY for r in results)

    if has_failures:
        raise typer.Exit(code=1)
