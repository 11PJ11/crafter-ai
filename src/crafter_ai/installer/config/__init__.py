"""Configuration modules for the crafter-ai installer."""

from crafter_ai.installer.config.urls import (
    URLConfig,
    get_default_urls,
    get_pypi_version_url,
    get_release_notes_url,
    get_test_urls,
)


__all__ = [
    "URLConfig",
    "get_default_urls",
    "get_pypi_version_url",
    "get_release_notes_url",
    "get_test_urls",
]
