"""IdeBundleBuildService for building IDE bundles from nWave source.

This service scans the nWave/ source directory for agents, commands,
templates, and scripts, copies them to the output directory (dist/ide/),
and returns counts of processed components.

Uses FileSystemPort for all file operations (hexagonal architecture).
"""

from __future__ import annotations

from pathlib import Path

from crafter_ai.installer.domain.ide_bundle_build_result import IdeBundleBuildResult
from crafter_ai.installer.domain.ide_bundle_constants import (
    AGENTS_SUBDIR,
    COMMANDS_SUBDIR,
    SCRIPTS_SUBDIR,
    TEMPLATES_SUBDIR,
)
from crafter_ai.installer.ports.filesystem_port import FileSystemPort


class IdeBundleBuildService:
    """Service for building IDE bundle from nWave/ source directory.

    Scans nWave/ for agents, commands, templates, scripts, and copies
    them to dist/ide/. Counts components and tracks YAML warnings.
    """

    def __init__(self, filesystem: FileSystemPort) -> None:
        """Initialize with filesystem port.

        Args:
            filesystem: FileSystemPort adapter for file operations.
        """
        self._filesystem = filesystem

    def build(self, source_dir: Path, output_dir: Path) -> IdeBundleBuildResult:
        """Build IDE bundle from source directory.

        Scans source_dir for agents, commands, templates, and scripts,
        copies each file to output_dir preserving subdirectory structure,
        and returns component counts.

        Args:
            source_dir: Path to nWave/ source directory.
            output_dir: Path to dist/ide/ output directory.

        Returns:
            IdeBundleBuildResult with component counts and status.
        """
        if not self._filesystem.exists(source_dir):
            return IdeBundleBuildResult(
                success=False,
                output_dir=None,
                agent_count=0,
                command_count=0,
                template_count=0,
                script_count=0,
                team_count=0,
                yaml_warnings=[],
                embed_injection_count=0,
                error_message=f"Source directory not found: {source_dir}",
            )

        self._filesystem.mkdir(output_dir, parents=True)

        agent_count = self._copy_subdir(source_dir, output_dir, AGENTS_SUBDIR)
        command_count = self._copy_subdir(source_dir, output_dir, COMMANDS_SUBDIR)
        template_count = self._copy_subdir(source_dir, output_dir, TEMPLATES_SUBDIR)
        script_count = self._copy_subdir(source_dir, output_dir, SCRIPTS_SUBDIR)
        team_count = self._count_teams(source_dir)

        return IdeBundleBuildResult(
            success=True,
            output_dir=output_dir,
            agent_count=agent_count,
            command_count=command_count,
            template_count=template_count,
            script_count=script_count,
            team_count=team_count,
            yaml_warnings=[],
            embed_injection_count=0,
        )

    def _copy_subdir(
        self, source_dir: Path, output_dir: Path, subdir: str
    ) -> int:
        """Copy files from a source subdirectory to the output.

        Args:
            source_dir: Root source directory (nWave/).
            output_dir: Root output directory (dist/ide/).
            subdir: Relative subdirectory path (e.g. 'agents/nw').

        Returns:
            Number of files copied.
        """
        src_path = source_dir / subdir
        dst_path = output_dir / subdir

        if not self._filesystem.exists(src_path):
            return 0

        self._filesystem.mkdir(dst_path, parents=True)

        files = self._filesystem.list_dir(src_path)
        for src_file in files:
            dst_file = dst_path / src_file.name
            self._filesystem.copy_file(src_file, dst_file)

        return len(files)

    def _count_teams(self, source_dir: Path) -> int:
        """Count team files, returning 0 if teams/ directory is missing.

        Args:
            source_dir: Root source directory (nWave/).

        Returns:
            Number of team files, or 0 if directory does not exist.
        """
        teams_path = source_dir / "teams"
        if not self._filesystem.exists(teams_path):
            return 0

        return len(self._filesystem.list_dir(teams_path))
