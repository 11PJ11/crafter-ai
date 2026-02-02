"""Tests for ReleaseReadinessService.

This module tests the release readiness validation service that validates
wheel files for PyPI release requirements, including twine check, metadata
completeness, entry points, and license/readme bundling.
"""

import zipfile
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.services.release_readiness_service import (
    ReleaseReadinessResult,
    ReleaseReadinessService,
)


class TestReleaseReadinessResult:
    """Tests for ReleaseReadinessResult dataclass."""

    def test_creation_with_ready_status(self) -> None:
        """Test ReleaseReadinessResult can be created with ready status."""
        checks = [
            CheckResult(
                id="twine_check",
                name="Twine Check",
                passed=True,
                severity=CheckSeverity.BLOCKING,
                message="Twine check passed",
            )
        ]
        result = ReleaseReadinessResult(
            ready=True,
            checks=checks,
            blocking_issues=[],
            warnings=[],
            status_message="READY FOR PYPI",
        )

        assert result.ready is True
        assert len(result.checks) == 1
        assert result.blocking_issues == []
        assert result.warnings == []
        assert result.status_message == "READY FOR PYPI"

    def test_creation_with_not_ready_status(self) -> None:
        """Test ReleaseReadinessResult can represent not ready status."""
        checks = [
            CheckResult(
                id="twine_check",
                name="Twine Check",
                passed=False,
                severity=CheckSeverity.BLOCKING,
                message="Twine check failed",
            )
        ]
        result = ReleaseReadinessResult(
            ready=False,
            checks=checks,
            blocking_issues=["Twine check failed"],
            warnings=[],
            status_message="NOT READY: 1 blocking issue(s)",
        )

        assert result.ready is False
        assert len(result.blocking_issues) == 1
        assert "Twine check failed" in result.blocking_issues

    def test_creation_with_warnings(self) -> None:
        """Test ReleaseReadinessResult can have warnings while being ready."""
        result = ReleaseReadinessResult(
            ready=True,
            checks=[],
            blocking_issues=[],
            warnings=["CHANGELOG entry missing for version"],
            status_message="READY FOR PYPI",
        )

        assert result.ready is True
        assert len(result.warnings) == 1
        assert "CHANGELOG" in result.warnings[0]

    def test_is_frozen(self) -> None:
        """Test ReleaseReadinessResult is immutable (frozen dataclass)."""
        result = ReleaseReadinessResult(
            ready=True,
            checks=[],
            blocking_issues=[],
            warnings=[],
            status_message="READY FOR PYPI",
        )

        with pytest.raises(AttributeError):
            result.ready = False  # type: ignore[misc]


class TestReleaseReadinessService:
    """Tests for ReleaseReadinessService."""

    @pytest.fixture
    def service(self) -> ReleaseReadinessService:
        """Create a ReleaseReadinessService instance."""
        return ReleaseReadinessService()

    @pytest.fixture
    def valid_wheel(self, tmp_path: Path) -> Path:
        """Create a valid wheel file with all required content for testing."""
        wheel_name = "crafter_ai-1.2.3-py3-none-any.whl"
        wheel_path = tmp_path / wheel_name

        # Create a valid wheel with all required files
        with zipfile.ZipFile(wheel_path, "w") as zf:
            # Package content
            zf.writestr("crafter_ai/__init__.py", "")

            # Metadata with all required fields
            metadata = """Metadata-Version: 2.1
Name: crafter-ai
Version: 1.2.3
Summary: AI-powered software craftsmanship tools
Author: Mike
Author-email: mike@example.com
License: MIT
"""
            zf.writestr("crafter_ai-1.2.3.dist-info/METADATA", metadata)

            # Entry points with crafter-ai CLI
            entry_points = """[console_scripts]
crafter-ai = crafter_ai.cli:main
"""
            zf.writestr("crafter_ai-1.2.3.dist-info/entry_points.txt", entry_points)

            # LICENSE file
            zf.writestr("crafter_ai-1.2.3.dist-info/LICENSE", "MIT License\n...")

            # README
            zf.writestr(
                "crafter_ai-1.2.3.dist-info/README.md", "# Crafter AI\n\nDescription"
            )

            # RECORD file
            zf.writestr("crafter_ai-1.2.3.dist-info/RECORD", "")

            # WHEEL file
            zf.writestr(
                "crafter_ai-1.2.3.dist-info/WHEEL",
                "Wheel-Version: 1.0\nGenerator: test",
            )

        return wheel_path

    @pytest.fixture
    def wheel_missing_metadata(self, tmp_path: Path) -> Path:
        """Create a wheel file with incomplete metadata."""
        wheel_name = "crafter_ai-1.0.0-py3-none-any.whl"
        wheel_path = tmp_path / wheel_name

        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("crafter_ai/__init__.py", "")
            # Metadata missing author and license
            metadata = """Metadata-Version: 2.1
Name: crafter-ai
Version: 1.0.0
"""
            zf.writestr("crafter_ai-1.0.0.dist-info/METADATA", metadata)
            zf.writestr("crafter_ai-1.0.0.dist-info/RECORD", "")
            zf.writestr(
                "crafter_ai-1.0.0.dist-info/WHEEL",
                "Wheel-Version: 1.0\nGenerator: test",
            )

        return wheel_path

    @pytest.fixture
    def wheel_missing_entry_points(self, tmp_path: Path) -> Path:
        """Create a wheel file without entry points."""
        wheel_name = "crafter_ai-1.0.0-py3-none-any.whl"
        wheel_path = tmp_path / wheel_name

        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("crafter_ai/__init__.py", "")
            metadata = """Metadata-Version: 2.1
Name: crafter-ai
Version: 1.0.0
Summary: Test package
Author: Test
License: MIT
"""
            zf.writestr("crafter_ai-1.0.0.dist-info/METADATA", metadata)
            zf.writestr("crafter_ai-1.0.0.dist-info/RECORD", "")
            zf.writestr(
                "crafter_ai-1.0.0.dist-info/WHEEL",
                "Wheel-Version: 1.0\nGenerator: test",
            )
            # No entry_points.txt file

        return wheel_path

    @pytest.fixture
    def wheel_invalid_version(self, tmp_path: Path) -> Path:
        """Create a wheel file with invalid PEP 440 version."""
        wheel_name = "crafter_ai-invalid.version-py3-none-any.whl"
        wheel_path = tmp_path / wheel_name

        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("crafter_ai/__init__.py", "")
            metadata = """Metadata-Version: 2.1
Name: crafter-ai
Version: invalid.version
Summary: Test package
Author: Test
License: MIT
"""
            zf.writestr("crafter_ai-invalid.version.dist-info/METADATA", metadata)
            zf.writestr("crafter_ai-invalid.version.dist-info/RECORD", "")
            zf.writestr(
                "crafter_ai-invalid.version.dist-info/WHEEL",
                "Wheel-Version: 1.0\nGenerator: test",
            )

        return wheel_path

    @pytest.fixture
    def wheel_missing_license(self, tmp_path: Path) -> Path:
        """Create a wheel file without LICENSE bundled."""
        wheel_name = "crafter_ai-1.0.0-py3-none-any.whl"
        wheel_path = tmp_path / wheel_name

        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("crafter_ai/__init__.py", "")
            metadata = """Metadata-Version: 2.1
Name: crafter-ai
Version: 1.0.0
Summary: Test package
Author: Test
License: MIT
"""
            zf.writestr("crafter_ai-1.0.0.dist-info/METADATA", metadata)
            entry_points = """[console_scripts]
crafter-ai = crafter_ai.cli:main
"""
            zf.writestr("crafter_ai-1.0.0.dist-info/entry_points.txt", entry_points)
            zf.writestr("crafter_ai-1.0.0.dist-info/README.md", "# README")
            zf.writestr("crafter_ai-1.0.0.dist-info/RECORD", "")
            zf.writestr(
                "crafter_ai-1.0.0.dist-info/WHEEL",
                "Wheel-Version: 1.0\nGenerator: test",
            )
            # No LICENSE file

        return wheel_path

    @pytest.fixture
    def wheel_missing_readme(self, tmp_path: Path) -> Path:
        """Create a wheel file without README bundled."""
        wheel_name = "crafter_ai-1.0.0-py3-none-any.whl"
        wheel_path = tmp_path / wheel_name

        with zipfile.ZipFile(wheel_path, "w") as zf:
            zf.writestr("crafter_ai/__init__.py", "")
            metadata = """Metadata-Version: 2.1
Name: crafter-ai
Version: 1.0.0
Summary: Test package
Author: Test
License: MIT
"""
            zf.writestr("crafter_ai-1.0.0.dist-info/METADATA", metadata)
            entry_points = """[console_scripts]
crafter-ai = crafter_ai.cli:main
"""
            zf.writestr("crafter_ai-1.0.0.dist-info/entry_points.txt", entry_points)
            zf.writestr("crafter_ai-1.0.0.dist-info/LICENSE", "MIT License")
            zf.writestr("crafter_ai-1.0.0.dist-info/RECORD", "")
            zf.writestr(
                "crafter_ai-1.0.0.dist-info/WHEEL",
                "Wheel-Version: 1.0\nGenerator: test",
            )
            # No README file

        return wheel_path

    @pytest.fixture
    def changelog_with_version(self, tmp_path: Path) -> Path:
        """Create a CHANGELOG file with version entry."""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(
            "# Changelog\n\n## [1.2.3] - 2026-02-02\n\n- Initial release\n"
        )
        return changelog_path

    @pytest.fixture
    def changelog_without_version(self, tmp_path: Path) -> Path:
        """Create a CHANGELOG file without version entry."""
        changelog_path = tmp_path / "CHANGELOG.md"
        changelog_path.write_text(
            "# Changelog\n\n## [1.0.0] - 2025-01-01\n\n- Old release\n"
        )
        return changelog_path

    # Tests for validate method - ready status
    @patch("subprocess.run")
    def test_validate_returns_ready_when_all_blocking_checks_pass(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        valid_wheel: Path,
        changelog_with_version: Path,
    ) -> None:
        """Test validate returns ready=True when all blocking checks pass."""
        # Mock twine check success
        mock_run.return_value = MagicMock(
            returncode=0,
            stdout="Checking distribution...\nPASSED",
            stderr="",
        )

        result = service.validate(
            valid_wheel, changelog_path=changelog_with_version.parent
        )

        assert result.ready is True
        assert result.status_message == "READY FOR PYPI"
        assert result.blocking_issues == []

    # Tests for twine_check
    @patch("subprocess.run")
    def test_validate_returns_not_ready_when_twine_check_fails(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test validate returns ready=False when twine_check fails."""
        # Mock twine check failure
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="Checking distribution...\nFAILED",
            stderr="error: Invalid distribution",
        )

        result = service.validate(valid_wheel)

        assert result.ready is False
        assert any("twine" in issue.lower() for issue in result.blocking_issues)
        # Verify twine was called with the wheel path
        mock_run.assert_called_once()
        call_args = mock_run.call_args
        assert "twine" in call_args[0][0][0]
        assert str(valid_wheel) in call_args[0][0]

    # Tests for metadata_complete
    @patch("subprocess.run")
    def test_validate_returns_not_ready_when_metadata_incomplete(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        wheel_missing_metadata: Path,
    ) -> None:
        """Test validate returns ready=False when metadata is incomplete."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        result = service.validate(wheel_missing_metadata)

        assert result.ready is False
        assert any("metadata" in issue.lower() for issue in result.blocking_issues)

    # Tests for entry_points_defined
    @patch("subprocess.run")
    def test_validate_detects_missing_entry_points(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        wheel_missing_entry_points: Path,
    ) -> None:
        """Test validate detects missing entry points."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        result = service.validate(wheel_missing_entry_points)

        assert result.ready is False
        assert any("entry" in issue.lower() for issue in result.blocking_issues)

    # Tests for changelog_entry (WARNING only)
    @patch("subprocess.run")
    def test_validate_returns_ready_with_warning_when_changelog_missing(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        valid_wheel: Path,
        changelog_without_version: Path,
    ) -> None:
        """Test validate returns ready=True with warnings when changelog entry missing."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        result = service.validate(
            valid_wheel, changelog_path=changelog_without_version.parent
        )

        assert result.ready is True  # Should still be ready (non-blocking)
        assert any("changelog" in warning.lower() for warning in result.warnings)

    # Tests for pep440_version
    @patch("subprocess.run")
    def test_validate_detects_invalid_pep440_version(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        wheel_invalid_version: Path,
    ) -> None:
        """Test validate detects invalid PEP 440 version."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        result = service.validate(wheel_invalid_version)

        assert result.ready is False
        assert any(
            "version" in issue.lower() or "pep" in issue.lower()
            for issue in result.blocking_issues
        )

    # Tests for license_bundled
    @patch("subprocess.run")
    def test_validate_detects_missing_license(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        wheel_missing_license: Path,
    ) -> None:
        """Test validate detects missing LICENSE file."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        result = service.validate(wheel_missing_license)

        assert result.ready is False
        assert any("license" in issue.lower() for issue in result.blocking_issues)

    # Tests for readme_bundled
    @patch("subprocess.run")
    def test_validate_detects_missing_readme(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        wheel_missing_readme: Path,
    ) -> None:
        """Test validate detects missing README file."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        result = service.validate(wheel_missing_readme)

        assert result.ready is False
        assert any("readme" in issue.lower() for issue in result.blocking_issues)

    # Tests for blocking_issues and warnings list population
    @patch("subprocess.run")
    def test_blocking_issues_list_populated_correctly(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        wheel_missing_metadata: Path,
    ) -> None:
        """Test blocking_issues list is populated with all blocking failures."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="FAILED",
            stderr="Invalid distribution",
        )

        result = service.validate(wheel_missing_metadata)

        assert result.ready is False
        # Should have multiple blocking issues (twine + metadata)
        assert len(result.blocking_issues) >= 2

    @patch("subprocess.run")
    def test_warnings_list_populated_for_non_blocking_issues(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test warnings list populated for non-blocking issues like missing changelog."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        # Don't provide changelog path, should generate warning
        result = service.validate(valid_wheel, changelog_path=None)

        # Should be ready but with warnings about changelog
        assert result.ready is True
        assert len(result.warnings) >= 1

    # Tests for individual check methods
    @patch("subprocess.run")
    def test_run_twine_check_passes(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test run_twine_check returns passing CheckResult when twine succeeds."""
        mock_run.return_value = MagicMock(returncode=0, stdout="PASSED", stderr="")

        result = service.run_twine_check(valid_wheel)

        assert isinstance(result, CheckResult)
        assert result.passed is True
        assert result.severity == CheckSeverity.BLOCKING
        assert result.id == "twine_check"

    @patch("subprocess.run")
    def test_run_twine_check_fails(
        self,
        mock_run: MagicMock,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test run_twine_check returns failing CheckResult when twine fails."""
        mock_run.return_value = MagicMock(
            returncode=1,
            stdout="FAILED",
            stderr="Invalid metadata",
        )

        result = service.run_twine_check(valid_wheel)

        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING

    def test_check_metadata_complete_passes(
        self,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test check_metadata_complete passes for complete metadata."""
        result = service.check_metadata_complete(valid_wheel)

        assert result.passed is True
        assert result.id == "metadata_complete"

    def test_check_metadata_complete_fails(
        self,
        service: ReleaseReadinessService,
        wheel_missing_metadata: Path,
    ) -> None:
        """Test check_metadata_complete fails for incomplete metadata."""
        result = service.check_metadata_complete(wheel_missing_metadata)

        assert result.passed is False

    def test_check_entry_points_passes(
        self,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test check_entry_points_defined passes when crafter-ai entry point exists."""
        result = service.check_entry_points_defined(valid_wheel)

        assert result.passed is True
        assert result.id == "entry_points_defined"

    def test_check_entry_points_fails(
        self,
        service: ReleaseReadinessService,
        wheel_missing_entry_points: Path,
    ) -> None:
        """Test check_entry_points_defined fails when entry points missing."""
        result = service.check_entry_points_defined(wheel_missing_entry_points)

        assert result.passed is False

    def test_check_pep440_version_passes(
        self,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test check_pep440_version passes for valid PEP 440 version."""
        result = service.check_pep440_version(valid_wheel)

        assert result.passed is True
        assert result.id == "pep440_version"

    def test_check_pep440_version_fails(
        self,
        service: ReleaseReadinessService,
        wheel_invalid_version: Path,
    ) -> None:
        """Test check_pep440_version fails for invalid version."""
        result = service.check_pep440_version(wheel_invalid_version)

        assert result.passed is False

    def test_check_license_bundled_passes(
        self,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test check_license_bundled passes when LICENSE in wheel."""
        result = service.check_license_bundled(valid_wheel)

        assert result.passed is True
        assert result.id == "license_bundled"

    def test_check_license_bundled_fails(
        self,
        service: ReleaseReadinessService,
        wheel_missing_license: Path,
    ) -> None:
        """Test check_license_bundled fails when LICENSE missing."""
        result = service.check_license_bundled(wheel_missing_license)

        assert result.passed is False

    def test_check_readme_bundled_passes(
        self,
        service: ReleaseReadinessService,
        valid_wheel: Path,
    ) -> None:
        """Test check_readme_bundled passes when README in wheel."""
        result = service.check_readme_bundled(valid_wheel)

        assert result.passed is True
        assert result.id == "readme_bundled"

    def test_check_readme_bundled_fails(
        self,
        service: ReleaseReadinessService,
        wheel_missing_readme: Path,
    ) -> None:
        """Test check_readme_bundled fails when README missing."""
        result = service.check_readme_bundled(wheel_missing_readme)

        assert result.passed is False

    def test_check_changelog_entry_passes(
        self,
        service: ReleaseReadinessService,
        changelog_with_version: Path,
    ) -> None:
        """Test check_changelog_entry passes when version entry exists."""
        result = service.check_changelog_entry("1.2.3", changelog_with_version.parent)

        assert result.passed is True
        assert result.id == "changelog_entry"
        assert result.severity == CheckSeverity.WARNING

    def test_check_changelog_entry_fails(
        self,
        service: ReleaseReadinessService,
        changelog_without_version: Path,
    ) -> None:
        """Test check_changelog_entry fails when version entry missing."""
        result = service.check_changelog_entry(
            "1.2.3", changelog_without_version.parent
        )

        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING

    def test_check_changelog_entry_handles_missing_changelog(
        self,
        service: ReleaseReadinessService,
        tmp_path: Path,
    ) -> None:
        """Test check_changelog_entry handles missing CHANGELOG file gracefully."""
        # Empty directory with no CHANGELOG
        result = service.check_changelog_entry("1.0.0", tmp_path)

        assert result.passed is False
        assert result.severity == CheckSeverity.WARNING
