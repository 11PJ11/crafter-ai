"""DeploymentValidationService for validating deployed IDE bundle assets.

This service validates that deployed assets in ~/.claude/ match the expected
counts from the IDE bundle build. It counts files in each subdirectory,
compares against expected values, writes a manifest JSON file, and reports
schema version and phases.

Uses FileSystemPort for all file operations (hexagonal architecture).
"""

from __future__ import annotations

import json
from pathlib import Path

from crafter_ai.installer.domain.deployment_validation_result import (
    DeploymentValidationResult,
)
from crafter_ai.installer.domain.ide_bundle_constants import (
    AGENTS_SUBDIR,
    COMMANDS_SUBDIR,
    EXPECTED_SCHEMA_PHASES,
    EXPECTED_SCHEMA_VERSION,
    SCRIPTS_SUBDIR,
    TEMPLATES_SUBDIR,
)
from crafter_ai.installer.ports.filesystem_port import FileSystemPort


class DeploymentValidationService:
    """Service for validating deployed assets match bundle expectations.

    Compares filesystem counts against expected values, writes manifest,
    and validates schema version.
    """

    def __init__(self, filesystem: FileSystemPort) -> None:
        """Initialize with filesystem port.

        Args:
            filesystem: FileSystemPort adapter for file operations.
        """
        self._filesystem = filesystem

    def validate(
        self,
        target_dir: Path,
        expected_agents: int,
        expected_commands: int,
        expected_templates: int,
        expected_scripts: int,
    ) -> DeploymentValidationResult:
        """Validate deployed assets match expected counts.

        Counts actual files in each subdirectory under target_dir,
        compares against expected values, writes a manifest JSON file,
        and returns a validation result.

        Args:
            target_dir: Path to ~/.claude/ target directory.
            expected_agents: Expected agent file count.
            expected_commands: Expected command file count.
            expected_templates: Expected template file count.
            expected_scripts: Expected script file count.

        Returns:
            DeploymentValidationResult with match status and mismatches.
        """
        actual_agents = self._count_files(target_dir, AGENTS_SUBDIR)
        actual_commands = self._count_files(target_dir, COMMANDS_SUBDIR)
        actual_templates = self._count_files(target_dir, TEMPLATES_SUBDIR)
        actual_scripts = self._count_files(target_dir, SCRIPTS_SUBDIR)

        agent_match = actual_agents == expected_agents
        command_match = actual_commands == expected_commands
        template_match = actual_templates == expected_templates
        script_match = actual_scripts == expected_scripts

        mismatches: list[str] = []
        if not agent_match:
            mismatches.append(
                f"Expected {expected_agents} agents, found {actual_agents}"
            )
        if not command_match:
            mismatches.append(
                f"Expected {expected_commands} commands, found {actual_commands}"
            )
        if not template_match:
            mismatches.append(
                f"Expected {expected_templates} templates, found {actual_templates}"
            )
        if not script_match:
            mismatches.append(
                f"Expected {expected_scripts} scripts, found {actual_scripts}"
            )

        all_match = agent_match and command_match and template_match and script_match

        manifest_written = self._write_manifest(
            target_dir,
            valid=all_match,
            actual_agents=actual_agents,
            actual_commands=actual_commands,
            actual_templates=actual_templates,
            actual_scripts=actual_scripts,
            mismatches=mismatches,
        )

        return DeploymentValidationResult(
            valid=all_match,
            agent_count_match=agent_match,
            command_count_match=command_match,
            template_count_match=template_match,
            script_count_match=script_match,
            manifest_written=manifest_written,
            schema_version=EXPECTED_SCHEMA_VERSION,
            schema_phases=EXPECTED_SCHEMA_PHASES,
            mismatches=mismatches,
        )

    def _count_files(self, target_dir: Path, subdir: str) -> int:
        """Count files in a subdirectory under target_dir.

        Only counts regular files with expected extensions, excludes directories
        and hidden files.

        Args:
            target_dir: Root target directory (~/.claude/).
            subdir: Relative subdirectory path (e.g. 'agents/nw').

        Returns:
            Number of files found, or 0 if directory does not exist.
        """
        subdir_path = target_dir / subdir
        if not self._filesystem.exists(subdir_path):
            return 0

        items = self._filesystem.list_dir(subdir_path)
        # Count only files with expected extensions (exclude directories and hidden files)
        # Expected extensions: .md (agents/commands), .yaml/.json (templates), .py (scripts)
        valid_extensions = {'.md', '.yaml', '.json', '.py'}
        return len([
            item for item in items
            if item.suffix in valid_extensions and not item.name.startswith('.')
        ])

    def _write_manifest(
        self,
        target_dir: Path,
        *,
        valid: bool,
        actual_agents: int,
        actual_commands: int,
        actual_templates: int,
        actual_scripts: int,
        mismatches: list[str],
    ) -> bool:
        """Write validation manifest JSON to target directory.

        Args:
            target_dir: Root target directory (~/.claude/).
            valid: Whether all validations passed.
            actual_agents: Actual agent file count found.
            actual_commands: Actual command file count found.
            actual_templates: Actual template file count found.
            actual_scripts: Actual script file count found.
            mismatches: List of mismatch descriptions.

        Returns:
            True if manifest was written successfully, False otherwise.
        """
        manifest = {
            "valid": valid,
            "schema_version": EXPECTED_SCHEMA_VERSION,
            "schema_phases": EXPECTED_SCHEMA_PHASES,
            "counts": {
                "agents": actual_agents,
                "commands": actual_commands,
                "templates": actual_templates,
                "scripts": actual_scripts,
            },
            "mismatches": mismatches,
        }

        try:
            if not self._filesystem.exists(target_dir):
                self._filesystem.mkdir(target_dir, parents=True)
            manifest_path = target_dir / "manifest.json"
            self._filesystem.write_text(manifest_path, json.dumps(manifest, indent=2))
            return True
        except (OSError, PermissionError):
            return False
