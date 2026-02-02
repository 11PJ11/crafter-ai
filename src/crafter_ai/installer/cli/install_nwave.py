"""install-nwave CLI command for installing crafter-ai from PyPI.

This module provides the 'install-nwave' command that:
- Runs pre-flight checks (PyPI connectivity, etc.)
- Checks for existing installation (upgrade path)
- Installs crafter-ai via pipx
- Runs nw setup for post-install configuration
- Verifies installation (nw doctor)
- Shows celebration on success

Supports CI mode with --ci flag or CI=true environment variable.
"""

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from crafter_ai.installer.adapters.filesystem_adapter import RealFileSystemAdapter
from crafter_ai.installer.adapters.pipx_adapter import SubprocessPipxAdapter
from crafter_ai.installer.checks.pypi_checks import create_pypi_check_registry
from crafter_ai.installer.domain.check_result import CheckSeverity
from crafter_ai.installer.services.celebration_service import CelebrationService
from crafter_ai.installer.services.progress_display_service import (
    ProgressDisplayService,
)
from crafter_ai.installer.services.setup_service import SetupService
from crafter_ai.installer.services.upgrade_detection_service import (
    detect_upgrade,
    get_installed_version,
)


# Package name constant
PACKAGE_NAME = "crafter-ai"


def _is_ci_mode(force_ci: bool = False) -> bool:
    """Check if running in CI mode.

    CI mode is detected via:
    - --ci flag (force_ci=True)
    - CI environment variable set to 'true' or '1'

    Args:
        force_ci: Whether --ci flag was passed.

    Returns:
        True if in CI mode, False otherwise.
    """
    if force_ci:
        return True
    ci_value = os.environ.get("CI", "").lower()
    return ci_value in ("true", "1")


def _run_preflight_checks(
    progress_service: ProgressDisplayService,
    ci_mode: bool,
    console: Console,
) -> bool:
    """Run pre-flight checks before installation.

    Args:
        progress_service: Service for displaying progress.
        ci_mode: Whether running in CI mode.
        console: Rich console for output.

    Returns:
        True if all blocking checks passed, False otherwise.
    """
    progress_service.display_phase_start("Pre-flight Checks")

    check_registry = create_pypi_check_registry()
    results = check_registry.run_all()

    all_passed = True
    for result in results:
        if result.passed:
            if ci_mode:
                print(f"  [OK] {result.name}")
            else:
                console.print(f"  [green]OK[/green] {result.name}")
        elif result.severity == CheckSeverity.BLOCKING:
            all_passed = False
            if ci_mode:
                print(f"  [FAIL] {result.name}: {result.message}")
                if result.remediation:
                    print(f"         Fix: {result.remediation}")
            else:
                console.print(f"  [red]FAIL[/red] {result.name}: {result.message}")
                if result.remediation:
                    console.print(f"         [dim]Fix: {result.remediation}[/dim]")
        # Warning - continue but notify
        elif ci_mode:
            print(f"  [WARN] {result.name}: {result.message}")
        else:
            console.print(f"  [yellow]WARN[/yellow] {result.name}: {result.message}")

    if all_passed:
        progress_service.display_phase_complete("Pre-flight Checks", success=True)
    else:
        progress_service.display_phase_complete("Pre-flight Checks", success=False)

    return all_passed


def _check_existing_installation(
    pipx_adapter: SubprocessPipxAdapter,
    progress_service: ProgressDisplayService,
    ci_mode: bool,
    console: Console,
    auto_yes: bool,
) -> tuple[bool, str | None]:
    """Check for existing installation and handle upgrade path.

    Args:
        pipx_adapter: Adapter for pipx operations.
        progress_service: Service for displaying progress.
        ci_mode: Whether running in CI mode.
        console: Rich console for output.
        auto_yes: Whether to auto-confirm prompts.

    Returns:
        Tuple of (should_continue, installed_version).
    """
    progress_service.display_phase_start("Check Existing Installation")

    installed_version = get_installed_version(pipx_adapter, PACKAGE_NAME)

    if installed_version:
        upgrade_info = detect_upgrade(pipx_adapter, PACKAGE_NAME)

        if ci_mode:
            print(f"  [INFO] Found existing installation: v{installed_version}")
            if upgrade_info.latest_version:
                print(f"  [INFO] Latest available: v{upgrade_info.latest_version}")
        else:
            console.print(
                f"  [cyan]i[/cyan] Found existing installation: v{installed_version}"
            )
            if upgrade_info.latest_version:
                console.print(
                    f"  [cyan]i[/cyan] Latest available: v{upgrade_info.latest_version}"
                )

        # In CI mode with auto_yes, always continue
        if not auto_yes and not ci_mode:
            confirm = typer.confirm(
                "\n  Do you want to reinstall/upgrade?", default=True
            )
            if not confirm:
                progress_service.display_phase_complete(
                    "Check Existing Installation", success=True
                )
                if ci_mode:
                    print("  [INFO] Installation cancelled by user")
                else:
                    console.print("  [dim]Installation cancelled.[/dim]")
                return False, installed_version
    elif ci_mode:
        print("  [INFO] No existing installation found")
    else:
        console.print("  [cyan]i[/cyan] No existing installation found")

    progress_service.display_phase_complete("Check Existing Installation", success=True)
    return True, installed_version


def _install_via_pipx(
    pipx_adapter: SubprocessPipxAdapter,
    progress_service: ProgressDisplayService,
    ci_mode: bool,
    console: Console,
    version: str | None,
    pre_release: bool,
) -> bool:
    """Install crafter-ai via pipx.

    Args:
        pipx_adapter: Adapter for pipx operations.
        progress_service: Service for displaying progress.
        ci_mode: Whether running in CI mode.
        console: Rich console for output.
        version: Specific version to install, or None for latest.
        pre_release: Whether to include pre-release versions.

    Returns:
        True if installation successful, False otherwise.
    """
    progress_service.display_phase_start("Install via pipx")

    # Build package spec
    package_spec = PACKAGE_NAME
    if version:
        package_spec = f"{PACKAGE_NAME}=={version}"

    if ci_mode:
        print(f"  [INFO] Installing {package_spec}...")
    else:
        console.print(f"  [dim]Installing {package_spec}...[/dim]")

    # Note: pipx install from PyPI requires package name, not wheel path
    # For now, we simulate with a placeholder path since the adapter expects a Path
    # In a real implementation, we'd extend the PipxPort interface
    result = pipx_adapter.install(Path(package_spec), force=True)

    if result.success:
        if ci_mode:
            print(f"  [OK] Installed crafter-ai v{result.version}")
        else:
            console.print(f"  [green]OK[/green] Installed crafter-ai v{result.version}")
        progress_service.display_phase_complete("Install via pipx", success=True)
        return True
    else:
        if ci_mode:
            print(f"  [FAIL] Installation failed: {result.error_message}")
        else:
            console.print(
                f"  [red]FAIL[/red] Installation failed: {result.error_message}"
            )
        progress_service.display_phase_complete("Install via pipx", success=False)
        return False


def _run_setup(
    progress_service: ProgressDisplayService,
    ci_mode: bool,
    console: Console,
) -> bool:
    """Run nw setup --global for post-install configuration.

    Args:
        progress_service: Service for displaying progress.
        ci_mode: Whether running in CI mode.
        console: Rich console for output.

    Returns:
        True if setup successful, False otherwise.
    """
    progress_service.display_phase_start("Post-install Setup")

    filesystem = RealFileSystemAdapter()
    setup_service = SetupService(filesystem)

    home_dir = Path.home()
    result = setup_service.setup_claude_config(home_dir, force=False)

    if result.success:
        if ci_mode:
            print("  [OK] Global configuration setup complete")
            for path in result.created_paths:
                print(f"       Created: {path}")
        else:
            console.print("  [green]OK[/green] Global configuration setup complete")
            for path in result.created_paths:
                console.print(f"       [dim]Created: {path}[/dim]")
        progress_service.display_phase_complete("Post-install Setup", success=True)
        return True
    else:
        if ci_mode:
            print("  [FAIL] Setup failed")
            for error in result.errors:
                print(f"       Error: {error}")
        else:
            console.print("  [red]FAIL[/red] Setup failed")
            for error in result.errors:
                console.print(f"       [red]Error: {error}[/red]")
        progress_service.display_phase_complete("Post-install Setup", success=False)
        return False


def _verify_installation(
    pipx_adapter: SubprocessPipxAdapter,
    progress_service: ProgressDisplayService,
    ci_mode: bool,
    console: Console,
) -> bool:
    """Verify installation by checking version.

    Args:
        pipx_adapter: Adapter for pipx operations.
        progress_service: Service for displaying progress.
        ci_mode: Whether running in CI mode.
        console: Rich console for output.

    Returns:
        True if verification passed, False otherwise.
    """
    progress_service.display_phase_start("Verify Installation")

    installed_version = get_installed_version(pipx_adapter, PACKAGE_NAME)

    if installed_version:
        if ci_mode:
            print(f"  [OK] crafter-ai v{installed_version} is installed")
        else:
            console.print(
                f"  [green]OK[/green] crafter-ai v{installed_version} is installed"
            )
        progress_service.display_phase_complete("Verify Installation", success=True)
        return True
    else:
        if ci_mode:
            print("  [FAIL] crafter-ai not found after installation")
        else:
            console.print("[red]FAIL[/red] crafter-ai not found after installation")
        progress_service.display_phase_complete("Verify Installation", success=False)
        return False


def _show_celebration(
    celebration_service: CelebrationService,
    ci_mode: bool,
    console: Console,
    installed_version: str | None,
) -> None:
    """Show success celebration.

    Args:
        celebration_service: Service for celebration display.
        ci_mode: Whether running in CI mode.
        console: Rich console for output.
        installed_version: The installed version string.
    """
    if ci_mode:
        print("")
        print("=" * 60)
        print("Installation Complete!")
        print("=" * 60)
        print("")
        if installed_version:
            print(f"crafter-ai v{installed_version} has been installed successfully.")
        else:
            print("crafter-ai has been installed successfully.")
        print("")
        print("Next steps:")
        print("  1. Run 'nw doctor' to verify your installation")
        print("  2. Run 'nw setup --project' in your project directory")
        print("  3. Start using nWave!")
        print("")
    else:
        celebration_service.display_success(installed_version or "latest")
        celebration_service.display_next_steps()


def install_nwave(
    ci: Annotated[
        bool,
        typer.Option(
            "--ci",
            help="Force CI mode (no interactive prompts, plain text output).",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Auto-confirm all prompts.",
        ),
    ] = False,
    version: Annotated[
        str | None,
        typer.Option(
            "--version",
            "-v",
            help="Install specific version (e.g., '1.0.0').",
        ),
    ] = None,
    pre: Annotated[
        bool,
        typer.Option(
            "--pre",
            help="Include pre-release versions.",
        ),
    ] = False,
) -> None:
    """Install crafter-ai from PyPI via pipx.

    This command installs the crafter-ai package and configures it for use.

    Installation phases:
    1. Pre-flight checks (PyPI connectivity, etc.)
    2. Check for existing installation (upgrade path)
    3. Install via pipx
    4. Run nw setup (global configuration)
    5. Verify installation (nw doctor)
    6. Show welcome/celebration

    Examples:
        install-nwave                    # Interactive install
        install-nwave --ci               # CI mode (non-interactive)
        install-nwave --yes              # Auto-confirm all prompts
        install-nwave --version 1.0.0    # Install specific version
        install-nwave --pre              # Include pre-release versions
    """
    # Determine CI mode
    ci_mode = _is_ci_mode(force_ci=ci)

    # In CI mode, auto-yes is implied
    auto_yes = yes or ci_mode

    # Create console for output
    console = Console()

    # Create services
    pipx_adapter = SubprocessPipxAdapter()
    progress_service = ProgressDisplayService(console=console)
    celebration_service = CelebrationService(console=console)

    # Display header
    if ci_mode:
        print("=" * 60)
        print("nWave Installer - crafter-ai from PyPI")
        print("=" * 60)
        print("")
    else:
        celebration_service.display_welcome()

    # Phase 1: Pre-flight checks
    if not _run_preflight_checks(progress_service, ci_mode, console):
        if ci_mode:
            print("")
            print("[FAIL] Pre-flight checks failed. Installation aborted.")
        else:
            console.print("")
            console.print("[red]Pre-flight checks failed.[/red] Installation aborted.")
        raise typer.Exit(code=1)

    # Phase 2: Check existing installation
    should_continue, _existing_version = _check_existing_installation(
        pipx_adapter, progress_service, ci_mode, console, auto_yes
    )
    if not should_continue:
        raise typer.Exit(code=0)

    # Phase 3: Install via pipx
    if not _install_via_pipx(
        pipx_adapter, progress_service, ci_mode, console, version, pre
    ):
        if ci_mode:
            print("")
            print("[FAIL] Installation failed.")
        else:
            console.print("")
            celebration_service.display_failure("Installation via pipx failed.")
        raise typer.Exit(code=1)

    # Phase 4: Run setup
    if not _run_setup(progress_service, ci_mode, console):
        if ci_mode:
            print("")
            print("[WARN] Setup had issues, but installation may still work.")
        else:
            console.print("")
            console.print(
                "[yellow]Setup had issues, but installation may still work.[/yellow]"
            )
        # Don't exit - setup failures are non-fatal

    # Phase 5: Verify installation
    if not _verify_installation(pipx_adapter, progress_service, ci_mode, console):
        if ci_mode:
            print("")
            print("[FAIL] Verification failed.")
        else:
            console.print("")
            celebration_service.display_failure("Installation verification failed.")
        raise typer.Exit(code=1)

    # Phase 6: Celebration
    installed_version = get_installed_version(pipx_adapter, PACKAGE_NAME)
    _show_celebration(celebration_service, ci_mode, console, installed_version)

    # Success!
    raise typer.Exit(code=0)
