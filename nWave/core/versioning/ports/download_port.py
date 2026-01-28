"""
DownloadPort - Port interface for file download operations.

This port defines the contract for downloading release assets from remote servers.
Adapters implementing this port handle the actual network communication,
streaming for large files, and progress reporting.

Example:
    class HttpDownloadAdapter(DownloadPort):
        def download(
            self,
            url: str,
            destination: Path,
            progress_callback: Optional[Callable[[int, int], None]] = None
        ) -> None:
            # Implementation with httpx/requests streaming
            ...
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Callable, Optional


class NetworkError(Exception):
    """
    Raised when a network operation fails during download.

    This exception indicates a transient failure that may be retryable,
    such as connection timeouts, DNS failures, server unreachable errors,
    or interrupted transfers.

    Example:
        >>> raise NetworkError("Download failed: connection timeout")
        NetworkError: Download failed: connection timeout
    """

    pass


class DownloadPort(ABC):
    """
    Port interface for file download operations.

    This abstract class defines the contract for downloading files from remote
    URLs. Implementations handle HTTP communication, streaming for large files,
    and progress reporting.

    Implementers must handle:
        - HTTP request construction and execution
        - Streaming downloads for large files
        - Progress callback invocation
        - Network error detection and signaling
        - Partial download cleanup on failure

    Example:
        >>> class MockDownloadAdapter(DownloadPort):
        ...     def download(
        ...         self,
        ...         url: str,
        ...         destination: Path,
        ...         progress_callback: Optional[Callable[[int, int], None]] = None
        ...     ) -> None:
        ...         # Write test data to destination
        ...         destination.write_text("test content")
    """

    @abstractmethod
    def download(
        self,
        url: str,
        destination: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """
        Download a file from a URL to a local destination.

        Downloads the file at the given URL and saves it to the destination path.
        For large files, the download is streamed to avoid memory issues.
        Progress can be reported via an optional callback.

        Args:
            url: The URL of the file to download (e.g., "https://github.com/...release.tar.gz")
            destination: Local filesystem path where the file will be saved
            progress_callback: Optional callback function invoked during download.
                               Called with (bytes_downloaded, total_bytes).
                               If total_bytes is unknown, it may be 0 or -1.

        Returns:
            None

        Raises:
            NetworkError: If the network request fails (timeout, connection error, etc.)
            OSError: If the destination cannot be written to

        Example:
            >>> adapter = HttpDownloadAdapter()
            >>> def show_progress(downloaded: int, total: int) -> None:
            ...     print(f"Downloaded {downloaded}/{total} bytes")
            >>> adapter.download(
            ...     "https://example.com/file.tar.gz",
            ...     Path("/tmp/file.tar.gz"),
            ...     progress_callback=show_progress
            ... )
            Downloaded 1024/10240 bytes
            Downloaded 2048/10240 bytes
            ...
        """
        pass
