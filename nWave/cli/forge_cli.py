"""
Forge CLI - Driving adapter for build command.

Entry point for /nw:forge command that builds custom distributions
from local modifications.

HEXAGONAL ARCHITECTURE:
- This is a DRIVING ADAPTER (outside the hexagon)
- Invokes BuildService application service
- Formats output and prompts for user interaction
"""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING, Tuple

if TYPE_CHECKING:
    from nWave.core.versioning.application.build_service import BuildResult


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
    from datetime import date

    from nWave.core.versioning.application.build_service import BuildService
    from nWave.infrastructure.versioning.git_adapter import GitAdapter

    try:
        # Create adapters
        git_adapter = GitAdapter()

        # TODO: Create real adapters for test_runner and file_system
        # For now, this will fail until adapters are implemented

        raise NotImplementedError(
            "Forge CLI not fully implemented - adapters needed"
        )

    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
