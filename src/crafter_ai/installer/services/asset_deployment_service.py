"""AssetDeploymentService for deploying IDE bundle assets to ~/.claude/.

This service copies agents, commands, templates, and scripts from the
built IDE bundle (dist/ide/) to the Claude configuration directory
(~/.claude/), preserving the subdirectory structure.

Uses FileSystemPort for all file operations (hexagonal architecture).
"""

from __future__ import annotations

from pathlib import Path

from crafter_ai.installer.domain.asset_deployment_result import AssetDeploymentResult
from crafter_ai.installer.domain.ide_bundle_constants import (
    AGENTS_SUBDIR,
    COMMANDS_SUBDIR,
    SCRIPTS_SUBDIR,
    TEMPLATES_SUBDIR,
)
from crafter_ai.installer.ports.filesystem_port import FileSystemPort


class AssetDeploymentService:
    """Service for deploying IDE bundle assets to ~/.claude/.

    Copies agents, commands, templates, scripts from dist/ide/
    to their correct destinations under the Claude config directory.
    """

    def __init__(self, filesystem: FileSystemPort) -> None:
        """Initialize with filesystem port.

        Args:
            filesystem: FileSystemPort adapter for file operations.
        """
        self._filesystem = filesystem

    def deploy(self, source_dir: Path, target_dir: Path) -> AssetDeploymentResult:
        """Deploy IDE bundle assets to target directory.

        Copies files from source subdirectories (agents/nw, commands/nw,
        templates, scripts) to matching subdirectories under target_dir.

        Args:
            source_dir: Path to dist/ide/ bundle directory.
            target_dir: Path to ~/.claude/ target directory.

        Returns:
            AssetDeploymentResult with deployment counts and status.
        """
        if not self._filesystem.exists(source_dir):
            return AssetDeploymentResult(
                success=False,
                agents_deployed=0,
                commands_deployed=0,
                templates_deployed=0,
                scripts_deployed=0,
                target_path=target_dir,
                error_message=f"Source directory not found: {source_dir}",
            )

        self._filesystem.mkdir(target_dir, parents=True)

        agents_deployed = self._copy_subdir(source_dir, target_dir, AGENTS_SUBDIR)
        commands_deployed = self._copy_subdir(source_dir, target_dir, COMMANDS_SUBDIR)
        templates_deployed = self._copy_subdir(
            source_dir, target_dir, TEMPLATES_SUBDIR
        )
        scripts_deployed = self._copy_subdir(source_dir, target_dir, SCRIPTS_SUBDIR)

        return AssetDeploymentResult(
            success=True,
            agents_deployed=agents_deployed,
            commands_deployed=commands_deployed,
            templates_deployed=templates_deployed,
            scripts_deployed=scripts_deployed,
            target_path=target_dir,
        )

    def _copy_subdir(
        self, source_dir: Path, target_dir: Path, subdir: str
    ) -> int:
        """Copy files from a source subdirectory to the target.

        Args:
            source_dir: Root source directory (dist/ide/).
            target_dir: Root target directory (~/.claude/).
            subdir: Relative subdirectory path (e.g. 'agents/nw').

        Returns:
            Number of files copied.
        """
        src_path = source_dir / subdir
        dst_path = target_dir / subdir

        if not self._filesystem.exists(src_path):
            return 0

        self._filesystem.mkdir(dst_path, parents=True)

        files = self._filesystem.list_dir(src_path)
        for src_file in files:
            dst_file = dst_path / src_file.name
            self._filesystem.copy_file(src_file, dst_file)

        return len(files)
