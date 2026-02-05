"""Tests for AssetDeploymentService.

This service deploys IDE bundle assets from dist/ide/ to ~/.claude/,
copying agents, commands, templates, scripts, and config to their
correct destinations under the Claude configuration directory.

Unit test strategy: Each test instantiates AssetDeploymentService, calls
its deploy() method, and asserts outcomes. The service stub raises
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
DEPLOY_TARGET = Path.home() / ".claude"


# ═══════════════════════════════════════════════════════════════════════════════
# Result stub (until production class exists)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class AssetDeploymentResult:
    """Immutable result of asset deployment.

    Attributes:
        success: Whether deployment completed successfully.
        agents_deployed: Number of agent files deployed.
        commands_deployed: Number of command files deployed.
        templates_deployed: Number of template files deployed.
        scripts_deployed: Number of script files deployed.
        target_path: Deployment target directory (e.g. ~/.claude/).
        error_message: Error message if deployment failed.
    """

    success: bool
    agents_deployed: int
    commands_deployed: int
    templates_deployed: int
    scripts_deployed: int
    target_path: Path
    error_message: str | None = None


# ═══════════════════════════════════════════════════════════════════════════════
# Service Stub (NotImplementedError pattern for Outside-In TDD)
# ═══════════════════════════════════════════════════════════════════════════════


class AssetDeploymentService:
    """Service for deploying IDE bundle assets to ~/.claude/.

    Copies agents, commands, templates, scripts from dist/ide/
    to their correct destinations under the Claude config directory.
    """

    def __init__(self, filesystem: InMemoryFileSystemAdapter) -> None:
        self._filesystem = filesystem

    def deploy(self, source_dir: Path, target_dir: Path) -> AssetDeploymentResult:
        """Deploy IDE bundle assets to target directory.

        Args:
            source_dir: Path to dist/ide/ bundle directory.
            target_dir: Path to ~/.claude/ target directory.

        Returns:
            AssetDeploymentResult with deployment counts and status.

        Raises:
            PermissionError: If target directory is not writable.
        """
        raise NotImplementedError(
            "AssetDeploymentService.deploy() not yet implemented"
        )


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
    mock_filesystem.mkdir(source / "agents" / "nw", parents=True)
    mock_filesystem.mkdir(source / "commands" / "nw", parents=True)
    mock_filesystem.mkdir(source / "templates", parents=True)
    mock_filesystem.mkdir(source / "scripts", parents=True)

    # Create agent files (30 agents from design YAML)
    for i in range(EXPECTED_AGENT_COUNT):
        mock_filesystem.write_text(
            source / "agents" / "nw" / f"agent_{i}.md", f"agent {i}"
        )

    # Create command files (23 commands from design YAML)
    for i in range(EXPECTED_COMMAND_COUNT):
        mock_filesystem.write_text(
            source / "commands" / "nw" / f"cmd_{i}.md", f"command {i}"
        )

    # Create template files (17 templates from design YAML)
    for i in range(EXPECTED_TEMPLATE_COUNT):
        mock_filesystem.write_text(
            source / "templates" / f"tpl_{i}.yaml", f"template: {i}"
        )

    # Create script files (4 scripts from design YAML)
    for i in range(EXPECTED_SCRIPT_COUNT):
        mock_filesystem.write_text(
            source / "scripts" / f"script_{i}.py", f"script {i}"
        )

    # Include config.json as part of the bundle
    mock_filesystem.write_text(
        source / "agents" / "nw" / "config.json", '{"version": "1.0"}'
    )

    return source


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestAssetDeploymentService:
    """Tests for asset deployment service behavior.

    Each test calls the service's deploy() method. The service raises
    NotImplementedError until implemented, which proves the contract.
    When the developer implements deploy(), the tests will pass naturally.
    """

    def test_deploys_agents_to_claude_agents_nw(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Agents should be deployed to ~/.claude/agents/nw/."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        # Verify source has agents (fixture validation)
        source_agents = mock_filesystem.list_dir(ide_bundle_dir / "agents" / "nw")
        # Includes config.json, so count is EXPECTED_AGENT_COUNT + 1
        assert len(source_agents) >= EXPECTED_AGENT_COUNT

        with pytest.raises(
            NotImplementedError, match="AssetDeploymentService.deploy"
        ):
            service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

    def test_deploys_commands_to_claude_commands_nw(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Commands should be deployed to ~/.claude/commands/nw/."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        source_commands = mock_filesystem.list_dir(ide_bundle_dir / "commands" / "nw")
        assert len(source_commands) == EXPECTED_COMMAND_COUNT

        with pytest.raises(
            NotImplementedError, match="AssetDeploymentService.deploy"
        ):
            service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

    def test_deploys_templates_to_claude_templates(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Templates should be deployed to ~/.claude/templates/ (17 templates)."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        source_templates = mock_filesystem.list_dir(ide_bundle_dir / "templates")
        assert len(source_templates) == EXPECTED_TEMPLATE_COUNT, (
            f"Design YAML specifies {EXPECTED_TEMPLATE_COUNT} templates"
        )

        with pytest.raises(
            NotImplementedError, match="AssetDeploymentService.deploy"
        ):
            service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

    def test_deploys_scripts_to_claude_scripts(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Scripts should be deployed to ~/.claude/scripts/ (4 scripts)."""
        service = AssetDeploymentService(filesystem=mock_filesystem)

        source_scripts = mock_filesystem.list_dir(ide_bundle_dir / "scripts")
        assert len(source_scripts) == EXPECTED_SCRIPT_COUNT, (
            f"Design YAML specifies {EXPECTED_SCRIPT_COUNT} scripts"
        )

        with pytest.raises(
            NotImplementedError, match="AssetDeploymentService.deploy"
        ):
            service.deploy(source_dir=ide_bundle_dir, target_dir=DEPLOY_TARGET)

    def test_deploy_target_is_claude_directory(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
    ) -> None:
        """Deploy target should be ~/.claude/ directory."""
        service = AssetDeploymentService(filesystem=mock_filesystem)
        expected_target = Path.home() / ".claude"

        with pytest.raises(
            NotImplementedError, match="AssetDeploymentService.deploy"
        ):
            service.deploy(source_dir=ide_bundle_dir, target_dir=expected_target)

    def test_deployment_accepts_custom_target(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        ide_bundle_dir: Path,
        tmp_path: Path,
    ) -> None:
        """Deployment should accept custom target directory for testing."""
        service = AssetDeploymentService(filesystem=mock_filesystem)
        custom_target = tmp_path / ".claude-test"

        with pytest.raises(
            NotImplementedError, match="AssetDeploymentService.deploy"
        ):
            service.deploy(source_dir=ide_bundle_dir, target_dir=custom_target)

    def test_deployment_fails_on_missing_source(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Deployment should fail if source directory does not exist."""
        service = AssetDeploymentService(filesystem=mock_filesystem)
        missing_source = Path("nonexistent/dist/ide")

        assert not mock_filesystem.exists(missing_source)

        with pytest.raises(
            NotImplementedError, match="AssetDeploymentService.deploy"
        ):
            service.deploy(source_dir=missing_source, target_dir=DEPLOY_TARGET)

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
