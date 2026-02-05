"""Tests for IdeBundleBuildService.

This service builds the IDE bundle by scanning the nWave/ source directory,
copying agents, commands, templates, scripts to dist/ide/, counting
components, tracking YAML warnings and embed injections.

Unit test strategy: Each test instantiates IdeBundleBuildService, calls
its build() method, and asserts outcomes through the IdeBundleBuildResult
domain object. Tests use the InMemoryFileSystemAdapter from conftest.py
to avoid real filesystem operations.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from crafter_ai.installer.domain.ide_bundle_build_result import IdeBundleBuildResult
from crafter_ai.installer.domain.ide_bundle_constants import (
    EXPECTED_AGENT_COUNT,
    EXPECTED_COMMAND_COUNT,
    EXPECTED_SCRIPT_COUNT,
    EXPECTED_TEAM_COUNT,
    EXPECTED_TEMPLATE_COUNT,
)
from crafter_ai.installer.services.ide_bundle_build_service import (
    IdeBundleBuildService,
)
from tests.installer.conftest import InMemoryFileSystemAdapter


# ===============================================================================
# Fixtures
# ===============================================================================


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


# ===============================================================================
# Tests
# ===============================================================================


class TestIdeBundleBuildService:
    """Tests for IDE bundle build service behavior."""

    def test_build_produces_dist_ide_directory(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should create dist/ide/ output directory structure."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        result = service.build(source_dir=nwave_source_dir, output_dir=output_dir)

        assert result.success is True
        assert result.output_dir == output_dir

    def test_build_counts_agents_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count agents from nWave/agents/nw/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        result = service.build(source_dir=nwave_source_dir, output_dir=output_dir)

        assert result.agent_count == EXPECTED_AGENT_COUNT

    def test_build_counts_commands_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count commands from nWave/commands/nw/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        result = service.build(source_dir=nwave_source_dir, output_dir=output_dir)

        assert result.command_count == EXPECTED_COMMAND_COUNT

    def test_build_counts_templates_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count 17 templates from nWave/templates/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        result = service.build(source_dir=nwave_source_dir, output_dir=output_dir)

        assert result.template_count == EXPECTED_TEMPLATE_COUNT

    def test_build_counts_scripts_from_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Build should count 4 scripts from nWave/scripts/ scan."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        result = service.build(source_dir=nwave_source_dir, output_dir=output_dir)

        assert result.script_count == EXPECTED_SCRIPT_COUNT

    def test_build_team_count_zero_when_dir_missing(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        nwave_source_dir: Path,
    ) -> None:
        """Team count defaults to 0 when teams/ directory is missing."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        result = service.build(source_dir=nwave_source_dir, output_dir=output_dir)

        assert result.team_count == 0

    def test_build_fails_when_source_missing(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Build should fail with error when nWave/ directory is absent."""
        service = IdeBundleBuildService(filesystem=mock_filesystem)
        missing_source = Path("nonexistent/nWave")
        output_dir = Path("dist/ide")

        result = service.build(source_dir=missing_source, output_dir=output_dir)

        assert result.success is False
        assert result.error_message is not None

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
