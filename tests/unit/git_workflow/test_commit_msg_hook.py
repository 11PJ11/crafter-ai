"""
Unit tests for commit-msg hook installation and behavior.

These tests verify that:
1. Commit-msg hook installation script exists
2. Hook validates conventional commit format
3. Hook rejects invalid commit messages
"""

import os
import subprocess
from pathlib import Path
import pytest


class TestCommitMsgHook:
    """Test commit-msg hook installation and validation."""

    @pytest.fixture
    def project_root(self):
        """Get project root directory."""
        current_file = Path(__file__)
        return current_file.parent.parent.parent.parent

    @pytest.fixture
    def git_hooks_dir(self, project_root):
        """Get git hooks directory."""
        return project_root / ".git" / "hooks"

    def test_commit_msg_hook_exists(self, git_hooks_dir):
        """Verify commit-msg hook is installed.

        Note: This test validates local developer setup. It is skipped in CI
        environments where hooks are not installed (fresh clone).
        """
        # Skip in CI environments - hooks are local-only and not part of git clone
        if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
            pytest.skip("Skipping hook existence test in CI - hooks are local-only")

        hook_file = git_hooks_dir / "commit-msg"
        assert hook_file.exists(), "commit-msg hook not found in .git/hooks/"

    def test_commit_msg_hook_is_executable(self, git_hooks_dir):
        """Verify commit-msg hook has execute permissions."""
        hook_file = git_hooks_dir / "commit-msg"

        if not hook_file.exists():
            pytest.skip("Hook not installed yet")

        assert os.access(hook_file, os.X_OK), "commit-msg hook is not executable"

    def test_commit_msg_hook_validates_conventional_format(
        self, git_hooks_dir, tmp_path
    ):
        """Verify hook validates conventional commit format."""
        hook_file = git_hooks_dir / "commit-msg"

        if not hook_file.exists():
            pytest.skip("Hook not installed yet")

        # Create temporary commit message file
        msg_file = tmp_path / "commit-msg.txt"
        msg_file.write_text("feat: add user dashboard")

        # Run hook with valid message
        result = subprocess.run(
            [str(hook_file), str(msg_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode == 0, (
            f"Hook rejected valid commit message. "
            f"stderr: {result.stderr}, stdout: {result.stdout}"
        )

    def test_commit_msg_hook_rejects_invalid_format(self, git_hooks_dir, tmp_path):
        """Verify hook rejects non-conventional commit messages."""
        hook_file = git_hooks_dir / "commit-msg"

        if not hook_file.exists():
            pytest.skip("Hook not installed yet")

        # Create temporary commit message file with invalid format
        msg_file = tmp_path / "commit-msg.txt"
        msg_file.write_text("fixed the login bug")

        # Run hook with invalid message
        result = subprocess.run(
            [str(hook_file), str(msg_file)],
            capture_output=True,
            text=True,
        )

        assert result.returncode != 0, "Hook accepted invalid commit message"
        output = result.stdout + result.stderr
        assert (
            "Conventional Commits" in output
        ), "Hook should mention Conventional Commits in error message"

    def test_commit_msg_hook_accepts_scoped_commits(self, git_hooks_dir, tmp_path):
        """Verify hook accepts scoped conventional commits (e.g., fix(auth): message)."""
        hook_file = git_hooks_dir / "commit-msg"

        if not hook_file.exists():
            pytest.skip("Hook not installed yet")

        # Test various scoped commit formats
        scoped_messages = [
            "fix(auth): resolve login timeout issue",
            "feat(ui): add new dashboard",
            "refactor(api): simplify endpoint logic",
            "test(auth): add login tests",
        ]

        for msg in scoped_messages:
            msg_file = tmp_path / f"commit-msg-{scoped_messages.index(msg)}.txt"
            msg_file.write_text(msg)

            result = subprocess.run(
                [str(hook_file), str(msg_file)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0, (
                f"Hook rejected valid scoped commit: '{msg}'. "
                f"stderr: {result.stderr}, stdout: {result.stdout}"
            )

    def test_commit_msg_hook_accepts_breaking_change_commits(
        self, git_hooks_dir, tmp_path
    ):
        """Verify hook accepts breaking change commits with ! syntax."""
        hook_file = git_hooks_dir / "commit-msg"

        if not hook_file.exists():
            pytest.skip("Hook not installed yet")

        # Test various breaking change formats
        breaking_messages = [
            "feat!: redesign API endpoints",
            "fix!: change authentication flow",
            "refactor(api)!: remove deprecated endpoints",
        ]

        for msg in breaking_messages:
            msg_file = (
                tmp_path / f"commit-msg-breaking-{breaking_messages.index(msg)}.txt"
            )
            msg_file.write_text(msg)

            result = subprocess.run(
                [str(hook_file), str(msg_file)],
                capture_output=True,
                text=True,
            )

            assert result.returncode == 0, (
                f"Hook rejected valid breaking change commit: '{msg}'. "
                f"stderr: {result.stderr}, stdout: {result.stdout}"
            )
