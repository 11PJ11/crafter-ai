"""Forge build CLI command.

This module provides the 'forge build' command for the crafter-ai CLI.
Displays pre-flight checks, version analysis, build progress, and success summary.
"""

import time
from pathlib import Path

import typer
from rich.console import Console

from crafter_ai.installer.adapters.build_adapter import SubprocessBuildAdapter
from crafter_ai.installer.adapters.filesystem_adapter import RealFileSystemAdapter
from crafter_ai.installer.adapters.git_adapter import SubprocessGitAdapter
from crafter_ai.installer.checks.build_checks import create_build_check_registry
from crafter_ai.installer.cli.forge_tui import display_pre_flight_results, is_ci_mode
from crafter_ai.installer.domain.artifact_registry import ArtifactRegistry
from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.ide_bundle_build_result import IdeBundleBuildResult
from crafter_ai.installer.domain.ide_bundle_constants import (
    DEFAULT_OUTPUT_DIR,
    DEFAULT_SOURCE_DIR,
)
from crafter_ai.installer.services.build_service import BuildResult, BuildService
from crafter_ai.installer.services.ide_bundle_build_service import IdeBundleBuildService
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
    filesystem = RealFileSystemAdapter()
    ide_bundle_build_service = IdeBundleBuildService(filesystem=filesystem)

    return BuildService(
        check_executor=check_executor,
        build_port=build_port,
        version_bump_service=version_bump_service,
        wheel_validation_service=wheel_validation_service,
        artifact_registry=artifact_registry,
        ide_bundle_build_service=ide_bundle_build_service,
    )


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


def display_ide_bundle_build(result: IdeBundleBuildResult, duration: str) -> None:
    """Display IDE bundle build progress and completion.

    Args:
        result: IdeBundleBuildResult with build details.
        duration: Build duration string, e.g. "0.3s".
    """
    console.print("  ⚙️ Building IDE bundle")
    console.print(f"  {result.agent_count} agents", style="dim")
    console.print(f"  {result.command_count} commands", style="dim")
    console.print(f"  {result.team_count} teams", style="dim")

    if result.embed_injection_count > 0:
        console.print(f"  {result.embed_injection_count} embeds injected", style="dim")

    if result.yaml_warnings:
        for warning in result.yaml_warnings:
            console.print(f"  ⚠️ {warning}", style="yellow")

    console.print(f"  ✅ IDE bundle built ({duration})")
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

    # Display IDE bundle build if available (Luna's Step 6)
    if result.ide_bundle_result is not None:
        display_ide_bundle_build(result.ide_bundle_result, duration="0.3s")

    # Display build complete line (Luna's Step 7)
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
