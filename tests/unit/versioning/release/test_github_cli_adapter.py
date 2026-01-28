"""
Unit tests for GitHubCLIAdapter - Infrastructure adapter for GitHub CLI operations.

HEXAGONAL ARCHITECTURE:
- GitHubCLIAdapter implements GitHubCLIPort interface
- Tests validate adapter correctly executes gh CLI commands
- Adapter is INFRASTRUCTURE layer (outside hexagon)

Test coverage:
- test_github_cli_adapter_creates_pr: Adapter invokes gh pr create
"""

from dataclasses import dataclass
from typing import Optional
from unittest.mock import Mock, patch



@dataclass(frozen=True)
class PRResult:
    """Result of PR creation operation."""

    success: bool
    pr_number: Optional[int]
    pr_url: Optional[str]
    error_message: Optional[str] = None


class TestGitHubCLIAdapterCreatesPR:
    """
    Test: GitHubCLIAdapter creates PR via gh CLI.

    Acceptance Criteria:
    - PR is created from development to main via gh CLI
    - Output displays the PR number and URL
    """

    def test_github_cli_adapter_creates_pr_via_gh_command(self):
        """
        GIVEN: Valid branch names and title
        WHEN: create_pr() is called
        THEN: gh pr create command is executed
        """
        # Act - Import adapter (will fail until implemented)
        from nWave.infrastructure.versioning.github_cli_adapter import GitHubCLIAdapter

        adapter = GitHubCLIAdapter()

        # Mock subprocess to avoid actual CLI execution
        with patch("subprocess.run") as mock_run:
            # Configure mock to return successful PR creation
            mock_run.return_value = Mock(
                returncode=0,
                stdout="https://github.com/UndeadGrishnackh/crafter-ai/pull/123\n",
                stderr="",
            )

            adapter.create_pr(
                base_branch="main",
                head_branch="development",
                title="Release: development -> main",
            )

            # Assert - gh CLI was called with correct arguments
            mock_run.assert_called_once()
            call_args = mock_run.call_args
            cmd = call_args[0][0] if call_args[0] else call_args.kwargs.get("args", [])

            assert "gh" in cmd
            assert "pr" in cmd
            assert "create" in cmd
            assert "--base" in cmd or "main" in cmd
            assert "--head" in cmd or "development" in cmd

    def test_github_cli_adapter_returns_pr_number_from_output(self):
        """
        GIVEN: gh CLI returns PR URL
        WHEN: create_pr() completes successfully
        THEN: PR number is extracted from URL
        """
        from nWave.infrastructure.versioning.github_cli_adapter import GitHubCLIAdapter

        adapter = GitHubCLIAdapter()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout="https://github.com/owner/repo/pull/456\n",
                stderr="",
            )

            result = adapter.create_pr(
                base_branch="main",
                head_branch="development",
                title="Release PR",
            )

            # Assert
            assert result.success is True
            assert result.pr_number == 456
            assert "pull/456" in result.pr_url

    def test_github_cli_adapter_handles_permission_error(self):
        """
        GIVEN: User lacks repository permissions
        WHEN: gh CLI returns permission error
        THEN: Error result is returned with appropriate message
        """
        from nWave.infrastructure.versioning.github_cli_adapter import GitHubCLIAdapter

        adapter = GitHubCLIAdapter()

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=1,
                stdout="",
                stderr="HTTP 403: Permission denied",
            )

            result = adapter.create_pr(
                base_branch="main",
                head_branch="development",
                title="Release PR",
            )

            # Assert
            assert result.success is False
            assert result.pr_number is None
            assert "permission" in result.error_message.lower() or "denied" in result.error_message.lower()

    def test_github_cli_adapter_returns_full_pr_url(self):
        """
        GIVEN: gh CLI returns PR URL
        WHEN: create_pr() completes
        THEN: Full PR URL is returned in result
        """
        from nWave.infrastructure.versioning.github_cli_adapter import GitHubCLIAdapter

        adapter = GitHubCLIAdapter()

        expected_url = "https://github.com/UndeadGrishnackh/crafter-ai/pull/789"

        with patch("subprocess.run") as mock_run:
            mock_run.return_value = Mock(
                returncode=0,
                stdout=f"{expected_url}\n",
                stderr="",
            )

            result = adapter.create_pr(
                base_branch="main",
                head_branch="development",
                title="Release PR",
            )

            # Assert
            assert result.success is True
            assert result.pr_url == expected_url
