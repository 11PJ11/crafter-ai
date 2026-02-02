"""URL configuration management for the crafter-ai installer.

Provides centralized URL configuration for PyPI, TestPyPI, GitHub, and documentation.
Uses frozen dataclasses to ensure URL immutability at runtime.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class URLConfig:
    """Frozen dataclass containing all installer URLs.

    Attributes:
        pypi_url: PyPI package page URL
        pypi_api_url: PyPI JSON API endpoint
        testpypi_url: TestPyPI package page URL
        testpypi_api_url: TestPyPI JSON API endpoint
        github_repo_url: GitHub repository URL
        docs_url: Documentation URL
        issues_url: GitHub issues URL
    """

    pypi_url: str
    pypi_api_url: str
    testpypi_url: str
    testpypi_api_url: str
    github_repo_url: str
    docs_url: str
    issues_url: str


def get_default_urls() -> URLConfig:
    """Return production URL configuration.

    Returns:
        URLConfig with production PyPI and GitHub URLs.
    """
    return URLConfig(
        pypi_url="https://pypi.org/project/crafter-ai/",
        pypi_api_url="https://pypi.org/pypi/crafter-ai/json",
        testpypi_url="https://test.pypi.org/project/crafter-ai/",
        testpypi_api_url="https://test.pypi.org/pypi/crafter-ai/json",
        github_repo_url="https://github.com/Undeadgrishnackh/crafter-ai",
        docs_url="https://github.com/Undeadgrishnackh/crafter-ai#readme",
        issues_url="https://github.com/Undeadgrishnackh/crafter-ai/issues",
    )


def get_test_urls() -> URLConfig:
    """Return test URL configuration for CI/CD workflows.

    Returns:
        URLConfig with TestPyPI URLs for testing purposes.
    """
    return URLConfig(
        pypi_url="https://test.pypi.org/project/crafter-ai/",
        pypi_api_url="https://test.pypi.org/pypi/crafter-ai/json",
        testpypi_url="https://test.pypi.org/project/crafter-ai/",
        testpypi_api_url="https://test.pypi.org/pypi/crafter-ai/json",
        github_repo_url="https://github.com/Undeadgrishnackh/crafter-ai",
        docs_url="https://github.com/Undeadgrishnackh/crafter-ai#readme",
        issues_url="https://github.com/Undeadgrishnackh/crafter-ai/issues",
    )


def get_pypi_version_url(version: str) -> str:
    """Get URL for a specific version on PyPI.

    Args:
        version: The version string (e.g., "1.0.0" or "0.1.0.dev1")

    Returns:
        URL to the specific version page on PyPI.
    """
    return f"https://pypi.org/project/crafter-ai/{version}/"


def get_release_notes_url(version: str) -> str:
    """Get URL for release notes of a specific version.

    Args:
        version: The version string (e.g., "1.0.0")

    Returns:
        URL to the release notes on GitHub.
    """
    return f"https://github.com/Undeadgrishnackh/crafter-ai/releases/tag/v{version}"
