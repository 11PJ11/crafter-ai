"""WheelValidationService for validating wheel files before installation.

This module provides services for validating wheel file integrity, format,
and extracting metadata like version and package name from wheel filenames.
Follows PEP 427 wheel filename format specification.
"""

import re
import zipfile
from dataclasses import dataclass
from pathlib import Path

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


# PEP 427 wheel filename pattern: {distribution}-{version}(-{build tag})?-{python tag}-{abi tag}-{platform tag}.whl
# Simplified pattern for common wheels
WHEEL_FILENAME_PATTERN = re.compile(
    r"^(?P<name>[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?)-"
    r"(?P<version>[A-Za-z0-9_.!+]+)-"
    r"(?P<python>[A-Za-z0-9_.]+)-"
    r"(?P<abi>[A-Za-z0-9_.]+)-"
    r"(?P<platform>[A-Za-z0-9_.]+)\.whl$"
)


@dataclass(frozen=True)
class WheelValidationResult:
    """Immutable result of wheel validation.

    Attributes:
        wheel_path: Path to the wheel file that was validated.
        is_valid: Whether the wheel passed all validation checks.
        version: Version extracted from wheel filename, None if parsing failed.
        package_name: Package name extracted from wheel filename, None if parsing failed.
        errors: List of validation error messages, empty if valid.
    """

    wheel_path: Path
    is_valid: bool
    version: str | None
    package_name: str | None
    errors: list[str]


class WheelValidationService:
    """Service for validating wheel files before installation.

    Validates wheel files for:
    - File existence
    - Correct .whl extension
    - Valid PEP 427 filename format
    - Valid zip file structure

    Also extracts metadata from wheel filenames.
    """

    def validate(self, wheel_path: Path) -> WheelValidationResult:
        """Perform full validation of a wheel file.

        Args:
            wheel_path: Path to the wheel file to validate.

        Returns:
            WheelValidationResult with validation outcome and extracted metadata.
        """
        errors: list[str] = []

        # Check file exists
        exists_check = self.validate_wheel_exists(wheel_path)
        if not exists_check.passed:
            errors.append(exists_check.message)
            return WheelValidationResult(
                wheel_path=wheel_path,
                is_valid=False,
                version=None,
                package_name=None,
                errors=errors,
            )

        # Check extension
        if wheel_path.suffix.lower() != ".whl":
            errors.append(f"File must have .whl extension, got '{wheel_path.suffix}'")
            return WheelValidationResult(
                wheel_path=wheel_path,
                is_valid=False,
                version=None,
                package_name=None,
                errors=errors,
            )

        # Check filename format
        format_check = self.validate_wheel_format(wheel_path)
        if not format_check.passed:
            errors.append(format_check.message)

        # Check valid zip
        if not self._is_valid_zip(wheel_path):
            errors.append("File is not a valid zip archive")

        # Extract metadata
        version = self.extract_version_from_wheel(wheel_path)
        package_name = self.extract_package_name_from_wheel(wheel_path)

        is_valid = len(errors) == 0

        return WheelValidationResult(
            wheel_path=wheel_path,
            is_valid=is_valid,
            version=version,
            package_name=package_name,
            errors=errors,
        )

    def validate_wheel_exists(self, wheel_path: Path) -> CheckResult:
        """Check that the wheel file exists.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether the file exists.
        """
        if wheel_path.exists():
            return CheckResult(
                id="wheel_exists",
                name="Wheel File Exists",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message=f"Wheel file exists at {wheel_path}",
            )
        else:
            return CheckResult(
                id="wheel_exists",
                name="Wheel File Exists",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Wheel file does not exist at {wheel_path}",
                remediation="Ensure the wheel file path is correct and the file has been built",
            )

    def validate_wheel_format(self, wheel_path: Path) -> CheckResult:
        """Check that the wheel filename follows PEP 427 format.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether the filename format is valid.
        """
        filename = wheel_path.name
        match = WHEEL_FILENAME_PATTERN.match(filename)

        if match:
            return CheckResult(
                id="wheel_format",
                name="Wheel Filename Format",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message=f"Wheel filename '{filename}' follows PEP 427 format",
            )
        else:
            return CheckResult(
                id="wheel_format",
                name="Wheel Filename Format",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Wheel filename pattern is invalid: '{filename}'. "
                "Expected format: {{name}}-{{version}}-{{python}}-{{abi}}-{{platform}}.whl",
                remediation="Rebuild the wheel with a valid filename format",
            )

    def extract_version_from_wheel(self, wheel_path: Path) -> str | None:
        """Extract version string from wheel filename.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            Version string if successfully extracted, None otherwise.
        """
        match = WHEEL_FILENAME_PATTERN.match(wheel_path.name)
        if match:
            return match.group("version")
        return None

    def extract_package_name_from_wheel(self, wheel_path: Path) -> str | None:
        """Extract package name from wheel filename.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            Package name if successfully extracted, None otherwise.
        """
        match = WHEEL_FILENAME_PATTERN.match(wheel_path.name)
        if match:
            return match.group("name")
        return None

    def _is_valid_zip(self, wheel_path: Path) -> bool:
        """Check if the file is a valid zip archive.

        Args:
            wheel_path: Path to the file to check.

        Returns:
            True if the file is a valid zip, False otherwise.
        """
        return zipfile.is_zipfile(wheel_path)
