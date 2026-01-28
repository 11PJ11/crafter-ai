"""
Forge Install CLI - Driving adapter for /nw:forge:install command.

Entry point for installing a built distribution from dist/ to ~/.claude/.

HEXAGONAL ARCHITECTURE:
- This is a DRIVING ADAPTER (outside the hexagon)
- Invokes InstallService application service
- Formats output for user display

TEST MODE:
When NWAVE_TEST_MODE=true, uses environment-configured paths:
- NWAVE_HOME: Target ~/.claude/ directory
- NWAVE_DIST_DIR: Source dist/ directory
"""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Optional

if TYPE_CHECKING:
    from nWave.core.versioning.application.install_service import InstallResult


def _is_test_mode() -> bool:
    """Check if running in test mode."""
    return os.getenv("NWAVE_TEST_MODE", "false").lower() == "true"


def _get_nwave_home() -> Path:
    """Get the target ~/.claude/ directory."""
    env_home = os.getenv("NWAVE_HOME")
    if env_home:
        return Path(env_home)
    return Path.home() / ".claude"


def _get_dist_dir() -> Path:
    """Get the source dist/ directory."""
    env_dist = os.getenv("NWAVE_DIST_DIR")
    if env_dist:
        return Path(env_dist)
    # Default: look in current working directory
    return Path.cwd() / "dist"


class InstallationFileSystemAdapter:
    """
    File system adapter for installation operations.

    Handles copying dist/ contents to ~/.claude/ with proper
    nWave content replacement.
    """

    def __init__(self, dist_dir: Path, nwave_home: Path) -> None:
        """
        Create adapter with source and target directories.

        Args:
            dist_dir: Source directory containing built distribution
            nwave_home: Target ~/.claude/ directory
        """
        self._dist_dir = dist_dir
        self._nwave_home = nwave_home

    def copy_dist_to_claude(self) -> None:
        """
        Copy all dist/ files to ~/.claude/.

        Preserves directory structure. Replaces existing nWave content
        in agents/nw/ and commands/nw/.
        """
        # Ensure target directory exists
        self._nwave_home.mkdir(parents=True, exist_ok=True)

        # Clear existing nWave content before copying
        self._clear_nwave_content()

        # Copy dist/ contents to ~/.claude/
        for source_path in self._dist_dir.rglob("*"):
            if source_path.is_file():
                relative = source_path.relative_to(self._dist_dir)
                target_path = self._nwave_home / relative

                # Ensure parent directories exist
                target_path.parent.mkdir(parents=True, exist_ok=True)

                # Copy file
                shutil.copy2(source_path, target_path)

    def _clear_nwave_content(self) -> None:
        """Clear existing nWave-prefixed content before installation."""
        nwave_dirs = [
            self._nwave_home / "agents" / "nw",
            self._nwave_home / "commands" / "nw",
        ]

        for nw_dir in nwave_dirs:
            if nw_dir.exists():
                shutil.rmtree(nw_dir)

    def file_exists_in_claude(self, relative_path: str) -> bool:
        """Check if file exists in ~/.claude/."""
        return (self._nwave_home / relative_path).exists()

    def get_installed_file(self, relative_path: str) -> str | None:
        """Get content of installed file."""
        file_path = self._nwave_home / relative_path
        if file_path.exists():
            return file_path.read_text()
        return None

    def list_dist_files(self) -> list[str]:
        """List all files in dist/."""
        return [str(p) for p in self._dist_dir.rglob("*") if p.is_file()]


def _is_smoke_test_forced_failure() -> bool:
    """Check if smoke test should be forced to fail (for testing)."""
    return os.getenv("NWAVE_FORCE_SMOKE_FAILURE", "false").lower() == "true"


def _create_smoke_test_runner(nwave_home: Path) -> Callable[[], bool]:
    """
    Create a smoke test runner that executes /nw:version.

    The smoke test validates the installation by running the version
    command and checking for successful execution.

    In test mode with NWAVE_FORCE_SMOKE_FAILURE=true, the smoke test
    will always fail to simulate corrupted installation.
    """
    def run_smoke_test() -> bool:
        # If forced failure is set, return False immediately
        if _is_smoke_test_forced_failure():
            return False

        # Find version_cli.py
        cli_path = Path(__file__).parent / "version_cli.py"

        if not cli_path.exists():
            return False

        try:
            # Set up environment for test
            env = os.environ.copy()
            env["NWAVE_HOME"] = str(nwave_home)

            result = subprocess.run(
                [sys.executable, str(cli_path)],
                capture_output=True,
                timeout=10,
                env=env,
            )
            return result.returncode == 0
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return False

    return run_smoke_test


def main() -> int:
    """
    Main entry point for /nw:forge:install command.

    Returns:
        Exit code: 0 for success, non-zero for error
    """
    from nWave.core.versioning.application.install_service import InstallService

    try:
        dist_dir = _get_dist_dir()
        nwave_home = _get_nwave_home()

        # Validate dist/ exists
        if not dist_dir.exists():
            print("No distribution found. Run /nw:forge first to build.", file=sys.stderr)
            return 1

        # Validate dist/ has required structure
        if not (dist_dir / "VERSION").exists():
            print("Invalid distribution: missing required files. Rebuild with /nw:forge.", file=sys.stderr)
            return 1

        # Create file system adapter
        file_system = InstallationFileSystemAdapter(
            dist_dir=dist_dir,
            nwave_home=nwave_home,
        )

        # Create smoke test runner
        smoke_test_runner = _create_smoke_test_runner(nwave_home)

        # Create service and perform installation
        service = InstallService(
            file_system=file_system,
            smoke_test_runner=smoke_test_runner,
        )

        result = service.install()

        # Display result
        print(result.message)

        return 0 if result.success else 1

    except PermissionError:
        print("Permission denied. Check directory access rights.", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Installation failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
