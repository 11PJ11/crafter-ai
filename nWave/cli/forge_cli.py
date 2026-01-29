"""
Forge CLI - Driving adapter for build command.

Entry point for /nw:forge command that builds custom distributions
from local modifications.

HEXAGONAL ARCHITECTURE:
- This is a DRIVING ADAPTER (outside the hexagon)
- Invokes BuildService application service
- Formats output and prompts for user interaction

Step 05-07: User accepts install after successful build
- handle_install_response() processes user input to install prompt
- Accepts "Y", "y", or empty string (default) as acceptance
- Invokes InstallService when user accepts
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional, Tuple

if TYPE_CHECKING:
    from nWave.core.versioning.application.build_service import BuildResult
    from nWave.core.versioning.application.install_service import FileSystemProtocol


@dataclass(frozen=True)
class InstallResponseResult:
    """
    Result of handling install response.

    Attributes:
        install_invoked: True if install command was invoked
        success: True if installation succeeded
        message: Human-readable result message
        installed_version: Version that was installed (if successful)
        installation_performed: True if files were actually copied
        exit_code: CLI exit code (0 for success, non-zero for error)
        dist_cleaned: True if dist/ was cleaned after install
    """

    install_invoked: bool
    success: bool
    message: str
    installed_version: Optional[str] = None
    installation_performed: bool = False
    exit_code: int = 0
    dist_cleaned: bool = False


def handle_install_response(
    user_response: str,
    build_result: "BuildResult",
    install_file_system: "FileSystemProtocol",
) -> InstallResponseResult:
    """
    Handle user response to install prompt after successful build.

    Accepts:
    - "Y", "y", "" (empty - default) as acceptance -> invokes install
    - "n", "N", "no", "No", "NO" as decline -> skips install

    Args:
        user_response: User input string
        build_result: Result from BuildService.build()
        install_file_system: File system adapter for installation

    Returns:
        InstallResponseResult with install status
    """
    normalized_response = user_response.strip().lower()

    is_acceptance = normalized_response in ("y", "yes", "")
    is_decline = normalized_response in ("n", "no")

    if is_decline:
        return InstallResponseResult(
            install_invoked=False,
            success=True,
            message="Installation skipped.",
            installed_version=None,
            installation_performed=False,
            exit_code=0,
            dist_cleaned=False,
        )

    if is_acceptance:
        install_file_system.copy_dist_to_claude()
        installed_version = install_file_system.get_installed_file("VERSION")
        if installed_version:
            installed_version = installed_version.strip()

        return InstallResponseResult(
            install_invoked=True,
            success=True,
            message="Installation complete.",
            installed_version=installed_version or build_result.version,
            installation_performed=True,
            exit_code=0,
            dist_cleaned=False,
        )

    return InstallResponseResult(
        install_invoked=False,
        success=False,
        message=f"Invalid response: '{user_response}'. Expected Y or n.",
        installed_version=None,
        installation_performed=False,
        exit_code=1,
        dist_cleaned=False,
    )


def format_build_output(result: "BuildResult") -> Tuple[str, str]:
    """
    Format BuildResult for CLI display.

    Args:
        result: BuildResult from BuildService

    Returns:
        Tuple of (output_message, prompt)
        - output_message: Build status and version info
        - prompt: Install prompt (empty if build failed)
    """
    if not result.success:
        return _format_failure_output(result), ""

    output = _format_success_output(result)
    prompt = "Install: [Y/n]"

    return output, prompt


def _format_failure_output(result: "BuildResult") -> str:
    """Format output for failed build."""
    return f"Build failed: {result.error_message}"


def _format_success_output(result: "BuildResult") -> str:
    """Format output for successful build."""
    output_lines = []

    if result.dist_cleaned:
        output_lines.append("Cleaned dist/ directory")

    if result.tests_passed:
        output_lines.append("All tests passed")

    if result.distribution_created:
        output_lines.append(f"Built distribution: {result.version}")

    return "\n".join(output_lines)


def main() -> int:
    """
    Main entry point for /nw:forge command.

    Returns:
        Exit code: 0 for success, non-zero for error
    """

    from nWave.infrastructure.versioning.git_adapter import GitAdapter

    try:
        # Create adapters
        _git_adapter = GitAdapter()  # noqa: F841 - Reserved for future use

        # TODO: Create real adapters for test_runner and file_system
        # For now, this will fail until adapters are implemented

        raise NotImplementedError("Forge CLI not fully implemented - adapters needed")

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
