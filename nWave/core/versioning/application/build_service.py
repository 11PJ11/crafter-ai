"""
BuildService - Application service for build operations.

Orchestrates the build workflow for creating custom distributions:
1. Clean dist/ directory
2. Run all tests
3. Create RC version from base version, branch, and date
4. Build distribution

HEXAGONAL ARCHITECTURE:
- This is an APPLICATION SERVICE (inside the hexagon)
- Depends only on PORT interfaces, not concrete adapters
- Uses real domain objects (RCVersion), never mocks

Example:
    >>> service = BuildService(git=adapter, test_runner=runner, file_system=fs, date_provider=dp)
    >>> result = service.build()
    >>> if result.success:
    ...     print(f"Built version {result.version}")
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import TYPE_CHECKING, Optional, Protocol

from nWave.core.versioning.domain.rc_version import RCVersion

if TYPE_CHECKING:
    pass


@dataclass(frozen=True)
class BuildResult:
    """
    Result of a build operation.

    Contains the build outcome and metadata for display.

    Attributes:
        success: True if build completed successfully
        version: The RC version string (e.g., "1.2.3-rc.main.20260127.1")
        dist_cleaned: True if dist/ was cleaned before build
        tests_passed: True if all tests passed
        distribution_created: True if distribution was created in dist/
        error_message: Optional error message if build failed
    """

    success: bool
    version: Optional[str]
    dist_cleaned: bool
    tests_passed: bool
    distribution_created: bool
    error_message: Optional[str] = None


class GitProtocol(Protocol):
    """Protocol for Git operations."""

    def get_current_branch(self) -> str: ...
    def has_uncommitted_changes(self) -> bool: ...


class TestRunnerProtocol(Protocol):
    """Protocol for test runner operations."""

    def run_tests(self) -> tuple[bool, int]: ...


class FileSystemProtocol(Protocol):
    """Protocol for file system operations for build."""

    def read_base_version(self) -> str: ...
    def clean_dist(self) -> bool: ...
    def create_distribution(self, version: str) -> bool: ...
    def get_previous_build_version(self) -> Optional[str]: ...


class DateProviderProtocol(Protocol):
    """Protocol for date provider."""

    def today(self) -> date: ...


class BuildService:
    """
    Application service for build operations.

    Orchestrates the build workflow:
    1. Clean dist/ directory
    2. Run all tests
    3. Create RC version from base version, branch, and date
    4. Build distribution in dist/

    Example:
        >>> service = BuildService(git=adapter, test_runner=runner, file_system=fs, date_provider=dp)
        >>> result = service.build()
        >>> if result.success:
        ...     print(f"Built {result.version}")
    """

    def __init__(
        self,
        git: GitProtocol,
        test_runner: TestRunnerProtocol,
        file_system: FileSystemProtocol,
        date_provider: DateProviderProtocol,
    ) -> None:
        """
        Create a BuildService.

        Args:
            git: Adapter implementing GitPort
            test_runner: Adapter for running tests
            file_system: Adapter implementing file system operations
            date_provider: Provider for current date
        """
        self._git = git
        self._test_runner = test_runner
        self._file_system = file_system
        self._date_provider = date_provider

    def build(self) -> BuildResult:
        """
        Execute the build workflow.

        Workflow:
        1. Clean dist/ directory
        2. Run all tests (abort if any fail)
        3. Create RC version from base version + branch + date
        4. Build distribution in dist/

        Returns:
            BuildResult with success status and version info
        """
        # Step 1: Clean dist/ directory
        dist_cleaned = self._file_system.clean_dist()

        # Step 2: Run all tests
        tests_passed, failure_count = self._test_runner.run_tests()
        if not tests_passed:
            return BuildResult(
                success=False,
                version=None,
                dist_cleaned=dist_cleaned,
                tests_passed=False,
                distribution_created=False,
                error_message=f"Build failed: {failure_count} test failures. Fix tests before building.",
            )

        # Step 3: Create RC version
        base_version = self._file_system.read_base_version()
        branch = self._git.get_current_branch()
        today = self._date_provider.today()

        # Calculate build number based on previous build
        build_number = self._calculate_build_number(base_version, branch, today)

        rc_version = RCVersion.create(
            base_version=base_version,
            branch=branch,
            build_date=today,
            build_number=build_number,
        )

        version_string = str(rc_version)

        # Step 4: Create distribution
        distribution_created = self._file_system.create_distribution(version_string)

        return BuildResult(
            success=True,
            version=version_string,
            dist_cleaned=dist_cleaned,
            tests_passed=True,
            distribution_created=distribution_created,
        )

    def _calculate_build_number(
        self, base_version: str, branch: str, today: date
    ) -> int:
        """
        Calculate the build number for the current build.

        If a previous build exists from the same day, branch, and base version,
        increment the build number. Otherwise, start at 1.

        Args:
            base_version: The base semantic version
            branch: The current git branch
            today: Today's date

        Returns:
            The build number to use for this build
        """
        previous_version = self._file_system.get_previous_build_version()

        if previous_version is None:
            return 1

        try:
            previous_rc = RCVersion.parse(previous_version)
        except ValueError:
            return 1

        if self._is_same_build_context(previous_rc, base_version, branch, today):
            return previous_rc.build_number + 1

        return 1

    def _is_same_build_context(
        self,
        previous_rc: RCVersion,
        base_version: str,
        branch: str,
        today: date,
    ) -> bool:
        """
        Check if the previous build was in the same context as the current build.

        Same context means same base version, branch, and date.

        Args:
            previous_rc: The previous RC version
            base_version: The current base version
            branch: The current branch
            today: Today's date

        Returns:
            True if the previous build was in the same context
        """
        normalized_branch = RCVersion._normalize_branch_name(branch)
        return (
            previous_rc.base_version == base_version
            and previous_rc.branch == normalized_branch
            and previous_rc.build_date == today
        )
