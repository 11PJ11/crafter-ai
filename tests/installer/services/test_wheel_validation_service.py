"""Tests for WheelValidationService.

This module tests the wheel validation service that validates wheel files
before installation, checking file existence, format, and extracting metadata.
"""

import zipfile
from pathlib import Path

import pytest

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.services.wheel_validation_service import (
    WheelValidationResult,
    WheelValidationService,
)


class TestWheelValidationResult:
    """Tests for WheelValidationResult dataclass."""

    def test_creation_with_valid_wheel(self) -> None:
        """Test WheelValidationResult can be created with valid wheel data."""
        result = WheelValidationResult(
            wheel_path=Path("/path/to/wheel.whl"),
            is_valid=True,
            version="1.0.0",
            package_name="my_package",
            errors=[],
        )

        assert result.wheel_path == Path("/path/to/wheel.whl")
        assert result.is_valid is True
        assert result.version == "1.0.0"
        assert result.package_name == "my_package"
        assert result.errors == []

    def test_creation_with_invalid_wheel(self) -> None:
        """Test WheelValidationResult can represent invalid wheel."""
        validation_errors = ["File does not exist", "Invalid format"]
        result = WheelValidationResult(
            wheel_path=Path("/path/to/invalid.whl"),
            is_valid=False,
            version=None,
            package_name=None,
            errors=validation_errors,
        )

        assert result.is_valid is False
        assert result.version is None
        assert result.package_name is None
        assert len(result.errors) == len(validation_errors)

    def test_is_frozen(self) -> None:
        """Test WheelValidationResult is immutable (frozen dataclass)."""
        result = WheelValidationResult(
            wheel_path=Path("/path/to/wheel.whl"),
            is_valid=True,
            version="1.0.0",
            package_name="my_package",
            errors=[],
        )

        with pytest.raises(AttributeError):
            result.is_valid = False  # type: ignore[misc]


class TestWheelValidationService:
    """Tests for WheelValidationService."""

    @pytest.fixture
    def service(self) -> WheelValidationService:
        """Create a WheelValidationService instance."""
        return WheelValidationService()

    @pytest.fixture
    def valid_wheel(self, tmp_path: Path) -> Path:
        """Create a valid wheel file for testing."""
        wheel_name = "crafter_ai-1.2.3-py3-none-any.whl"
        wheel_path = tmp_path / wheel_name
        # Create a valid zip file (wheels are zip files)
        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("crafter_ai/__init__.py", "")
        return wheel_path

    @pytest.fixture
    def invalid_wheel_name(self, tmp_path: Path) -> Path:
        """Create a wheel file with invalid naming pattern."""
        wheel_path = tmp_path / "invalid_name.whl"
        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("dummy.py", "")
        return wheel_path

    @pytest.fixture
    def non_zip_wheel(self, tmp_path: Path) -> Path:
        """Create a file with .whl extension that is not a valid zip."""
        wheel_path = tmp_path / "crafter_ai-1.0.0-py3-none-any.whl"
        wheel_path.write_text("not a zip file")
        return wheel_path

    # Tests for validate method
    def test_validate_returns_valid_result_for_correct_wheel(
        self, service: WheelValidationService, valid_wheel: Path
    ) -> None:
        """Test validate returns valid result for a properly formatted wheel."""
        result = service.validate(valid_wheel)

        assert result.is_valid is True
        assert result.wheel_path == valid_wheel
        assert result.version == "1.2.3"
        assert result.package_name == "crafter_ai"
        assert result.errors == []

    def test_validate_returns_invalid_for_non_existent_file(
        self, service: WheelValidationService, tmp_path: Path
    ) -> None:
        """Test validate returns invalid for non-existent file."""
        non_existent = tmp_path / "does_not_exist.whl"

        result = service.validate(non_existent)

        assert result.is_valid is False
        assert "does not exist" in result.errors[0].lower()

    def test_validate_returns_invalid_for_wrong_extension(
        self, service: WheelValidationService, tmp_path: Path
    ) -> None:
        """Test validate returns invalid for file without .whl extension."""
        wrong_ext = tmp_path / "package.tar.gz"
        wrong_ext.touch()

        result = service.validate(wrong_ext)

        assert result.is_valid is False
        assert any(".whl" in err for err in result.errors)

    def test_validate_returns_invalid_for_invalid_filename_pattern(
        self, service: WheelValidationService, invalid_wheel_name: Path
    ) -> None:
        """Test validate returns invalid for wheel with incorrect filename pattern."""
        result = service.validate(invalid_wheel_name)

        assert result.is_valid is False
        assert any("filename pattern" in err.lower() for err in result.errors)

    def test_validate_returns_invalid_for_non_zip_file(
        self, service: WheelValidationService, non_zip_wheel: Path
    ) -> None:
        """Test validate returns invalid for file that is not a valid zip."""
        result = service.validate(non_zip_wheel)

        assert result.is_valid is False
        assert any("zip" in err.lower() for err in result.errors)

    # Tests for validate_wheel_exists
    def test_validate_wheel_exists_passes_for_existing_file(
        self, service: WheelValidationService, valid_wheel: Path
    ) -> None:
        """Test validate_wheel_exists passes for existing wheel file."""
        result = service.validate_wheel_exists(valid_wheel)

        assert isinstance(result, CheckResult)
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING

    def test_validate_wheel_exists_fails_for_non_existent_file(
        self, service: WheelValidationService, tmp_path: Path
    ) -> None:
        """Test validate_wheel_exists fails for non-existent file."""
        non_existent = tmp_path / "missing.whl"

        result = service.validate_wheel_exists(non_existent)

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING

    # Tests for validate_wheel_format
    def test_validate_wheel_format_passes_for_valid_name(
        self, service: WheelValidationService, valid_wheel: Path
    ) -> None:
        """Test validate_wheel_format passes for valid wheel filename."""
        result = service.validate_wheel_format(valid_wheel)

        assert isinstance(result, CheckResult)
        assert result.passed is True

    def test_validate_wheel_format_fails_for_invalid_name(
        self, service: WheelValidationService, invalid_wheel_name: Path
    ) -> None:
        """Test validate_wheel_format fails for invalid filename pattern."""
        result = service.validate_wheel_format(invalid_wheel_name)

        assert result.passed is False

    # Tests for extract_version_from_wheel
    def test_extract_version_from_wheel_parses_correctly(
        self, service: WheelValidationService, valid_wheel: Path
    ) -> None:
        """Test extract_version_from_wheel extracts version from filename."""
        version = service.extract_version_from_wheel(valid_wheel)

        assert version == "1.2.3"

    def test_extract_version_from_wheel_returns_none_for_invalid(
        self, service: WheelValidationService, invalid_wheel_name: Path
    ) -> None:
        """Test extract_version_from_wheel returns None for invalid filename."""
        version = service.extract_version_from_wheel(invalid_wheel_name)

        assert version is None

    # Tests for extract_package_name_from_wheel
    def test_extract_package_name_from_wheel_parses_correctly(
        self, service: WheelValidationService, valid_wheel: Path
    ) -> None:
        """Test extract_package_name_from_wheel extracts name from filename."""
        name = service.extract_package_name_from_wheel(valid_wheel)

        assert name == "crafter_ai"

    def test_extract_package_name_from_wheel_returns_none_for_invalid(
        self, service: WheelValidationService, invalid_wheel_name: Path
    ) -> None:
        """Test extract_package_name_from_wheel returns None for invalid filename."""
        name = service.extract_package_name_from_wheel(invalid_wheel_name)

        assert name is None

    # Additional edge cases
    def test_extract_version_handles_complex_version(
        self, service: WheelValidationService, tmp_path: Path
    ) -> None:
        """Test version extraction handles complex version strings."""
        wheel_path = tmp_path / "package-1.0.0a1.post2.dev3-py3-none-any.whl"
        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("package/__init__.py", "")

        version = service.extract_version_from_wheel(wheel_path)

        assert version == "1.0.0a1.post2.dev3"

    def test_extract_package_name_handles_hyphens_and_underscores(
        self, service: WheelValidationService, tmp_path: Path
    ) -> None:
        """Test package name extraction handles various naming conventions."""
        wheel_path = tmp_path / "my_cool_package-2.0.0-py3-none-any.whl"
        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("my_cool_package/__init__.py", "")

        name = service.extract_package_name_from_wheel(wheel_path)

        assert name == "my_cool_package"
