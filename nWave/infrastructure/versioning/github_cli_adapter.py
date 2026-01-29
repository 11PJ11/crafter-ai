"""
GitHubCLIAdapter - Infrastructure adapter for GitHub CLI operations.

Implements GitHubCLIPort interface for actual gh CLI command execution.

HEXAGONAL ARCHITECTURE:
- This is an INFRASTRUCTURE ADAPTER (outside the hexagon)
- Implements GitHubCLIPort abstract interface
- Uses subprocess to execute gh CLI commands
"""

from __future__ import annotations

import re
import subprocess
from typing import Optional

from nWave.core.versioning.ports.github_cli_port import (
    GitHubCLIError,
    GitHubCLIPort,
    PRResult,
)


class GitHubCLIAdapter(GitHubCLIPort):
    """
    Infrastructure adapter for GitHub CLI operations.

    Implements GitHubCLIPort interface by executing gh commands via subprocess.

    Example:
        >>> adapter = GitHubCLIAdapter()
        >>> result = adapter.create_pr("main", "development", "Release PR")
        >>> if result.success:
        ...     print(f"PR #{result.pr_number}: {result.pr_url}")
    """

    def create_pr(self, base_branch: str, head_branch: str, title: str) -> PRResult:
        """
        Create a pull request from head branch to base branch.

        Uses: gh pr create --base {base} --head {head} --title "{title}"

        Args:
            base_branch: The target branch (e.g., "main")
            head_branch: The source branch (e.g., "development")
            title: The PR title

        Returns:
            PRResult: Contains success status, PR number, URL, or error message

        Raises:
            GitHubCLIError: If gh CLI is not installed
        """
        try:
            result = subprocess.run(
                [
                    "gh",
                    "pr",
                    "create",
                    "--base",
                    base_branch,
                    "--head",
                    head_branch,
                    "--title",
                    title,
                    "--body",
                    f"Release pull request from {head_branch} to {base_branch}.",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode != 0:
                error_msg = result.stderr.strip()
                if "permission" in error_msg.lower() or "403" in error_msg:
                    return PRResult(
                        success=False,
                        pr_number=None,
                        pr_url=None,
                        error_message="Permission denied. You don't have access to create releases for this repository.",
                    )
                return PRResult(
                    success=False,
                    pr_number=None,
                    pr_url=None,
                    error_message=error_msg or "Unknown error creating PR",
                )

            # Extract PR URL from stdout
            pr_url = result.stdout.strip()

            # Extract PR number from URL (e.g., "https://github.com/owner/repo/pull/123")
            pr_number = self._extract_pr_number(pr_url)

            return PRResult(
                success=True,
                pr_number=pr_number,
                pr_url=pr_url,
            )

        except FileNotFoundError:
            raise GitHubCLIError("gh CLI is not installed or not in PATH")

    def _extract_pr_number(self, pr_url: str) -> Optional[int]:
        """
        Extract PR number from GitHub PR URL.

        Args:
            pr_url: Full GitHub PR URL (e.g., "https://github.com/owner/repo/pull/123")

        Returns:
            PR number as integer, or None if extraction fails
        """
        match = re.search(r"/pull/(\d+)", pr_url)
        if match:
            return int(match.group(1))
        return None
