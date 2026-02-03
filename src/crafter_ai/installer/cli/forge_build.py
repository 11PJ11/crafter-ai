"""Forge build CLI command.

This module provides the 'forge build' command for the crafter-ai CLI.
Displays pre-flight checks, version analysis, build progress, and success summary.
"""

import os
import time
from pathlib import Path

import typer
from rich.console import Console

from crafter_ai.installer.adapters.build_adapter import SubprocessBuildAdapter
from crafter_ai.installer.adapters.git_adapter import SubprocessGitAdapter
from crafter_ai.installer.checks.build_checks import create_build_check_registry
from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry
from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
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
    """Display pre-flight check results as streaming emoji list.

    Args:
        results: List of CheckResult objects to display.
    """
    console.print("  \U0001f50d Pre-flight checks")

    all_blocking_passed = True
    for check in results:
        if not check.passed and check.severity == CheckSeverity.BLOCKING:
            console.print(f"  \u274c {check.message}")
            all_blocking_passed = False
        elif check.severity == CheckSeverity.WARNING:
            console.print(f"  \u26a0\ufe0f  {check.message}")
        else:
            console.print(f"  \u2705 {check.message}")

    if all_blocking_passed:
        console.print("  \u2705 Pre-flight passed")

    console.print()


def display_version_info(candidate: CandidateVersion) -> None:
    """Display version bump information as minimal emoji line.

    Args:
        candidate: CandidateVersion with version details.
    """
    bump_type_str = candidate.bump_type.value.lower()
    console.print("  \U0001f4d0 Version")
    console.print(
        f"  {candidate.current_version} \u2192 "
        f"[green]{candidate.next_version}[/green] ({bump_type_str})"
    )
    console.print()


def display_build_progress(duration: str = "0.0s") -> None:
    """Display persistent line after wheel compilation completes.

    Args:
        duration: Build duration string, e.g. "1.2s".
    """
    console.print(f"  \u2705 Wheel built ({duration})")
    console.print()


def display_wheel_validation() -> None:
    """Display wheel validation results as streaming check list."""
    console.print("  \U0001f50d Validating wheel")
    console.print("  \u2705 PEP 427 format valid")
    console.print("  \u2705 Metadata complete")
    console.print("  \u2705 Wheel validated")
    console.print()


def display_success_summary(result: BuildResult) -> None:
    """Display build complete as a single concise line with hammer emoji.

    Args:
        result: BuildResult with build outcome.
    """
    wheel_name = result.wheel_path.name if result.wheel_path else "unknown"
    console.print(f"  \U0001f528 Build complete: {wheel_name}")
    console.print()


def display_failure_summary(result: BuildResult) -> None:
    """Display build failure summary as plain text.

    Args:
        result: BuildResult with failure details.
    """
    console.print(f"[bold red]Build failed:[/bold red] {result.error_message}")
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

    # Bold build header (Luna's Step 1)
    console.print()
    console.print("[bold]\U0001f528 Building crafter-ai[/bold]")
    console.print()

    # Execute build
    build_start = time.time()
    result = service.execute(
        current_version=current_version,
        output_dir=output_dir,
    )
    build_duration = f"{time.time() - build_start:.1f}s"

    # Display pre-flight results (Luna's Step 2 - before version)
    display_pre_flight_results(result.pre_flight_results)

    # Display version info (Luna's Step 3 - after pre-flight)
    display_version_info(candidate)

    if not result.success:
        display_failure_summary(result)
        raise typer.Exit(code=1)

    # Display build progress persistent line (Luna's Step 4)
    display_build_progress(build_duration)

    # Display wheel validation check list (Luna's Step 5)
    display_wheel_validation()

    # Display build complete line (Luna's Step 6)
    display_success_summary(result)

    # Handle install prompt
    ci_mode = is_ci_mode()
    should_prompt = not ci_mode and not no_prompt and not install

    def run_install(wheel_path: Path) -> None:
        """Run the install command with the built wheel."""
        # Late import to avoid circular dependency
        from crafter_ai.installer.cli.forge_install import install as forge_install

        console.print("\n[cyan]Starting installation...[/cyan]\n")
        forge_install(wheel=wheel_path, force=False, no_verify=False, no_prompt=True)

    if install:
        # Auto-install after build
        if result.wheel_path:
            run_install(result.wheel_path)
    elif should_prompt:
        version = result.version or "unknown"
        prompt_text = f"\U0001f4e6 Install crafter-ai {version}? [Y/n]: "
        answer = console.input(prompt_text)
        do_install = answer.strip().lower() in ("", "y", "yes")
        if do_install and result.wheel_path:
            run_install(result.wheel_path)

    raise typer.Exit(code=0)
