"""
Unit tests for GitHubAPIAdapter (driven adapter).

GitHubAPIAdapter implements GitHubAPIPort to fetch release info from GitHub API.
"""

import json
import pytest
from unittest.mock import Mock, patch, MagicMock
import urllib.error

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.ports.github_api_port import ReleaseInfo, NetworkError, RateLimitError


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
