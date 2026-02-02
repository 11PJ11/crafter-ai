"""Forge build CLI command.

This module provides the 'forge build' command for the crafter-ai CLI.
Displays pre-flight checks, version analysis, build progress, and success summary.
"""

import os
from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from crafter_ai.installer.adapters.build_adapter import SubprocessBuildAdapter
from crafter_ai.installer.adapters.git_adapter import SubprocessGitAdapter
from crafter_ai.installer.checks.build_checks import create_build_check_registry
from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry
from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult
from crafter_ai.installer.services.build_service import BuildResult, BuildService
from crafter_ai.installer.services.version_bump_service import VersionBumpService
from crafter_ai.installer.services.wheel_validation_service import (
    WheelValidationService,
)


console = Console()

forge_app = typer.Typer(
    name="forge",
    help="Build and release commands for crafter-ai.",
    no_args_is_help=True,
)


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


def is_ci_mode() -> bool:
    """Check if running in CI environment.

    Returns:
        True if CI environment variable is set to 'true'.
    """
    return os.environ.get("CI", "").lower() == "true"


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
        status = "[green]✓[/green]" if check.passed else "[red]✗[/red]"

        table.add_row(check.name, status, check.message)

    console.print(table)
    console.print()


def display_version_info(candidate: CandidateVersion) -> None:
    """Display version bump information.

    Args:
        candidate: CandidateVersion with version details.
    """
    bump_type_str = candidate.bump_type.value.upper()
    console.print(
        Panel(
            f"[bold]Version Bump:[/bold] {candidate.current_version} -> "
            f"[green]{candidate.next_version}[/green] ({bump_type_str})",
            title="Version Analysis",
        )
    )
    console.print()


def display_success_summary(result: BuildResult) -> None:
    """Display build success summary.

    Args:
        result: BuildResult with build outcome.
    """
    wheel_name = result.wheel_path.name if result.wheel_path else "unknown"
    version = result.version or "unknown"
    package_name = (
        result.validation_result.package_name if result.validation_result else "unknown"
    )

    summary = (
        f"[bold green]FORGE: BUILD COMPLETE[/bold green]\n\n"
        f"Wheel: {wheel_name}\n"
        f"Version: {version}\n"
        f"Package: {package_name}"
    )

    console.print(Panel(summary, title="Build Summary", border_style="green"))
    console.print()


def display_failure_summary(result: BuildResult) -> None:
    """Display build failure summary.

    Args:
        result: BuildResult with failure details.
    """
    console.print(
        Panel(
            f"[bold red]FORGE: BUILD FAILED[/bold red]\n\n{result.error_message}",
            title="Build Failed",
            border_style="red",
        )
    )
    console.print()


@forge_app.command("build")
def build(
    no_prompt: bool = typer.Option(
        False,
        "--no-prompt",
        help="Skip install prompt after build.",
    ),
    install: bool = typer.Option(
        False,
        "--install",
        help="Automatically install after successful build.",
    ),
    force_version: str | None = typer.Option(
        None,
        "--force-version",
        help="Override auto-calculated version with specified version.",
    ),
) -> None:
    """Build a wheel package for crafter-ai.

    Runs pre-flight checks, determines version bump, builds wheel,
    and validates the result.
    """
    service = create_build_service()

    # Get current version from package
    from crafter_ai import __version__

    current_version = __version__

    # Determine output directory
    output_dir = Path("dist")
    output_dir.mkdir(exist_ok=True)

    # Determine version (possibly forced)
    if force_version:
        # Create a forced candidate
        candidate = CandidateVersion(
            current_version=current_version,
            bump_type=BumpType.NONE,
            next_version=force_version,
            commit_messages=[],
            is_prerelease=False,
            prerelease_suffix=None,
        )
    else:
        candidate = service.determine_version(current_version)

    # Display version info
    display_version_info(candidate)

    # Execute build
    result = service.execute(
        current_version=current_version,
        output_dir=output_dir,
    )

    # Display pre-flight results
    display_pre_flight_results(result.pre_flight_results)

    if not result.success:
        display_failure_summary(result)
        raise typer.Exit(code=1)

    # Display success summary
    display_success_summary(result)

    # Handle install prompt
    ci_mode = is_ci_mode()
    should_prompt = not ci_mode and not no_prompt and not install

    if install:
        # Auto-install (implementation not yet done, just skip prompt)
        console.print("[yellow]Auto-install not yet implemented.[/yellow]")
    elif should_prompt:
        do_install = typer.confirm("Install locally now?", default=True)
        if do_install:
            console.print("[yellow]Install not yet implemented.[/yellow]")

    raise typer.Exit(code=0)
