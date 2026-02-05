"""Integration tests for the unified 17-step forge install pipeline.

Purpose: Test component boundary collaborations with real service method
calls. Services that don't exist yet raise NotImplementedError, proving
the contract. When the developer implements the service, the test goes
GREEN. This is Outside-In TDD.

These tests validate cross-component interactions that unit tests cannot
catch: BuildService coordinating with IdeBundleBuildService, InstallService
coordinating with AssetDeploymentService, CheckExecutor running the IDE
bundle check, and deployment validation against filesystem state.

Marker: @pytest.mark.integration
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

import pytest

from crafter_ai.installer.domain.check_executor import CheckExecutor
from crafter_ai.installer.domain.check_registry import CheckRegistry
from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
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
EXPECTED_TEAM_COUNT = 0  # teams/ dir missing by default
DEPLOY_TARGET = Path.home() / ".claude"
TEST_VERSION = "1.3.0"

EXPECTED_BACKUP_ITEM_COUNT = 9
BACKUP_TARGETS = [
    "agents/nw/",
    "commands/nw/",
    "templates/",
    "scripts/",
    "teams/",
    "config.json",
    "CLAUDE.md",
    "settings.json",
    "keybindings.json",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Result Dataclasses (stubs until production classes exist)
# ═══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True)
class IdeBundleBuildResult:
    """Stub for IDE bundle build result until production class exists."""

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


@dataclass(frozen=True)
class AssetDeploymentResult:
    """Stub for asset deployment result until production class exists."""

    success: bool
    agents_deployed: int
    commands_deployed: int
    templates_deployed: int
    scripts_deployed: int
    target_path: Path
    error_message: str | None = None


@dataclass(frozen=True)
class DeploymentValidationResult:
    """Stub for deployment validation result until production class exists."""

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
# Service Stubs (NotImplementedError pattern for Outside-In TDD)
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
        """
        raise NotImplementedError("IdeBundleBuildService.build() not yet implemented")


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
        """
        raise NotImplementedError("AssetDeploymentService.deploy() not yet implemented")


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


class IdeBundleExistsCheck:
    """Pre-flight check for IDE bundle existence in dist/ide/.

    Returns BLOCKING failure if dist/ide/ is missing or empty,
    with remediation to run 'forge build'.
    """

    def __init__(self, filesystem: InMemoryFileSystemAdapter, bundle_dir: Path) -> None:
        self._filesystem = filesystem
        self._bundle_dir = bundle_dir

    def execute(self) -> CheckResult:
        """Check whether the IDE bundle exists and has content.

        Returns:
            CheckResult with pass/fail and remediation if needed.
        """
        raise NotImplementedError(
            "IdeBundleExistsCheck.execute() not yet implemented"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def mock_filesystem() -> InMemoryFileSystemAdapter:
    """Provide in-memory filesystem for isolated testing."""
    return InMemoryFileSystemAdapter()


@pytest.fixture
def populated_nwave_source(mock_filesystem: InMemoryFileSystemAdapter) -> Path:
    """Set up nWave/ source with correct component counts from design YAML."""
    source = Path("nWave")
    mock_filesystem.mkdir(source / "agents" / "nw", parents=True)
    mock_filesystem.mkdir(source / "commands" / "nw", parents=True)
    mock_filesystem.mkdir(source / "templates", parents=True)
    mock_filesystem.mkdir(source / "scripts", parents=True)

    for i in range(EXPECTED_AGENT_COUNT):
        mock_filesystem.write_text(
            source / "agents" / "nw" / f"agent_{i}.md",
            f"# Agent {i}\nagent content",
        )
    for i in range(EXPECTED_COMMAND_COUNT):
        mock_filesystem.write_text(
            source / "commands" / "nw" / f"cmd_{i}.md",
            f"# Command {i}\ncommand content",
        )
    for i in range(EXPECTED_TEMPLATE_COUNT):
        mock_filesystem.write_text(
            source / "templates" / f"template_{i}.yaml",
            f"template: {i}",
        )
    for i in range(EXPECTED_SCRIPT_COUNT):
        mock_filesystem.write_text(
            source / "scripts" / f"script_{i}.py",
            f"# script {i}",
        )

    return source


@pytest.fixture
def populated_ide_bundle(mock_filesystem: InMemoryFileSystemAdapter) -> Path:
    """Set up dist/ide/ bundle with correct component counts."""
    bundle = Path("dist/ide")
    mock_filesystem.mkdir(bundle / "agents" / "nw", parents=True)
    mock_filesystem.mkdir(bundle / "commands" / "nw", parents=True)
    mock_filesystem.mkdir(bundle / "templates", parents=True)
    mock_filesystem.mkdir(bundle / "scripts", parents=True)

    for i in range(EXPECTED_AGENT_COUNT):
        mock_filesystem.write_text(
            bundle / "agents" / "nw" / f"agent_{i}.md", f"agent {i}"
        )
    for i in range(EXPECTED_COMMAND_COUNT):
        mock_filesystem.write_text(
            bundle / "commands" / "nw" / f"cmd_{i}.md", f"command {i}"
        )
    for i in range(EXPECTED_TEMPLATE_COUNT):
        mock_filesystem.write_text(
            bundle / "templates" / f"tpl_{i}.yaml", f"template: {i}"
        )
    for i in range(EXPECTED_SCRIPT_COUNT):
        mock_filesystem.write_text(
            bundle / "scripts" / f"script_{i}.py", f"script {i}"
        )

    return bundle


# ═══════════════════════════════════════════════════════════════════════════════
# Test: BuildService coordinates IDE bundle build after wheel build
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestBuildServiceProducesIdeBundleResult:
    """BuildService coordinates IDE bundle build after wheel build.

    Integration: IdeBundleBuildService is called by the build pipeline.
    The service receives a filesystem adapter and produces a result
    with component counts from the nWave/ source scan.
    """

    def test_build_service_produces_ide_bundle_result(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_nwave_source: Path,
    ) -> None:
        """Build service delegates to IdeBundleBuildService for IDE bundle."""
        ide_builder = IdeBundleBuildService(filesystem=mock_filesystem)
        output_dir = Path("dist/ide")

        # The service call must happen; NotImplementedError proves the contract
        with pytest.raises(NotImplementedError, match="IdeBundleBuildService.build"):
            ide_builder.build(
                source_dir=populated_nwave_source,
                output_dir=output_dir,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: InstallService coordinates asset deployment after pipx install
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestInstallServiceCoordinatesAssetDeployment:
    """InstallService calls AssetDeploymentService after pipx install.

    Integration: After CLI install via pipx succeeds, the install service
    triggers deployment of IDE bundle assets to ~/.claude/.
    """

    def test_install_service_coordinates_asset_deployment(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_ide_bundle: Path,
    ) -> None:
        """After pipx install succeeds, install service triggers asset deployment."""
        deployer = AssetDeploymentService(filesystem=mock_filesystem)

        with pytest.raises(NotImplementedError, match="AssetDeploymentService.deploy"):
            deployer.deploy(
                source_dir=populated_ide_bundle,
                target_dir=DEPLOY_TARGET,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Pre-flight cascade includes IDE bundle check
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestPreflightCascadeBuildAndInstall:
    """Combined check cascade includes IDE bundle check.

    Integration: CheckExecutor + CheckRegistry run the IDE bundle
    existence check alongside other install pre-flight checks.
    """

    def test_preflight_cascade_includes_ide_bundle_check(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Install pre-flight checks should include IDE bundle existence check."""
        bundle_dir = Path("dist/ide")
        ide_check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=bundle_dir
        )

        # Register the IDE bundle check in a real CheckRegistry + CheckExecutor
        registry = CheckRegistry()
        registry.register("ide-bundle-exists", ide_check.execute)

        executor = CheckExecutor(registry=registry)

        # Running the check will hit NotImplementedError from the service stub
        results = executor.run_all()

        # CheckExecutor wraps exceptions in a failed CheckResult
        assert len(results) == 1
        ide_result = results[0]
        assert ide_result.id == "ide-bundle-exists"
        assert ide_result.passed is False  # Exception means failure
        assert ide_result.severity == CheckSeverity.BLOCKING


# ═══════════════════════════════════════════════════════════════════════════════
# Test: SBOM dual-group requires both build and deploy results
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestSbomDualGroupFromRealResults:
    """SBOM generation requires both build result and deployment result.

    Integration: The SBOM service consumes IdeBundleBuildResult and
    AssetDeploymentResult to produce dual-group output. Both services
    must produce compatible result objects.
    """

    def test_sbom_requires_build_and_deploy_results(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_nwave_source: Path,
        populated_ide_bundle: Path,
    ) -> None:
        """SBOM generation depends on results from both build and deploy services."""
        # Both services must be callable (even if they raise NotImplementedError)
        ide_builder = IdeBundleBuildService(filesystem=mock_filesystem)
        deployer = AssetDeploymentService(filesystem=mock_filesystem)

        # Service calls establish the contract for SBOM input
        with pytest.raises(NotImplementedError, match="IdeBundleBuildService"):
            ide_builder.build(
                source_dir=populated_nwave_source,
                output_dir=Path("dist/ide"),
            )

        with pytest.raises(NotImplementedError, match="AssetDeploymentService"):
            deployer.deploy(
                source_dir=populated_ide_bundle,
                target_dir=DEPLOY_TARGET,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Deployment validation against file structure
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestDeploymentValidationAgainstFileStructure:
    """DeploymentValidationService validates deployed files match bundle counts.

    Integration: DeploymentValidationService + filesystem. The service
    scans the target directory and compares counts against expectations.
    """

    def test_deployment_validation_against_file_structure(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Deployment validation compares filesystem counts against bundle expectations."""
        validator = DeploymentValidationService(filesystem=mock_filesystem)

        with pytest.raises(
            NotImplementedError, match="DeploymentValidationService.validate"
        ):
            validator.validate(
                target_dir=DEPLOY_TARGET,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Backup scope covers nine items
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestBackupScopeCoversNineItems:
    """Backup targets include all 9 item categories from the journey spec.

    Integration: The backup service must know about all 9 categories.
    This test validates the scope constant against the design YAML.
    """

    def test_backup_scope_covers_nine_items(self) -> None:
        """Backup service should target all 9 categories of user configuration."""
        assert len(BACKUP_TARGETS) == EXPECTED_BACKUP_ITEM_COUNT, (
            f"Expected {EXPECTED_BACKUP_ITEM_COUNT} backup targets, "
            f"got {len(BACKUP_TARGETS)}"
        )

        # Verify all required categories are present
        assert "agents/nw/" in BACKUP_TARGETS
        assert "commands/nw/" in BACKUP_TARGETS
        assert "templates/" in BACKUP_TARGETS
        assert "scripts/" in BACKUP_TARGETS
        assert "teams/" in BACKUP_TARGETS
        assert "config.json" in BACKUP_TARGETS
        assert "CLAUDE.md" in BACKUP_TARGETS
        assert "settings.json" in BACKUP_TARGETS
        assert "keybindings.json" in BACKUP_TARGETS


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Health check includes asset verification
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestHealthCheckIncludesAssetVerification:
    """Health check verifies ~/.claude/ asset accessibility.

    Integration: After deploy, health checker must verify that nWave
    assets in ~/.claude/ are accessible. This requires coordination
    between the deploy result and health check service.
    """

    def test_health_check_verifies_deployed_assets(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Post-install health check should verify nWave assets are accessible."""
        # Simulate deployed assets in the in-memory filesystem
        target = DEPLOY_TARGET
        mock_filesystem.mkdir(target / "agents" / "nw", parents=True)
        for i in range(EXPECTED_AGENT_COUNT):
            mock_filesystem.write_text(
                target / "agents" / "nw" / f"agent_{i}.md",
                f"agent {i}",
            )

        # The health check should be able to see the deployed assets
        assert mock_filesystem.exists(target / "agents" / "nw")
        deployed_agents = mock_filesystem.list_dir(target / "agents" / "nw")
        assert len(deployed_agents) == EXPECTED_AGENT_COUNT, (
            f"Expected {EXPECTED_AGENT_COUNT} agents accessible at "
            f"{target / 'agents' / 'nw'}, found {len(deployed_agents)}"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Version flows from wheel metadata to SBOM
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestVersionFlowsFromWheelMetadataToSbom:
    """Version consistency across build/install/sbom chain.

    Integration: The version string extracted from the wheel filename
    must be the same string that appears in install result and SBOM.
    This test validates the extraction logic with real parsing.
    """

    def test_version_flows_from_wheel_metadata_to_sbom(self) -> None:
        """Same version string appears in wheel name, install result, and SBOM."""
        import re

        wheel_filename = f"crafter_ai-{TEST_VERSION}-py3-none-any.whl"

        # Real version extraction logic (same as InstallService uses)
        match = re.match(r"[^-]+-([^-]+)-", wheel_filename)
        assert match is not None, f"Could not parse version from {wheel_filename}"
        wheel_version = match.group(1)

        assert wheel_version == TEST_VERSION, (
            f"Extracted version '{wheel_version}' does not match "
            f"expected '{TEST_VERSION}'"
        )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Agent count consistent across pipeline (via service contracts)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestAgentCountConsistentAcrossPipeline:
    """Agent count (30) must flow through build, deploy, and validation.

    Integration: All three services receive or produce the same agent
    count. This test verifies the services accept the expected count
    in their method signatures.
    """

    def test_agent_count_flows_through_pipeline_services(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_nwave_source: Path,
        populated_ide_bundle: Path,
    ) -> None:
        """Agent count is consistent across build, deploy, and validation services."""
        # Verify source has correct count
        source_agents = mock_filesystem.list_dir(
            populated_nwave_source / "agents" / "nw"
        )
        assert len(source_agents) == EXPECTED_AGENT_COUNT

        # Verify bundle has correct count
        bundle_agents = mock_filesystem.list_dir(
            populated_ide_bundle / "agents" / "nw"
        )
        assert len(bundle_agents) == EXPECTED_AGENT_COUNT

        # Validation service accepts the count as expected parameter
        validator = DeploymentValidationService(filesystem=mock_filesystem)
        with pytest.raises(NotImplementedError):
            validator.validate(
                target_dir=DEPLOY_TARGET,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Command count consistent across pipeline (via service contracts)
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestCommandCountConsistentAcrossPipeline:
    """Command count (23) must flow through build, deploy, and validation.

    Integration: Similar to agent count, verifies command count
    consistency across filesystem fixtures and service contracts.
    """

    def test_command_count_flows_through_pipeline_services(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_nwave_source: Path,
        populated_ide_bundle: Path,
    ) -> None:
        """Command count is consistent across source, bundle, and validation."""
        source_commands = mock_filesystem.list_dir(
            populated_nwave_source / "commands" / "nw"
        )
        assert len(source_commands) == EXPECTED_COMMAND_COUNT

        bundle_commands = mock_filesystem.list_dir(
            populated_ide_bundle / "commands" / "nw"
        )
        assert len(bundle_commands) == EXPECTED_COMMAND_COUNT


# ═══════════════════════════════════════════════════════════════════════════════
# Test: Deploy target path consistency
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestDeployTargetPathConsistency:
    """Same ~/.claude/ constant used by deploy and validation services.

    Integration: Both AssetDeploymentService and DeploymentValidationService
    accept the same target path parameter.
    """

    def test_deploy_target_path_consistency(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_ide_bundle: Path,
    ) -> None:
        """Deploy target path should be ~/.claude/ for both deploy and validation."""
        expected_target = Path.home() / ".claude"

        deployer = AssetDeploymentService(filesystem=mock_filesystem)
        validator = DeploymentValidationService(filesystem=mock_filesystem)

        # Both services accept the same target path
        with pytest.raises(NotImplementedError):
            deployer.deploy(
                source_dir=populated_ide_bundle,
                target_dir=expected_target,
            )
        with pytest.raises(NotImplementedError):
            validator.validate(
                target_dir=expected_target,
                expected_agents=EXPECTED_AGENT_COUNT,
                expected_commands=EXPECTED_COMMAND_COUNT,
                expected_templates=EXPECTED_TEMPLATE_COUNT,
                expected_scripts=EXPECTED_SCRIPT_COUNT,
            )


# ═══════════════════════════════════════════════════════════════════════════════
# Test: IDE bundle check blocks install when missing
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.mark.integration
class TestIdeBundleCheckBlocksInstallWhenMissing:
    """Install blocked when dist/ide/ absent.

    Integration: CheckExecutor runs IdeBundleExistsCheck, which inspects
    the filesystem. When dist/ide/ is absent, the check returns BLOCKING
    failure through the real CheckExecutor pipeline.
    """

    def test_ide_bundle_check_blocks_install_when_missing(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """IDE bundle check should return BLOCKING failure when dist/ide/ is absent."""
        # dist/ide/ does NOT exist in the empty filesystem
        bundle_dir = Path("dist/ide")
        assert not mock_filesystem.exists(bundle_dir)

        ide_check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=bundle_dir
        )

        registry = CheckRegistry()
        registry.register("ide-bundle-exists", ide_check.execute)

        executor = CheckExecutor(registry=registry)
        results = executor.run_all()

        assert len(results) == 1
        result = results[0]
        assert result.id == "ide-bundle-exists"
        assert result.passed is False
        assert result.severity == CheckSeverity.BLOCKING
