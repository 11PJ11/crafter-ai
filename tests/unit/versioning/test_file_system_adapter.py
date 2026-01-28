"""
Unit tests for FileSystemAdapter (driven adapter).

FileSystemAdapter implements FileSystemPort for reading/writing files.
"""

import json
import pytest
from datetime import datetime, timezone
from pathlib import Path

from nWave.core.versioning.domain.version import Version
from nWave.core.versioning.domain.watermark import Watermark


class TestFileSystemAdapterReadsVersion:
    """Test that FileSystemAdapter reads VERSION file correctly."""

    def test_file_system_adapter_reads_version_file(self, tmp_path):
        """Adapter should read and parse VERSION file content."""
        from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter

        # GIVEN: VERSION file exists with content "1.2.3"
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()
        version_file = nwave_home / "VERSION"
        version_file.write_text("1.2.3")

        adapter = FileSystemAdapter(nwave_home=nwave_home)

        # WHEN: read_version is called
        result = adapter.read_version()

        # THEN: Returns Version("1.2.3")
        assert result == Version("1.2.3")

    def test_file_system_adapter_raises_on_missing_version(self, tmp_path):
        """Adapter should raise FileNotFoundError if VERSION file missing."""
        from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter

        # GIVEN: No VERSION file exists
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()

        adapter = FileSystemAdapter(nwave_home=nwave_home)

        # WHEN/THEN: read_version raises FileNotFoundError
        with pytest.raises(FileNotFoundError):
            adapter.read_version()


class TestFileSystemAdapterWritesWatermark:
    """Test that FileSystemAdapter writes watermark file correctly."""

    def test_file_system_adapter_writes_watermark(self, tmp_path):
        """Adapter should write watermark to nwave.update file."""
        from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter

        # GIVEN: nwave home directory exists
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()

        adapter = FileSystemAdapter(nwave_home=nwave_home)

        watermark = Watermark(
            last_check=datetime(2026, 1, 28, 12, 0, 0, tzinfo=timezone.utc),
            latest_version=Version("1.3.0"),
        )

        # WHEN: write_watermark is called
        adapter.write_watermark(watermark)

        # THEN: nwave.update file exists with correct content
        watermark_file = nwave_home / "nwave.update"
        assert watermark_file.exists()

        content = json.loads(watermark_file.read_text())
        assert content["latest_version"] == "1.3.0"
        assert "last_check" in content

    def test_file_system_adapter_reads_watermark(self, tmp_path):
        """Adapter should read watermark from nwave.update file."""
        from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter

        # GIVEN: nwave.update file exists
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()

        watermark_data = {
            "last_check": "2026-01-28T12:00:00+00:00",
            "latest_version": "1.3.0",
        }
        watermark_file = nwave_home / "nwave.update"
        watermark_file.write_text(json.dumps(watermark_data))

        adapter = FileSystemAdapter(nwave_home=nwave_home)

        # WHEN: read_watermark is called
        result = adapter.read_watermark()

        # THEN: Returns Watermark with correct data
        assert result is not None
        assert result.latest_version == Version("1.3.0")

    def test_file_system_adapter_returns_none_for_missing_watermark(self, tmp_path):
        """Adapter should return None if watermark file missing."""
        from nWave.infrastructure.versioning.file_system_adapter import FileSystemAdapter

        # GIVEN: No nwave.update file exists
        nwave_home = tmp_path / ".claude"
        nwave_home.mkdir()

        adapter = FileSystemAdapter(nwave_home=nwave_home)

        # WHEN: read_watermark is called
        result = adapter.read_watermark()

        # THEN: Returns None
        assert result is None
