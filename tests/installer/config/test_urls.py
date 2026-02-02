"""Tests for URL configuration management.

Tests URLConfig frozen dataclass, factory functions, and URL helpers.
"""

import dataclasses

import pytest

from crafter_ai.installer.config.urls import (
    URLConfig,
    get_default_urls,
    get_pypi_version_url,
    get_release_notes_url,
    get_test_urls,
)


class TestURLConfigDataclass:
    """Tests for URLConfig dataclass structure."""

    def test_url_config_is_frozen_dataclass(self) -> None:
        """URLConfig must be a frozen dataclass (immutable)."""
        config = get_default_urls()
        assert dataclasses.is_dataclass(config)
        with pytest.raises(dataclasses.FrozenInstanceError):
            config.pypi_url = "https://malicious.com"

    def test_url_config_has_all_required_properties(self) -> None:
        """URLConfig must have all required URL properties."""
        config = get_default_urls()
        required_attrs = [
            "pypi_url",
            "pypi_api_url",
            "testpypi_url",
            "testpypi_api_url",
            "github_repo_url",
            "docs_url",
            "issues_url",
        ]
        for attr in required_attrs:
            assert hasattr(config, attr), f"Missing attribute: {attr}"


class TestGetDefaultUrls:
    """Tests for get_default_urls factory function."""

    def test_get_default_urls_returns_url_config(self) -> None:
        """get_default_urls must return URLConfig instance."""
        config = get_default_urls()
        assert isinstance(config, URLConfig)

    def test_pypi_url_is_correct(self) -> None:
        """pypi_url must point to PyPI project page."""
        config = get_default_urls()
        assert config.pypi_url == "https://pypi.org/project/crafter-ai/"

    def test_pypi_api_url_is_correct(self) -> None:
        """pypi_api_url must point to PyPI JSON API."""
        config = get_default_urls()
        assert config.pypi_api_url == "https://pypi.org/pypi/crafter-ai/json"

    def test_github_repo_url_is_correct(self) -> None:
        """github_repo_url must point to GitHub repository."""
        config = get_default_urls()
        assert "github.com" in config.github_repo_url
        assert "crafter-ai" in config.github_repo_url

    def test_docs_url_is_correct(self) -> None:
        """docs_url must be a valid documentation URL."""
        config = get_default_urls()
        assert config.docs_url.startswith("https://")

    def test_issues_url_is_correct(self) -> None:
        """issues_url must point to GitHub issues."""
        config = get_default_urls()
        assert "github.com" in config.issues_url
        assert "issues" in config.issues_url


class TestGetTestUrls:
    """Tests for get_test_urls factory function."""

    def test_get_test_urls_returns_url_config(self) -> None:
        """get_test_urls must return URLConfig instance."""
        config = get_test_urls()
        assert isinstance(config, URLConfig)

    def test_testpypi_url_is_correct(self) -> None:
        """testpypi_url must point to TestPyPI."""
        config = get_test_urls()
        assert config.testpypi_url == "https://test.pypi.org/project/crafter-ai/"

    def test_testpypi_api_url_is_correct(self) -> None:
        """testpypi_api_url must point to TestPyPI JSON API."""
        config = get_test_urls()
        assert config.testpypi_api_url == "https://test.pypi.org/pypi/crafter-ai/json"

    def test_pypi_url_points_to_testpypi(self) -> None:
        """In test config, pypi_url should point to TestPyPI."""
        config = get_test_urls()
        assert "test.pypi.org" in config.pypi_url


class TestUrlHelpers:
    """Tests for URL helper functions."""

    def test_get_pypi_version_url_formats_correctly(self) -> None:
        """get_pypi_version_url must format version URL correctly."""
        url = get_pypi_version_url("1.0.0")
        assert url == "https://pypi.org/project/crafter-ai/1.0.0/"

    def test_get_pypi_version_url_handles_prerelease(self) -> None:
        """get_pypi_version_url must handle prerelease versions."""
        url = get_pypi_version_url("0.1.0.dev1")
        assert "0.1.0.dev1" in url

    def test_get_release_notes_url_formats_correctly(self) -> None:
        """get_release_notes_url must format release notes URL correctly."""
        url = get_release_notes_url("1.0.0")
        assert "1.0.0" in url
        assert "github.com" in url


class TestAllUrlsHttps:
    """Tests that all URLs use HTTPS."""

    def test_default_urls_all_https(self) -> None:
        """All default URLs must start with https://."""
        config = get_default_urls()
        for field in dataclasses.fields(config):
            url = getattr(config, field.name)
            assert url.startswith("https://"), f"{field.name} does not use HTTPS: {url}"

    def test_test_urls_all_https(self) -> None:
        """All test URLs must start with https://."""
        config = get_test_urls()
        for field in dataclasses.fields(config):
            url = getattr(config, field.name)
            assert url.startswith("https://"), f"{field.name} does not use HTTPS: {url}"

    def test_version_url_uses_https(self) -> None:
        """Version URL must use HTTPS."""
        url = get_pypi_version_url("1.0.0")
        assert url.startswith("https://")

    def test_release_notes_url_uses_https(self) -> None:
        """Release notes URL must use HTTPS."""
        url = get_release_notes_url("1.0.0")
        assert url.startswith("https://")
