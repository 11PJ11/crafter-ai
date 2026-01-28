"""
InstallService - Application service for forge:install command.

Orchestrates installation of a built distribution to ~/.claude/:
1. Copy dist/ contents to ~/.claude/
2. Replace nWave-prefixed content in agents/nw/ and commands/nw/
3. Run smoke test (/nw:version)
4. Return result with success message

HEXAGONAL ARCHITECTURE:
- This is an APPLICATION SERVICE (inside the hexagon)
- Depends only on PORT interfaces, not concrete adapters
- Uses real domain objects (Version, CoreContentIdentifier), never mocks

Step 06-01: Successful installation with smoke test
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional, Protocol

if TYPE_CHECKING:
    from nWave.core.versioning.domain.version import Version


@dataclass(frozen=True)
class InstallResult:
    """
    Result of an installation operation.

    Attributes:
        success: True if installation completed (files copied)
        smoke_test_passed: True if smoke test succeeded
        message: Human-readable result message
        installed_version: Version that was installed (if successful)
    """

    success: bool
    smoke_test_passed: bool
    message: str
    installed_version: Optional[str] = None


class FileSystemProtocol(Protocol):
    """Protocol for file system operations needed by InstallService."""

    def copy_dist_to_claude(self) -> None:
        """Copy all dist/ files to ~/.claude/."""
        ...

    def file_exists_in_claude(self, relative_path: str) -> bool:
        """Check if file exists in ~/.claude/."""
        ...

    def get_installed_file(self, relative_path: str) -> str | None:
        """Get content of installed file."""
        ...

    def list_dist_files(self) -> list[str]:
        """List all files in dist/."""
        ...


class InstallService:
    """
    Application service for installing built distributions.

    Orchestrates the installation workflow:
    1. Copy dist/ contents to ~/.claude/ directory
    2. Replace nWave-prefixed content (agents/nw/, commands/nw/)
    3. Run smoke test to validate installation
    4. Return result with appropriate message

    Example:
        >>> service = InstallService(file_system=adapter, smoke_test_runner=runner)
        >>> result = service.install()
        >>> if result.success:
        ...     print(result.message)  # "Installation complete."
    """

    def __init__(
        self,
        file_system: FileSystemProtocol,
        smoke_test_runner: Optional[Callable[[], bool]] = None,
    ) -> None:
        """
        Create an InstallService.

        Args:
            file_system: Adapter implementing file system operations
            smoke_test_runner: Function that runs smoke test and returns True if passed
        """
        self._file_system = file_system
        self._smoke_test_runner = smoke_test_runner or self._default_smoke_test

    def install(self) -> InstallResult:
        """
        Install the distribution to ~/.claude/.

        Workflow:
        1. Validate dist/ contains required files
        2. Copy dist/ contents to ~/.claude/
        3. Run smoke test (/nw:version)
        4. Return result based on smoke test outcome

        Returns:
            InstallResult with success status and message
        """
        # Step 1: Copy dist/ to ~/.claude/
        self._file_system.copy_dist_to_claude()

        # Step 2: Get installed version
        version_content = self._file_system.get_installed_file("VERSION")
        installed_version = version_content.strip() if version_content else None

        # Step 3: Run smoke test
        smoke_test_passed = self._smoke_test_runner()

        # Step 4: Return appropriate result
        if smoke_test_passed:
            return InstallResult(
                success=True,
                smoke_test_passed=True,
                message="Installation complete.",
                installed_version=installed_version,
            )
        else:
            return InstallResult(
                success=True,
                smoke_test_passed=False,
                message="Installation complete but smoke test failed. Verify with /nw:version.",
                installed_version=installed_version,
            )

    def _default_smoke_test(self) -> bool:
        """
        Default smoke test runner that executes /nw:version command.

        Returns:
            True if version command exits with code 0
        """
        import subprocess
        import sys
        import os
        from pathlib import Path

        # Find version_cli.py relative to this module
        cli_path = Path(__file__).parent.parent.parent.parent / "cli" / "version_cli.py"

        if not cli_path.exists():
            return False

        try:
            result = subprocess.run(
                [sys.executable, str(cli_path)],
                capture_output=True,
                timeout=10,
                env=os.environ.copy(),
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False
