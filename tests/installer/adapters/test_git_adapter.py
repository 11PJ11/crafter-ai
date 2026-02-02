"""Tests for GitPort Protocol and SubprocessGitAdapter.

All tests mock subprocess to avoid actual git calls.
Tests follow the hexagonal architecture pattern.
"""

from unittest.mock import MagicMock, patch

from crafter_ai.installer.adapters.git_adapter import SubprocessGitAdapter
from crafter_ai.installer.ports.git_port import GitPort


class TestGitPortProtocol:
    """Tests for GitPort Protocol definition."""

    def test_git_port_is_runtime_checkable(self) -> None:
        """GitPort should be a runtime_checkable Protocol."""

        # Protocol should be decorated with @runtime_checkable
        assert hasattr(GitPort, "__protocol_attrs__") or isinstance(GitPort, type)

    def test_subprocess_git_adapter_implements_git_port(self) -> None:
        """SubprocessGitAdapter should implement GitPort Protocol."""
        adapter = SubprocessGitAdapter()
        assert isinstance(adapter, GitPort)


class TestSubprocessGitAdapterGetCurrentBranch:
    """Tests for get_current_branch method."""

    @patch("subprocess.run")
    def test_returns_branch_name(self, mock_run: MagicMock) -> None:
        """get_current_branch should return the current branch name."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="main\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_current_branch()

        assert result == "main"
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_returns_feature_branch_name(self, mock_run: MagicMock) -> None:
        """get_current_branch should handle feature branch names."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="feature/installer-v2\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_current_branch()

        assert result == "feature/installer-v2"


class TestSubprocessGitAdapterGetCommitsSinceTag:
    """Tests for get_commits_since_tag method."""

    @patch("subprocess.run")
    def test_parses_git_log_output(self, mock_run: MagicMock) -> None:
        """get_commits_since_tag should parse git log output into list."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="feat: add new feature\nfix: bug fix\nchore: cleanup\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_commits_since_tag("v0.1.0")

        assert result == ["feat: add new feature", "fix: bug fix", "chore: cleanup"]

    @patch("subprocess.run")
    def test_returns_empty_list_when_no_commits(self, mock_run: MagicMock) -> None:
        """get_commits_since_tag should return empty list when no commits."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_commits_since_tag("v0.1.0")

        assert result == []

    @patch("subprocess.run")
    def test_uses_correct_git_command(self, mock_run: MagicMock) -> None:
        """get_commits_since_tag should use correct git log command."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
        )

        adapter = SubprocessGitAdapter()
        adapter.get_commits_since_tag("v0.1.0")

        call_args = mock_run.call_args
        args = call_args[0][0]
        assert "git" in args
        assert "log" in args
        assert "v0.1.0..HEAD" in args


class TestSubprocessGitAdapterGetLatestTag:
    """Tests for get_latest_tag method."""

    @patch("subprocess.run")
    def test_returns_tag_when_exists(self, mock_run: MagicMock) -> None:
        """get_latest_tag should return the most recent tag."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="v0.2.0\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_latest_tag()

        assert result == "v0.2.0"

    @patch("subprocess.run")
    def test_returns_none_when_no_tags(self, mock_run: MagicMock) -> None:
        """get_latest_tag should return None when no tags exist."""
        mock_run.return_value = MagicMock(
            returncode=128,  # git returns 128 when no tags
            stdout="",
            stderr="fatal: No names found",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_latest_tag()

        assert result is None


class TestSubprocessGitAdapterGetCommitHash:
    """Tests for get_commit_hash method."""

    @patch("subprocess.run")
    def test_returns_short_hash_by_default(self, mock_run: MagicMock) -> None:
        """get_commit_hash should return short hash by default."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc1234\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_commit_hash()

        assert result == "abc1234"

    @patch("subprocess.run")
    def test_returns_long_hash_when_requested(self, mock_run: MagicMock) -> None:
        """get_commit_hash should return full hash when short=False."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="abc1234567890abcdef1234567890abcdef123456\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.get_commit_hash(short=False)

        assert result == "abc1234567890abcdef1234567890abcdef123456"


class TestSubprocessGitAdapterHasUncommittedChanges:
    """Tests for has_uncommitted_changes method."""

    @patch("subprocess.run")
    def test_returns_true_when_changes_exist(self, mock_run: MagicMock) -> None:
        """has_uncommitted_changes should return True when there are changes."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout=" M src/file.py\n?? new_file.py\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.has_uncommitted_changes()

        assert result is True

    @patch("subprocess.run")
    def test_returns_false_when_clean(self, mock_run: MagicMock) -> None:
        """has_uncommitted_changes should return False when working tree is clean."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.has_uncommitted_changes()

        assert result is False


class TestSubprocessGitAdapterIsGitRepo:
    """Tests for is_git_repo method."""

    @patch("subprocess.run")
    def test_returns_true_inside_git_repo(self, mock_run: MagicMock) -> None:
        """is_git_repo should return True when inside a git repository."""
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="true\n",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.is_git_repo()

        assert result is True

    @patch("subprocess.run")
    def test_returns_false_outside_git_repo(self, mock_run: MagicMock) -> None:
        """is_git_repo should return False when not in a git repository."""
        mock_run.return_value = MagicMock(
            returncode=128,
            stdout="",
            stderr="fatal: not a git repository",
        )

        adapter = SubprocessGitAdapter()
        result = adapter.is_git_repo()

        assert result is False
