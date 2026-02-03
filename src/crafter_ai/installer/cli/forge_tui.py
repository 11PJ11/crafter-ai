"""Shared TUI display components for forge CLI commands.

This module provides shared display functions used by both forge build
and forge install commands, eliminating duplication across CLI modules.
"""

import os

from rich.console import Console

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


console = Console()


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
