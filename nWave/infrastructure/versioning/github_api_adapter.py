"""
GitHubAPIAdapter - Concrete implementation of GitHubAPIPort.

Implements GitHub API operations for fetching release information.

HEXAGONAL ARCHITECTURE:
- This is a DRIVEN ADAPTER (outside the hexagon)
- Implements GitHubAPIPort interface
- Handles HTTP communication with GitHub API
"""

from __future__ import annotations

import json
import re
import socket
import urllib.error
import urllib.request
from typing import Optional

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.ports.github_api_port import (
    GitHubAPIPort,
    NetworkError,
    RateLimitError,
    ReleaseInfo,
)


class GitHubAPIAdapter(GitHubAPIPort):
    """
    Concrete GitHub API adapter for release information.

    Fetches release data from GitHub's REST API:
    - Latest release version (from tag_name)
    - Release checksum (from release body)
    - Download URL (from release assets)

    Example:
        >>> adapter = GitHubAPIAdapter()
        >>> info = adapter.get_latest_release("anthropics", "claude-code")
        >>> print(f"Latest: {info.version}")
    """

    GITHUB_API_BASE = "https://api.github.com"
    TIMEOUT_SECONDS = 10

    def __init__(self, timeout: int = None) -> None:
        """
        Create a GitHubAPIAdapter.

        Args:
            timeout: Request timeout in seconds (default: 10)
        """
        self._timeout = timeout or self.TIMEOUT_SECONDS

    def get_latest_release(self, owner: str, repo: str) -> ReleaseInfo:
        """
        Fetch the latest release information from GitHub.

        Args:
            owner: Repository owner (e.g., "anthropics")
            repo: Repository name (e.g., "claude-code")

        Returns:
            ReleaseInfo: Version, checksum, and download URL of latest release

        Raises:
            NetworkError: If the network request fails
            RateLimitError: If the GitHub API rate limit is exceeded
            ValueError: If the repository has no releases
        """
        url = f"{self.GITHUB_API_BASE}/repos/{owner}/{repo}/releases/latest"

        request = urllib.request.Request(
            url,
            headers={
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "nWave-VersionChecker/1.0",
            },
        )

        try:
            with urllib.request.urlopen(request, timeout=self._timeout) as response:
                status_code = response.getcode()
                headers = dict(response.headers)
                data = json.loads(response.read().decode("utf-8"))

        except urllib.error.HTTPError as e:
            status_code = e.code
            headers = dict(e.headers) if e.headers else {}

            # Handle rate limiting
            if status_code == 403:
                retry_after = self._parse_retry_after(headers)
                raise RateLimitError(
                    "GitHub API rate limit exceeded",
                    retry_after=retry_after,
                )

            # Handle not found
            if status_code == 404:
                raise ValueError(f"No releases found for {owner}/{repo}")

            # Handle other HTTP errors
            raise NetworkError(f"GitHub API returned status {status_code}")

        except urllib.error.URLError as e:
            raise NetworkError(f"Failed to connect to GitHub API: {e.reason}")

        except socket.timeout:
            raise NetworkError("GitHub API request timed out")

        except Exception as e:
            raise NetworkError(f"GitHub API request failed: {e}")

        # Parse version from tag_name
        tag_name = data.get("tag_name", "")
        version_str = tag_name.lstrip("v")
        version = Version(version_str)

        # Parse checksum from release body
        body = data.get("body", "")
        checksum = self._extract_checksum(body)

        # Get download URL from assets
        assets = data.get("assets", [])
        download_url = self._find_download_url(assets, repo)

        return ReleaseInfo(
            version=version,
            checksum=checksum,
            download_url=download_url,
        )

    def _parse_retry_after(self, headers: dict) -> Optional[int]:
        """Extract retry-after from rate limit headers."""
        reset_timestamp = headers.get("X-RateLimit-Reset")
        if reset_timestamp:
            try:
                import time

                return max(0, int(reset_timestamp) - int(time.time()))
            except ValueError:
                return None
        return None

    def _extract_checksum(self, body: str) -> str:
        """
        Extract SHA256 checksum from release body.

        Looks for patterns like:
        - SHA256: abc123def456
        - sha256sum: abc123def456
        """
        patterns = [
            r"SHA256:\s*([a-fA-F0-9]{64})",
            r"sha256sum:\s*([a-fA-F0-9]{64})",
            r"sha256:\s*([a-fA-F0-9]{64})",
        ]

        for pattern in patterns:
            match = re.search(pattern, body, re.IGNORECASE)
            if match:
                return match.group(1).lower()

        # Return empty string if no checksum found
        return ""

    def _find_download_url(self, assets: list, repo: str) -> str:
        """
        Find the download URL from release assets.

        Looks for .zip or .tar.gz files containing the repo name.
        """
        for asset in assets:
            name = asset.get("name", "")
            url = asset.get("browser_download_url", "")

            # Look for archive files
            if name.endswith(".zip") or name.endswith(".tar.gz"):
                return url

        # Fallback to first asset if no archive found
        if assets:
            return assets[0].get("browser_download_url", "")

        return ""
