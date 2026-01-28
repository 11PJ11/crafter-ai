"""
GitHubAPIPort - Port interface for GitHub API operations.

This port defines the contract for HTTP calls to the GitHub API.
Adapters implementing this port handle the actual network communication,
rate limiting, and error handling.

Example:
    class GitHubAPIAdapter(GitHubAPIPort):
        def get_latest_release(self, owner: str, repo: str) -> ReleaseInfo:
            # Implementation with httpx/requests
            ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from nWave.core.versioning.domain.version import Version


class NetworkError(Exception):
    """
    Raised when a network operation fails.

    This exception indicates a transient failure that may be retryable,
    such as connection timeouts, DNS failures, or server unreachable errors.

    Example:
        >>> raise NetworkError("Connection timed out")
        NetworkError: Connection timed out
    """

    pass


class RateLimitError(Exception):
    """
    Raised when the GitHub API rate limit is exceeded.

    This exception includes information about when the rate limit will reset,
    allowing callers to implement appropriate retry strategies.

    Attributes:
        retry_after: Number of seconds to wait before retrying (optional)

    Example:
        >>> raise RateLimitError("API rate limit exceeded", retry_after=60)
        RateLimitError: API rate limit exceeded
    """

    def __init__(self, message: str, retry_after: Optional[int] = None) -> None:
        """
        Create a RateLimitError.

        Args:
            message: Error description
            retry_after: Seconds to wait before retrying (from X-RateLimit-Reset header)
        """
        super().__init__(message)
        self.retry_after = retry_after


@dataclass(frozen=True)
class ReleaseInfo:
    """
    Information about a GitHub release.

    Contains the essential metadata needed to download and verify a release.

    Attributes:
        version: Semantic version of the release
        checksum: SHA256 checksum of the release artifact
        download_url: URL to download the release artifact
    """

    version: Version
    checksum: str
    download_url: str


class GitHubAPIPort(ABC):
    """
    Port interface for GitHub API operations.

    This abstract class defines the contract for fetching release information
    from GitHub. Implementations handle HTTP communication, authentication,
    and error handling.

    Implementers must handle:
        - HTTP request construction and execution
        - Response parsing and validation
        - Rate limit detection and signaling
        - Network error detection and signaling

    Example:
        >>> class MockGitHubAdapter(GitHubAPIPort):
        ...     def get_latest_release(self, owner: str, repo: str) -> ReleaseInfo:
        ...         return ReleaseInfo(
        ...             version=Version("1.0.0"),
        ...             checksum="abc123...",
        ...             download_url="https://github.com/..."
        ...         )
    """

    @abstractmethod
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
        pass
