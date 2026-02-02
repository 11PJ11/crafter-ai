"""
Unit tests for GitHubAPIAdapter (driven adapter).

GitHubAPIAdapter implements GitHubAPIPort to fetch release info from GitHub API.
"""

import json
import urllib.error
from unittest.mock import MagicMock, Mock, patch

import pytest
from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.ports.github_api_port import (
    NetworkError,
    RateLimitError,
    ReleaseInfo,
)


class TestGitHubAdapterFetchesLatestRelease:
    """Test that GitHubAPIAdapter fetches latest release info."""

    def test_github_adapter_fetches_latest_release(self):
        """Adapter should parse GitHub API response into ReleaseInfo."""
        from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter

        # GIVEN: A mock HTTP response from GitHub API
        mock_response_data = {
            "tag_name": "v1.3.0",
            "assets": [
                {
                    "name": "nwave-1.3.0.zip",
                    "browser_download_url": "https://github.com/test/releases/download/v1.3.0/nwave-1.3.0.zip",
                }
            ],
            "body": "Release notes\n\nSHA256: " + "a" * 64,
        }

        mock_response = MagicMock()
        mock_response.read.return_value = json.dumps(mock_response_data).encode("utf-8")
        mock_response.getcode.return_value = 200
        mock_response.headers = {}
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)

        with patch("urllib.request.urlopen", return_value=mock_response):
            adapter = GitHubAPIAdapter()

            # WHEN: get_latest_release is called
            result = adapter.get_latest_release("test-owner", "test-repo")

            # THEN: Result is ReleaseInfo with correct version
            assert isinstance(result, ReleaseInfo)
            assert result.version == Version("1.3.0")

    def test_github_adapter_handles_network_error(self):
        """Adapter should raise NetworkError on connection failure."""
        from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_urlopen.side_effect = urllib.error.URLError("Connection failed")

            adapter = GitHubAPIAdapter()

            # WHEN/THEN: get_latest_release raises NetworkError
            with pytest.raises(NetworkError):
                adapter.get_latest_release("test-owner", "test-repo")

    def test_github_adapter_handles_rate_limit(self):
        """Adapter should raise RateLimitError on HTTP 403."""
        from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_error = urllib.error.HTTPError(
                url="https://api.github.com/repos/test/test/releases/latest",
                code=403,
                msg="Forbidden",
                hdrs={"X-RateLimit-Reset": "1706500000"},
                fp=None,
            )
            mock_urlopen.side_effect = mock_error

            adapter = GitHubAPIAdapter()

            # WHEN/THEN: get_latest_release raises RateLimitError
            with pytest.raises(RateLimitError):
                adapter.get_latest_release("test-owner", "test-repo")


# ============================================================================
# Step 03-07: Handle GitHub API rate limit gracefully - Adapter tests
# ============================================================================


class TestGitHubAdapterRaisesRateLimitError:
    """
    Step 03-07: Test that GitHubAPIAdapter correctly raises RateLimitError on HTTP 403.

    This validates the adapter-level behavior that enables graceful degradation
    in the VersionService layer.
    """

    def test_github_adapter_raises_rate_limit_error_on_403(self):
        """
        Adapter should raise RateLimitError with message when GitHub returns HTTP 403.
        """
        from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_error = urllib.error.HTTPError(
                url="https://api.github.com/repos/anthropics/claude-code/releases/latest",
                code=403,
                msg="Forbidden",
                hdrs={},  # No rate limit headers
                fp=None,
            )
            mock_urlopen.side_effect = mock_error

            adapter = GitHubAPIAdapter()

            # WHEN/THEN: RateLimitError is raised with descriptive message
            with pytest.raises(RateLimitError) as exc_info:
                adapter.get_latest_release("anthropics", "claude-code")

            assert "rate limit" in str(exc_info.value).lower()

    def test_github_adapter_parses_rate_limit_reset_header(self):
        """
        Adapter should parse X-RateLimit-Reset header to determine retry_after.
        """
        import time

        from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter

        # Future timestamp (1 hour from now)
        future_timestamp = int(time.time()) + 3600

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_error = urllib.error.HTTPError(
                url="https://api.github.com/repos/test/test/releases/latest",
                code=403,
                msg="Forbidden",
                hdrs={"X-RateLimit-Reset": str(future_timestamp)},
                fp=None,
            )
            mock_urlopen.side_effect = mock_error

            adapter = GitHubAPIAdapter()

            # WHEN: RateLimitError is raised
            with pytest.raises(RateLimitError) as exc_info:
                adapter.get_latest_release("test-owner", "test-repo")

            # THEN: retry_after is approximately 1 hour (within tolerance)
            error = exc_info.value
            assert error.retry_after is not None
            # Allow 5 second tolerance for test execution time
            assert 3590 <= error.retry_after <= 3605

    def test_github_adapter_rate_limit_without_reset_header(self):
        """
        Adapter should handle rate limit without X-RateLimit-Reset header.
        """
        from nWave.infrastructure.versioning.github_api_adapter import GitHubAPIAdapter

        with patch("urllib.request.urlopen") as mock_urlopen:
            mock_error = urllib.error.HTTPError(
                url="https://api.github.com/repos/test/test/releases/latest",
                code=403,
                msg="Forbidden",
                hdrs={},  # No rate limit headers
                fp=None,
            )
            mock_urlopen.side_effect = mock_error

            adapter = GitHubAPIAdapter()

            # WHEN: RateLimitError is raised
            with pytest.raises(RateLimitError) as exc_info:
                adapter.get_latest_release("test-owner", "test-repo")

            # THEN: retry_after is None (unknown reset time)
            error = exc_info.value
            assert error.retry_after is None
