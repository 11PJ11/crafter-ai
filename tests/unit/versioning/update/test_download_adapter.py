"""
Unit tests for DownloadAdapter (driven adapter).

HEXAGONAL ARCHITECTURE:
- DownloadAdapter is a DRIVEN ADAPTER (outside the hexagon)
- Implements DownloadPort interface
- Tests verify adapter correctly implements port contract
"""

from pathlib import Path
from unittest.mock import MagicMock, patch
import tempfile

import pytest


class TestDownloadAdapterFetchesFile:
    """Test that DownloadAdapter correctly downloads files."""

    def test_download_adapter_fetches_file(self):
        """
        GIVEN: DownloadAdapter in test mode
        WHEN: download() is called with valid URL
        THEN: File is downloaded to destination path
        """
        import os
        from nWave.infrastructure.versioning.download_adapter import DownloadAdapter

        with tempfile.TemporaryDirectory() as tmp_dir:
            # Arrange
            adapter = DownloadAdapter()
            destination = Path(tmp_dir) / "downloaded_file.tar.gz"
            url = "https://example.com/release.tar.gz"

            # Act - Set test mode to use mock download
            with patch.dict(os.environ, {"NWAVE_TEST_MODE": "true"}):
                adapter.download(url, destination)

            # Assert: File was created at destination
            assert destination.exists(), "Downloaded file should exist"


class TestDownloadAdapterHandlesNetworkError:
    """Test that DownloadAdapter handles network errors correctly."""

    def test_download_adapter_raises_network_error_on_failure(self):
        """
        GIVEN: DownloadAdapter NOT in test mode
        WHEN: Network request fails
        THEN: NetworkError is raised

        NOTE: This test requires requests library to be installed.
        If not available, test is skipped.
        """
        import os
        from nWave.infrastructure.versioning.download_adapter import DownloadAdapter
        from nWave.core.versioning.ports.download_port import NetworkError

        # Skip if requests not installed
        try:
            import requests
        except ImportError:
            pytest.skip("requests library not installed")

        with tempfile.TemporaryDirectory() as tmp_dir:
            adapter = DownloadAdapter()
            destination = Path(tmp_dir) / "downloaded_file.tar.gz"

            # Ensure NOT in test mode and mock the imported requests module
            with patch.dict(os.environ, {"NWAVE_TEST_MODE": "false"}):
                # Patch the requests module in the adapter
                with patch.object(adapter, "_perform_real_download") as mock_download:
                    mock_download.side_effect = NetworkError("Network error")

                    with pytest.raises(NetworkError):
                        adapter.download("https://example.com/file.tar.gz", destination)
