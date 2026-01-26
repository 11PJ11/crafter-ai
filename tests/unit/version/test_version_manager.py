"""
Unit tests for VersionManager - Step 02-01: Display version when up to date.

Test Coverage:
- Reading local version from VERSION file
- Comparing with remote version
- Determining if system is up to date
- Displaying appropriate message
"""

import pytest


class TestVersionManagerShould:
    """Unit tests for VersionManager behavior."""

    def test_read_local_version_from_version_file(self, tmp_path):
        """
        GIVEN a VERSION file exists with version 1.5.7
        WHEN VersionManager reads the local version
        THEN it returns '1.5.7'
        """
        # Arrange
        from src.nwave.version.version_manager import VersionManager

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.5.7\n")

        manager = VersionManager(version_file_path=version_file)

        # Act
        local_version = manager.get_local_version()

        # Assert
        assert local_version == "1.5.7"

    def test_determine_up_to_date_when_versions_match(self, tmp_path):
        """
        GIVEN local version is 1.5.7
        AND remote version is 1.5.7
        WHEN checking for updates
        THEN system determines it is up to date
        """
        # Arrange
        from src.nwave.version.version_manager import VersionManager

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.5.7")

        manager = VersionManager(version_file_path=version_file)

        # Act
        is_up_to_date = manager.is_up_to_date(remote_version="1.5.7")

        # Assert
        assert is_up_to_date is True

    def test_determine_update_available_when_versions_differ(self, tmp_path):
        """
        GIVEN local version is 1.5.7
        AND remote version is 1.6.0
        WHEN checking for updates
        THEN system determines update is available
        """
        # Arrange
        from src.nwave.version.version_manager import VersionManager

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.5.7")

        manager = VersionManager(version_file_path=version_file)

        # Act
        is_up_to_date = manager.is_up_to_date(remote_version="1.6.0")

        # Assert
        assert is_up_to_date is False

    def test_format_up_to_date_message(self, tmp_path):
        """
        GIVEN local version is 1.5.7
        AND system is up to date
        WHEN formatting the display message
        THEN it returns 'nWave v1.5.7 (up to date)'
        """
        # Arrange
        from src.nwave.version.version_manager import VersionManager

        version_file = tmp_path / "VERSION"
        version_file.write_text("1.5.7")

        manager = VersionManager(version_file_path=version_file)

        # Act
        message = manager.format_status_message(is_up_to_date=True)

        # Assert
        assert message == "nWave v1.5.7 (up to date)"

    def test_raise_error_when_version_file_missing(self, tmp_path):
        """
        GIVEN VERSION file does not exist
        WHEN VersionManager attempts to read local version
        THEN it raises FileNotFoundError
        """
        # Arrange
        from src.nwave.version.version_manager import VersionManager

        non_existent_file = tmp_path / "VERSION"
        manager = VersionManager(version_file_path=non_existent_file)

        # Act & Assert
        with pytest.raises(FileNotFoundError):
            manager.get_local_version()
