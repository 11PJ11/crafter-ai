"""
DownloadAdapter - Concrete implementation of DownloadPort.

Implements file download operations for fetching release assets.

HEXAGONAL ARCHITECTURE:
- This is a DRIVEN ADAPTER (outside the hexagon)
- Implements DownloadPort interface
- Uses requests library for HTTP operations
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable, Optional

from nWave.core.versioning.ports.download_port import DownloadPort, NetworkError


class DownloadAdapter(DownloadPort):
    """
    Concrete adapter for file download operations.

    Downloads files from remote URLs with support for:
    - Streaming downloads for large files
    - Progress callback reporting
    - Network error handling

    Example:
        >>> adapter = DownloadAdapter()
        >>> adapter.download(
        ...     "https://github.com/releases/v1.3.0.tar.gz",
        ...     Path("/tmp/release.tar.gz"),
        ...     progress_callback=lambda d, t: print(f"{d}/{t}")
        ... )
    """

    # Chunk size for streaming downloads (8KB)
    CHUNK_SIZE = 8192

    # Request timeout in seconds
    TIMEOUT = 30

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
            url: The URL of the file to download
            destination: Local filesystem path where the file will be saved
            progress_callback: Optional callback function invoked during download.
                               Called with (bytes_downloaded, total_bytes).

        Raises:
            NetworkError: If the network request fails
            OSError: If the destination cannot be written to
        """
        # Check for test mode
        if os.getenv("NWAVE_TEST_MODE", "false").lower() == "true":
            self._handle_test_mode_download(url, destination)
            return

        self._perform_real_download(url, destination, progress_callback)

    def _handle_test_mode_download(self, url: str, destination: Path) -> None:
        """Handle download in test mode by creating mock file."""
        # In test mode, create a mock file
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"mock release content for testing")

    def _perform_real_download(
        self,
        url: str,
        destination: Path,
        progress_callback: Optional[Callable[[int, int], None]] = None,
    ) -> None:
        """Perform actual HTTP download."""
        try:
            import requests
        except ImportError:
            raise NetworkError("requests library not installed")

        try:
            with requests.get(url, stream=True, timeout=self.TIMEOUT) as response:
                response.raise_for_status()

                total_size = int(response.headers.get("content-length", 0))
                downloaded = 0

                destination.parent.mkdir(parents=True, exist_ok=True)

                with open(destination, "wb") as f:
                    for chunk in response.iter_content(chunk_size=self.CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if progress_callback:
                                progress_callback(downloaded, total_size)

        except requests.exceptions.ConnectionError as e:
            raise NetworkError(f"Connection failed: {e}") from e
        except requests.exceptions.Timeout as e:
            raise NetworkError(f"Request timed out: {e}") from e
        except requests.exceptions.RequestException as e:
            raise NetworkError(f"Download failed: {e}") from e
