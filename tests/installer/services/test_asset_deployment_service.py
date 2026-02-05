"""Tests for AssetDeploymentService.

This service deploys IDE bundle assets from dist/ide/ to ~/.claude/,
copying agents, commands, templates, scripts, and config to their
correct destinations under the Claude configuration directory.

Unit test strategy: Each test instantiates AssetDeploymentService, calls
its deploy() method, and asserts outcomes via the AssetDeploymentResult
domain value object.

These tests use the InMemoryFileSystemAdapter from conftest.py to
avoid real filesystem operations.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from crafter_ai.installer.domain.asset_deployment_result import AssetDeploymentResult
from crafter_ai.installer.domain.ide_bundle_constants import (
    EXPECTED_AGENT_COUNT,
    EXPECTED_COMMAND_COUNT,
    EXPECTED_SCRIPT_COUNT,
    EXPECTED_TEMPLATE_COUNT,
)
from crafter_ai.installer.services.asset_deployment_service import (
    AssetDeploymentService,
)
from tests.installer.conftest import InMemoryFileSystemAdapter


# ═══════════════════════════════════════════════════════════════════════════════
# Shared Constants
# ═══════════════════════════════════════════════════════════════════════════════

DEPLOY_TARGET = Path.home() / ".claude"


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_filesystem() -> InMemoryFileSystemAdapter:
    """Provide in-memory filesystem for isolated testing."""
    return InMemoryFileSystemAdapter()


@pytest.fixture
def ide_bundle_dir(mock_filesystem: InMemoryFileSystemAdapter) -> Path:
    """Set up a mock IDE bundle source directory with correct component counts."""
    source = Path("dist/ide")
    mock_filesystem.mkdir(source / "agents", parents=True)
    mock_filesystem.mkdir(source / "tasks" / "nw", parents=True)
    mock_filesystem.mkdir(source / "templates", parents=True)
    mock_filesystem.mkdir(source / "scripts", parents=True)

    # Create agent files (30 agents from design YAML)
    for i in range(EXPECTED_AGENT_COUNT):
        mock_filesystem.write_text(
            source / "agents" / f"agent_{i}.md", f"agent {i}"
        )

    # Create command files (23 commands from design YAML)
    for i in range(EXPECTED_COMMAND_COUNT):
        mock_filesystem.write_text(
            source / "tasks" / "nw" / f"cmd_{i}.md", f"command {i}"
        )

    # Create template files (17 templates from design YAML)
    for i in range(EXPECTED_TEMPLATE_COUNT):
        mock_filesystem.write_text(
            source / "templates" / f"tpl_{i}.yaml", f"template: {i}"
        )

    # Create script files (4 scripts from design YAML)
    for i in range(EXPECTED_SCRIPT_COUNT):
        mock_filesystem.write_text(source / "scripts" / f"script_{i}.py", f"script {i}")

    # Include config.json as part of the bundle
    mock_filesystem.write_text(
        source / "agents" / "config.json", '{"version": "1.0"}'
    )

    return source


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAssetDeploymentService:
    """Tests for asset deployment service behavior.

    Each test calls the service's deploy() method and asserts outcomes
    through the AssetDeploymentResult domain value object.
    """

    def test_deploys_agents_to_claude_agents_nw(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Agents should be deployed to ~/.claude/agents/nw/."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        result = service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

        # Fixture adds config.json to agents/nw, so count >= EXPECTED_AGENT_COUNT
        assert result.agents_deployed >= EXPECTED_AGENT_COUNT

    def test_deploys_commands_to_claude_commands_nw(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Commands should be deployed to ~/.claude/commands/nw/."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        result = service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

        assert result.commands_deployed == EXPECTED_COMMAND_COUNT

    def test_deploys_templates_to_claude_templates(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Templates should be deployed to ~/.claude/templates/ (17 templates)."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        result = service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

        assert result.templates_deployed == EXPECTED_TEMPLATE_COUNT, (
            f"Design YAML specifies {EXPECTED_TEMPLATE_COUNT} templates"
        )

    def test_deploys_scripts_to_claude_scripts(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Scripts should be deployed to ~/.claude/scripts/ (4 scripts)."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        result = service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

        assert result.scripts_deployed == EXPECTED_SCRIPT_COUNT, (
            f"Design YAML specifies {EXPECTED_SCRIPT_COUNT} scripts"
        )

    def test_deploy_target_is_claude_directory(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Deploy target should be ~/.claude/ directory."""
        service = AssetDeploymentService(filesystem=mock_filesystem)
        expected_target = Path.home() / ".claude"

        result = service.deploy(source_dir=ide_bundle_dir, target_dir=expected_target)

        assert result.target_path == expected_target
        assert result.success is True

    def test_deployment_accepts_custom_target(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
        tmp_path: Path,
    ) -> None:
        """Deployment should accept custom target directory for testing."""
        service = AssetDeploymentService(filesystem=mock_filesystem)
        custom_target = tmp_path / ".claude-test"

        result = service.deploy(source_dir=ide_bundle_dir, target_dir=custom_target)

        assert result.success is True

    def test_deployment_fails_on_missing_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Deployment should fail if source directory does not exist."""
        service = AssetDeploymentService(filesystem=mock_filesystem)
        missing_source = Path("nonexistent/dist/ide")

        assert not mock_filesystem.exists(missing_source)

        result = service.deploy(source_dir=missing_source, target_dir=DEPLOY_TARGET)

        assert result.success is False
        assert result.error_message is not None

    def test_deployment_result_is_frozen_dataclass(self) -> None:
        """AssetDeploymentResult should be immutable (frozen dataclass)."""
        result = AssetDeploymentResult(
            success=True,
            agents_deployed=EXPECTED_AGENT_COUNT,
            commands_deployed=EXPECTED_COMMAND_COUNT,
            templates_deployed=EXPECTED_TEMPLATE_COUNT,
            scripts_deployed=EXPECTED_SCRIPT_COUNT,
            target_path=DEPLOY_TARGET,
        )

        with pytest.raises(FrozenInstanceError):
            result.agents_deployed = 99  # type: ignore[misc]
