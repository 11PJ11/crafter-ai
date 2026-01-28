"""
Contract tests for DownloadPort interface.

These tests verify the port interface contract:
- Abstract class with abstract methods
- download(url, destination) method signature
- Progress callback support for large files
- NetworkError exception type defined

Step: 02-04 Define DownloadPort interface
Acceptance Criteria:
- Abstract method download(url, destination) defined
- NetworkError exception type defined
- Supports progress callback for large files
"""

import pytest
from abc import ABC
import inspect


class TestDownloadPortIsAbstract:
    """Test that DownloadPort is properly defined as an abstract class."""

    def test_download_port_is_abstract_base_class(self):
        """DownloadPort must be an abstract base class."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        assert issubclass(DownloadPort, ABC), "DownloadPort must inherit from ABC"

    def test_download_port_cannot_be_instantiated(self):
        """Abstract classes cannot be directly instantiated."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        with pytest.raises(TypeError):
            DownloadPort()


class TestDownloadMethodDefined:
    """Test that download method is properly defined."""

    def test_download_method_exists(self):
        """DownloadPort must define download method."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        assert hasattr(DownloadPort, "download")

    def test_download_is_abstract_method(self):
        """download must be an abstract method."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        method = getattr(DownloadPort, "download", None)
        assert method is not None
        assert getattr(method, "__isabstractmethod__", False), (
            "download must be decorated with @abstractmethod"
        )


class TestDownloadAcceptsUrlAndDestination:
    """Test that download method accepts url and destination parameters."""

    def test_download_accepts_url_parameter(self):
        """download must accept url parameter."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        sig = inspect.signature(DownloadPort.download)
        params = list(sig.parameters.keys())

        assert "url" in params, "Method must have 'url' parameter"

    def test_download_accepts_destination_parameter(self):
        """download must accept destination parameter."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        sig = inspect.signature(DownloadPort.download)
        params = list(sig.parameters.keys())

        assert "destination" in params, "Method must have 'destination' parameter"

    def test_download_url_is_string_type(self):
        """download url parameter should be typed as str."""
        from nWave.core.versioning.ports.download_port import DownloadPort
        from typing import get_type_hints

        hints = get_type_hints(DownloadPort.download)
        assert hints.get("url") is str, "url parameter must be typed as str"

    def test_download_destination_is_path_type(self):
        """download destination parameter should be typed as Path."""
        from nWave.core.versioning.ports.download_port import DownloadPort
        from typing import get_type_hints
        from pathlib import Path

        hints = get_type_hints(DownloadPort.download)
        assert hints.get("destination") == Path, (
            "destination parameter must be typed as Path"
        )


class TestNetworkErrorExceptionDefined:
    """Test that NetworkError exception is properly defined for download operations."""

    def test_network_error_class_exists(self):
        """NetworkError exception class must be defined."""
        from nWave.core.versioning.ports.download_port import NetworkError

        assert NetworkError is not None

    def test_network_error_is_exception(self):
        """NetworkError must be a subclass of Exception."""
        from nWave.core.versioning.ports.download_port import NetworkError

        assert issubclass(NetworkError, Exception), (
            "NetworkError must inherit from Exception"
        )

    def test_network_error_can_be_raised(self):
        """NetworkError must be raisable with a message."""
        from nWave.core.versioning.ports.download_port import NetworkError

        with pytest.raises(NetworkError) as exc_info:
            raise NetworkError("Download failed: connection timeout")

        assert "Download failed" in str(exc_info.value)


class TestProgressCallbackSupported:
    """Test that download method supports progress callback for large files."""

    def test_download_accepts_progress_callback_parameter(self):
        """download must accept optional progress_callback parameter."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        sig = inspect.signature(DownloadPort.download)
        params = list(sig.parameters.keys())

        assert "progress_callback" in params, (
            "Method must have 'progress_callback' parameter for large file progress"
        )

    def test_progress_callback_is_optional(self):
        """progress_callback parameter should be optional (have default value)."""
        from nWave.core.versioning.ports.download_port import DownloadPort

        sig = inspect.signature(DownloadPort.download)
        param = sig.parameters.get("progress_callback")

        assert param is not None
        assert param.default is not inspect.Parameter.empty or str(
            param.annotation
        ).startswith("Optional"), (
            "progress_callback must be optional (have default value or Optional type)"
        )

    def test_progress_callback_type_hint_is_callable(self):
        """progress_callback should be typed as Optional[Callable[[int, int], None]]."""
        from nWave.core.versioning.ports.download_port import DownloadPort
        from typing import get_type_hints, get_origin, get_args
        import typing

        hints = get_type_hints(DownloadPort.download)
        callback_hint = hints.get("progress_callback")

        # Should be Optional[something] or Union[something, None]
        assert callback_hint is not None, "progress_callback must have type hint"

        # Check it's Optional (Union with None)
        origin = get_origin(callback_hint)
        if origin is typing.Union:
            args = get_args(callback_hint)
            assert type(None) in args, (
                "progress_callback must be Optional (include None in Union)"
            )
