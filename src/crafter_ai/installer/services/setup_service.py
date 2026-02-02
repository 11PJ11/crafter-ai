"""SetupService for configuring Claude AI agent directories.

This module provides the SetupService application service that:
- Creates ~/.claude/ directory structure for user-level config
- Creates .claude/ directory structure for project-level config
- Copies default template files (CLAUDE.md, CLAUDE.local.md)
- Verifies setup completion

Used by: nw setup CLI command
"""

from dataclasses import dataclass, field
from pathlib import Path

from crafter_ai.installer.ports.filesystem_port import FileSystemPort


# Default template content for CLAUDE.md (user-level instructions)
DEFAULT_CLAUDE_MD = """# CLAUDE.md - User Instructions for Claude AI

This file contains your personal instructions that apply to all projects.
Claude Code will read this file when starting conversations.

## About You
- Name: [Your name]
- Role: [Your role, e.g., "Senior Software Engineer"]

## Preferences
- Preferred languages: [e.g., Python, TypeScript]
- Code style: [e.g., "Follow PEP 8", "Use functional patterns"]

## Working Style
- [Add your working style preferences here]

## Important Notes
- [Add any important notes for Claude to remember]
"""

# Default template content for CLAUDE.local.md (project-level instructions)
DEFAULT_CLAUDE_LOCAL_MD = """# CLAUDE.local.md - Project Instructions

This file contains project-specific instructions for Claude AI.
It complements ~/.claude/CLAUDE.md with project-level context.

## Project Overview
- Name: [Project name]
- Description: [Brief description]

## Architecture
- [Describe the project architecture]

## Key Files
- [List important files and their purposes]

## Development Guidelines
- [Add project-specific guidelines]

## Testing
- [Describe testing approach and commands]
"""


@dataclass
class SetupResult:
    """Result of a setup operation.

    Attributes:
        success: Whether the setup completed successfully.
        created_paths: List of paths that were created.
        errors: List of error messages if any.
    """

    success: bool
    created_paths: list[Path] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


class SetupService:
    """Application service for setting up Claude AI agent directories.

    This service:
    - Creates ~/.claude/ structure (user-level config)
    - Creates .claude/ structure (project-level config)
    - Handles existing files with optional force overwrite
    - Verifies setup completion
    """

    def __init__(self, filesystem: FileSystemPort) -> None:
        """Initialize SetupService.

        Args:
            filesystem: FileSystemPort implementation for file operations.
        """
        self._filesystem = filesystem

    def setup_claude_config(
        self,
        home_dir: Path,
        force: bool = False,
    ) -> SetupResult:
        """Create ~/.claude/ directory structure.

        Creates:
        - ~/.claude/
        - ~/.claude/commands/
        - ~/.claude/CLAUDE.md

        Args:
            home_dir: The user's home directory.
            force: If True, overwrite existing files.

        Returns:
            SetupResult with success status and created paths.
        """
        created_paths: list[Path] = []
        errors: list[str] = []

        claude_dir = home_dir / ".claude"
        commands_dir = claude_dir / "commands"
        claude_md = claude_dir / "CLAUDE.md"

        # Create directories
        try:
            if not self._filesystem.exists(claude_dir):
                self._filesystem.mkdir(claude_dir, parents=True)
                created_paths.append(claude_dir)

            if not self._filesystem.exists(commands_dir):
                self._filesystem.mkdir(commands_dir, parents=True)
                created_paths.append(commands_dir)
        except OSError as e:
            errors.append(f"Failed to create directories: {e}")
            return SetupResult(
                success=False, created_paths=created_paths, errors=errors
            )

        # Create CLAUDE.md
        try:
            if not self._filesystem.exists(claude_md) or force:
                self._filesystem.write_text(claude_md, DEFAULT_CLAUDE_MD)
                created_paths.append(claude_md)
        except OSError as e:
            errors.append(f"Failed to create CLAUDE.md: {e}")
            return SetupResult(
                success=False, created_paths=created_paths, errors=errors
            )

        return SetupResult(success=True, created_paths=created_paths, errors=errors)

    def setup_project_config(
        self,
        project_dir: Path,
        force: bool = False,
    ) -> SetupResult:
        """Create .claude/ directory structure in project.

        Creates:
        - .claude/
        - .claude/CLAUDE.local.md

        Args:
            project_dir: The project root directory.
            force: If True, overwrite existing files.

        Returns:
            SetupResult with success status and created paths.
        """
        created_paths: list[Path] = []
        errors: list[str] = []

        claude_dir = project_dir / ".claude"
        claude_local_md = claude_dir / "CLAUDE.local.md"

        # Create directory
        try:
            if not self._filesystem.exists(claude_dir):
                self._filesystem.mkdir(claude_dir, parents=True)
                created_paths.append(claude_dir)
        except OSError as e:
            errors.append(f"Failed to create .claude directory: {e}")
            return SetupResult(
                success=False, created_paths=created_paths, errors=errors
            )

        # Create CLAUDE.local.md
        try:
            if not self._filesystem.exists(claude_local_md) or force:
                self._filesystem.write_text(claude_local_md, DEFAULT_CLAUDE_LOCAL_MD)
                created_paths.append(claude_local_md)
        except OSError as e:
            errors.append(f"Failed to create CLAUDE.local.md: {e}")
            return SetupResult(
                success=False, created_paths=created_paths, errors=errors
            )

        return SetupResult(success=True, created_paths=created_paths, errors=errors)

    def verify_setup(
        self,
        home_dir: Path | None = None,
        project_dir: Path | None = None,
    ) -> SetupResult:
        """Verify that required setup files exist.

        Args:
            home_dir: The user's home directory (for global config check).
            project_dir: The project root directory (for project config check).

        Returns:
            SetupResult with success=True if all required files exist.
        """
        errors: list[str] = []
        found_paths: list[Path] = []

        # Check global config
        if home_dir is not None:
            claude_dir = home_dir / ".claude"
            commands_dir = claude_dir / "commands"
            claude_md = claude_dir / "CLAUDE.md"

            if not self._filesystem.exists(claude_dir):
                errors.append(f"Missing directory: {claude_dir}")
            else:
                found_paths.append(claude_dir)

            if not self._filesystem.exists(commands_dir):
                errors.append(f"Missing directory: {commands_dir}")
            else:
                found_paths.append(commands_dir)

            if not self._filesystem.exists(claude_md):
                errors.append(f"Missing file: {claude_md}")
            else:
                found_paths.append(claude_md)

        # Check project config
        if project_dir is not None:
            claude_dir = project_dir / ".claude"
            claude_local_md = claude_dir / "CLAUDE.local.md"

            if not self._filesystem.exists(claude_dir):
                errors.append(f"Missing directory: {claude_dir}")
            else:
                found_paths.append(claude_dir)

            if not self._filesystem.exists(claude_local_md):
                errors.append(f"Missing file: {claude_local_md}")
            else:
                found_paths.append(claude_local_md)

        return SetupResult(
            success=len(errors) == 0,
            created_paths=found_paths,
            errors=errors,
        )
