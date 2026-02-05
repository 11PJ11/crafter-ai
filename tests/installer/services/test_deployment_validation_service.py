"""Tests for DeploymentValidationService.

This service validates that deployed assets match the IDE bundle
expectations: agent count, command count, template count, script count.
It also writes a manifest file and validates schema version.

Unit test strategy: Each test instantiates DeploymentValidationService,
calls its validate() method, and asserts outcomes. Tests use the
InMemoryFileSystemAdapter from conftest.py to avoid real filesystem operations.
"""

from __future__ import annotations

from dataclasses import FrozenInstanceError
from pathlib import Path

import pytest

from crafter_ai.installer.domain.deployment_validation_result import (
    DeploymentValidationResult,
)
from crafter_ai.installer.domain.ide_bundle_constants import (
    EXPECTED_AGENT_COUNT,
    EXPECTED_COMMAND_COUNT,
    EXPECTED_SCHEMA_PHASES,
    EXPECTED_SCHEMA_VERSION,
    EXPECTED_SCRIPT_COUNT,
    EXPECTED_TEMPLATE_COUNT,
)
from crafter_ai.installer.services.deployment_validation_service import (
    DeploymentValidationService,
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
def deployed_filesystem(
    mock_filesystem: InMemoryFileSystemAdapter, tmp_path: Path
) -> Path:
    """Create a correctly deployed filesystem structure with correct counts."""
    target = tmp_path / ".claude"
    agents_dir = target / "agents" / "nw"
    commands_dir = target / "commands" / "nw"
    templates_dir = target / "templates"
    scripts_dir = target / "scripts"

    mock_filesystem.mkdir(agents_dir, parents=True)
    mock_filesystem.mkdir(commands_dir, parents=True)
    mock_filesystem.mkdir(templates_dir, parents=True)
    mock_filesystem.mkdir(scripts_dir, parents=True)

    for i in range(EXPECTED_AGENT_COUNT):
        mock_filesystem.write_text(agents_dir / f"agent_{i}.md", f"agent {i}")
    for i in range(EXPECTED_COMMAND_COUNT):
        mock_filesystem.write_text(commands_dir / f"cmd_{i}.md", f"command {i}")
    for i in range(EXPECTED_TEMPLATE_COUNT):
        mock_filesystem.write_text(templates_dir / f"tpl_{i}.yaml", f"template: {i}")
    for i in range(EXPECTED_SCRIPT_COUNT):
        mock_filesystem.write_text(scripts_dir / f"script_{i}.py", f"script {i}")

    return target


# ═══════════════════════════════════════════════════════════════════════════════
# Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestDeploymentValidationService:
    """Tests for deployment validation service behavior."""

    def test_validates_agent_count_matches_bundle(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Deployed agent count (30) should match expected from bundle."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        result = service.validate(
            target_dir=deployed_filesystem,
            expected_agents=EXPECTED_AGENT_COUNT,
            expected_commands=EXPECTED_COMMAND_COUNT,
            expected_templates=EXPECTED_TEMPLATE_COUNT,
            expected_scripts=EXPECTED_SCRIPT_COUNT,
        )

        assert result.agent_count_match is True
        assert result.valid is True

    def test_validates_command_count_matches_bundle(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Deployed command count (23) should match expected from bundle."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        result = service.validate(
            target_dir=deployed_filesystem,
            expected_agents=EXPECTED_AGENT_COUNT,
            expected_commands=EXPECTED_COMMAND_COUNT,
            expected_templates=EXPECTED_TEMPLATE_COUNT,
            expected_scripts=EXPECTED_SCRIPT_COUNT,
        )

        assert result.command_count_match is True

    def test_validates_template_count(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Template count (17) should be validated from filesystem scan."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        result = service.validate(
            target_dir=deployed_filesystem,
            expected_agents=EXPECTED_AGENT_COUNT,
            expected_commands=EXPECTED_COMMAND_COUNT,
            expected_templates=EXPECTED_TEMPLATE_COUNT,
            expected_scripts=EXPECTED_SCRIPT_COUNT,
        )

        assert result.template_count_match is True

    def test_validates_script_count(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Script count (4) should be validated from filesystem scan."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        result = service.validate(
            target_dir=deployed_filesystem,
            expected_agents=EXPECTED_AGENT_COUNT,
            expected_commands=EXPECTED_COMMAND_COUNT,
            expected_templates=EXPECTED_TEMPLATE_COUNT,
            expected_scripts=EXPECTED_SCRIPT_COUNT,
        )

        assert result.script_count_match is True

    def test_validates_schema_version(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Schema version should be v3.0 per design YAML."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        result = service.validate(
            target_dir=deployed_filesystem,
            expected_agents=EXPECTED_AGENT_COUNT,
            expected_commands=EXPECTED_COMMAND_COUNT,
            expected_templates=EXPECTED_TEMPLATE_COUNT,
            expected_scripts=EXPECTED_SCRIPT_COUNT,
        )

        assert result.schema_version == EXPECTED_SCHEMA_VERSION

    def test_validates_schema_phases(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Schema should have 7 phases per design YAML."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        result = service.validate(
            target_dir=deployed_filesystem,
            expected_agents=EXPECTED_AGENT_COUNT,
            expected_commands=EXPECTED_COMMAND_COUNT,
            expected_templates=EXPECTED_TEMPLATE_COUNT,
            expected_scripts=EXPECTED_SCRIPT_COUNT,
        )

        assert result.schema_phases == EXPECTED_SCHEMA_PHASES

    def test_validation_on_empty_target(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        tmp_path: Path,
    ) -> None:
        """Validation should detect missing files when target is empty."""
        service = DeploymentValidationService(filesystem=mock_filesystem)
        empty_target = tmp_path / ".claude-empty"

        assert not mock_filesystem.exists(empty_target)

        result = service.validate(
            target_dir=empty_target,
            expected_agents=EXPECTED_AGENT_COUNT,
            expected_commands=EXPECTED_COMMAND_COUNT,
            expected_templates=EXPECTED_TEMPLATE_COUNT,
            expected_scripts=EXPECTED_SCRIPT_COUNT,
        )

        assert result.valid is False
        assert len(result.mismatches) > 0

    def test_validation_result_is_frozen_dataclass(self) -> None:
        """DeploymentValidationResult should be immutable (frozen dataclass)."""
        result = DeploymentValidationResult(
            valid=True,
            agent_count_match=True,
            command_count_match=True,
            template_count_match=True,
            script_count_match=True,
            manifest_written=True,
            schema_version=EXPECTED_SCHEMA_VERSION,
            schema_phases=EXPECTED_SCHEMA_PHASES,
            mismatches=[],
        )

        with pytest.raises(FrozenInstanceError):
            result.valid = False  # type: ignore[misc]
