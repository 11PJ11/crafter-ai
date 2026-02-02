"""Tests for build-specific pre-flight checks.

All tests use mocking to avoid depending on actual system state.
No actual git calls or file system checks are made.
"""

import subprocess
from unittest.mock import MagicMock, patch

from crafter_ai.installer.checks.build_checks import (
    check_build_package_installed,
    check_clean_git_status,
    check_pyproject_exists,
    check_src_directory_exists,
    check_version_not_released,
    create_build_check_registry,
)
from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


EXPECTED_BUILD_CHECK_COUNT = 5


class TestCheckPyprojectExists:
    """Tests for check_pyproject_exists."""

    def test_passes_when_pyproject_exists(self) -> None:
        """Test that check passes when pyproject.toml exists."""
        with patch(
            "crafter_ai.installer.checks.build_checks.Path.exists",
            return_value=True,
        ):
            result = check_pyproject_exists()

        assert isinstance(result, CheckResult)
        assert result.id == "pyproject-exists"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_pyproject_missing(self) -> None:
        """Test that check fails when pyproject.toml is missing."""
        with patch(
            "crafter_ai.installer.checks.build_checks.Path.exists",
            return_value=False,
        ):
            result = check_pyproject_exists()

        assert result.id == "pyproject-exists"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None
        assert "pyproject.toml" in result.remediation


class TestCheckBuildPackageInstalled:
    """Tests for check_build_package_installed."""

    def test_is_fixable_with_correct_fix_command(self) -> None:
        """Test that build package check is fixable with correct fix_command."""
        with patch(
            "crafter_ai.installer.checks.build_checks.shutil.which",
            return_value=None,
        ):
            result = check_build_package_installed()

        assert result.id == "build-package"
        assert result.fixable is True
        assert result.fix_command == "pip install build"

    def test_passes_when_build_available(self) -> None:
        """Test that check passes when build package is available."""
        with patch(
            "crafter_ai.installer.checks.build_checks.shutil.which",
            return_value="/usr/local/bin/pyproject-build",
        ):
            result = check_build_package_installed()

        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_build_missing(self) -> None:
        """Test that check fails when build package is not available."""
        with patch(
            "crafter_ai.installer.checks.build_checks.shutil.which",
            return_value=None,
        ):
            result = check_build_package_installed()

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None


class TestCheckSrcDirectoryExists:
    """Tests for check_src_directory_exists."""

    def test_passes_when_src_exists(self) -> None:
        """Test that check passes when src/ directory exists."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True

        with patch(
            "crafter_ai.installer.checks.build_checks.Path",
            return_value=mock_path,
        ):
            result = check_src_directory_exists()

        assert isinstance(result, CheckResult)
        assert result.id == "src-directory"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_src_missing(self) -> None:
        """Test that check fails when src/ directory is missing."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False

        with patch(
            "crafter_ai.installer.checks.build_checks.Path",
            return_value=mock_path,
        ):
            result = check_src_directory_exists()

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None


class TestCheckCleanGitStatus:
    """Tests for check_clean_git_status."""

    def test_has_warning_severity(self) -> None:
        """Test that git status check has WARNING severity."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""

        with patch(
            "crafter_ai.installer.checks.build_checks.subprocess.run",
            return_value=mock_result,
        ):
            result = check_clean_git_status()

        assert result.id == "clean-git-status"
        assert result.severity == CheckSeverity.WARNING

    def test_passes_when_git_clean(self) -> None:
        """Test that check passes when git status is clean."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = ""

        with patch(
            "crafter_ai.installer.checks.build_checks.subprocess.run",
            return_value=mock_result,
        ):
            result = check_clean_git_status()

        assert result.passed is True
        assert "clean" in result.message.lower()

    def test_fails_when_uncommitted_changes(self) -> None:
        """Test that check fails when there are uncommitted changes."""
        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = " M src/main.py\n"

        with patch(
            "crafter_ai.installer.checks.build_checks.subprocess.run",
            return_value=mock_result,
        ):
            result = check_clean_git_status()

        assert result.passed is False
        assert result.remediation is not None

    def test_handles_git_not_repo(self) -> None:
        """Test that check handles when not in a git repository."""
        with patch(
            "crafter_ai.installer.checks.build_checks.subprocess.run",
            side_effect=subprocess.CalledProcessError(128, "git"),
        ):
            result = check_clean_git_status()

        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING


class TestCheckVersionNotReleased:
    """Tests for check_version_not_released."""

    def test_has_warning_severity(self) -> None:
        """Test that version check has WARNING severity."""
        with patch(
            "crafter_ai.installer.checks.build_checks.subprocess.run",
        ) as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1  # Not found on PyPI
            mock_run.return_value = mock_result

            result = check_version_not_released()

        assert result.id == "version-not-released"
        assert result.severity == CheckSeverity.WARNING

    def test_passes_when_version_not_on_pypi(self) -> None:
        """Test that check passes when version is not already on PyPI."""
        with patch(
            "crafter_ai.installer.checks.build_checks.subprocess.run",
        ) as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 1  # pip index returns 1 when version not found
            mock_run.return_value = mock_result

            result = check_version_not_released()

        assert result.passed is True

    def test_fails_when_version_already_released(self) -> None:
        """Test that check fails when version is already on PyPI."""
        with patch(
            "crafter_ai.installer.checks.build_checks.subprocess.run",
        ) as mock_run:
            mock_result = MagicMock()
            mock_result.returncode = 0  # Found on PyPI
            mock_run.return_value = mock_result

            result = check_version_not_released()

        assert result.passed is False
        assert result.remediation is not None


class TestCreateBuildCheckRegistry:
    """Tests for create_build_check_registry factory."""

    def test_returns_registry_with_all_five_checks(self) -> None:
        """Test that factory returns a registry with all 5 build checks."""
        registry = create_build_check_registry()

        assert isinstance(registry, CheckRegistry)
        assert registry.count == EXPECTED_BUILD_CHECK_COUNT
        assert registry.has("pyproject-exists")
        assert registry.has("build-package")
        assert registry.has("src-directory")
        assert registry.has("clean-git-status")
        assert registry.has("version-not-released")

    def test_all_registered_checks_are_callable(self) -> None:
        """Test that all registered checks can be called and return CheckResult."""
        registry = create_build_check_registry()

        # We need to mock all the external dependencies for all checks
        with (
            patch("crafter_ai.installer.checks.build_checks.Path") as mock_path_class,
            patch(
                "crafter_ai.installer.checks.build_checks.shutil.which",
                return_value="/usr/bin/build",
            ),
            patch(
                "crafter_ai.installer.checks.build_checks.subprocess.run"
            ) as mock_run,
        ):
            # Setup Path mocks
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_dir.return_value = True
            mock_path_class.return_value = mock_path_instance

            # Setup subprocess mock
            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = ""
            mock_run.return_value = mock_result

            for check_id, check_fn in registry.get_all():
                result = check_fn()
                assert isinstance(result, CheckResult)
                assert result.id == check_id
