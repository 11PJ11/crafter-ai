"""Tests for doctor health checks.

Tests use mocking to avoid system dependencies.
"""

from unittest.mock import MagicMock, patch

from crafter_ai.installer.checks.health_checks import (
    check_agent_files,
    check_config_directory,
    check_package_installation,
    check_python_environment,
    check_update_available,
    create_doctor_health_checker,
)
from crafter_ai.installer.domain.health_checker import HealthChecker
from crafter_ai.installer.domain.health_result import HealthStatus


EXPECTED_DOCTOR_CHECK_COUNT = 5


class TestCheckPythonEnvironment:
    """Tests for check_python_environment."""

    def test_returns_healthy_with_correct_python_version(self) -> None:
        """Should return HEALTHY when Python version meets requirements."""
        with patch(
            "crafter_ai.installer.checks.health_checks.sys.version_info",
            MagicMock(major=3, minor=12),
        ):
            result = check_python_environment()

        assert result.status == HealthStatus.HEALTHY
        assert result.component == "python-environment"
        assert "3.12" in result.message

    def test_includes_version_in_details(self) -> None:
        """Should include Python version in details dict."""
        with patch(
            "crafter_ai.installer.checks.health_checks.sys.version_info",
            MagicMock(major=3, minor=11, micro=5),
        ):
            result = check_python_environment()

        assert result.details is not None
        assert "version" in result.details
        assert "3.11" in result.details["version"]

    def test_includes_venv_status_in_details(self) -> None:
        """Should include virtual environment status in details."""
        with (
            patch(
                "crafter_ai.installer.checks.health_checks.sys.version_info",
                MagicMock(major=3, minor=12),
            ),
            patch(
                "crafter_ai.installer.checks.health_checks.sys.prefix",
                "/home/user/venv",
            ),
            patch(
                "crafter_ai.installer.checks.health_checks.sys.base_prefix",
                "/usr",
            ),
        ):
            result = check_python_environment()

        assert result.details is not None
        assert "venv_active" in result.details
        assert result.details["venv_active"] == "true"


class TestCheckPackageInstallation:
    """Tests for check_package_installation."""

    def test_returns_healthy_when_installed(self) -> None:
        """Should return HEALTHY when crafter-ai is installed."""
        mock_version = MagicMock(return_value="0.1.0")
        with patch(
            "crafter_ai.installer.checks.health_checks.importlib_metadata.version",
            mock_version,
        ):
            result = check_package_installation()

        assert result.status == HealthStatus.HEALTHY
        assert result.component == "package-installation"
        assert "0.1.0" in result.message or result.details.get("version") == "0.1.0"

    def test_returns_unhealthy_when_not_installed(self) -> None:
        """Should return UNHEALTHY when crafter-ai is not installed."""
        with patch(
            "crafter_ai.installer.checks.health_checks.importlib_metadata.version",
            side_effect=Exception("Package not found"),
        ):
            result = check_package_installation()

        assert result.status == HealthStatus.UNHEALTHY
        assert result.component == "package-installation"


class TestCheckConfigDirectory:
    """Tests for check_config_directory."""

    def test_returns_healthy_when_exists(self) -> None:
        """Should return HEALTHY when config directory exists."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.__str__ = MagicMock(return_value="/home/user/.crafter-ai")

        with (
            patch(
                "crafter_ai.installer.checks.health_checks.Path",
                return_value=mock_path,
            ),
            patch(
                "crafter_ai.installer.checks.health_checks.platformdirs.user_config_dir",
                return_value="/home/user/.crafter-ai",
            ),
        ):
            result = check_config_directory()

        assert result.status == HealthStatus.HEALTHY
        assert result.component == "config-directory"

    def test_returns_unhealthy_when_missing(self) -> None:
        """Should return UNHEALTHY when config directory does not exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False
        mock_path.__str__ = MagicMock(return_value="/home/user/.crafter-ai")

        with (
            patch(
                "crafter_ai.installer.checks.health_checks.Path",
                return_value=mock_path,
            ),
            patch(
                "crafter_ai.installer.checks.health_checks.platformdirs.user_config_dir",
                return_value="/home/user/.crafter-ai",
            ),
        ):
            result = check_config_directory()

        assert result.status == HealthStatus.UNHEALTHY
        assert result.component == "config-directory"


class TestCheckAgentFiles:
    """Tests for check_agent_files."""

    def test_returns_healthy_when_all_files_exist(self) -> None:
        """Should return HEALTHY when all agent files exist."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.glob.return_value = [MagicMock(), MagicMock(), MagicMock()]

        with (
            patch(
                "crafter_ai.installer.checks.health_checks.Path",
                return_value=mock_path,
            ),
            patch(
                "crafter_ai.installer.checks.health_checks.platformdirs.user_config_dir",
                return_value="/home/user/.crafter-ai",
            ),
        ):
            result = check_agent_files()

        assert result.status == HealthStatus.HEALTHY
        assert result.component == "agent-files"

    def test_returns_degraded_when_some_files_missing(self) -> None:
        """Should return DEGRADED when some agent files are missing."""
        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.glob.return_value = []  # No agent files found

        with (
            patch(
                "crafter_ai.installer.checks.health_checks.Path",
                return_value=mock_path,
            ),
            patch(
                "crafter_ai.installer.checks.health_checks.platformdirs.user_config_dir",
                return_value="/home/user/.crafter-ai",
            ),
        ):
            result = check_agent_files()

        assert result.status == HealthStatus.DEGRADED
        assert result.component == "agent-files"

    def test_returns_unhealthy_when_config_dir_missing(self) -> None:
        """Should return UNHEALTHY when config directory is missing."""
        mock_path = MagicMock()
        mock_path.exists.return_value = False

        with (
            patch(
                "crafter_ai.installer.checks.health_checks.Path",
                return_value=mock_path,
            ),
            patch(
                "crafter_ai.installer.checks.health_checks.platformdirs.user_config_dir",
                return_value="/home/user/.crafter-ai",
            ),
        ):
            result = check_agent_files()

        assert result.status == HealthStatus.UNHEALTHY
        assert result.component == "agent-files"


class TestCheckUpdateAvailable:
    """Tests for check_update_available."""

    def test_returns_healthy_when_up_to_date(self) -> None:
        """Should return HEALTHY when package is up to date."""
        with (
            patch(
                "crafter_ai.installer.checks.health_checks.importlib_metadata.version",
                return_value="1.0.0",
            ),
            patch(
                "crafter_ai.installer.checks.health_checks._fetch_pypi_version",
                return_value="1.0.0",
            ),
        ):
            result = check_update_available()

        assert result.status == HealthStatus.HEALTHY
        assert result.component == "update-available"

    def test_returns_degraded_when_update_available(self) -> None:
        """Should return DEGRADED when a newer version is available."""
        with (
            patch(
                "crafter_ai.installer.checks.health_checks.importlib_metadata.version",
                return_value="1.0.0",
            ),
            patch(
                "crafter_ai.installer.checks.health_checks._fetch_pypi_version",
                return_value="2.0.0",
            ),
        ):
            result = check_update_available()

        assert result.status == HealthStatus.DEGRADED
        assert result.component == "update-available"
        assert "2.0.0" in result.message or (
            result.details and "2.0.0" in result.details.get("latest_version", "")
        )

    def test_returns_healthy_when_pypi_unreachable(self) -> None:
        """Should return HEALTHY when PyPI is unreachable (cannot check for updates)."""
        with (
            patch(
                "crafter_ai.installer.checks.health_checks.importlib_metadata.version",
                return_value="1.0.0",
            ),
            patch(
                "crafter_ai.installer.checks.health_checks._fetch_pypi_version",
                return_value=None,
            ),
        ):
            result = check_update_available()

        assert result.status == HealthStatus.HEALTHY
        assert result.component == "update-available"


class TestCreateDoctorHealthChecker:
    """Tests for create_doctor_health_checker factory."""

    def test_returns_health_checker_with_all_checks(self) -> None:
        """Should return HealthChecker with all 5 doctor checks registered."""
        checker = create_doctor_health_checker()

        # Verify it returns a HealthChecker
        assert isinstance(checker, HealthChecker)

        # Verify all 5 checks are registered
        expected_components = [
            "python-environment",
            "package-installation",
            "config-directory",
            "agent-files",
            "update-available",
        ]
        assert len(checker._checks) == EXPECTED_DOCTOR_CHECK_COUNT
        for component in expected_components:
            assert component in checker._checks
