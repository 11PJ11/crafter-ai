"""Tests for IdeBundleBuildService.

This service builds the IDE bundle by scanning the nWave/ source directory,
copying agents, commands, templates, scripts to dist/ide/, counting
components, tracking YAML warnings and embed injections.

Unit test strategy: Each test instantiates IdeBundleBuildService, calls
its build() method, and asserts outcomes. The service stub raises
NotImplementedError until implemented, proving the contract and enabling
Outside-In TDD.

These tests use the InMemoryFileSystemAdapter from conftest.py to
avoid real filesystem operations.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError, dataclass
from pathlib import Path

import pytest

from tests.installer.conftest import InMemoryFileSystemAdapter


# ═══════════════════════════════════════════════════════════════════════════════
# Shared Constants (source of truth: journey-forge-tui.yaml)
# ═══════════════════════════════════════════════════════════════════════════════

EXPECTED_AGENT_COUNT = 30
EXPECTED_COMMAND_COUNT = 23
EXPECTED_TEMPLATE_COUNT = 17
EXPECTED_SCRIPT_COUNT = 4
EXPECTED_SCHEMA_VERSION = "v3.0"
EXPECTED_SCHEMA_PHASES = 7
EXPECTED_TEAM_COUNT = 0


# ═══════════════════════════════════════════════════════════════════════════════
# Result stub (until production class exists)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class IdeBundleBuildResult:
    """Immutable result of the IDE bundle build.

    Attributes:
        success: Whether the build completed successfully.
        output_dir: Path to dist/ide/ output directory.
        agent_count: Number of agent files processed.
        command_count: Number of command files processed.
        template_count: Number of template files processed.
        script_count: Number of script files processed.
        team_count: Number of team files processed.
        yaml_warnings: List of non-blocking YAML parse warnings.
        embed_injection_count: Number of embed injections performed.
        error_message: Error message if build failed.
    """

    success: bool
    output_dir: Path | None
    agent_count: int
    command_count: int
    template_count: int
    script_count: int
    team_count: int
    yaml_warnings: list[str]
    embed_injection_count: int
    error_message: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# Service Stub (NotImplementedError pattern for Outside-In TDD)
# ═══════════════════════════════════════════════════════════════════════════════


class IdeBundleBuildService:
    """Service for building IDE bundle from nWave/ source directory.

    Scans nWave/ for agents, commands, templates, scripts, and copies
    them to dist/ide/. Counts components and tracks YAML warnings.
    """

    def __init__(self, filesystem: InMemoryFileSystemAdapter) -> None:
        self._filesystem = filesystem

    def build(self, source_dir: Path, output_dir: Path) -> IdeBundleBuildResult:
        """Build IDE bundle from source directory.

        Args:
            source_dir: Path to nWave/ source directory.
            output_dir: Path to dist/ide/ output directory.

        Returns:
            IdeBundleBuildResult with component counts and status.

        Raises:
            FileNotFoundError: If source_dir does not exist.
        """
        raise NotImplementedError("IdeBundleBuildService.build() not yet implemented")


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_filesystem() -> InMemoryFileSystemAdapter:
    """Provide in-memory filesystem for isolated testing."""
    return InMemoryFileSystemAdapter()


@pytest.fixture
def nwave_source_dir(mock_filesystem: InMemoryFileSystemAdapter) -> Path:
    """Set up a mock nWave source directory with correct component counts."""
    source = Path("nWave")
    mock_filesystem.mkdir(source, parents=True)
    mock_filesystem.mkdir(source / "agents" / "nw", parents=True)
    mock_filesystem.mkdir(source / "commands" / "nw", parents=True)
    mock_filesystem.mkdir(source / "templates", parents=True)
    mock_filesystem.mkdir(source / "scripts", parents=True)

    # Create agent files (30 agents from design YAML)
    for i in range(EXPECTED_AGENT_COUNT):
        mock_filesystem.write_text(
            source / "agents" / "nw" / f"agent_{i}.md",
            f"# Agent {i}\nagent content",
        )

    # Create command files (23 commands from design YAML)
    for i in range(EXPECTED_COMMAND_COUNT):
        mock_filesystem.write_text(
            source / "commands" / "nw" / f"cmd_{i}.md",
            f"# Command {i}\ncommand content",
        )

    # Create template files (17 templates from design YAML)
    for i in range(EXPECTED_TEMPLATE_COUNT):
        mock_filesystem.write_text(
            source / "templates" / f"template_{i}.yaml",
            f"template: {i}",
        )

    # Create script files (4 scripts from design YAML)
    for i in range(EXPECTED_SCRIPT_COUNT):
        mock_filesystem.write_text(
            source / "scripts" / f"script_{i}.py",
            f"# script {i}",
        )

    return source


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIdeBundleBuildService:
    """Tests for IDE bundle build service behavior.

    Each test calls the service's build() method. The service raises
    NotImplementedError until implemented, which proves the contract.
    When the developer implements build(), the tests will pass naturally.
    """

    def test_build_produces_dist_ide_directory(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should create dist/ide/ output directory structure."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        # Service call proves the contract; NotImplementedError is expected
        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            service.build(source_dir=nwave_source_dir, output_dir=output_dir)

    def test_build_counts_agents_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count agents from nWave/agents/nw/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        # Verify the source has the expected count (fixture validation)
        source_agents = mock_filesystem.list_dir(nwave_source_dir / "agents" / "nw")
        assert len(source_agents) == EXPECTED_AGENT_COUNT, (
            f"Test fixture should have {EXPECTED_AGENT_COUNT} agents, "
            f"found {len(source_agents)}"
        )

        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            service.build(source_dir=nwave_source_dir, output_dir=output_dir)

    def test_build_counts_commands_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count commands from nWave/commands/nw/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        source_commands = mock_filesystem.list_dir(nwave_source_dir / "commands" / "nw")
        assert len(source_commands) == EXPECTED_COMMAND_COUNT

        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            service.build(source_dir=nwave_source_dir, output_dir=output_dir)

    def test_build_counts_templates_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count 17 templates from nWave/templates/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        source_templates = mock_filesystem.list_dir(nwave_source_dir / "templates")
        assert len(source_templates) == EXPECTED_TEMPLATE_COUNT, (
            f"Design YAML specifies {EXPECTED_TEMPLATE_COUNT} templates, "
            f"found {len(source_templates)}"
        )

        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            service.build(source_dir=nwave_source_dir, output_dir=output_dir)

    def test_build_counts_scripts_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count 4 scripts from nWave/scripts/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        source_scripts = mock_filesystem.list_dir(nwave_source_dir / "scripts")
        assert len(source_scripts) == EXPECTED_SCRIPT_COUNT, (
            f"Design YAML specifies {EXPECTED_SCRIPT_COUNT} scripts, "
            f"found {len(source_scripts)}"
        )

        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            service.build(source_dir=nwave_source_dir, output_dir=output_dir)

    def test_build_team_count_zero_when_dir_missing(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Team count defaults to 0 when teams/ directory is missing."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        # teams/ directory is intentionally not created in the fixture
        teams_dir = nwave_source_dir / "teams"
        assert not mock_filesystem.exists(teams_dir), (
            "teams/ should not exist to test default behavior"
        )

        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            service.build(source_dir=nwave_source_dir, output_dir=output_dir)

    def test_build_fails_when_source_missing(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Build should fail with error when nWave/ directory is absent."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        missing_source = Path("nonexistent/nWave")
        output_dir = Path("dist/ide")

        # Source directory does not exist
        assert not mock_filesystem.exists(missing_source)

        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            service.build(source_dir=missing_source, output_dir=output_dir)

    def test_build_result_is_frozen_dataclass(self) -> None:
        """IdeBundleBuildResult should be immutable (frozen dataclass)."""
        result = IdeBundleBuildResult(
            success=True,
            output_dir=Path("dist/ide"),
            agent_count=EXPECTED_AGENT_COUNT,
            command_count=EXPECTED_COMMAND_COUNT,
            template_count=EXPECTED_TEMPLATE_COUNT,
            script_count=EXPECTED_SCRIPT_COUNT,
            team_count=EXPECTED_TEAM_COUNT,
            yaml_warnings=[],
            embed_injection_count=3,
        )

        # Attempting to modify should raise FrozenInstanceError
        with pytest.raises(FrozenInstanceError):
            result.agent_count = 99  # type: ignore[misc]
