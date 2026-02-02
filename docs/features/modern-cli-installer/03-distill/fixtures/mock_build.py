"""
Mock BuildPort for Acceptance Tests
===================================

Provides controlled build behavior for testing wheel creation
without actually running python -m build.

Port Interface: nWave/core/installer/ports/build_port.py
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Protocol


@dataclass(frozen=True)
class BuildWheelResult:
    """Result of wheel build operation."""
    success: bool
    wheel_path: Optional[Path]
    error_message: Optional[str] = None
    duration_seconds: float = 2.3


class BuildPort(Protocol):
    """
    Port interface for build operations (python -m build).

    Abstracts build commands for testability.
    """

    def is_available(self) -> bool:
        """Check if build package is available."""
        ...

    def get_version(self) -> str:
        """Get build package version."""
        ...

    def build_wheel(
        self,
        output_dir: Path = Path("dist"),
    ) -> BuildWheelResult:
        """Build wheel in output directory."""
        ...

    def clean_dist(self, dist_dir: Path = Path("dist")) -> bool:
        """Clean dist directory."""
        ...


@dataclass
class MockBuildAdapter:
    """
    Mock implementation of BuildPort for testing.

    Provides controlled build behavior for wheel creation tests.
    """

    # Build package availability
    available: bool = True
    version: str = "1.2.1"

    # Build result configuration
    fail_build: bool = False
    fail_build_message: str = "Invalid entry point configuration"

    # Expected wheel path
    wheel_path: str = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl"

    # Build metrics
    build_duration: float = 2.3
    files_processed: int = 127

    # Call tracking
    build_calls: List[Path] = field(default_factory=list)
    clean_calls: List[Path] = field(default_factory=list)

    # Old wheels in dist
    old_wheels: List[str] = field(default_factory=list)

    def is_available(self) -> bool:
        """Return configured availability."""
        return self.available

    def get_version(self) -> str:
        """Return configured version."""
        return self.version

    def build_wheel(
        self,
        output_dir: Path = Path("dist"),
    ) -> BuildWheelResult:
        """Simulate wheel build."""
        self.build_calls.append(output_dir)

        if self.fail_build:
            return BuildWheelResult(
                success=False,
                wheel_path=None,
                error_message=self.fail_build_message,
                duration_seconds=self.build_duration,
            )

        return BuildWheelResult(
            success=True,
            wheel_path=Path(self.wheel_path),
            duration_seconds=self.build_duration,
        )

    def clean_dist(self, dist_dir: Path = Path("dist")) -> bool:
        """Simulate cleaning dist directory."""
        self.clean_calls.append(dist_dir)
        cleaned = len(self.old_wheels)
        self.old_wheels.clear()
        return cleaned > 0

    # Test setup helpers

    def setup_available(self, version: str = "1.2.1") -> None:
        """Configure build package as available."""
        self.available = True
        self.version = version

    def setup_unavailable(self) -> None:
        """Configure build package as unavailable."""
        self.available = False

    def setup_build_success(
        self,
        wheel_path: str = "dist/nwave-1.3.0-dev-20260201-001-py3-none-any.whl",
        duration: float = 2.3
    ) -> None:
        """Configure mock for successful build."""
        self.fail_build = False
        self.wheel_path = wheel_path
        self.build_duration = duration

    def setup_build_failure(self, message: str = "Invalid entry point configuration") -> None:
        """Configure mock to fail build."""
        self.fail_build = True
        self.fail_build_message = message

    def setup_old_wheels(self, wheel_paths: List[str]) -> None:
        """Configure mock with old wheels to clean."""
        self.old_wheels = wheel_paths.copy()

    def setup_invalid_entry_point(self) -> None:
        """Configure mock to fail with entry point error."""
        self.fail_build = True
        self.fail_build_message = (
            "ERROR: Invalid entry point configuration\n"
            "  [project.scripts]\n"
            "  nw = 'nWave.cli:main'  # Module 'nWave.cli' not found"
        )

    def setup_syntax_error(self, line: int = 42) -> None:
        """Configure mock to fail with syntax error."""
        self.fail_build = True
        self.fail_build_message = (
            f"ERROR: pyproject.toml syntax error\n"
            f"  Line {line}: unexpected token"
        )

    def get_build_count(self) -> int:
        """Get number of build calls."""
        return len(self.build_calls)

    def get_clean_count(self) -> int:
        """Get number of clean calls."""
        return len(self.clean_calls)

    def assert_build_called(self) -> None:
        """Assert build was called at least once."""
        assert len(self.build_calls) > 0, "Build was never called"

    def assert_clean_called(self) -> None:
        """Assert clean was called at least once."""
        assert len(self.clean_calls) > 0, "Clean was never called"


@dataclass
class WheelValidationResult:
    """Result of wheel validation."""
    wheel_path: Path
    is_valid: bool
    format_valid: bool = True
    metadata_valid: bool = True
    entry_points_valid: bool = True
    agents_count: int = 47
    commands_count: int = 23
    templates_count: int = 12
    pipx_compatible: bool = True
    error_message: Optional[str] = None


@dataclass
class MockWheelValidator:
    """
    Mock wheel validator for testing wheel validation scenarios.
    """

    # Validation results
    fail_validation: bool = False
    fail_message: str = "Wheel validation failed"

    # Component counts
    agents_count: int = 47
    commands_count: int = 23
    templates_count: int = 12

    # Individual check failures
    fail_format: bool = False
    fail_metadata: bool = False
    fail_entry_points: bool = False
    fail_pipx_compatible: bool = False

    def validate(self, wheel_path: Path) -> WheelValidationResult:
        """Validate wheel file."""
        if self.fail_validation:
            return WheelValidationResult(
                wheel_path=wheel_path,
                is_valid=False,
                error_message=self.fail_message,
            )

        return WheelValidationResult(
            wheel_path=wheel_path,
            is_valid=not any([
                self.fail_format,
                self.fail_metadata,
                self.fail_entry_points,
                self.fail_pipx_compatible,
            ]),
            format_valid=not self.fail_format,
            metadata_valid=not self.fail_metadata,
            entry_points_valid=not self.fail_entry_points,
            agents_count=self.agents_count,
            commands_count=self.commands_count,
            templates_count=self.templates_count,
            pipx_compatible=not self.fail_pipx_compatible,
        )

    def setup_missing_agents(self) -> None:
        """Configure validator to report missing agents."""
        self.agents_count = 0
        self.fail_validation = True
        self.fail_message = "Agents bundled [x] 0 found"

    def setup_missing_entry_points(self) -> None:
        """Configure validator to report missing entry points."""
        self.fail_entry_points = True
        self.fail_validation = True
        self.fail_message = "Entry points [x] nw CLI not found"


def create_build_mock_available() -> MockBuildAdapter:
    """Factory: Create mock with build package available."""
    mock = MockBuildAdapter()
    mock.setup_available()
    return mock


def create_build_mock_unavailable() -> MockBuildAdapter:
    """Factory: Create mock with build package unavailable."""
    mock = MockBuildAdapter()
    mock.setup_unavailable()
    return mock
