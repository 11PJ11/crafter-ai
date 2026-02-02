"""BuildPort Protocol - abstract interface for Python wheel building operations.

This is a hexagonal architecture port that defines how the application
builds Python packages (wheels and sdists). Adapters implement this protocol
for different build mechanisms (subprocess with python -m build, etc.).
"""

from pathlib import Path
from typing import Protocol, runtime_checkable


class BuildError(Exception):
    """Exception raised when a build operation fails.

    Attributes:
        message: Description of what went wrong.
        return_code: The subprocess return code, if applicable.
        output: Captured stderr/stdout from the build process.
    """

    def __init__(
        self,
        message: str,
        return_code: int | None = None,
        output: str | None = None,
    ) -> None:
        """Initialize BuildError.

        Args:
            message: Description of the build failure.
            return_code: The subprocess return code (optional).
            output: Captured stderr/stdout from build (optional).
        """
        super().__init__(message)
        self._message = message
        self._return_code = return_code
        self._output = output

    @property
    def message(self) -> str:
        """Return the error message."""
        return self._message

    @property
    def return_code(self) -> int | None:
        """Return the subprocess return code, or None if not applicable."""
        return self._return_code

    @property
    def output(self) -> str | None:
        """Return captured stderr/stdout, or None if not captured."""
        return self._output

    def __str__(self) -> str:
        """Return string representation including message and details."""
        parts = [self._message]
        if self._return_code is not None:
            parts.append(f"(return code: {self._return_code})")
        if self._output:
            parts.append(f"Output: {self._output}")
        return " ".join(parts)


@runtime_checkable
class BuildPort(Protocol):
    """Protocol defining build operations interface.

    This is a hexagonal port - the application depends on this interface,
    not on concrete implementations. Adapters (like SubprocessBuildAdapter)
    implement this protocol.

    Used by:
        - BuildService for creating wheel artifacts
        - InstallService for building before installation
    """

    def build_wheel(self, output_dir: Path) -> Path:
        """Build a wheel package.

        Args:
            output_dir: Directory where the wheel should be placed.

        Returns:
            Path to the built .whl file.

        Raises:
            BuildError: If the build fails.
        """
        ...

    def build_sdist(self, output_dir: Path) -> Path:
        """Build a source distribution.

        Args:
            output_dir: Directory where the sdist should be placed.

        Returns:
            Path to the built .tar.gz file.

        Raises:
            BuildError: If the build fails.
        """
        ...

    def clean_build_artifacts(self) -> None:
        """Remove build artifacts (build/, dist/, *.egg-info).

        Cleans up temporary build directories to ensure fresh builds.
        """
        ...

    def get_wheel_path(self, dist_dir: Path) -> Path | None:
        """Find a wheel file in the specified directory.

        Args:
            dist_dir: Directory to search for .whl files.

        Returns:
            Path to the .whl file, or None if not found.
        """
        ...
