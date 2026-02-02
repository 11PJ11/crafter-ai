"""Tests for install-specific pre-flight checks.

All tests use mocking to avoid depending on actual system state.
No actual file system operations, subprocess calls, or external dependencies.
"""

from unittest.mock import MagicMock, patch

from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


EXPECTED_INSTALL_CHECK_COUNT = 4


class TestCheckWheelExists:
    """Tests for check_wheel_exists."""

    def test_passes_when_wheel_file_present_in_dist(self) -> None:
        """Test that check passes when .whl file exists in dist/."""
        from crafter_ai.installer.checks.install_checks import check_wheel_exists

        mock_dist_path = MagicMock()
        mock_dist_path.exists.return_value = True
        mock_dist_path.is_dir.return_value = True
        mock_wheel_file = MagicMock()
        mock_wheel_file.name = "crafter_ai-0.1.0-py3-none-any.whl"
        mock_dist_path.glob.return_value = [mock_wheel_file]

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_dist_path,
        ):
            result = check_wheel_exists()

        assert isinstance(result, CheckResult)
        assert result.id == "wheel-exists"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_with_fixable_when_no_wheel(self) -> None:
        """Test that check fails with fixable=True when no wheel file exists."""
        from crafter_ai.installer.checks.install_checks import check_wheel_exists

        mock_dist_path = MagicMock()
        mock_dist_path.exists.return_value = True
        mock_dist_path.is_dir.return_value = True
        mock_dist_path.glob.return_value = []

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_dist_path,
        ):
            result = check_wheel_exists()

        assert result.id == "wheel-exists"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.fixable is True
        assert result.fix_command is not None
        assert (
            "forge:build" in result.fix_command or "build" in result.fix_command.lower()
        )

    def test_fails_when_dist_directory_missing(self) -> None:
        """Test that check fails when dist/ directory does not exist."""
        from crafter_ai.installer.checks.install_checks import check_wheel_exists

        mock_dist_path = MagicMock()
        mock_dist_path.exists.return_value = False

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_dist_path,
        ):
            result = check_wheel_exists()

        assert result.id == "wheel-exists"
        assert result.passed is False
        assert result.fixable is True
        assert result.remediation is not None


class TestCheckWheelFormat:
    """Tests for check_wheel_format."""

    def test_passes_for_valid_pep427_wheel_name(self) -> None:
        """Test that check passes for valid PEP 427 wheel filename."""
        from crafter_ai.installer.checks.install_checks import check_wheel_format

        mock_dist_path = MagicMock()
        mock_dist_path.exists.return_value = True
        mock_dist_path.is_dir.return_value = True
        mock_wheel_file = MagicMock()
        mock_wheel_file.name = "crafter_ai-0.1.0-py3-none-any.whl"
        mock_dist_path.glob.return_value = [mock_wheel_file]

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_dist_path,
        ):
            result = check_wheel_format()

        assert isinstance(result, CheckResult)
        assert result.id == "wheel-format"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_for_invalid_wheel_name_format(self) -> None:
        """Test that check fails for invalid wheel filename format."""
        from crafter_ai.installer.checks.install_checks import check_wheel_format

        mock_dist_path = MagicMock()
        mock_dist_path.exists.return_value = True
        mock_dist_path.is_dir.return_value = True
        mock_wheel_file = MagicMock()
        mock_wheel_file.name = "invalid-wheel-name.whl"
        mock_dist_path.glob.return_value = [mock_wheel_file]

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_dist_path,
        ):
            result = check_wheel_format()

        assert result.id == "wheel-format"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None
        assert "PEP 427" in result.remediation or "wheel" in result.remediation.lower()

    def test_fails_when_no_wheel_file_found(self) -> None:
        """Test that check fails when no wheel file is found to validate."""
        from crafter_ai.installer.checks.install_checks import check_wheel_format

        mock_dist_path = MagicMock()
        mock_dist_path.exists.return_value = True
        mock_dist_path.is_dir.return_value = True
        mock_dist_path.glob.return_value = []

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_dist_path,
        ):
            result = check_wheel_format()

        assert result.id == "wheel-format"
        assert result.passed is False

    def test_validates_wheel_with_build_number(self) -> None:
        """Test that check passes for wheel with optional build number."""
        from crafter_ai.installer.checks.install_checks import check_wheel_format

        mock_dist_path = MagicMock()
        mock_dist_path.exists.return_value = True
        mock_dist_path.is_dir.return_value = True
        mock_wheel_file = MagicMock()
        mock_wheel_file.name = "crafter_ai-0.1.0-1-py3-none-any.whl"
        mock_dist_path.glob.return_value = [mock_wheel_file]

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_dist_path,
        ):
            result = check_wheel_format()

        assert result.id == "wheel-format"
        assert result.passed is True


class TestCheckPipxIsolation:
    """Tests for check_pipx_isolation."""

    def test_passes_when_pipx_can_create_venv(self) -> None:
        """Test that check passes when pipx can create isolated venv."""
        from crafter_ai.installer.checks.install_checks import check_pipx_isolation

        mock_result = MagicMock()
        mock_result.returncode = 0
        mock_result.stdout = "/home/user/.local/pipx/venvs"

        with patch(
            "crafter_ai.installer.checks.install_checks.subprocess.run",
            return_value=mock_result,
        ):
            result = check_pipx_isolation()

        assert isinstance(result, CheckResult)
        assert result.id == "pipx-isolation"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_pipx_unavailable(self) -> None:
        """Test that check fails when pipx is not available."""
        from crafter_ai.installer.checks.install_checks import check_pipx_isolation

        with patch(
            "crafter_ai.installer.checks.install_checks.subprocess.run",
            side_effect=FileNotFoundError("pipx not found"),
        ):
            result = check_pipx_isolation()

        assert result.id == "pipx-isolation"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None

    def test_fails_when_pipx_environment_broken(self) -> None:
        """Test that check fails when pipx environment is broken."""
        from crafter_ai.installer.checks.install_checks import check_pipx_isolation

        mock_result = MagicMock()
        mock_result.returncode = 1
        mock_result.stderr = "pipx environment is not set up correctly"

        with patch(
            "crafter_ai.installer.checks.install_checks.subprocess.run",
            return_value=mock_result,
        ):
            result = check_pipx_isolation()

        assert result.id == "pipx-isolation"
        assert result.passed is False
        assert result.remediation is not None


class TestCheckInstallPathResolved:
    """Tests for check_install_path_resolved."""

    def test_passes_when_path_writable(self) -> None:
        """Test that check passes when target path is writable."""
        from crafter_ai.installer.checks.install_checks import (
            check_install_path_resolved,
        )

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True

        with (
            patch(
                "crafter_ai.installer.checks.install_checks.Path",
                return_value=mock_path,
            ),
            patch(
                "crafter_ai.installer.checks.install_checks.os.access",
                return_value=True,
            ),
        ):
            result = check_install_path_resolved()

        assert isinstance(result, CheckResult)
        assert result.id == "install-path-resolved"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_path_not_accessible(self) -> None:
        """Test that check fails when target path is not accessible."""
        from crafter_ai.installer.checks.install_checks import (
            check_install_path_resolved,
        )

        mock_path = MagicMock()
        mock_path.exists.return_value = True
        mock_path.is_dir.return_value = True

        with (
            patch(
                "crafter_ai.installer.checks.install_checks.Path",
                return_value=mock_path,
            ),
            patch(
                "crafter_ai.installer.checks.install_checks.os.access",
                return_value=False,
            ),
        ):
            result = check_install_path_resolved()

        assert result.id == "install-path-resolved"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None

    def test_fails_when_path_does_not_exist(self) -> None:
        """Test that check fails when target path does not exist."""
        from crafter_ai.installer.checks.install_checks import (
            check_install_path_resolved,
        )

        mock_path = MagicMock()
        mock_path.exists.return_value = False

        with patch(
            "crafter_ai.installer.checks.install_checks.Path",
            return_value=mock_path,
        ):
            result = check_install_path_resolved()

        assert result.id == "install-path-resolved"
        assert result.passed is False
        assert result.remediation is not None


class TestCreateInstallCheckRegistry:
    """Tests for create_install_check_registry factory."""

    def test_returns_registry_with_all_four_checks(self) -> None:
        """Test that factory returns a registry with all 4 install checks."""
        from crafter_ai.installer.checks.install_checks import (
            create_install_check_registry,
        )

        registry = create_install_check_registry()

        assert isinstance(registry, CheckRegistry)
        assert registry.count == EXPECTED_INSTALL_CHECK_COUNT
        assert registry.has("wheel-exists")
        assert registry.has("wheel-format")
        assert registry.has("pipx-isolation")
        assert registry.has("install-path-resolved")

    def test_all_checks_registered_for_install_local_journey(self) -> None:
        """Test that all checks are accessible from registry for 'install-local' journey."""
        from crafter_ai.installer.checks.install_checks import (
            create_install_check_registry,
        )

        registry = create_install_check_registry()

        check_ids = [check_id for check_id, _ in registry.get_all()]
        expected_checks = [
            "wheel-exists",
            "wheel-format",
            "pipx-isolation",
            "install-path-resolved",
        ]

        for expected_id in expected_checks:
            assert expected_id in check_ids, f"Check '{expected_id}' not registered"

    def test_all_registered_checks_are_callable(self) -> None:
        """Test that all registered checks can be called and return CheckResult."""
        from crafter_ai.installer.checks.install_checks import (
            create_install_check_registry,
        )

        registry = create_install_check_registry()

        with (
            patch("crafter_ai.installer.checks.install_checks.Path") as mock_path_class,
            patch(
                "crafter_ai.installer.checks.install_checks.subprocess.run"
            ) as mock_run,
            patch(
                "crafter_ai.installer.checks.install_checks.os.access",
                return_value=True,
            ),
        ):
            mock_path_instance = MagicMock()
            mock_path_instance.exists.return_value = True
            mock_path_instance.is_dir.return_value = True
            mock_wheel_file = MagicMock()
            mock_wheel_file.name = "crafter_ai-0.1.0-py3-none-any.whl"
            mock_path_instance.glob.return_value = [mock_wheel_file]
            mock_path_class.return_value = mock_path_instance

            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "/home/user/.local/pipx/venvs"
            mock_run.return_value = mock_result

            for check_id, check_fn in registry.get_all():
                result = check_fn()
                assert isinstance(result, CheckResult)
                assert result.id == check_id
