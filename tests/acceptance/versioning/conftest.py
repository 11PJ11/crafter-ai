"""
pytest-bdd configuration for versioning acceptance tests.

HEXAGONAL BOUNDARY ENFORCEMENT:
- Tests invoke CLI entry points only
- No direct imports from nWave.core.*
- Mocking allowed only at port boundaries (GitHubAPIPort, FileSystemPort)
"""

from pathlib import Path

import pytest


@pytest.fixture(scope="function")
def isolated_home(tmp_path, monkeypatch):
    """
    Create isolated HOME directory for each test.
    Prevents tests from affecting real ~/.claude/ installation.
    """
    fake_home = tmp_path / "test-home"
    fake_home.mkdir()

    fake_claude = fake_home / ".claude"
    fake_claude.mkdir()

    monkeypatch.setenv("HOME", str(fake_home))
    monkeypatch.setenv("NWAVE_HOME", str(fake_claude))

    yield fake_home


@pytest.fixture
def test_installation(isolated_home):
    """
    Set up test installation structure.

    Structure:
        ~/.claude/
            VERSION             (installed version)
            nwave.update        (watermark file)
    """
    nwave_home = isolated_home / ".claude"
    nwave_home.mkdir(parents=True, exist_ok=True)

    return {
        "nwave_home": nwave_home,
        "version_file": nwave_home / "VERSION",
        "watermark_file": nwave_home / "nwave.update",
    }


@pytest.fixture
def mock_github_adapter():
    """
    In-memory mock for GitHubAPIPort.

    Returns configured release info for testing.
    """

    class MockGitHubAPIAdapter:
        def __init__(self):
            self.latest_version = "1.3.0"
            self.checksum = "abc123def456"
            self.download_url = "https://github.com/test/releases/v1.3.0.zip"
            self.should_raise_network_error = False
            self.should_raise_rate_limit_error = False

        def configure(
            self,
            latest_version: str,
            checksum: str = "abc123",
            download_url: str | None = None,
        ):
            self.latest_version = latest_version
            self.checksum = checksum
            self.download_url = (
                download_url
                or f"https://github.com/test/releases/v{latest_version}.zip"
            )

        def get_latest_release(self, owner: str, repo: str):
            from nWave.core.versioning.domain.version import Version
            from nWave.core.versioning.ports.github_api_port import (
                NetworkError,
                RateLimitError,
                ReleaseInfo,
            )

            if self.should_raise_network_error:
                raise NetworkError("Network unavailable")
            if self.should_raise_rate_limit_error:
                raise RateLimitError("Rate limit exceeded", retry_after=60)

            return ReleaseInfo(
                version=Version(self.latest_version),
                checksum=self.checksum,
                download_url=self.download_url,
            )

    return MockGitHubAPIAdapter()


@pytest.fixture
def in_memory_file_system_adapter(test_installation):
    """
    In-memory implementation of FileSystemPort.

    Stores data in test installation directories.
    """

    class InMemoryFileSystemAdapter:
        def __init__(self, test_dirs):
            self._test_dirs = test_dirs

        def read_version(self):
            from nWave.core.versioning.domain.version import Version

            version_file = self._test_dirs["version_file"]
            if not version_file.exists():
                raise FileNotFoundError(f"VERSION file not found at {version_file}")
            content = version_file.read_text().strip()
            return Version(content)

        def read_watermark(self):
            from nWave.core.versioning.domain.watermark import Watermark

            watermark_file = self._test_dirs["watermark_file"]
            if not watermark_file.exists():
                return None
            content = watermark_file.read_text()
            return Watermark.from_json(content)

        def write_watermark(self, watermark):
            watermark_file = self._test_dirs["watermark_file"]
            watermark_file.write_text(watermark.to_json())

        def create_backup(self, backup_path: Path):
            import shutil

            nwave_home = self._test_dirs["nwave_home"]
            shutil.copytree(nwave_home, backup_path)

        def list_backups(self):
            nwave_home = self._test_dirs["nwave_home"]
            parent = nwave_home.parent
            return sorted(parent.glob(".claude.backup.*"))

        def delete_backup(self, backup_path: Path):
            import shutil

            if backup_path.exists():
                shutil.rmtree(backup_path)
                return True
            return False

    return InMemoryFileSystemAdapter(test_installation)


@pytest.fixture
def cli_result():
    """Container for CLI execution results."""
    return {
        "stdout": "",
        "stderr": "",
        "returncode": 0,
        "output": "",
    }
