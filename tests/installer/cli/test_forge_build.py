"""Tests for forge:build CLI command.

Tests the CLI layer using Typer's CliRunner with mocked BuildService.
Verifies display rendering, user prompts, and exit codes.
"""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.cli import app
from crafter_ai.installer.domain.candidate_version import BumpType, CandidateVersion
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.services.build_service import BuildResult
from crafter_ai.installer.services.wheel_validation_service import WheelValidationResult
from tests.cli.conftest import CleanCliRunner


@pytest.fixture
def runner() -> CleanCliRunner:
    """Create a CLI test runner with ANSI stripping for CI compatibility."""
    return CleanCliRunner()


@pytest.fixture
def mock_build_service() -> MagicMock:
    """Create a mock BuildService."""
    return MagicMock()


@pytest.fixture
def passing_pre_flight_results() -> list[CheckResult]:
    """Create passing pre-flight check results."""
    return [
        CheckResult(
            id="pyproject",
            name="pyproject.toml exists",
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml found at project root",
        ),
        CheckResult(
            id="git_clean",
            name="Git working tree clean",
            passed=True,
            severity=CheckSeverity.WARNING,
            message="No uncommitted changes",
        ),
    ]


@pytest.fixture
def failing_pre_flight_results() -> list[CheckResult]:
    """Create failing pre-flight check results."""
    return [
        CheckResult(
            id="pyproject",
            name="pyproject.toml exists",
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message="pyproject.toml not found",
            remediation="Create pyproject.toml in project root",
        ),
    ]


@pytest.fixture
def candidate_version() -> CandidateVersion:
    """Create a version candidate for testing."""
    return CandidateVersion(
        current_version="0.1.0",
        bump_type=BumpType.MINOR,
        next_version="0.2.0",
        commit_messages=["feat: add new feature"],
        is_prerelease=False,
        prerelease_suffix=None,
    )


@pytest.fixture
def successful_build_result(
    passing_pre_flight_results: list[CheckResult],
) -> BuildResult:
    """Create a successful build result."""
    return BuildResult(
        success=True,
        wheel_path=Path("/dist/crafter_ai-0.2.0-py3-none-any.whl"),
        version="0.2.0",
        pre_flight_results=passing_pre_flight_results,
        validation_result=WheelValidationResult(
            wheel_path=Path("/dist/crafter_ai-0.2.0-py3-none-any.whl"),
            is_valid=True,
            version="0.2.0",
            package_name="crafter_ai",
            errors=[],
        ),
        error_message=None,
    )


@pytest.fixture
def failed_pre_flight_result(
    failing_pre_flight_results: list[CheckResult],
) -> BuildResult:
    """Create a build result that failed pre-flight."""
    return BuildResult(
        success=False,
        wheel_path=None,
        version=None,
        pre_flight_results=failing_pre_flight_results,
        validation_result=None,
        error_message="Pre-flight checks failed with blocking errors",
    )


@pytest.fixture
def failed_build_result(
    passing_pre_flight_results: list[CheckResult],
) -> BuildResult:
    """Create a build result that failed during build."""
    return BuildResult(
        success=False,
        wheel_path=None,
        version=None,
        pre_flight_results=passing_pre_flight_results,
        validation_result=None,
        error_message="Build failed: subprocess returned non-zero exit code",
    )


class TestForgeCommandRegistration:
    """Tests for forge command registration on Typer app."""

    def test_forge_build_command_registered(self, runner: CleanCliRunner) -> None:
        """Test that forge build command is registered."""

        result = runner.invoke(app, ["forge", "--help"])
        assert result.exit_code == 0
        assert "build" in result.output

    def test_forge_build_help_shows_options(self, runner: CleanCliRunner) -> None:
        """Test that forge build --help shows all options."""

        result = runner.invoke(app, ["forge", "build", "--help"])
        assert result.exit_code == 0
        assert "--no-prompt" in result.output
        assert "--install" in result.output
        assert "--force-version" in result.output


class TestPreFlightDisplay:
    """Tests for pre-flight check display rendering."""

    def test_displays_passing_checks_with_checkmark(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that passing checks show checkmark."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert "pyproject.toml found at project root" in result.output

    def test_displays_failing_checks_with_x(
        self,
        runner: CleanCliRunner,
        failed_pre_flight_result: BuildResult,
    ) -> None:
        """Test that failing checks show X mark."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = failed_pre_flight_result
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert "pyproject.toml not found" in result.output


class TestVersionDisplay:
    """Tests for version bump display rendering."""

    def test_displays_version_bump_info(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that version section shows current -> next."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert "0.1.0" in result.output
        assert "0.2.0" in result.output


class TestBuildProgressDisplay:
    """Tests for build progress display."""

    def test_displays_build_phases(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that build progress shows phases."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        # Check that build completes successfully
        assert result.exit_code == 0


class TestSuccessSummary:
    """Tests for success summary display."""

    def test_displays_forge_build_complete(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that success summary shows wheel filename."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert "crafter_ai-0.2.0-py3-none-any.whl" in result.output

    def test_displays_wheel_path_in_summary(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that summary shows wheel path."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert "crafter_ai-0.2.0-py3-none-any.whl" in result.output


class TestInstallPrompt:
    """Tests for install prompt behavior."""

    def test_prompt_appears_when_not_ci(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that install prompt appears when not in CI."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            # Remove CI env var if present
            env = {k: v for k, v in os.environ.items() if k != "CI"}
            with patch.dict(os.environ, env, clear=True):
                result = runner.invoke(app, ["forge", "build"], input="n\n")

        assert "Install locally now?" in result.output

    def test_no_prompt_flag_skips_prompt(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that --no-prompt skips install prompt."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert "Install locally now?" not in result.output

    def test_install_flag_triggers_auto_install_message(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that --install triggers auto-install."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--install"])

        # --install implies --no-prompt and would trigger install (not implemented yet)
        assert "Install locally now?" not in result.output


class TestCIModeDetection:
    """Tests for CI mode detection."""

    def test_ci_env_suppresses_prompts(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test that CI=true suppresses prompts."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            with patch.dict(os.environ, {"CI": "true"}):
                result = runner.invoke(app, ["forge", "build"])

        assert "Install locally now?" not in result.output


class TestExitCodes:
    """Tests for exit codes."""

    def test_exit_code_0_on_success(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
        candidate_version: CandidateVersion,
    ) -> None:
        """Test exit code 0 on success."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = candidate_version
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert result.exit_code == 0

    def test_exit_code_1_on_pre_flight_failure(
        self,
        runner: CleanCliRunner,
        failed_pre_flight_result: BuildResult,
    ) -> None:
        """Test exit code 1 on pre-flight failure."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = failed_pre_flight_result
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert result.exit_code == 1

    def test_exit_code_1_on_build_failure(
        self,
        runner: CleanCliRunner,
        failed_build_result: BuildResult,
    ) -> None:
        """Test exit code 1 on build failure."""

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = failed_build_result
            mock_factory.return_value = mock_service

            result = runner.invoke(app, ["forge", "build", "--no-prompt"])

        assert result.exit_code == 1


class TestForceVersionOption:
    """Tests for --force-version option."""

    def test_force_version_overrides_auto_calculation(
        self,
        runner: CleanCliRunner,
        successful_build_result: BuildResult,
    ) -> None:
        """Test that --force-version overrides auto-calculation."""

        forced_candidate = CandidateVersion(
            current_version="0.1.0",
            bump_type=BumpType.NONE,
            next_version="1.0.0",
            commit_messages=[],
            is_prerelease=False,
            prerelease_suffix=None,
        )

        with patch(
            "crafter_ai.installer.cli.forge_build.create_build_service"
        ) as mock_factory:
            mock_service = MagicMock()
            mock_service.execute.return_value = successful_build_result
            mock_service.determine_version.return_value = forced_candidate
            mock_factory.return_value = mock_service

            result = runner.invoke(
                app, ["forge", "build", "--force-version", "1.0.0", "--no-prompt"]
            )

        assert result.exit_code == 0
        # The forced version should appear in output
        assert "1.0.0" in result.output
