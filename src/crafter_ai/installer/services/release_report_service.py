"""ReleaseReportService for generating installation summary reports.

This module provides the ReleaseReportService application service that:
- Generates ReleaseReport from InstallResult and wheel metadata
- Formats reports for Rich-compatible console output
- Displays health status with appropriate colors

Used by: forge:install-local CLI command for final output
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from crafter_ai.installer.services.install_service import InstallResult


@dataclass(frozen=True)
class ReleaseReport:
    """Immutable report of a completed installation.

    Attributes:
        version: Installed version string.
        install_path: Path where package was installed.
        wheel_path: Path to the source wheel file.
        wheel_size_bytes: Size of the wheel file in bytes.
        phases_completed: List of phase names that completed.
        health_status: Overall health status (HEALTHY, DEGRADED, UNHEALTHY, UNKNOWN).
        warnings: List of warning messages from verification.
        timestamp: When the report was generated.
        duration_seconds: Total installation duration.
        backup_path: Path to backup if created, None otherwise.
    """

    version: str
    install_path: Path
    wheel_path: Path
    wheel_size_bytes: int
    phases_completed: list[str]
    health_status: str
    warnings: list[str]
    timestamp: datetime
    duration_seconds: float
    backup_path: Path | None


class ReleaseReportService:
    """Application service for generating and formatting release reports.

    This service:
    - Creates ReleaseReport from InstallResult and wheel metadata
    - Formats reports for Rich-compatible console display
    - Applies color coding based on health status
    """

    def generate(
        self,
        install_result: InstallResult,
        wheel_path: Path,
        start_time: datetime,
        backup_path: Path | None = None,
    ) -> ReleaseReport:
        """Generate a ReleaseReport from an InstallResult.

        Args:
            install_result: Result from InstallService.install().
            wheel_path: Path to the wheel file that was installed.
            start_time: When the install journey started.
            backup_path: Optional path to backup location.

        Returns:
            ReleaseReport with all installation details.
        """
        # Get current time for timestamp and duration
        now = datetime.now()
        duration = (now - start_time).total_seconds()

        # Get wheel file size
        wheel_size = wheel_path.stat().st_size

        # Convert phases to strings
        phases_completed = [phase.value for phase in install_result.phases_completed]

        # Convert health status to uppercase string
        if install_result.health_status is None:
            health_status = "UNKNOWN"
        else:
            health_status = install_result.health_status.value.upper()

        return ReleaseReport(
            version=install_result.version or "unknown",
            install_path=install_result.install_path or Path(),
            wheel_path=wheel_path,
            wheel_size_bytes=wheel_size,
            phases_completed=phases_completed,
            health_status=health_status,
            warnings=list(install_result.verification_warnings),
            timestamp=now,
            duration_seconds=duration,
            backup_path=backup_path,
        )

    def format_console(self, report: ReleaseReport) -> str:
        """Format a ReleaseReport for Rich-compatible console output.

        Args:
            report: The ReleaseReport to format.

        Returns:
            Rich-compatible formatted string with colors and styling.
        """
        # Determine health status color
        status_colors = {
            "HEALTHY": "green",
            "DEGRADED": "yellow",
            "UNHEALTHY": "red",
            "UNKNOWN": "dim",
        }
        color = status_colors.get(report.health_status, "dim")

        # Format wheel size
        wheel_size_str = self._format_size(report.wheel_size_bytes)

        # Build output lines
        lines = [
            "",
            "[bold cyan]" + "=" * 60 + "[/bold cyan]",
            "[bold cyan]  FORGE: INSTALL COMPLETE  [/bold cyan]",
            "[bold cyan]" + "=" * 60 + "[/bold cyan]",
            "",
            f"  [bold]Version:[/bold]       {report.version}",
            f"  [bold]Install Path:[/bold]  {report.install_path}",
            f"  [bold]Wheel:[/bold]         {report.wheel_path.name}",
            f"  [bold]Wheel Size:[/bold]    {wheel_size_str} ({report.wheel_size_bytes} bytes)",
            f"  [bold]Duration:[/bold]      {report.duration_seconds:.2f}s",
            f"  [bold]Phases:[/bold]        {len(report.phases_completed)} completed",
            "",
            f"  [bold]Health Status:[/bold] [{color}]{report.health_status}[/{color}]",
        ]

        # Add warnings if present
        if report.warnings:
            lines.append("")
            lines.append("  [bold yellow]Warnings:[/bold yellow]")
            for warning in report.warnings:
                lines.append(f"    [yellow]- {warning}[/yellow]")

        # Add backup path if present
        if report.backup_path:
            lines.append("")
            lines.append(f"  [dim]Backup:[/dim] {report.backup_path}")

        lines.append("")
        lines.append("[bold cyan]" + "=" * 60 + "[/bold cyan]")
        lines.append("")

        return "\n".join(lines)

    def _format_size(self, size_bytes: int) -> str:
        """Format bytes to human-readable size string.

        Args:
            size_bytes: Size in bytes.

        Returns:
            Human-readable size string (e.g., '53.0 KB').
        """
        for unit in ["B", "KB", "MB", "GB"]:
            if abs(size_bytes) < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes = size_bytes / 1024.0  # type: ignore[assignment]
        return f"{size_bytes:.1f} TB"
