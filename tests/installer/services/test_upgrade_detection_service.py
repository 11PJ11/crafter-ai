"""Tests for UpgradeDetectionService.

This module tests the upgrade detection functionality that compares
installed version (from pipx) vs latest version (from PyPI).
"""

import json
import urllib.error
from unittest.mock import MagicMock, create_autospec, patch

import pytest

from crafter_ai.installer.ports.pipx_port import InstalledPackage, PipxPort
from crafter_ai.installer.services.upgrade_detection_service import (
    DEFAULT_PACKAGE_NAME,
    PYPI_API_URL,
    UpgradeInfo,
    _get_major_version,
    _parse_version,
    detect_upgrade,
    get_installed_version,
    get_latest_pypi_version,
)


class TestUpgradeInfo:
    """Tests for UpgradeInfo dataclass."""

    def test_upgrade_info_is_frozen(self) -> None:
        """UpgradeInfo should be immutable."""
        info = UpgradeInfo(
            installed_version="1.0.0",
            latest_version="1.1.0",
            is_upgrade_available=True,
            is_major_upgrade=False,
            is_downgrade=False,
        )

        with pytest.raises(AttributeError):
            info.installed_version = "2.0.0"  # type: ignore[misc]

    def test_upgrade_info_stores_all_fields(self) -> None:
        """UpgradeInfo should store all version comparison fields."""
        info = UpgradeInfo(
            installed_version="1.0.0",
            latest_version="2.0.0",
            is_upgrade_available=True,
            is_major_upgrade=True,
            is_downgrade=False,
        )

        assert info.installed_version == "1.0.0"
        assert info.latest_version == "2.0.0"
        assert info.is_upgrade_available is True
        assert info.is_major_upgrade is True
        assert info.is_downgrade is False

    def test_upgrade_info_allows_none_versions(self) -> None:
        """UpgradeInfo should allow None for unavailable versions."""
        info = UpgradeInfo(
            installed_version=None,
            latest_version="1.0.0",
            is_upgrade_available=True,
            is_major_upgrade=False,
            is_downgrade=False,
        )

        assert info.installed_version is None
        assert info.latest_version == "1.0.0"


class TestGetInstalledVersion:
    """Tests for get_installed_version function."""

    def test_returns_version_when_package_installed(self) -> None:
        """get_installed_version returns version when package is installed."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="crafter-ai", version="1.2.3", path="/path/to/pkg"),
            InstalledPackage(name="other-pkg", version="2.0.0", path="/path/to/other"),
        ]

        result = get_installed_version(mock_pipx)

        assert result == "1.2.3"
        mock_pipx.list_packages.assert_called_once()

    def test_returns_none_when_package_not_installed(self) -> None:
        """get_installed_version returns None when package is not installed."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="other-pkg", version="2.0.0", path="/path/to/other"),
        ]

        result = get_installed_version(mock_pipx)

        assert result is None

    def test_returns_none_when_no_packages_installed(self) -> None:
        """get_installed_version returns None when no packages are installed."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = []

        result = get_installed_version(mock_pipx)

        assert result is None

    def test_uses_custom_package_name(self) -> None:
        """get_installed_version can check for custom package names."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="custom-pkg", version="3.0.0", path="/path"),
        ]

        result = get_installed_version(mock_pipx, package_name="custom-pkg")

        assert result == "3.0.0"


class TestGetLatestPypiVersion:
    """Tests for get_latest_pypi_version function."""

    def test_returns_latest_version_from_pypi(self) -> None:
        """get_latest_pypi_version returns latest version from PyPI API."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "2.0.0"},
                "releases": {"1.0.0": [], "2.0.0": []},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = get_latest_pypi_version()

        assert result == "2.0.0"

    def test_returns_none_when_pypi_unreachable(self) -> None:
        """get_latest_pypi_version returns None when PyPI is unreachable."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Network error")

            result = get_latest_pypi_version()

        assert result is None

    def test_returns_none_on_http_error(self) -> None:
        """get_latest_pypi_version returns None on HTTP error."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.HTTPError(
                url="http://pypi.org",
                code=404,
                msg="Not Found",
                hdrs={},
                fp=None,
            )

            result = get_latest_pypi_version()

        assert result is None

    def test_returns_none_on_timeout(self) -> None:
        """get_latest_pypi_version returns None on timeout."""
        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = TimeoutError()

            result = get_latest_pypi_version()

        assert result is None

    def test_returns_none_on_invalid_json(self) -> None:
        """get_latest_pypi_version returns None on invalid JSON response."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = b"invalid json"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = get_latest_pypi_version()

        assert result is None

    def test_uses_custom_package_name(self) -> None:
        """get_latest_pypi_version can query custom package names."""
        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "5.0.0"},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response) as mock_open:
            result = get_latest_pypi_version(package_name="custom-pkg")

        assert result == "5.0.0"
        # Verify the Request object was created with the custom package name
        call_args = mock_open.call_args
        request_obj = call_args[0][0]  # First positional arg is the Request
        assert "custom-pkg" in request_obj.full_url


class TestParseVersion:
    """Tests for _parse_version helper function."""

    def test_parses_valid_version(self) -> None:
        """_parse_version parses valid semver strings."""
        result = _parse_version("1.2.3")

        assert result is not None
        assert result.major == 1
        assert result.minor == 2
        assert result.micro == 3

    def test_returns_none_for_none_input(self) -> None:
        """_parse_version returns None for None input."""
        result = _parse_version(None)

        assert result is None

    def test_returns_none_for_invalid_version(self) -> None:
        """_parse_version returns None for invalid version strings."""
        result = _parse_version("not-a-version")

        assert result is None

    def test_parses_prerelease_version(self) -> None:
        """_parse_version handles prerelease versions."""
        result = _parse_version("1.0.0a1")

        assert result is not None
        assert result.major == 1


class TestGetMajorVersion:
    """Tests for _get_major_version helper function."""

    def test_extracts_major_version(self) -> None:
        """_get_major_version extracts major version number."""
        from packaging.version import Version

        result = _get_major_version(Version("2.1.0"))

        assert result == 2

    def test_returns_none_for_none_input(self) -> None:
        """_get_major_version returns None for None input."""
        result = _get_major_version(None)

        assert result is None


class TestDetectUpgrade:
    """Tests for detect_upgrade function."""

    def test_detects_upgrade_available(self) -> None:
        """detect_upgrade identifies when upgrade is available."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="crafter-ai", version="1.0.0", path="/path"),
        ]

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "1.1.0"},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = detect_upgrade(mock_pipx)

        assert result.installed_version == "1.0.0"
        assert result.latest_version == "1.1.0"
        assert result.is_upgrade_available is True
        assert result.is_major_upgrade is False
        assert result.is_downgrade is False

    def test_detects_major_upgrade(self) -> None:
        """detect_upgrade identifies when major upgrade is available."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="crafter-ai", version="1.5.0", path="/path"),
        ]

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "2.0.0"},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = detect_upgrade(mock_pipx)

        assert result.installed_version == "1.5.0"
        assert result.latest_version == "2.0.0"
        assert result.is_upgrade_available is True
        assert result.is_major_upgrade is True
        assert result.is_downgrade is False

    def test_detects_no_upgrade_when_up_to_date(self) -> None:
        """detect_upgrade identifies when already on latest version."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="crafter-ai", version="2.0.0", path="/path"),
        ]

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "2.0.0"},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = detect_upgrade(mock_pipx)

        assert result.installed_version == "2.0.0"
        assert result.latest_version == "2.0.0"
        assert result.is_upgrade_available is False
        assert result.is_major_upgrade is False
        assert result.is_downgrade is False

    def test_detects_downgrade_for_dev_version(self) -> None:
        """detect_upgrade identifies when installed version is newer (dev version)."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="crafter-ai", version="2.1.0", path="/path"),
        ]

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "2.0.0"},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = detect_upgrade(mock_pipx)

        assert result.installed_version == "2.1.0"
        assert result.latest_version == "2.0.0"
        assert result.is_upgrade_available is False
        assert result.is_major_upgrade is False
        assert result.is_downgrade is True

    def test_handles_not_installed(self) -> None:
        """detect_upgrade handles case when package is not installed."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = []

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "1.0.0"},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = detect_upgrade(mock_pipx)

        assert result.installed_version is None
        assert result.latest_version == "1.0.0"
        assert result.is_upgrade_available is True
        assert result.is_major_upgrade is False
        assert result.is_downgrade is False

    def test_handles_pypi_unreachable(self) -> None:
        """detect_upgrade handles case when PyPI is unreachable."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="crafter-ai", version="1.0.0", path="/path"),
        ]

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Network error")

            result = detect_upgrade(mock_pipx)

        assert result.installed_version == "1.0.0"
        assert result.latest_version is None
        assert result.is_upgrade_available is False
        assert result.is_major_upgrade is False
        assert result.is_downgrade is False

    def test_handles_both_unavailable(self) -> None:
        """detect_upgrade handles case when both versions unavailable."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = []

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Network error")

            result = detect_upgrade(mock_pipx)

        assert result.installed_version is None
        assert result.latest_version is None
        assert result.is_upgrade_available is False
        assert result.is_major_upgrade is False
        assert result.is_downgrade is False

    def test_uses_custom_package_name(self) -> None:
        """detect_upgrade can check custom package names."""
        mock_pipx = create_autospec(PipxPort)
        mock_pipx.list_packages.return_value = [
            InstalledPackage(name="custom-pkg", version="1.0.0", path="/path"),
        ]

        mock_response = MagicMock()
        mock_response.status = 200
        mock_response.read.return_value = json.dumps(
            {
                "info": {"version": "2.0.0"},
            }
        ).encode("utf-8")
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=None)

        with patch("urllib.request.urlopen", return_value=mock_response):
            result = detect_upgrade(mock_pipx, package_name="custom-pkg")

        assert result.installed_version == "1.0.0"
        assert result.latest_version == "2.0.0"
        assert result.is_upgrade_available is True


class TestConstants:
    """Tests for module constants."""

    def test_pypi_api_url_is_correct(self) -> None:
        """PYPI_API_URL should point to PyPI JSON API."""
        assert PYPI_API_URL == "https://pypi.org/pypi"

    def test_default_package_name_is_crafter_ai(self) -> None:
        """DEFAULT_PACKAGE_NAME should be 'crafter-ai'."""
        assert DEFAULT_PACKAGE_NAME == "crafter-ai"
