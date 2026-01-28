"""
Unit tests for forge_cli driving adapter.

Tests for Step 05-01: Install prompt display
Tests for Step 05-07: User accepts install after successful build

forge_cli is the driving adapter for /nw:forge command.
It invokes BuildService and formats output with install prompt.

HEXAGONAL ARCHITECTURE:
- forge_cli is a DRIVING ADAPTER (outside the hexagon)
- Invokes BuildService application service
- Formats output for user display
"""

import pytest
from typing import Optional


class MockInstallFileSystem:
    """In-memory mock for install file system operations."""

    def __init__(self):
        self._installation_completed = False
        self._installed_version: Optional[str] = None

    def copy_dist_to_claude(self) -> None:
        self._installation_completed = True

    def file_exists_in_claude(self, relative_path: str) -> bool:
        return self._installation_completed

    def get_installed_file(self, relative_path: str) -> Optional[str]:
        if relative_path == "VERSION" and self._installed_version:
            return self._installed_version
        return None

    def set_installed_version(self, version: str) -> None:
        self._installed_version = version

    def list_dist_files(self) -> list[str]:
        return []

    @property
    def installation_completed(self) -> bool:
        return self._installation_completed


class TestForgeCLIPromptsForInstall:
    """Test that forge_cli displays install prompt after successful build."""

    def test_forge_cli_prompts_for_install(self):
        """
        GIVEN a successful build result
        WHEN format_build_output() is called
        THEN the prompt displays "Install: [Y/n]"
        """
        # Arrange
        from nWave.cli.forge_cli import format_build_output
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        # Act
        output, prompt = format_build_output(build_result)

        # Assert
        assert "Install: [Y/n]" in prompt


# =============================================================================
# Step 05-06: User declines install after successful build
# =============================================================================


class TestForgeCLIAcceptsNResponse:
    """Test that forge_cli accepts 'n' response and skips install."""

    def test_forge_cli_accepts_n_response(self):
        """
        GIVEN a successful build result
        AND user responds "n" to install prompt
        WHEN handle_install_response() is called
        THEN the response is recognized as decline
        AND installation is NOT performed
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="n",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.install_invoked is False, (
            "Expected 'n' response to NOT invoke installation"
        )
        assert result.installation_performed is False, (
            "Expected no installation when user declines"
        )

    def test_forge_cli_accepts_uppercase_n_response(self):
        """
        GIVEN a successful build result
        AND user responds "N" (uppercase) to install prompt
        WHEN handle_install_response() is called
        THEN the response is recognized as decline
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="N",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.install_invoked is False, (
            "Expected 'N' (uppercase) response to NOT invoke installation"
        )

    def test_forge_cli_accepts_no_word_response(self):
        """
        GIVEN a successful build result
        AND user responds "no" to install prompt
        WHEN handle_install_response() is called
        THEN the response is recognized as decline
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="no",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.install_invoked is False, (
            "Expected 'no' response to NOT invoke installation"
        )


class TestNoInstallOnDecline:
    """Test that no installation occurs when user declines."""

    def test_no_install_on_decline(self):
        """
        GIVEN a successful build result
        WHEN user responds 'n' to install prompt
        THEN the file system copy operation is NOT called
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="n",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert mock_file_system.installation_completed is False, (
            "Expected NO file copy operation when user declines"
        )

    def test_exit_code_zero_on_decline(self):
        """
        GIVEN a successful build result
        WHEN user responds 'n' to install prompt
        THEN the exit code is 0 (success - decline is valid choice)
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="n",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.exit_code == 0, (
            f"Expected exit code 0 for successful decline, got {result.exit_code}"
        )


class TestDistPreservedOnDecline:
    """Test that dist/ directory is preserved when user declines."""

    def test_dist_preserved_on_decline(self):
        """
        GIVEN a successful build with dist/ containing the distribution
        WHEN user declines installation
        THEN dist/ directory remains unchanged (no cleanup)
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="n",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert: This is a negative test - we ensure nothing was modified
        # The build result still indicates the distribution was created
        assert build_result.distribution_created is True, (
            "Expected distribution to remain in dist/ after decline"
        )
        assert result.dist_cleaned is False, (
            "Expected dist/ to NOT be cleaned on decline"
        )


# =============================================================================
# Step 05-07: User accepts install after successful build
# =============================================================================


class TestForgeCLIAcceptsYResponse:
    """Test that forge_cli accepts 'Y' response and triggers install."""

    def test_forge_cli_accepts_y_response(self):
        """
        GIVEN a successful build result
        AND user responds "Y" to install prompt
        WHEN handle_install_response() is called
        THEN the response is recognized as acceptance
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="Y",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.install_invoked is True, (
            "Expected 'Y' response to invoke installation"
        )

    def test_forge_cli_accepts_lowercase_y_response(self):
        """
        GIVEN a successful build result
        AND user responds "y" to install prompt (lowercase)
        WHEN handle_install_response() is called
        THEN the response is recognized as acceptance
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="y",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.install_invoked is True, (
            "Expected 'y' (lowercase) response to invoke installation"
        )

    def test_forge_cli_accepts_empty_response_as_yes(self):
        """
        GIVEN a successful build result
        AND user responds with empty string (press Enter - default)
        WHEN handle_install_response() is called
        THEN the response is recognized as acceptance (default is Y)
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.install_invoked is True, (
            "Expected empty response (default Y) to invoke installation"
        )


class TestForgeCLIInvokesInstallCommand:
    """Test that forge_cli invokes install command when user accepts."""

    def test_forge_cli_invokes_install_command(self):
        """
        GIVEN a successful build result
        AND user responds "Y" to install prompt
        WHEN handle_install_response() is called
        THEN the install service is invoked
        AND the file system copy operation is called
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()

        # Act
        result = handle_install_response(
            user_response="Y",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert mock_file_system.installation_completed is True, (
            "Expected install service to copy files to ~/.claude/"
        )


class TestDistributionInstalledOnAccept:
    """Test that distribution is properly installed when user accepts."""

    def test_distribution_installed_on_accept(self):
        """
        GIVEN a successful build result with version "1.2.3-rc.main.20260127.1"
        AND user responds "Y" to install prompt
        WHEN handle_install_response() is called
        THEN the installation is completed
        AND the result indicates success
        """
        # Arrange
        from nWave.cli.forge_cli import handle_install_response
        from nWave.core.versioning.application.build_service import BuildResult

        build_result = BuildResult(
            success=True,
            version="1.2.3-rc.main.20260127.1",
            dist_cleaned=True,
            tests_passed=True,
            distribution_created=True,
            error_message=None,
        )

        mock_file_system = MockInstallFileSystem()
        mock_file_system.set_installed_version("1.2.3-rc.main.20260127.1")

        # Act
        result = handle_install_response(
            user_response="Y",
            build_result=build_result,
            install_file_system=mock_file_system,
        )

        # Assert
        assert result.install_invoked is True, (
            "Expected installation to be invoked"
        )
        assert result.success is True, (
            "Expected installation to succeed"
        )
        assert mock_file_system.installation_completed is True, (
            "Expected file system to show installation completed"
        )
