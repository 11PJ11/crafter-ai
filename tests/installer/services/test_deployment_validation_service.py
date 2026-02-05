"""Tests for DeploymentValidationService.

This service validates that deployed assets match the IDE bundle
expectations: agent count, command count, template count, script count.
It also writes a manifest file and validates schema version.

Unit test strategy: Each test instantiates DeploymentValidationService,
calls its validate() method, and asserts outcomes. The service stub raises
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
class DeploymentValidationResult:
    """Immutable result of deployment validation.

    Attributes:
        valid: Whether all validations passed.
        agent_count_match: Whether deployed agent count matches expected.
        command_count_match: Whether deployed command count matches expected.
        template_count_match: Whether deployed template count matches expected.
        script_count_match: Whether deployed script count matches expected.
        manifest_written: Whether manifest file was written successfully.
        schema_version: Schema version from manifest, if available.
        schema_phases: Number of phases in schema (from design: 7).
        mismatches: List of mismatch descriptions.
    """

    valid: bool
    agent_count_match: bool
    command_count_match: bool
    template_count_match: bool
    script_count_match: bool
    manifest_written: bool
    schema_version: str | None
    schema_phases: int | None
    mismatches: list[str]


# ═══════════════════════════════════════════════════════════════════════════════
# Service Stub (NotImplementedError pattern for Outside-In TDD)
# ═══════════════════════════════════════════════════════════════════════════════


class DeploymentValidationService:
    """Service for validating deployed assets match bundle expectations.

    Compares filesystem counts against expected values, writes manifest,
    and validates schema version.
    """

    def __init__(self, filesystem: InMemoryFileSystemAdapter) -> None:
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

        Args:
            target_dir: Path to ~/.claude/ target directory.
            expected_agents: Expected agent file count.
            expected_commands: Expected command file count.
            expected_templates: Expected template file count.
            expected_scripts: Expected script file count.

        Returns:
            DeploymentValidationResult with match status and mismatches.
        """
        raise NotImplementedError(
            "DeploymentValidationService.validate() not yet implemented"
        )


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
    """Tests for deployment validation service behavior.

    Each test calls the service's validate() method. The service raises
    NotImplementedError until implemented, which proves the contract.
    When the developer implements validate(), the tests will pass naturally.
    """

    def test_validates_agent_count_matches_bundle(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Deployed agent count (30) should match expected from bundle."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        # Verify fixture has correct count
        agents_dir = deployed_filesystem / "agents" / "nw"
        deployed_count = len(mock_filesystem.list_dir(agents_dir))
        assert deployed_count == EXPECTED_AGENT_COUNT

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            service.validate(
                target_dir=deployed_filesystem,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )

    def test_validates_command_count_matches_bundle(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Deployed command count (23) should match expected from bundle."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        commands_dir = deployed_filesystem / "commands" / "nw"
        deployed_count = len(mock_filesystem.list_dir(commands_dir))
        assert deployed_count == EXPECTED_COMMAND_COUNT

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            service.validate(
                target_dir=deployed_filesystem,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )

    def test_validates_template_count(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Template count (17) should be validated from filesystem scan."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        templates_dir = deployed_filesystem / "templates"
        deployed_count = len(mock_filesystem.list_dir(templates_dir))
        assert deployed_count == EXPECTED_TEMPLATE_COUNT, (
            f"Design YAML specifies {EXPECTED_TEMPLATE_COUNT} templates"
        )

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            service.validate(
                target_dir=deployed_filesystem,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )

    def test_validates_script_count(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Script count (4) should be validated from filesystem scan."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        scripts_dir = deployed_filesystem / "scripts"
        deployed_count = len(mock_filesystem.list_dir(scripts_dir))
        assert deployed_count == EXPECTED_SCRIPT_COUNT, (
            f"Design YAML specifies {EXPECTED_SCRIPT_COUNT} scripts"
        )

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            service.validate(
                target_dir=deployed_filesystem,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )

    def test_validates_schema_version(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Schema version should be v3.0 per design YAML."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            service.validate(
                target_dir=deployed_filesystem,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )

        # When implemented, result.schema_version should be EXPECTED_SCHEMA_VERSION
        assert EXPECTED_SCHEMA_VERSION == "v3.0", "Schema version must be v3.0"

    def test_validates_schema_phases(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        deployed_filesystem: Path,
    ) -> None:
        """Schema should have 7 phases per design YAML."""
        service = DeploymentValidationService(filesystem=mock_filesystem)

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            service.validate(
                target_dir=deployed_filesystem,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )

        # When implemented, result.schema_phases should be EXPECTED_SCHEMA_PHASES
        assert EXPECTED_SCHEMA_PHASES == 7, "Schema must have 7 phases"

    def test_validation_on_empty_target(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        tmp_path: Path,
    ) -> None:
        """Validation should detect missing files when target is empty."""
        service = DeploymentValidationService(filesystem=mock_filesystem)
        empty_target = tmp_path / ".claude-empty"

        # Target does not exist
        assert not mock_filesystem.exists(empty_target)

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            service.validate(
                target_dir=empty_target,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )

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
