"""Tests for CelebrationService.

Tests verify:
- Welcome banner display with ASCII art and message
- Success celebration display with version and checkmark
- Next steps display with numbered list
- Failure display with error message and help links
- CI mode detection and simple text output
- URLs come from config/urls.py
- Mock Rich console for all display tests
"""

import os
from io import StringIO
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.installer.config.urls import get_default_urls
from crafter_ai.installer.services.celebration_service import CelebrationService


class TestCelebrationServiceCIDetection:
    """Tests for CI mode detection."""

    def test_is_ci_mode_returns_true_when_ci_env_is_true(self) -> None:
        """is_ci_mode() should return True when CI=true."""
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService()
            assert service.is_ci_mode() is True

    def test_is_ci_mode_returns_true_when_ci_env_is_1(self) -> None:
        """is_ci_mode() should return True when CI=1."""
        with patch.dict(os.environ, {"CI": "1"}):
            service = CelebrationService()
            assert service.is_ci_mode() is True

    def test_is_ci_mode_returns_false_when_ci_env_not_set(self) -> None:
        """is_ci_mode() should return False when CI env var is not set."""
        with patch.dict(os.environ, {}, clear=True):
            env_copy = os.environ.copy()
            env_copy.pop("CI", None)
            with patch.dict(os.environ, env_copy, clear=True):
                service = CelebrationService()
                assert service.is_ci_mode() is False

    def test_is_ci_mode_returns_false_when_ci_env_is_false(self) -> None:
        """is_ci_mode() should return False when CI=false."""
        with patch.dict(os.environ, {"CI": "false"}):
            service = CelebrationService()
            assert service.is_ci_mode() is False


class TestCelebrationServiceDisplayWelcome:
    """Tests for display_welcome() method."""

    @pytest.fixture(autouse=True)
    def disable_ci_mode(self):
        """Disable CI mode for Rich console tests.

        GitHub Actions sets CI=true, which causes the service to use
        _print_ci() instead of the Rich console. This fixture ensures
        tests that verify Rich console behavior work in both local
        and CI environments.
        """
        with patch.dict(os.environ, {"CI": "false"}):
            yield

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(self, mock_console: MagicMock) -> CelebrationService:
        """Create service with mock console."""
        return CelebrationService(console=mock_console)

    def test_display_welcome_calls_console_print(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_welcome() should call console.print()."""
        service_with_mock_console.display_welcome()

        mock_console.print.assert_called()

    def test_display_welcome_shows_nwave_banner(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_welcome() should show nWave ASCII art banner."""
        service_with_mock_console.display_welcome()

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        # Banner should contain nWave text
        assert "nWave" in output_combined or "Wave" in output_combined

    def test_display_welcome_shows_welcome_message(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_welcome() should show welcome message."""
        service_with_mock_console.display_welcome()

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "Welcome" in output_combined or "welcome" in output_combined.lower()

    def test_display_welcome_shows_framework_description(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_welcome() should show AI-Powered Development Framework description."""
        service_with_mock_console.display_welcome()

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "AI-Powered" in output_combined or "Framework" in output_combined

    def test_display_welcome_ci_mode_uses_simple_text(self) -> None:
        """display_welcome() should use simple text in CI mode (no ASCII art)."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_welcome()

        output_text = output.getvalue()
        assert "nWave" in output_text
        assert "Welcome" in output_text
        # CI mode should not have complex ASCII art patterns
        # Just verify it contains the key text


class TestCelebrationServiceDisplaySuccess:
    """Tests for display_success() method."""

    @pytest.fixture(autouse=True)
    def disable_ci_mode(self):
        """Disable CI mode for Rich console tests."""
        with patch.dict(os.environ, {"CI": "false"}):
            yield

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(self, mock_console: MagicMock) -> CelebrationService:
        """Create service with mock console."""
        return CelebrationService(console=mock_console)

    def test_display_success_calls_console_print(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_success() should call console.print()."""
        service_with_mock_console.display_success("1.0.0")

        mock_console.print.assert_called()

    def test_display_success_shows_version(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_success() should show the installed version."""
        service_with_mock_console.display_success("1.2.3")

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "1.2.3" in output_combined

    def test_display_success_shows_success_message(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_success() should show 'installed successfully' message."""
        service_with_mock_console.display_success("2.0.0")

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "successfully" in output_combined.lower()

    def test_display_success_shows_green_checkmark(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_success() should show green checkmark or celebration."""
        service_with_mock_console.display_success("1.0.0")

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        # Should have green color or checkmark
        assert "green" in output_combined.lower() or "✓" in output_combined

    def test_display_success_ci_mode_uses_simple_text(self) -> None:
        """display_success() should use simple text in CI mode."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_success("1.0.0")

        output_text = output.getvalue()
        assert "1.0.0" in output_text
        assert "successfully" in output_text.lower()


class TestCelebrationServiceDisplayNextSteps:
    """Tests for display_next_steps() method."""

    @pytest.fixture(autouse=True)
    def disable_ci_mode(self):
        """Disable CI mode for Rich console tests."""
        with patch.dict(os.environ, {"CI": "false"}):
            yield

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(self, mock_console: MagicMock) -> CelebrationService:
        """Create service with mock console."""
        return CelebrationService(console=mock_console)

    def test_display_next_steps_calls_console_print(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_next_steps() should call console.print()."""
        service_with_mock_console.display_next_steps()

        mock_console.print.assert_called()

    def test_display_next_steps_shows_nw_setup(self) -> None:
        """display_next_steps() should show 'nw setup' command."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_next_steps()

        output_text = output.getvalue()
        assert "nw setup" in output_text

    def test_display_next_steps_shows_nw_doctor(self) -> None:
        """display_next_steps() should show 'nw doctor' command."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_next_steps()

        output_text = output.getvalue()
        assert "nw doctor" in output_text

    def test_display_next_steps_shows_docs_url(self) -> None:
        """display_next_steps() should show documentation URL."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_next_steps()

        output_text = output.getvalue()
        urls = get_default_urls()
        # URL should be present
        assert urls.docs_url in output_text

    def test_display_next_steps_shows_nw_help(self) -> None:
        """display_next_steps() should show 'nw --help' command."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_next_steps()

        output_text = output.getvalue()
        assert "nw --help" in output_text

    def test_display_next_steps_shows_numbered_list(self) -> None:
        """display_next_steps() should show numbered list (1, 2, 3, 4)."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_next_steps()

        output_text = output.getvalue()
        # Should have numbers 1-4
        assert "1." in output_text and "2." in output_text

    def test_display_next_steps_ci_mode_uses_simple_text(self) -> None:
        """display_next_steps() should use simple text in CI mode."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_next_steps()

        output_text = output.getvalue()
        assert "nw setup" in output_text
        assert "nw doctor" in output_text


class TestCelebrationServiceDisplayFailure:
    """Tests for display_failure() method."""

    @pytest.fixture(autouse=True)
    def disable_ci_mode(self):
        """Disable CI mode for Rich console tests."""
        with patch.dict(os.environ, {"CI": "false"}):
            yield

    @pytest.fixture
    def mock_console(self) -> MagicMock:
        """Create a mock Rich console."""
        return MagicMock()

    @pytest.fixture
    def service_with_mock_console(self, mock_console: MagicMock) -> CelebrationService:
        """Create service with mock console."""
        return CelebrationService(console=mock_console)

    def test_display_failure_calls_console_print(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_failure() should call console.print()."""
        service_with_mock_console.display_failure("Installation failed")

        mock_console.print.assert_called()

    def test_display_failure_shows_error_message(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_failure() should show the error message."""
        service_with_mock_console.display_failure("Permission denied")

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        assert "Permission denied" in output_combined

    def test_display_failure_shows_red_x(
        self, service_with_mock_console: CelebrationService, mock_console: MagicMock
    ) -> None:
        """display_failure() should show red X indicator."""
        service_with_mock_console.display_failure("Error occurred")

        call_args_list = mock_console.print.call_args_list
        output_texts = [str(call) for call in call_args_list]
        output_combined = " ".join(output_texts)
        # Should have red color or X mark
        assert "red" in output_combined.lower() or "✗" in output_combined

    def test_display_failure_shows_issues_url(self) -> None:
        """display_failure() should show issues URL for support."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_failure("Installation failed")

        output_text = output.getvalue()
        urls = get_default_urls()
        # Issues URL should be present
        assert urls.issues_url in output_text

    def test_display_failure_shows_troubleshooting_tips(self) -> None:
        """display_failure() should show troubleshooting tips."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_failure("Connection error")

        output_text = output.getvalue()
        # Should have troubleshooting info
        assert "Troubleshooting" in output_text

    def test_display_failure_ci_mode_uses_simple_text(self) -> None:
        """display_failure() should use simple text in CI mode."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_failure("Test error")

        output_text = output.getvalue()
        assert "Test error" in output_text
        assert "FAIL" in output_text or "Error" in output_text


class TestCelebrationServiceURLConfiguration:
    """Tests for URL configuration integration."""

    def test_next_steps_uses_docs_url_from_config(self) -> None:
        """display_next_steps() should use docs_url from config/urls.py."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_next_steps()

        output_text = output.getvalue()
        urls = get_default_urls()
        assert urls.docs_url in output_text

    def test_failure_uses_issues_url_from_config(self) -> None:
        """display_failure() should use issues_url from config/urls.py."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_failure("Test error")

        output_text = output.getvalue()
        urls = get_default_urls()
        assert urls.issues_url in output_text


class TestCelebrationServiceIntegration:
    """Integration tests for CelebrationService."""

    @pytest.fixture(autouse=True)
    def disable_ci_mode(self):
        """Disable CI mode for Rich console tests."""
        with patch.dict(os.environ, {"CI": "false"}):
            yield

    def test_full_success_workflow(self) -> None:
        """Test displaying a complete successful installation workflow."""
        mock_console = MagicMock()
        service = CelebrationService(console=mock_console)

        # Display welcome
        service.display_welcome()

        # Display success
        service.display_success("1.0.0")

        # Display next steps
        service.display_next_steps()

        # Verify console.print was called multiple times
        assert mock_console.print.call_count >= 3

    def test_full_failure_workflow(self) -> None:
        """Test displaying a complete failed installation workflow."""
        mock_console = MagicMock()
        service = CelebrationService(console=mock_console)

        # Display welcome
        service.display_welcome()

        # Display failure
        service.display_failure("Network connection timeout")

        # Verify console.print was called
        assert mock_console.print.call_count >= 2

    def test_ci_mode_full_workflow(self) -> None:
        """Test CI mode produces readable output for entire workflow."""
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)

            service.display_welcome()
            service.display_success("2.0.0")
            service.display_next_steps()

        output_text = output.getvalue()
        # Verify all key elements are present
        assert "nWave" in output_text
        assert "2.0.0" in output_text
        assert "nw setup" in output_text

    def test_service_with_custom_urls(self) -> None:
        """Test service can use custom URL configuration."""
        # Use CI mode for content verification (simple text output)
        from crafter_ai.installer.config.urls import URLConfig

        custom_urls = URLConfig(
            pypi_url="https://custom.pypi.org/",
            pypi_api_url="https://custom.pypi.org/api/",
            testpypi_url="https://custom.testpypi.org/",
            testpypi_api_url="https://custom.testpypi.org/api/",
            github_repo_url="https://custom.github.com/repo",
            docs_url="https://custom.docs.com/",
            issues_url="https://custom.github.com/issues",
        )

        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output, urls=custom_urls)
            service.display_next_steps()

        output_text = output.getvalue()
        assert "https://custom.docs.com/" in output_text

    def test_service_default_urls_when_none_provided(self) -> None:
        """Test service uses default URLs when none provided."""
        # Use CI mode for content verification (simple text output)
        output = StringIO()
        with patch.dict(os.environ, {"CI": "true"}):
            service = CelebrationService(file=output)
            service.display_failure("Test")

        output_text = output.getvalue()
        urls = get_default_urls()
        assert urls.issues_url in output_text
