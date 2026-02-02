"""Tests for core pre-flight checks.

All tests use mocking to avoid depending on actual system state.
"""

import sys
from collections import namedtuple
from unittest.mock import MagicMock, patch

from crafter_ai.installer.checks.core_checks import (
    check_git_available,
    check_internet_connectivity,
    check_pipx_available,
    check_python_version,
    create_core_check_registry,
)
from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


EXPECTED_CORE_CHECK_COUNT = 4


class TestCheckPythonVersion:
    """Tests for check_python_version."""

    def test_passes_on_current_python(self) -> None:
        """Test that check passes on current Python (which is >= 3.10)."""
        result = check_python_version()

        assert isinstance(result, CheckResult)
        assert result.id == "python-version"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_on_old_python(self) -> None:
        """Test that check fails when Python version is too old."""
        MockVersionInfo = namedtuple(
            "version_info", ["major", "minor", "micro", "releaselevel", "serial"]
        )
        mock_version = MockVersionInfo(3, 9, 0, "final", 0)

        with patch.object(sys, "version_info", mock_version):
            result = check_python_version()

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None
        assert "3.10" in result.remediation


class TestCheckGitAvailable:
    """Tests for check_git_available."""

    def test_passes_when_git_exists(self) -> None:
        """Test that check passes when git is available."""
        with patch(
            "crafter_ai.installer.checks.core_checks.shutil.which",
            return_value="/usr/bin/git",
        ):
            result = check_git_available()

        assert isinstance(result, CheckResult)
        assert result.id == "git-available"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_git_missing(self) -> None:
        """Test that check fails when git is not available."""
        with patch(
            "crafter_ai.installer.checks.core_checks.shutil.which", return_value=None
        ):
            result = check_git_available()

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None


class TestCheckPipxAvailable:
    """Tests for check_pipx_available."""

    def test_has_warning_severity_and_is_fixable(self) -> None:
        """Test that pipx check has WARNING severity and is fixable."""
        with patch(
            "crafter_ai.installer.checks.core_checks.shutil.which", return_value=None
        ):
            result = check_pipx_available()

        assert result.id == "pipx-available"
        assert result.severity == CheckSeverity.WARNING
        assert result.fixable is True
        assert result.fix_command == "pip install pipx"

    def test_passes_when_pipx_exists(self) -> None:
        """Test that check passes when pipx is available."""
        with patch(
            "crafter_ai.installer.checks.core_checks.shutil.which",
            return_value="/usr/local/bin/pipx",
        ):
            result = check_pipx_available()

        assert result.passed is True
        assert result.severity == CheckSeverity.WARNING


class TestCheckInternetConnectivity:
    """Tests for check_internet_connectivity."""

    def test_has_warning_severity(self) -> None:
        """Test that internet check has WARNING severity."""
        with patch(
            "crafter_ai.installer.checks.core_checks.socket.create_connection",
            side_effect=OSError("No connection"),
        ):
            result = check_internet_connectivity()

        assert result.id == "internet-connectivity"
        assert result.severity == CheckSeverity.WARNING

    def test_passes_when_connected(self) -> None:
        """Test that check passes when internet is available."""
        mock_socket = MagicMock()
        with patch(
            "crafter_ai.installer.checks.core_checks.socket.create_connection",
            return_value=mock_socket,
        ):
            result = check_internet_connectivity()

        assert result.passed is True
        mock_socket.close.assert_called_once()

    def test_fails_when_no_connection(self) -> None:
        """Test that check fails when internet is not available."""
        with patch(
            "crafter_ai.installer.checks.core_checks.socket.create_connection",
            side_effect=OSError("Connection refused"),
        ):
            result = check_internet_connectivity()

        assert result.passed is False
        assert result.remediation is not None


class TestCreateCoreCheckRegistry:
    """Tests for create_core_check_registry factory."""

    def test_returns_registry_with_all_four_checks(self) -> None:
        """Test that factory returns a registry with all 4 core checks."""
        registry = create_core_check_registry()

        assert isinstance(registry, CheckRegistry)
        assert registry.count == EXPECTED_CORE_CHECK_COUNT
        assert registry.has("python-version")
        assert registry.has("git-available")
        assert registry.has("pipx-available")
        assert registry.has("internet-connectivity")

    def test_all_registered_checks_are_callable(self) -> None:
        """Test that all registered checks can be called and return CheckResult."""
        registry = create_core_check_registry()

        for check_id, check_fn in registry.get_all():
            result = check_fn()
            assert isinstance(result, CheckResult)
            assert result.id == check_id
