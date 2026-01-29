"""
Unit tests for BuildService application service.

Tests for Step 05-01: Successful build with install prompt on main branch

BuildService orchestrates the build workflow:
1. Clean dist/ directory
2. Run tests
3. Create RC version
4. Build distribution

HEXAGONAL ARCHITECTURE:
- BuildService is an APPLICATION SERVICE (inside the hexagon)
- Uses real domain objects (RCVersion), never mocks them
- Mocks allowed ONLY for ports (GitPort, FileSystemPort, TestRunnerPort)
"""

from datetime import date
from unittest.mock import Mock


class TestBuildServiceCleansDistBeforeBuild:
    """Test that BuildService cleans dist/ directory before building."""

    def test_build_service_cleans_dist_before_build(self):
        """
        GIVEN a BuildService with configured dependencies
        WHEN build() is called
        THEN the dist/ directory is cleaned before any other operation
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        mock_file_system.get_previous_build_version.return_value = (
            None  # No previous build
        )

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        mock_file_system.clean_dist.assert_called_once()
        assert result.dist_cleaned is True


class TestBuildServiceRunsTestsFirst:
    """Test that BuildService runs tests before building."""

    def test_build_service_runs_tests_first(self):
        """
        GIVEN a BuildService with configured dependencies
        WHEN build() is called
        THEN tests are run before creating the distribution
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        mock_file_system.get_previous_build_version.return_value = None

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        mock_test_runner.run_tests.assert_called_once()
        assert result.tests_passed is True


class TestBuildServiceCreatesDistribution:
    """Test that BuildService creates distribution in dist/."""

    def test_build_service_creates_distribution(self):
        """
        GIVEN a BuildService with all tests passing
        WHEN build() is called
        THEN a distribution is created in dist/ directory
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        mock_file_system.get_previous_build_version.return_value = None

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        mock_file_system.create_distribution.assert_called_once()
        assert result.distribution_created is True


class TestBuildServiceCreatesRCVersion:
    """Test that BuildService creates proper RC version."""

    def test_build_service_creates_rc_version(self):
        """
        GIVEN a BuildService on main branch with base version 1.2.3
        AND today's date is 2026-01-27
        WHEN build() is called
        THEN the version is "1.2.3-rc.main.20260127.1"
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        mock_file_system.get_previous_build_version.return_value = None

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        assert result.version == "1.2.3-rc.main.20260127.1"


# =============================================================================
# Step 05-02: Build fails when tests fail
# =============================================================================


class TestBuildServiceAbortsOnTestFailure:
    """Test that BuildService aborts build when tests fail."""

    def test_build_service_aborts_on_test_failure(self):
        """
        GIVEN a BuildService with configured dependencies
        AND tests fail when run
        WHEN build() is called
        THEN the build returns failure status
        AND no distribution is created
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (False, 3)  # 3 test failures

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        assert result.success is False, "Expected build to fail when tests fail"
        assert result.tests_passed is False, "Expected tests_passed to be False"
        mock_file_system.create_distribution.assert_not_called()


class TestBuildServiceReportsFailureCount:
    """Test that BuildService reports test failure count in error message."""

    def test_build_service_reports_failure_count(self):
        """
        GIVEN a BuildService with configured dependencies
        AND 3 tests fail when run
        WHEN build() is called
        THEN the error message includes the failure count
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (False, 3)  # 3 test failures

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        expected_message = "Build failed: 3 test failures. Fix tests before building."
        assert (
            result.error_message == expected_message
        ), f"Expected error message '{expected_message}', got: {result.error_message}"


class TestDistUnchangedOnTestFailure:
    """Test that dist/ directory is unchanged when tests fail."""

    def test_dist_unchanged_on_test_failure(self):
        """
        GIVEN a BuildService with configured dependencies
        AND tests fail when run
        WHEN build() is called
        THEN create_distribution is never called
        AND distribution_created is False
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (False, 5)  # 5 test failures

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        mock_file_system.create_distribution.assert_not_called()
        assert (
            result.distribution_created is False
        ), "Expected distribution_created to be False when tests fail"
        assert result.version is None, "Expected version to be None when build fails"


# =============================================================================
# Step 05-03: RC counter increments on same day builds
# =============================================================================


class TestBuildServiceIncrementsCounterSameDay:
    """Test that BuildService increments counter for same-day builds."""

    def test_build_service_increments_counter_same_day(self):
        """
        GIVEN a previous build version "1.2.3-rc.main.20260127.1" exists
        AND today's date is 2026-01-27 (same day)
        WHEN build() is called
        THEN the version becomes "1.2.3-rc.main.20260127.2" (counter incremented)
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        # Configure previous build
        mock_file_system.get_previous_build_version.return_value = (
            "1.2.3-rc.main.20260127.1"
        )

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        assert (
            result.version == "1.2.3-rc.main.20260127.2"
        ), f"Expected counter to increment from .1 to .2, got: {result.version}"


class TestBuildServiceDetectsExistingBuild:
    """Test that BuildService detects existing builds for counter calculation."""

    def test_build_service_detects_existing_build(self):
        """
        GIVEN a previous build version exists in dist/
        WHEN build() is called
        THEN the file system is queried for the previous build version
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        mock_file_system.get_previous_build_version.return_value = (
            "1.2.3-rc.main.20260127.1"
        )

        mock_date_provider = Mock()
        mock_date_provider.today.return_value = date(2026, 1, 27)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        service.build()

        # Assert
        mock_file_system.get_previous_build_version.assert_called_once()


class TestRCVersionIncrementsBuildNumber:
    """Test that RCVersion domain object can increment build number."""

    def test_rc_version_increments_build_number(self):
        """
        GIVEN an RCVersion with build_number 1
        WHEN increment_build_number() is called
        THEN a new RCVersion with build_number 2 is returned
        """
        # Arrange
        from nWave.core.versioning.domain.rc_version import RCVersion

        rc_version = RCVersion.create(
            base_version="1.2.3",
            branch="main",
            build_date=date(2026, 1, 27),
            build_number=1,
        )

        # Act
        incremented = rc_version.increment_build_number()

        # Assert
        assert incremented.build_number == 2
        assert str(incremented) == "1.2.3-rc.main.20260127.2"


# =============================================================================
# Step 05-04: RC counter resets on new day
# =============================================================================


class TestBuildServiceResetsCounterOnNewDay:
    """Test that BuildService resets counter when building on a new day."""

    def test_build_service_resets_counter_new_day(self):
        """
        GIVEN a previous build version "1.2.3-rc.main.20260127.3" exists
        AND today's date is 2026-01-28 (different day)
        WHEN build() is called
        THEN the version becomes "1.2.3-rc.main.20260128.1" (counter reset to 1)
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        # Configure previous build from yesterday (day 27)
        mock_file_system.get_previous_build_version.return_value = (
            "1.2.3-rc.main.20260127.3"
        )

        mock_date_provider = Mock()
        # Today is day 28 (different from previous build)
        mock_date_provider.today.return_value = date(2026, 1, 28)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert
        assert (
            result.version == "1.2.3-rc.main.20260128.1"
        ), f"Expected counter to reset to .1 on new day, got: {result.version}"


class TestBuildServiceDetectsDateChange:
    """Test that BuildService detects date change between builds."""

    def test_build_service_detects_date_change(self):
        """
        GIVEN a previous build from a different day
        WHEN build() is called
        THEN the counter is reset instead of incremented
        """
        # Arrange
        from nWave.core.versioning.application.build_service import BuildService

        mock_git = Mock()
        mock_git.get_current_branch.return_value = "main"

        mock_test_runner = Mock()
        mock_test_runner.run_tests.return_value = (True, 0)

        mock_file_system = Mock()
        mock_file_system.read_base_version.return_value = "1.2.3"
        mock_file_system.clean_dist.return_value = True
        mock_file_system.create_distribution.return_value = True
        # Previous build was on 2026-01-25 with build number 5
        mock_file_system.get_previous_build_version.return_value = (
            "1.2.3-rc.main.20260125.5"
        )

        mock_date_provider = Mock()
        # Today is 2026-01-28
        mock_date_provider.today.return_value = date(2026, 1, 28)

        service = BuildService(
            git=mock_git,
            test_runner=mock_test_runner,
            file_system=mock_file_system,
            date_provider=mock_date_provider,
        )

        # Act
        result = service.build()

        # Assert - counter resets to 1, NOT continues from 5
        assert (
            result.version == "1.2.3-rc.main.20260128.1"
        ), f"Expected counter to reset to .1 (not continue from .5), got: {result.version}"


class TestRCVersionParseExtractsDate:
    """Test that RCVersion.parse correctly extracts date from version string."""

    def test_rc_version_parse_extracts_date(self):
        """
        GIVEN a version string "1.2.3-rc.main.20260127.3"
        WHEN RCVersion.parse() is called
        THEN the build_date is 2026-01-27
        """
        # Arrange
        from nWave.core.versioning.domain.rc_version import RCVersion

        version_string = "1.2.3-rc.main.20260127.3"

        # Act
        rc_version = RCVersion.parse(version_string)

        # Assert
        assert rc_version.build_date == date(2026, 1, 27)
        assert rc_version.build_number == 3
