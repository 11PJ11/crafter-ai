"""
Unit tests for InstallService - Application service for forge:install command.

HEXAGONAL ARCHITECTURE:
- Uses REAL domain objects (CoreContentIdentifier, Version)
- Mocks ONLY at port boundaries (FileSystemPort)
- Tests business behavior, not implementation details

Step 06-01: Successful installation with smoke test
Expected unit tests:
- test_forge_install_copies_dist_to_claude_dir
- test_forge_install_replaces_nw_content
- test_forge_install_runs_smoke_test
- test_forge_install_shows_success_message
- test_forge_install_validates_smoke_test_result
"""

from pathlib import Path
from unittest.mock import MagicMock

import pytest


class InMemoryFileSystemAdapter:
    """
    In-memory implementation of FileSystemPort for testing.

    CRITICAL: This is a Fake, not a Mock - implements actual port behavior.
    """

    def __init__(self):
        self._files: dict[str, str] = {}
        self._directories: set[str] = set()
        self._nwave_home: Path = Path("/test/.claude")
        self._dist_dir: Path = Path("/test/repo/dist")

    def set_dist_file(self, relative_path: str, content: str) -> None:
        """Add a file to the simulated dist/ directory."""
        full_path = str(self._dist_dir / relative_path)
        self._files[full_path] = content
        # Ensure parent directories exist
        parent = str(Path(full_path).parent)
        self._directories.add(parent)

    def get_installed_file(self, relative_path: str) -> str | None:
        """Get content of an installed file in ~/.claude/."""
        full_path = str(self._nwave_home / relative_path)
        return self._files.get(full_path)

    def file_exists_in_claude(self, relative_path: str) -> bool:
        """Check if file was installed to ~/.claude/."""
        full_path = str(self._nwave_home / relative_path)
        return full_path in self._files

    def copy_dist_to_claude(self) -> None:
        """Copy all dist/ files to ~/.claude/."""
        dist_prefix = str(self._dist_dir)
        for path, content in list(self._files.items()):
            if path.startswith(dist_prefix):
                relative = path[len(dist_prefix):].lstrip("/")
                target_path = str(self._nwave_home / relative)
                self._files[target_path] = content

    def list_dist_files(self) -> list[str]:
        """List all files in dist/."""
        dist_prefix = str(self._dist_dir)
        return [p for p in self._files if p.startswith(dist_prefix)]

    def read_version(self) -> "Version":
        """Read VERSION file from ~/.claude/."""
        from nWave.core.versioning.domain.version import Version
        content = self.get_installed_file("VERSION")
        if content is None:
            raise FileNotFoundError("VERSION file not found")
        return Version(content.strip())


@pytest.fixture
def in_memory_file_system():
    """Create an in-memory file system for testing."""
    return InMemoryFileSystemAdapter()


@pytest.fixture
def valid_dist_files(in_memory_file_system):
    """Set up valid dist/ structure in the in-memory file system."""
    fs = in_memory_file_system

    # VERSION file
    fs.set_dist_file("VERSION", "1.2.3-rc.main.20260127.1")

    # agents/nw/ content
    fs.set_dist_file("agents/nw/software-crafter.md", "# Software Crafter\nversion: 1.2.3")

    # commands/nw/ content
    fs.set_dist_file("commands/nw/version.md", "# Version Command\nversion: 1.2.3")

    return fs


# ============================================================================
# Test: Install service copies dist to claude dir
# ============================================================================


def test_forge_install_copies_dist_to_claude_dir(valid_dist_files):
    """
    InstallService should copy all contents of dist/ to ~/.claude/.

    Given: A valid dist/ directory with VERSION and nWave content
    When: InstallService.install() is called
    Then: All files from dist/ are copied to ~/.claude/
    """
    from nWave.core.versioning.application.install_service import InstallService

    fs = valid_dist_files

    service = InstallService(file_system=fs)

    # When: Install is called
    result = service.install()

    # Then: VERSION file is copied
    assert fs.file_exists_in_claude("VERSION"), "VERSION file should be copied"
    assert fs.get_installed_file("VERSION") == "1.2.3-rc.main.20260127.1"


# ============================================================================
# Test: Install service replaces nw content
# ============================================================================


def test_forge_install_replaces_nw_content(valid_dist_files):
    """
    InstallService should replace nWave-prefixed content in agents/nw/ and commands/nw/.

    Given: A valid dist/ directory with nWave content
    And: Existing nWave content in ~/.claude/
    When: InstallService.install() is called
    Then: nWave content in ~/.claude/agents/nw/ and commands/nw/ is replaced
    """
    from nWave.core.versioning.application.install_service import InstallService

    fs = valid_dist_files

    # Pre-existing content that should be replaced
    fs._files[str(fs._nwave_home / "agents" / "nw" / "old-agent.md")] = "old content"

    service = InstallService(file_system=fs)

    # When: Install is called
    result = service.install()

    # Then: New agent content is installed
    assert fs.file_exists_in_claude("agents/nw/software-crafter.md")
    assert "Software Crafter" in fs.get_installed_file("agents/nw/software-crafter.md")

    # And: New command content is installed
    assert fs.file_exists_in_claude("commands/nw/version.md")


# ============================================================================
# Test: Install service runs smoke test
# ============================================================================


def test_forge_install_runs_smoke_test(valid_dist_files):
    """
    InstallService should run /nw:version as a smoke test after installation.

    Given: Installation completed successfully
    When: InstallService.install() completes
    Then: The smoke test (/nw:version) is executed
    """
    from nWave.core.versioning.application.install_service import InstallService

    fs = valid_dist_files

    # Track if smoke test was called
    smoke_test_called = False

    def mock_smoke_test():
        nonlocal smoke_test_called
        smoke_test_called = True
        return True  # Smoke test passes

    service = InstallService(file_system=fs, smoke_test_runner=mock_smoke_test)

    # When: Install is called
    result = service.install()

    # Then: Smoke test was executed
    assert smoke_test_called, "Smoke test should be executed after installation"


# ============================================================================
# Test: Install service shows success message
# ============================================================================


def test_forge_install_shows_success_message(valid_dist_files):
    """
    InstallService should return success message "Installation complete.".

    Given: Installation and smoke test both succeed
    When: InstallService.install() returns
    Then: The result contains success message "Installation complete."
    """
    from nWave.core.versioning.application.install_service import InstallService

    fs = valid_dist_files

    service = InstallService(
        file_system=fs,
        smoke_test_runner=lambda: True,  # Smoke test passes
    )

    # When: Install is called
    result = service.install()

    # Then: Success message is in the result
    assert result.success is True
    assert result.message == "Installation complete."


# ============================================================================
# Test: Install service validates smoke test result
# ============================================================================


def test_forge_install_validates_smoke_test_result(valid_dist_files):
    """
    InstallService should validate the smoke test result before declaring success.

    Given: Installation succeeded but smoke test fails
    When: InstallService.install() is called
    Then: The result indicates warning about smoke test failure
    """
    from nWave.core.versioning.application.install_service import InstallService

    fs = valid_dist_files

    service = InstallService(
        file_system=fs,
        smoke_test_runner=lambda: False,  # Smoke test fails
    )

    # When: Install is called
    result = service.install()

    # Then: Installation complete but with warning
    assert result.success is True  # Installation itself succeeded
    assert result.smoke_test_passed is False
    assert "smoke test failed" in result.message.lower()
