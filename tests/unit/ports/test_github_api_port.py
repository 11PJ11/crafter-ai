"""
Contract tests for GitHubAPIPort interface.

These tests verify the port interface contract:
- Abstract class with abstract methods
- Return type includes version, checksum, download_url
- Exception types for network and rate limit errors
"""

import pytest
from abc import ABC
import inspect


class TestGitHubApiPortIsAbstract:
    """Test that GitHubAPIPort is properly defined as an abstract class."""

    def test_github_api_port_is_abstract_base_class(self):
        """GitHubAPIPort must be an abstract base class."""
        from nWave.core.versioning.ports.github_api_port import GitHubAPIPort

        assert issubclass(GitHubAPIPort, ABC), "GitHubAPIPort must inherit from ABC"

    def test_github_api_port_cannot_be_instantiated(self):
        """Abstract classes cannot be directly instantiated."""
        from nWave.core.versioning.ports.github_api_port import GitHubAPIPort

        with pytest.raises(TypeError):
            GitHubAPIPort()


class TestGetLatestReleaseMethodDefined:
    """Test that get_latest_release method is properly defined."""

    def test_get_latest_release_method_exists(self):
        """GitHubAPIPort must define get_latest_release method."""
        from nWave.core.versioning.ports.github_api_port import GitHubAPIPort

        assert hasattr(GitHubAPIPort, "get_latest_release")

    def test_get_latest_release_is_abstract_method(self):
        """get_latest_release must be an abstract method."""
        from nWave.core.versioning.ports.github_api_port import GitHubAPIPort

        method = getattr(GitHubAPIPort, "get_latest_release", None)
        assert method is not None
        assert getattr(method, "__isabstractmethod__", False), \
            "get_latest_release must be decorated with @abstractmethod"

    def test_get_latest_release_accepts_owner_repo_parameters(self):
        """get_latest_release must accept owner and repo parameters."""
        from nWave.core.versioning.ports.github_api_port import GitHubAPIPort

        sig = inspect.signature(GitHubAPIPort.get_latest_release)
        params = list(sig.parameters.keys())

        # Should have self, owner, repo
        assert "owner" in params, "Method must have 'owner' parameter"
        assert "repo" in params, "Method must have 'repo' parameter"


class TestReturnTypeIncludesVersion:
    """Test that return type includes version information."""

    def test_release_info_dataclass_exists(self):
        """ReleaseInfo dataclass must be defined."""
        from nWave.core.versioning.ports.github_api_port import ReleaseInfo

        assert ReleaseInfo is not None

    def test_release_info_has_version_field(self):
        """ReleaseInfo must have a version field."""
        from nWave.core.versioning.ports.github_api_port import ReleaseInfo
        import dataclasses

        assert dataclasses.is_dataclass(ReleaseInfo), "ReleaseInfo must be a dataclass"
        field_names = [f.name for f in dataclasses.fields(ReleaseInfo)]
        assert "version" in field_names, "ReleaseInfo must have 'version' field"

    def test_release_info_version_is_version_type(self):
        """ReleaseInfo.version must be of type Version."""
        from nWave.core.versioning.ports.github_api_port import ReleaseInfo
        from nWave.core.versioning.domain.version import Version
        from typing import get_type_hints

        hints = get_type_hints(ReleaseInfo)
        assert hints.get("version") == Version, \
            "ReleaseInfo.version must be typed as Version"


class TestReturnTypeIncludesChecksum:
    """Test that return type includes checksum information."""

    def test_release_info_has_checksum_field(self):
        """ReleaseInfo must have a checksum field."""
        from nWave.core.versioning.ports.github_api_port import ReleaseInfo
        import dataclasses

        field_names = [f.name for f in dataclasses.fields(ReleaseInfo)]
        assert "checksum" in field_names, "ReleaseInfo must have 'checksum' field"

    def test_release_info_checksum_is_string_type(self):
        """ReleaseInfo.checksum must be of type str."""
        from nWave.core.versioning.ports.github_api_port import ReleaseInfo
        from typing import get_type_hints

        hints = get_type_hints(ReleaseInfo)
        assert hints.get("checksum") is str, \
            "ReleaseInfo.checksum must be typed as str"


class TestReturnTypeIncludesDownloadUrl:
    """Test that return type includes download URL."""

    def test_release_info_has_download_url_field(self):
        """ReleaseInfo must have a download_url field."""
        from nWave.core.versioning.ports.github_api_port import ReleaseInfo
        import dataclasses

        field_names = [f.name for f in dataclasses.fields(ReleaseInfo)]
        assert "download_url" in field_names, "ReleaseInfo must have 'download_url' field"

    def test_release_info_download_url_is_string_type(self):
        """ReleaseInfo.download_url must be of type str."""
        from nWave.core.versioning.ports.github_api_port import ReleaseInfo
        from typing import get_type_hints

        hints = get_type_hints(ReleaseInfo)
        assert hints.get("download_url") is str, \
            "ReleaseInfo.download_url must be typed as str"


class TestNetworkErrorExceptionDefined:
    """Test that NetworkError exception is properly defined."""

    def test_network_error_class_exists(self):
        """NetworkError exception class must be defined."""
        from nWave.core.versioning.ports.github_api_port import NetworkError

        assert NetworkError is not None

    def test_network_error_is_exception(self):
        """NetworkError must be a subclass of Exception."""
        from nWave.core.versioning.ports.github_api_port import NetworkError

        assert issubclass(NetworkError, Exception), \
            "NetworkError must inherit from Exception"

    def test_network_error_can_be_raised(self):
        """NetworkError must be raisable with a message."""
        from nWave.core.versioning.ports.github_api_port import NetworkError

        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError("Connection failed")

        assert "Connection failed" in str(exc_info.value)


class TestRateLimitErrorExceptionDefined:
    """Test that RateLimitError exception is properly defined."""

    def test_rate_limit_error_class_exists(self):
        """RateLimitError exception class must be defined."""
        from nWave.core.versioning.ports.github_api_port import RateLimitError

        assert RateLimitError is not None

    def test_rate_limit_error_is_exception(self):
        """RateLimitError must be a subclass of Exception."""
        from nWave.core.versioning.ports.github_api_port import RateLimitError

        assert issubclass(RateLimitError, Exception), \
            "RateLimitError must inherit from Exception"

    def test_rate_limit_error_can_be_raised(self):
        """RateLimitError must be raisable with a message."""
        from nWave.core.versioning.ports.github_api_port import RateLimitError

        with pytest.raises(RateLimitError) as exc_info:
            raise RateLimitError("API rate limit exceeded")

        assert "rate limit" in str(exc_info.value).lower()

    def test_rate_limit_error_has_retry_after_attribute(self):
        """RateLimitError should have retry_after attribute for retry timing."""
        from nWave.core.versioning.ports.github_api_port import RateLimitError

        error = RateLimitError("Rate limit exceeded", retry_after=60)
        assert hasattr(error, "retry_after")
        assert error.retry_after == 60
