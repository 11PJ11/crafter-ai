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

import pytest
from datetime import date
from unittest.mock import Mock, MagicMock


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
