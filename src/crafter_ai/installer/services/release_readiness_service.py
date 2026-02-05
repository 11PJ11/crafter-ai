"""ReleaseReadinessService for validating wheel files before PyPI release.

This module provides services for validating wheel files against PyPI release
requirements, including twine check, metadata completeness, entry points,
version format, and bundled files (LICENSE, README).
"""

import re
import subprocess
import zipfile
from dataclasses import dataclass
from pathlib import Path

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity


# PEP 440 version pattern
PEP440_PATTERN = re.compile(
    r"^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*"
    r"((a|b|rc)(0|[1-9][0-9]*))?"
    r"(\.post(0|[1-9][0-9]*))?"
    r"(\.dev(0|[1-9][0-9]*))?$"
)


@dataclass(frozen=True)
class ReleaseReadinessResult:
    """Immutable result of release readiness validation.

    Attributes:
        ready: Whether the wheel is ready for PyPI release (all blocking checks pass).
        checks: List of all individual check results.
        blocking_issues: List of blocking failure messages.
        warnings: List of non-blocking warning messages.
        status_message: Human-readable status message.
    """

    ready: bool
    checks: list[CheckResult]
    blocking_issues: list[str]
    warnings: list[str]
    status_message: str


class ReleaseReadinessService:
    """Service for validating wheel files for PyPI release readiness.

    Validates wheel files for:
    - Twine check (BLOCKING)
    - Metadata completeness (BLOCKING)
    - Entry points defined (BLOCKING)
    - PEP 440 version format (BLOCKING)
    - LICENSE file bundled (BLOCKING)
    - README file bundled (BLOCKING)
    - CHANGELOG entry (WARNING only)
    """

    def validate(
        self, wheel_path: Path, changelog_path: Path | None = None
    ) -> ReleaseReadinessResult:
        """Perform full release readiness validation of a wheel file.

        Args:
            wheel_path: Path to the wheel file to validate.
            changelog_path: Optional path to directory containing CHANGELOG.md.

        Returns:
            ReleaseReadinessResult with validation outcome.
        """
        checks: list[CheckResult] = []
        blocking_issues: list[str] = []
        warnings: list[str] = []

        # Extract version from wheel for changelog check
        version = self._extract_version_from_wheel(wheel_path)

        # Run all checks
        # 1. Twine check (BLOCKING)
        twine_result = self.run_twine_check(wheel_path)
        checks.append(twine_result)
        if not twine_result.passed:
            blocking_issues.append(twine_result.message)

        # 2. Metadata complete (BLOCKING)
        metadata_result = self.check_metadata_complete(wheel_path)
        checks.append(metadata_result)
        if not metadata_result.passed:
            blocking_issues.append(metadata_result.message)

        # 3. Entry points defined (BLOCKING)
        entry_points_result = self.check_entry_points_defined(wheel_path)
        checks.append(entry_points_result)
        if not entry_points_result.passed:
            blocking_issues.append(entry_points_result.message)

        # 4. PEP 440 version (BLOCKING)
        pep440_result = self.check_pep440_version(wheel_path)
        checks.append(pep440_result)
        if not pep440_result.passed:
            blocking_issues.append(pep440_result.message)

        # 5. LICENSE bundled (BLOCKING)
        license_result = self.check_license_bundled(wheel_path)
        checks.append(license_result)
        if not license_result.passed:
            blocking_issues.append(license_result.message)

        # 6. README bundled (BLOCKING)
        readme_result = self.check_readme_bundled(wheel_path)
        checks.append(readme_result)
        if not readme_result.passed:
            blocking_issues.append(readme_result.message)

        # 7. CHANGELOG entry (WARNING only)
        changelog_result = self.check_changelog_entry(version, changelog_path)
        checks.append(changelog_result)
        if not changelog_result.passed:
            warnings.append(changelog_result.message)

        # Determine overall readiness (only blocking issues matter)
        ready = len(blocking_issues) == 0

        if ready:
            status_message = "READY FOR PYPI"
        else:
            status_message = f"NOT READY: {len(blocking_issues)} blocking issue(s)"

        return ReleaseReadinessResult(
            ready=ready,
            checks=checks,
            blocking_issues=blocking_issues,
            warnings=warnings,
            status_message=status_message,
        )

    def run_twine_check(self, wheel_path: Path) -> CheckResult:
        """Run twine check on the wheel file.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether twine check passed.
        """
        try:
            result = subprocess.run(
                ["twine", "check", str(wheel_path)],
                capture_output=True,
                text=True,
                timeout=60,
            )

            if result.returncode == 0:
                return CheckResult(
                    id="twine_check",
                    name="Twine Check",
                    passed=True,
                    severity=CheckSeverity.BLOCKING,
                    message="Twine check passed",
                )
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return CheckResult(
                    id="twine_check",
                    name="Twine Check",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    message=f"Twine check failed: {error_msg.strip()}",
                    remediation="Fix the issues reported by twine check",
                )

        except FileNotFoundError:
            return CheckResult(
                id="twine_check",
                name="Twine Check",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Twine is not installed or not found in PATH",
                remediation="Install twine with: pip install twine",
            )
        except subprocess.TimeoutExpired:
            return CheckResult(
                id="twine_check",
                name="Twine Check",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Twine check timed out",
                remediation="Check the wheel file for issues",
            )

    def check_metadata_complete(self, wheel_path: Path) -> CheckResult:
        """Check that the wheel has complete metadata.

        Required fields: name, version, summary (description), author, license.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether metadata is complete.
        """
        required_fields = ["name", "version", "summary", "author", "license"]
        missing_fields: list[str] = []

        try:
            metadata = self._read_metadata_from_wheel(wheel_path)

            for field in required_fields:
                if field not in metadata or not metadata[field]:
                    missing_fields.append(field)

            if not missing_fields:
                return CheckResult(
                    id="metadata_complete",
                    name="Metadata Complete",
                    passed=True,
                    severity=CheckSeverity.BLOCKING,
                    message="All required metadata fields present",
                )
            else:
                return CheckResult(
                    id="metadata_complete",
                    name="Metadata Complete",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    message=f"Missing metadata fields: {', '.join(missing_fields)}",
                    remediation="Add missing fields to pyproject.toml [project] section",
                )

        except Exception as e:
            return CheckResult(
                id="metadata_complete",
                name="Metadata Complete",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Failed to read metadata: {e}",
                remediation="Ensure the wheel contains valid METADATA file",
            )

    def check_entry_points_defined(self, wheel_path: Path) -> CheckResult:
        """Check that crafter-ai CLI entry point is defined.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether entry points are defined.
        """
        try:
            entry_points = self._read_entry_points_from_wheel(wheel_path)

            if "crafter-ai" in entry_points:
                return CheckResult(
                    id="entry_points_defined",
                    name="Entry Points Defined",
                    passed=True,
                    severity=CheckSeverity.BLOCKING,
                    message="crafter-ai CLI entry point is defined",
                )
            else:
                return CheckResult(
                    id="entry_points_defined",
                    name="Entry Points Defined",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    message="crafter-ai CLI entry point not found",
                    remediation=(
                        "Add [project.scripts] crafter-ai = 'crafter_ai.cli:main' "
                        "to pyproject.toml"
                    ),
                )

        except Exception as e:
            return CheckResult(
                id="entry_points_defined",
                name="Entry Points Defined",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Failed to read entry points: {e}",
                remediation="Ensure the wheel contains entry_points.txt",
            )

    def check_pep440_version(self, wheel_path: Path) -> CheckResult:
        """Check that the version follows PEP 440 format.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether version is PEP 440 compliant.
        """
        version = self._extract_version_from_wheel(wheel_path)

        if version and PEP440_PATTERN.match(version):
            return CheckResult(
                id="pep440_version",
                name="PEP 440 Version",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message=f"Version '{version}' is PEP 440 compliant",
            )
        else:
            return CheckResult(
                id="pep440_version",
                name="PEP 440 Version",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Version '{version}' does not follow PEP 440 format",
                remediation="Use a valid PEP 440 version like '1.0.0', '1.0.0a1', '1.0.0.dev1'",
            )

    def check_license_bundled(self, wheel_path: Path) -> CheckResult:
        """Check that LICENSE file is bundled in the wheel.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether LICENSE is bundled.
        """
        try:
            with zipfile.ZipFile(wheel_path, "r") as zf:
                names = zf.namelist()
                # Look for LICENSE in dist-info directory
                has_license = any(
                    "LICENSE" in name.upper() and ".dist-info/" in name
                    for name in names
                )

                if has_license:
                    return CheckResult(
                        id="license_bundled",
                        name="LICENSE Bundled",
                        passed=True,
                        severity=CheckSeverity.BLOCKING,
                        message="LICENSE file is bundled in wheel",
                    )
                else:
                    return CheckResult(
                        id="license_bundled",
                        name="LICENSE Bundled",
                        passed=False,
                        severity=CheckSeverity.BLOCKING,
                        message="LICENSE file not found in wheel",
                        remediation="Add LICENSE file and include it in wheel via pyproject.toml",
                    )

        except Exception as e:
            return CheckResult(
                id="license_bundled",
                name="LICENSE Bundled",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Failed to check LICENSE: {e}",
            )

    def check_readme_bundled(self, wheel_path: Path) -> CheckResult:
        """Check that README content is bundled in the wheel.

        Modern wheels may include README as:
        1. A separate file in dist-info (README, README.md, README.rst, etc.)
        2. Embedded in METADATA file after the headers (Description field)

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            CheckResult indicating whether README is bundled.
        """
        try:
            with zipfile.ZipFile(wheel_path, "r") as zf:
                names = zf.namelist()
                # Method 1: Look for README file in dist-info directory
                has_readme_file = any(
                    "README" in name.upper() and ".dist-info/" in name for name in names
                )

                if has_readme_file:
                    return CheckResult(
                        id="readme_bundled",
                        name="README Bundled",
                        passed=True,
                        severity=CheckSeverity.BLOCKING,
                        message="README file is bundled in wheel",
                    )

                # Method 2: Check for embedded description in METADATA
                metadata_file = None
                for name in names:
                    if name.endswith(".dist-info/METADATA"):
                        metadata_file = name
                        break

                if metadata_file:
                    content = zf.read(metadata_file).decode("utf-8")
                    # METADATA format: headers end with blank line, then description
                    # If file is large (>2KB) it likely contains embedded description
                    # Also check for Description-Content-Type header
                    has_description_type = (
                        "description-content-type:" in content.lower()
                    )
                    # Look for content after headers (blank line followed by content)
                    parts = content.split("\n\n", 1)
                    has_description_content = (
                        len(parts) > 1 and len(parts[1].strip()) > 100
                    )

                    if has_description_type and has_description_content:
                        return CheckResult(
                            id="readme_bundled",
                            name="README Bundled",
                            passed=True,
                            severity=CheckSeverity.BLOCKING,
                            message="README content embedded in wheel METADATA",
                        )

                return CheckResult(
                    id="readme_bundled",
                    name="README Bundled",
                    passed=False,
                    severity=CheckSeverity.BLOCKING,
                    message="README file not found in wheel",
                    remediation="Add README.md and include it in wheel via pyproject.toml",
                )

        except Exception as e:
            return CheckResult(
                id="readme_bundled",
                name="README Bundled",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message=f"Failed to check README: {e}",
            )

    def check_changelog_entry(
        self, version: str | None, changelog_path: Path | None
    ) -> CheckResult:
        """Check that CHANGELOG has an entry for this version.

        This is a WARNING-level check, not blocking.

        Args:
            version: Version string to look for.
            changelog_path: Path to directory containing CHANGELOG.md.

        Returns:
            CheckResult indicating whether CHANGELOG entry exists.
        """
        if not changelog_path:
            return CheckResult(
                id="changelog_entry",
                name="CHANGELOG Entry",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="CHANGELOG path not provided",
                remediation="Provide changelog_path to validate CHANGELOG entry",
            )

        changelog_file = changelog_path / "CHANGELOG.md"
        if not changelog_file.exists():
            return CheckResult(
                id="changelog_entry",
                name="CHANGELOG Entry",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="CHANGELOG.md not found",
                remediation="Create CHANGELOG.md with version entry",
            )

        if not version:
            return CheckResult(
                id="changelog_entry",
                name="CHANGELOG Entry",
                passed=False,
                severity=CheckSeverity.WARNING,
                message="Could not determine version for CHANGELOG check",
            )

        try:
            content = changelog_file.read_text()
            # Look for version in common changelog formats like [1.2.3] or ## 1.2.3
            if version in content:
                return CheckResult(
                    id="changelog_entry",
                    name="CHANGELOG Entry",
                    passed=True,
                    severity=CheckSeverity.WARNING,
                    message=f"CHANGELOG entry found for version {version}",
                )
            else:
                return CheckResult(
                    id="changelog_entry",
                    name="CHANGELOG Entry",
                    passed=False,
                    severity=CheckSeverity.WARNING,
                    message=f"No CHANGELOG entry found for version {version}",
                    remediation=f"Add entry for [{version}] to CHANGELOG.md",
                )

        except Exception as e:
            return CheckResult(
                id="changelog_entry",
                name="CHANGELOG Entry",
                passed=False,
                severity=CheckSeverity.WARNING,
                message=f"Failed to read CHANGELOG: {e}",
            )

    def _read_metadata_from_wheel(self, wheel_path: Path) -> dict[str, str]:
        """Read METADATA from wheel file.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            Dictionary of metadata fields.
        """
        metadata: dict[str, str] = {}

        with zipfile.ZipFile(wheel_path, "r") as zf:
            # Find METADATA file in dist-info
            metadata_file = None
            for name in zf.namelist():
                if name.endswith(".dist-info/METADATA"):
                    metadata_file = name
                    break

            if not metadata_file:
                return metadata

            content = zf.read(metadata_file).decode("utf-8")

            # Parse email-style headers
            for line in content.split("\n"):
                if ":" in line and not line.startswith(" "):
                    key, _, value = line.partition(":")
                    key = key.strip().lower()
                    value = value.strip()
                    # Map common metadata fields (supporting both legacy and modern formats)
                    if key == "name":
                        metadata["name"] = value
                    elif key == "version":
                        metadata["version"] = value
                    elif key == "summary":
                        metadata["summary"] = value
                    elif key == "author":
                        metadata["author"] = value
                    elif key == "author-email" and "author" not in metadata:
                        # Modern format: Author-email: Name <email>
                        # Extract just the name part before the angle bracket
                        if "<" in value:
                            metadata["author"] = value.split("<")[0].strip()
                        else:
                            metadata["author"] = value
                    elif key == "license":
                        metadata["license"] = value
                    elif key == "license-expression" and "license" not in metadata:
                        # Modern format: License-Expression: MIT
                        metadata["license"] = value

        return metadata

    def _read_entry_points_from_wheel(self, wheel_path: Path) -> dict[str, str]:
        """Read entry points from wheel file.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            Dictionary mapping entry point names to their values.
        """
        entry_points: dict[str, str] = {}

        with zipfile.ZipFile(wheel_path, "r") as zf:
            # Find entry_points.txt in dist-info
            entry_points_file = None
            for name in zf.namelist():
                if name.endswith(".dist-info/entry_points.txt"):
                    entry_points_file = name
                    break

            if not entry_points_file:
                return entry_points

            content = zf.read(entry_points_file).decode("utf-8")

            # Parse INI-style entry points
            in_console_scripts = False
            for line in content.split("\n"):
                line = line.strip()
                if line == "[console_scripts]":
                    in_console_scripts = True
                elif line.startswith("["):
                    in_console_scripts = False
                elif in_console_scripts and "=" in line:
                    name, _, value = line.partition("=")
                    entry_points[name.strip()] = value.strip()

        return entry_points

    def _extract_version_from_wheel(self, wheel_path: Path) -> str | None:
        """Extract version from wheel filename or metadata.

        Args:
            wheel_path: Path to the wheel file.

        Returns:
            Version string if found, None otherwise.
        """
        # Try to get from filename first
        filename = wheel_path.name
        parts = filename.split("-")
        if len(parts) >= 2:
            return parts[1]
        return None
