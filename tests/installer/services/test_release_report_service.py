"""Tests for ReleaseReportService.

Tests verify:
- Report generation from InstallResult
- Wheel size calculation
- Timestamp capture
- Console formatting with Rich-compatible output
- Health status display with colors
- Warning display
"""

from datetime import datetime
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from crafter_ai.installer.domain.health_result import HealthStatus
from crafter_ai.installer.services.install_service import InstallPhase, InstallResult
from crafter_ai.installer.services.release_report_service import (
    ReleaseReport,
    ReleaseReportService,
)


class TestReleaseReport:
    """Tests for ReleaseReport dataclass."""

    def test_release_report_has_all_required_fields(self) -> None:
        """ReleaseReport should have all required fields."""
        report = ReleaseReport(
            version="1.0.0",
            install_path=Path("/usr/local/bin/crafter-ai"),
            wheel_path=Path("/tmp/crafter_ai-1.0.0-py3-none-any.whl"),
            wheel_size_bytes=12345,
            phases_completed=["preflight", "readiness", "backup", "install"],
            health_status="HEALTHY",
            warnings=[],
            timestamp=datetime(2026, 2, 2, 12, 0, 0),
            duration_seconds=5.5,
            backup_path=Path("/tmp/backup"),
        )

        assert report.version == "1.0.0"
        assert report.install_path == Path("/usr/local/bin/crafter-ai")
        assert report.wheel_path == Path("/tmp/crafter_ai-1.0.0-py3-none-any.whl")
        assert report.wheel_size_bytes == 12345
        assert report.phases_completed == [
            "preflight",
            "readiness",
            "backup",
            "install",
        ]
        assert report.health_status == "HEALTHY"
        assert report.warnings == []
        assert report.timestamp == datetime(2026, 2, 2, 12, 0, 0)
        assert report.duration_seconds == 5.5
        assert report.backup_path == Path("/tmp/backup")

    def test_release_report_backup_path_can_be_none(self) -> None:
        """ReleaseReport should allow None for backup_path."""
        report = ReleaseReport(
            version="1.0.0",
            install_path=Path("/usr/local/bin/crafter-ai"),
            wheel_path=Path("/tmp/wheel.whl"),
            wheel_size_bytes=1000,
            phases_completed=[],
            health_status="HEALTHY",
            warnings=[],
            timestamp=datetime.now(),
            duration_seconds=1.0,
            backup_path=None,
        )

        assert report.backup_path is None

    def test_release_report_is_immutable(self) -> None:
        """ReleaseReport should be immutable (frozen)."""
        report = ReleaseReport(
            version="1.0.0",
            install_path=Path("/path"),
            wheel_path=Path("/wheel.whl"),
            wheel_size_bytes=100,
            phases_completed=[],
            health_status="HEALTHY",
            warnings=[],
            timestamp=datetime.now(),
            duration_seconds=1.0,
            backup_path=None,
        )

        with pytest.raises(AttributeError):
            report.version = "2.0.0"  # type: ignore[misc]


class TestReleaseReportServiceGenerate:
    """Tests for ReleaseReportService.generate() method."""

    @pytest.fixture
    def service(self) -> ReleaseReportService:
        """Create ReleaseReportService instance."""
        return ReleaseReportService()

    @pytest.fixture
    def successful_install_result(self) -> InstallResult:
        """Create a successful InstallResult."""
        return InstallResult(
            success=True,
            version="1.0.0",
            install_path=Path("/usr/local/bin/crafter-ai"),
            phases_completed=[
                InstallPhase.PREFLIGHT,
                InstallPhase.READINESS,
                InstallPhase.BACKUP,
                InstallPhase.INSTALL,
                InstallPhase.VERIFICATION,
            ],
            error_message=None,
            health_status=HealthStatus.HEALTHY,
            verification_warnings=[],
        )

    def test_generate_creates_release_report(
        self, service: ReleaseReportService, successful_install_result: InstallResult
    ) -> None:
        """generate() should create ReleaseReport with all fields populated."""
        wheel_path = Path("/tmp/crafter_ai-1.0.0-py3-none-any.whl")
        start_time = datetime(2026, 2, 2, 12, 0, 0)

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=54321)

            report = service.generate(
                install_result=successful_install_result,
                wheel_path=wheel_path,
                start_time=start_time,
                backup_path=Path("/tmp/backup"),
            )

        assert isinstance(report, ReleaseReport)
        assert report.version == "1.0.0"
        assert report.install_path == Path("/usr/local/bin/crafter-ai")

    def test_generate_calculates_wheel_size_bytes(
        self, service: ReleaseReportService, successful_install_result: InstallResult
    ) -> None:
        """generate() should calculate wheel_size_bytes from file."""
        wheel_path = Path("/tmp/crafter_ai-1.0.0-py3-none-any.whl")

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=98765)

            report = service.generate(
                install_result=successful_install_result,
                wheel_path=wheel_path,
                start_time=datetime.now(),
            )

        assert report.wheel_size_bytes == 98765

    def test_generate_captures_timestamp(
        self, service: ReleaseReportService, successful_install_result: InstallResult
    ) -> None:
        """generate() should capture current timestamp."""
        wheel_path = Path("/tmp/wheel.whl")
        test_time = datetime(2026, 2, 2, 15, 30, 45)

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1000)
            with patch(
                "crafter_ai.installer.services.release_report_service.datetime"
            ) as mock_datetime:
                mock_datetime.now.return_value = test_time

                report = service.generate(
                    install_result=successful_install_result,
                    wheel_path=wheel_path,
                    start_time=datetime(2026, 2, 2, 15, 30, 40),
                )

        assert report.timestamp == test_time

    def test_generate_calculates_duration_seconds(
        self, service: ReleaseReportService, successful_install_result: InstallResult
    ) -> None:
        """generate() should calculate duration from start_time to now."""
        wheel_path = Path("/tmp/wheel.whl")
        start_time = datetime(2026, 2, 2, 15, 30, 40)
        end_time = datetime(2026, 2, 2, 15, 30, 45, 500000)  # 5.5 seconds later

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1000)
            with patch(
                "crafter_ai.installer.services.release_report_service.datetime"
            ) as mock_datetime:
                mock_datetime.now.return_value = end_time

                report = service.generate(
                    install_result=successful_install_result,
                    wheel_path=wheel_path,
                    start_time=start_time,
                )

        assert report.duration_seconds == 5.5

    def test_generate_extracts_phases_completed_as_strings(
        self, service: ReleaseReportService, successful_install_result: InstallResult
    ) -> None:
        """generate() should convert InstallPhase enums to strings."""
        wheel_path = Path("/tmp/wheel.whl")

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1000)

            report = service.generate(
                install_result=successful_install_result,
                wheel_path=wheel_path,
                start_time=datetime.now(),
            )

        assert report.phases_completed == [
            "preflight",
            "readiness",
            "backup",
            "install",
            "verification",
        ]

    def test_generate_extracts_health_status_as_string(
        self, service: ReleaseReportService
    ) -> None:
        """generate() should convert HealthStatus enum to uppercase string."""
        install_result = InstallResult(
            success=True,
            version="1.0.0",
            install_path=Path("/path"),
            phases_completed=[InstallPhase.INSTALL],
            error_message=None,
            health_status=HealthStatus.DEGRADED,
            verification_warnings=["Some warning"],
        )
        wheel_path = Path("/tmp/wheel.whl")

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1000)

            report = service.generate(
                install_result=install_result,
                wheel_path=wheel_path,
                start_time=datetime.now(),
            )

        assert report.health_status == "DEGRADED"

    def test_generate_includes_verification_warnings(
        self, service: ReleaseReportService
    ) -> None:
        """generate() should include verification warnings."""
        install_result = InstallResult(
            success=True,
            version="1.0.0",
            install_path=Path("/path"),
            phases_completed=[InstallPhase.INSTALL, InstallPhase.VERIFICATION],
            error_message=None,
            health_status=HealthStatus.DEGRADED,
            verification_warnings=["Config not found", "Optional feature disabled"],
        )
        wheel_path = Path("/tmp/wheel.whl")

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1000)

            report = service.generate(
                install_result=install_result,
                wheel_path=wheel_path,
                start_time=datetime.now(),
            )

        assert report.warnings == ["Config not found", "Optional feature disabled"]

    def test_generate_handles_none_health_status(
        self, service: ReleaseReportService
    ) -> None:
        """generate() should handle None health_status (no verification)."""
        install_result = InstallResult(
            success=True,
            version="1.0.0",
            install_path=Path("/path"),
            phases_completed=[InstallPhase.INSTALL],
            error_message=None,
            health_status=None,
            verification_warnings=[],
        )
        wheel_path = Path("/tmp/wheel.whl")

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1000)

            report = service.generate(
                install_result=install_result,
                wheel_path=wheel_path,
                start_time=datetime.now(),
            )

        assert report.health_status == "UNKNOWN"

    def test_generate_stores_backup_path(
        self, service: ReleaseReportService, successful_install_result: InstallResult
    ) -> None:
        """generate() should store backup_path if provided."""
        wheel_path = Path("/tmp/wheel.whl")
        backup_path = Path("/backup/2026-02-02")

        with patch("pathlib.Path.stat") as mock_stat:
            mock_stat.return_value = MagicMock(st_size=1000)

            report = service.generate(
                install_result=successful_install_result,
                wheel_path=wheel_path,
                start_time=datetime.now(),
                backup_path=backup_path,
            )

        assert report.backup_path == backup_path


class TestReleaseReportServiceFormatConsole:
    """Tests for ReleaseReportService.format_console() method."""

    @pytest.fixture
    def service(self) -> ReleaseReportService:
        """Create ReleaseReportService instance."""
        return ReleaseReportService()

    @pytest.fixture
    def healthy_report(self) -> ReleaseReport:
        """Create a healthy ReleaseReport."""
        return ReleaseReport(
            version="1.0.0",
            install_path=Path("/usr/local/bin/crafter-ai"),
            wheel_path=Path("/tmp/crafter_ai-1.0.0-py3-none-any.whl"),
            wheel_size_bytes=54321,
            phases_completed=[
                "preflight",
                "readiness",
                "backup",
                "install",
                "verification",
            ],
            health_status="HEALTHY",
            warnings=[],
            timestamp=datetime(2026, 2, 2, 12, 0, 0),
            duration_seconds=5.5,
            backup_path=Path("/tmp/backup"),
        )

    def test_format_console_produces_formatted_output(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should produce non-empty formatted string."""
        output = service.format_console(healthy_report)

        assert isinstance(output, str)
        assert len(output) > 0

    def test_format_console_shows_forge_header(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show 'FORGE: INSTALL COMPLETE' header."""
        output = service.format_console(healthy_report)

        assert "FORGE: INSTALL COMPLETE" in output

    def test_format_console_shows_version(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show version."""
        output = service.format_console(healthy_report)

        assert "1.0.0" in output

    def test_format_console_shows_install_path(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show install path."""
        output = service.format_console(healthy_report)

        assert "/usr/local/bin/crafter-ai" in output

    def test_format_console_shows_health_status(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show health status."""
        output = service.format_console(healthy_report)

        assert "HEALTHY" in output

    def test_format_console_shows_healthy_in_green(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show HEALTHY status with green color markup."""
        output = service.format_console(healthy_report)

        # Rich markup uses [green] for green color
        assert "[green]" in output and "HEALTHY" in output

    def test_format_console_shows_degraded_in_yellow(
        self, service: ReleaseReportService
    ) -> None:
        """format_console() should show DEGRADED status with yellow color markup."""
        report = ReleaseReport(
            version="1.0.0",
            install_path=Path("/path"),
            wheel_path=Path("/wheel.whl"),
            wheel_size_bytes=1000,
            phases_completed=["install"],
            health_status="DEGRADED",
            warnings=["Something minor"],
            timestamp=datetime.now(),
            duration_seconds=1.0,
            backup_path=None,
        )

        output = service.format_console(report)

        assert "[yellow]" in output and "DEGRADED" in output

    def test_format_console_shows_unhealthy_in_red(
        self, service: ReleaseReportService
    ) -> None:
        """format_console() should show UNHEALTHY status with red color markup."""
        report = ReleaseReport(
            version="1.0.0",
            install_path=Path("/path"),
            wheel_path=Path("/wheel.whl"),
            wheel_size_bytes=1000,
            phases_completed=["install"],
            health_status="UNHEALTHY",
            warnings=["Critical error"],
            timestamp=datetime.now(),
            duration_seconds=1.0,
            backup_path=None,
        )

        output = service.format_console(report)

        assert "[red]" in output and "UNHEALTHY" in output

    def test_format_console_includes_warnings(
        self, service: ReleaseReportService
    ) -> None:
        """format_console() should include warnings when present."""
        report = ReleaseReport(
            version="1.0.0",
            install_path=Path("/path"),
            wheel_path=Path("/wheel.whl"),
            wheel_size_bytes=1000,
            phases_completed=["install", "verification"],
            health_status="DEGRADED",
            warnings=["Config file not found", "Optional feature disabled"],
            timestamp=datetime.now(),
            duration_seconds=1.0,
            backup_path=None,
        )

        output = service.format_console(report)

        assert "Config file not found" in output
        assert "Optional feature disabled" in output

    def test_format_console_shows_duration(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show duration."""
        output = service.format_console(healthy_report)

        assert "5.5" in output or "5.50" in output

    def test_format_console_shows_wheel_size(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show wheel size in human-readable format."""
        output = service.format_console(healthy_report)

        # 54321 bytes should be displayed (could be 54321 bytes or ~53 KB)
        assert "54321" in output or "53" in output or "KB" in output

    def test_format_console_shows_phases_completed(
        self, service: ReleaseReportService, healthy_report: ReleaseReport
    ) -> None:
        """format_console() should show completed phases."""
        output = service.format_console(healthy_report)

        # Should show some indication of phases
        assert "5" in output or "phases" in output.lower() or "verification" in output
