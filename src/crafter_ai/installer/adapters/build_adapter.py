"""SubprocessBuildAdapter - subprocess-based implementation of BuildPort.

This adapter implements the BuildPort protocol using subprocess to execute
python -m build commands. It provides PEP 517 compliant wheel and sdist
building with proper error handling.
"""

import shutil
import subprocess
from pathlib import Path

from crafter_ai.installer.ports.build_port import BuildError


class SubprocessBuildAdapter:
    """Subprocess-based build adapter implementing BuildPort.

    This adapter executes 'python -m build' via subprocess.run() and
    handles errors by raising BuildError with captured output.

    Used by:
        - BuildService for creating wheel artifacts
        - InstallService for building before installation
    """

    def build_wheel(self, output_dir: Path) -> Path:
        """Build a wheel package using python -m build.

        Args:
            output_dir: Directory where the wheel should be placed.

        Returns:
            Path to the built .whl file.

        Raises:
            BuildError: If the build fails.
        """
        result = subprocess.run(
            ["python", "-m", "build", "--wheel", "--outdir", str(output_dir)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise BuildError(
                message="Wheel build failed",
                return_code=result.returncode,
                output=result.stderr or result.stdout,
            )

        wheel_path = self.get_wheel_path(output_dir)
        if wheel_path is None:
            raise BuildError(
                message="Build succeeded but no wheel file found",
                output=result.stdout,
            )

        return wheel_path

    def build_sdist(self, output_dir: Path) -> Path:
        """Build a source distribution using python -m build.

        Args:
            output_dir: Directory where the sdist should be placed.

        Returns:
            Path to the built .tar.gz file.

        Raises:
            BuildError: If the build fails.
        """
        result = subprocess.run(
            ["python", "-m", "build", "--sdist", "--outdir", str(output_dir)],
            capture_output=True,
            text=True,
            check=False,
        )

        if result.returncode != 0:
            raise BuildError(
                message="Sdist build failed",
                return_code=result.returncode,
                output=result.stderr or result.stdout,
            )

        sdist_path = self._get_sdist_path(output_dir)
        if sdist_path is None:
            raise BuildError(
                message="Build succeeded but no sdist file found",
                output=result.stdout,
            )

        return sdist_path

    def clean_build_artifacts(self) -> None:
        """Remove build artifacts (build/, dist/, *.egg-info).

        Cleans up temporary build directories to ensure fresh builds.
        Silently ignores directories that don't exist.
        """
        cwd = Path.cwd()

        # Remove build/ directory
        build_dir = cwd / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)

        # Remove dist/ directory
        dist_dir = cwd / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir)

        # Remove *.egg-info directories
        for egg_info in cwd.glob("*.egg-info"):
            shutil.rmtree(egg_info)

    def get_wheel_path(self, dist_dir: Path) -> Path | None:
        """Find a wheel file in the specified directory.

        Args:
            dist_dir: Directory to search for .whl files.

        Returns:
            Path to the first .whl file found, or None if not found.
        """
        wheels = list(dist_dir.glob("*.whl"))
        if not wheels:
            return None
        return wheels[0]

    def _get_sdist_path(self, dist_dir: Path) -> Path | None:
        """Find a source distribution file in the specified directory.

        Args:
            dist_dir: Directory to search for .tar.gz files.

        Returns:
            Path to the first .tar.gz file found, or None if not found.
        """
        sdists = list(dist_dir.glob("*.tar.gz"))
        if not sdists:
            return None
        return sdists[0]
