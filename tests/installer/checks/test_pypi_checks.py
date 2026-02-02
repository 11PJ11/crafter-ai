"""Tests for PyPI-specific pre-flight checks.

All tests use mocking to avoid depending on actual network connectivity.
No actual HTTP requests, socket connections, or external dependencies.
"""

import json
import ssl
import urllib.error
from unittest.mock import MagicMock, patch

from crafter_ai.installer.checks.pypi_checks import (
    check_package_exists,
    check_pypi_connectivity,
    check_pypi_tls,
    check_version_available,
    create_pypi_check_registry,
)
from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


EXPECTED_PYPI_CHECK_COUNT = 4


class TestCheckPypiConnectivity:
    """Tests for check_pypi_connectivity."""

    def test_passes_when_pypi_is_reachable(self) -> None:
        """Test that check passes when PyPI API is reachable."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            return_value=mock_response,
        ):
            result = check_pypi_connectivity()

        assert isinstance(result, CheckResult)
        assert result.id == "pypi-connectivity"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_network_error(self) -> None:
        """Test that check fails when there is a network error."""
        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            side_effect=urllib.error.URLError("Connection refused"),
        ):
            result = check_pypi_connectivity()

        assert result.id == "pypi-connectivity"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None

    def test_fails_when_timeout(self) -> None:
        """Test that check fails when connection times out."""
        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            side_effect=TimeoutError("Connection timed out"),
        ):
            result = check_pypi_connectivity()

        assert result.id == "pypi-connectivity"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert "timed out" in result.message.lower()

    def test_fails_when_unexpected_status(self) -> None:
        """Test that check fails when PyPI returns unexpected status."""
        mock_response = MagicMock()
        mock_response.status = 503
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            return_value=mock_response,
        ):
            result = check_pypi_connectivity()

        assert result.id == "pypi-connectivity"
        assert result.passed is False
        assert "503" in result.message


class TestCheckPackageExists:
    """Tests for check_package_exists."""

    def test_passes_when_package_found(self) -> None:
        """Test that check passes when package exists on PyPI."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            return_value=mock_response,
        ):
            result = check_package_exists("crafter-ai")

        assert isinstance(result, CheckResult)
        assert result.id == "package-exists"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING
        assert "crafter-ai" in result.message

    def test_fails_when_package_not_found(self) -> None:
        """Test that check fails when package does not exist (404)."""
        http_error = urllib.error.HTTPError(
            url="https://pypi.org/pypi/nonexistent/json",
            code=404,
            msg="Not Found",
            hdrs={},  # type: ignore
            fp=None,
        )

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            side_effect=http_error,
        ):
            result = check_package_exists("nonexistent-package")

        assert result.id == "package-exists"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert "not found" in result.message.lower()
        assert result.remediation is not None

    def test_fails_when_network_error(self) -> None:
        """Test that check fails when there is a network error."""
        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            side_effect=urllib.error.URLError("No route to host"),
        ):
            result = check_package_exists("crafter-ai")

        assert result.id == "package-exists"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_http_error_not_404(self) -> None:
        """Test that check fails with appropriate message for non-404 HTTP errors."""
        http_error = urllib.error.HTTPError(
            url="https://pypi.org/pypi/crafter-ai/json",
            code=500,
            msg="Internal Server Error",
            hdrs={},  # type: ignore
            fp=None,
        )

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            side_effect=http_error,
        ):
            result = check_package_exists("crafter-ai")

        assert result.id == "package-exists"
        assert result.passed is False
        assert "500" in result.message


class TestCheckVersionAvailable:
    """Tests for check_version_available."""

    def test_returns_warning_when_no_version_specified(self) -> None:
        """Test that check returns warning when no version is specified."""
        result = check_version_available(version=None)

        assert isinstance(result, CheckResult)
        assert result.id == "version-available"
        assert result.passed is True
        assert result.severity == CheckSeverity.WARNING
        assert "latest" in result.message.lower()

    def test_passes_when_version_exists(self) -> None:
        """Test that check passes when specified version exists on PyPI."""
        pypi_response = {
            "info": {"name": "crafter-ai", "version": "1.0.0"},
            "releases": {"0.1.0": [], "0.2.0": [], "1.0.0": []},
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(pypi_response).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            return_value=mock_response,
        ):
            result = check_version_available("crafter-ai", version="1.0.0")

        assert result.id == "version-available"
        assert result.passed is True
        assert result.severity == CheckSeverity.WARNING
        assert "1.0.0" in result.message

    def test_fails_when_version_not_found(self) -> None:
        """Test that check fails when specified version does not exist."""
        pypi_response = {
            "info": {"name": "crafter-ai", "version": "1.0.0"},
            "releases": {"0.1.0": [], "0.2.0": [], "1.0.0": []},
        }

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(pypi_response).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            return_value=mock_response,
        ):
            result = check_version_available("crafter-ai", version="9.9.9")

        assert result.id == "version-available"
        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING
        assert "9.9.9" in result.message
        assert "not found" in result.message.lower()
        assert result.remediation is not None
        assert "1.0.0" in result.remediation  # Latest version mentioned

    def test_fails_when_package_not_found(self) -> None:
        """Test that check fails when package does not exist (404)."""
        http_error = urllib.error.HTTPError(
            url="https://pypi.org/pypi/nonexistent/json",
            code=404,
            msg="Not Found",
            hdrs={},  # type: ignore
            fp=None,
        )

        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            side_effect=http_error,
        ):
            result = check_version_available("nonexistent", version="1.0.0")

        assert result.id == "version-available"
        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING

    def test_fails_when_network_error(self) -> None:
        """Test that check fails when there is a network error."""
        with patch(
            "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
            side_effect=urllib.error.URLError("Connection refused"),
        ):
            result = check_version_available("crafter-ai", version="1.0.0")

        assert result.id == "version-available"
        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING


class TestCheckPypiTls:
    """Tests for check_pypi_tls."""

    def test_passes_when_certificate_valid(self) -> None:
        """Test that check passes when TLS certificate is valid."""
        mock_socket = MagicMock()
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = {
            "subject": ((("commonName", "pypi.org"),),),
            "issuer": ((("commonName", "DigiCert"),),),
        }
        mock_ssl_socket.__enter__ = MagicMock(return_value=mock_ssl_socket)
        mock_ssl_socket.__exit__ = MagicMock(return_value=False)

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value = mock_ssl_socket

        mock_socket.__enter__ = MagicMock(return_value=mock_socket)
        mock_socket.__exit__ = MagicMock(return_value=False)

        with (
            patch(
                "crafter_ai.installer.checks.pypi_checks.ssl.create_default_context",
                return_value=mock_context,
            ),
            patch(
                "crafter_ai.installer.checks.pypi_checks.socket.create_connection",
                return_value=mock_socket,
            ),
        ):
            result = check_pypi_tls()

        assert isinstance(result, CheckResult)
        assert result.id == "pypi-tls"
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_certificate_verification_fails(self) -> None:
        """Test that check fails when certificate verification fails."""
        mock_socket = MagicMock()
        mock_socket.__enter__ = MagicMock(return_value=mock_socket)
        mock_socket.__exit__ = MagicMock(return_value=False)

        mock_context = MagicMock()
        mock_context.wrap_socket.side_effect = ssl.SSLCertVerificationError(
            "certificate verify failed"
        )

        with (
            patch(
                "crafter_ai.installer.checks.pypi_checks.ssl.create_default_context",
                return_value=mock_context,
            ),
            patch(
                "crafter_ai.installer.checks.pypi_checks.socket.create_connection",
                return_value=mock_socket,
            ),
        ):
            result = check_pypi_tls()

        assert result.id == "pypi-tls"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert "verification failed" in result.message.lower()
        assert result.remediation is not None

    def test_fails_when_ssl_error(self) -> None:
        """Test that check fails when there is a general SSL error."""
        mock_socket = MagicMock()
        mock_socket.__enter__ = MagicMock(return_value=mock_socket)
        mock_socket.__exit__ = MagicMock(return_value=False)

        mock_context = MagicMock()
        mock_context.wrap_socket.side_effect = ssl.SSLError("SSL handshake failed")

        with (
            patch(
                "crafter_ai.installer.checks.pypi_checks.ssl.create_default_context",
                return_value=mock_context,
            ),
            patch(
                "crafter_ai.installer.checks.pypi_checks.socket.create_connection",
                return_value=mock_socket,
            ),
        ):
            result = check_pypi_tls()

        assert result.id == "pypi-tls"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING

    def test_fails_when_connection_error(self) -> None:
        """Test that check fails when there is a connection error."""
        with patch(
            "crafter_ai.installer.checks.pypi_checks.socket.create_connection",
            side_effect=OSError("Connection refused"),
        ):
            result = check_pypi_tls()

        assert result.id == "pypi-tls"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
        assert result.remediation is not None

    def test_fails_when_no_certificate_returned(self) -> None:
        """Test that check fails when no certificate is returned."""
        mock_socket = MagicMock()
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = None
        mock_ssl_socket.__enter__ = MagicMock(return_value=mock_ssl_socket)
        mock_ssl_socket.__exit__ = MagicMock(return_value=False)

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value = mock_ssl_socket

        mock_socket.__enter__ = MagicMock(return_value=mock_socket)
        mock_socket.__exit__ = MagicMock(return_value=False)

        with (
            patch(
                "crafter_ai.installer.checks.pypi_checks.ssl.create_default_context",
                return_value=mock_context,
            ),
            patch(
                "crafter_ai.installer.checks.pypi_checks.socket.create_connection",
                return_value=mock_socket,
            ),
        ):
            result = check_pypi_tls()

        assert result.id == "pypi-tls"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING


class TestCreatePypiCheckRegistry:
    """Tests for create_pypi_check_registry factory."""

    def test_returns_registry_with_all_four_checks(self) -> None:
        """Test that factory returns a registry with all 4 PyPI checks."""
        registry = create_pypi_check_registry()

        assert isinstance(registry, CheckRegistry)
        assert registry.count == EXPECTED_PYPI_CHECK_COUNT
        assert registry.has("pypi-connectivity")
        assert registry.has("package-exists")
        assert registry.has("version-available")
        assert registry.has("pypi-tls")

    def test_all_checks_registered_for_pypi_install_journey(self) -> None:
        """Test that all checks are accessible from registry for 'pypi-install' journey."""
        registry = create_pypi_check_registry()

        check_ids = [check_id for check_id, _ in registry.get_all()]
        expected_checks = [
            "pypi-connectivity",
            "package-exists",
            "version-available",
            "pypi-tls",
        ]

        for expected_id in expected_checks:
            assert expected_id in check_ids, f"Check '{expected_id}' not registered"

    def test_all_registered_checks_are_callable(self) -> None:
        """Test that all registered checks can be called and return CheckResult."""
        registry = create_pypi_check_registry()

        # Create comprehensive mocks for all checks
        mock_http_response = MagicMock()
        mock_http_response.status = 200
        mock_http_response.read.return_value = json.dumps(
            {
                "info": {"name": "crafter-ai", "version": "1.0.0"},
                "releases": {"1.0.0": []},
            }
        ).encode("utf-8")
        mock_http_response.__enter__ = MagicMock(return_value=mock_http_response)
        mock_http_response.__exit__ = MagicMock(return_value=False)

        mock_socket = MagicMock()
        mock_ssl_socket = MagicMock()
        mock_ssl_socket.getpeercert.return_value = {"subject": "pypi.org"}
        mock_ssl_socket.__enter__ = MagicMock(return_value=mock_ssl_socket)
        mock_ssl_socket.__exit__ = MagicMock(return_value=False)

        mock_context = MagicMock()
        mock_context.wrap_socket.return_value = mock_ssl_socket

        mock_socket.__enter__ = MagicMock(return_value=mock_socket)
        mock_socket.__exit__ = MagicMock(return_value=False)

        with (
            patch(
                "crafter_ai.installer.checks.pypi_checks.urllib.request.urlopen",
                return_value=mock_http_response,
            ),
            patch(
                "crafter_ai.installer.checks.pypi_checks.ssl.create_default_context",
                return_value=mock_context,
            ),
            patch(
                "crafter_ai.installer.checks.pypi_checks.socket.create_connection",
                return_value=mock_socket,
            ),
        ):
            for check_id, check_fn in registry.get_all():
                result = check_fn()
                assert isinstance(result, CheckResult)
                assert result.id == check_id
