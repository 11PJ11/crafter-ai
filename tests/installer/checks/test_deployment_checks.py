"""Tests for deployment pre-flight checks.

These checks validate that the IDE bundle exists in dist/ide/ before
the install phase begins. If dist/ide/ is missing or empty, the check
returns a BLOCKING failure with remediation to run 'forge build'.

Unit test strategy: Each test instantiates IdeBundleExistsCheck, calls
its execute() method, and asserts the CheckResult outcome. The check
stub raises NotImplementedError until implemented, proving the contract
and enabling Outside-In TDD.

All tests use the InMemoryFileSystemAdapter to avoid depending on actual
filesystem state. No actual file system operations, subprocess calls, or
external dependencies.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from tests.installer.conftest import InMemoryFileSystemAdapter


# ═══════════════════════════════════════════════════════════════════════════════
# Shared Constants (source of truth: journey-forge-tui.yaml)
# ═══════════════════════════════════════════════════════════════════════════════

EXPECTED_AGENT_COUNT = 30
EXPECTED_COMMAND_COUNT = 23
EXPECTED_TEMPLATE_COUNT = 17
EXPECTED_SCRIPT_COUNT = 4


# ═══════════════════════════════════════════════════════════════════════════════
# Check Stub (NotImplementedError pattern for Outside-In TDD)
# ═══════════════════════════════════════════════════════════════════════════════


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
            CheckResult with pass/fail, component counts, and remediation.
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
def populated_ide_bundle(mock_filesystem: InMemoryFileSystemAdapter) -> Path:
    """Set up dist/ide/ with correct component counts from design YAML."""
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
# Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestIdeBundleExistsCheck:
    """Tests for the IDE bundle existence pre-flight check.

    Each test instantiates IdeBundleExistsCheck, calls execute(), and
    asserts the CheckResult outcome. The check raises NotImplementedError
    until implemented, which proves the contract.
    """

    def test_ide_bundle_exists_check_passes_when_present(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_ide_bundle: Path,
    ) -> None:
        """Check should pass when dist/ide/ directory has content."""
        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=populated_ide_bundle
        )

        # Verify bundle has expected content
        agents = mock_filesystem.list_dir(populated_ide_bundle / "agents" / "nw")
        assert len(agents) == EXPECTED_AGENT_COUNT

        with pytest.raises(NotImplementedError, match="IdeBundleExistsCheck.execute"):
            check.execute()

    def test_ide_bundle_exists_check_fails_when_missing(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Check should fail with BLOCKING severity when dist/ide/ is absent."""
        missing_bundle = Path("dist/ide")
        assert not mock_filesystem.exists(missing_bundle)

        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=missing_bundle
        )

        with pytest.raises(NotImplementedError, match="IdeBundleExistsCheck.execute"):
            check.execute()

    def test_ide_bundle_check_reports_agent_command_counts(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
        populated_ide_bundle: Path,
    ) -> None:
        """Pass message should include agent and command counts."""
        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=populated_ide_bundle
        )

        # Verify expected counts are available for the check to report
        agents = mock_filesystem.list_dir(populated_ide_bundle / "agents" / "nw")
        commands = mock_filesystem.list_dir(populated_ide_bundle / "commands" / "nw")
        assert len(agents) == EXPECTED_AGENT_COUNT
        assert len(commands) == EXPECTED_COMMAND_COUNT

        with pytest.raises(NotImplementedError, match="IdeBundleExistsCheck.execute"):
            check.execute()

    def test_ide_bundle_check_remediation_message(
        self,
        mock_filesystem: InMemoryFileSystemAdapter,
    ) -> None:
        """Remediation should say 'Run forge build'."""
        missing_bundle = Path("dist/ide")
        check = IdeBundleExistsCheck(
            filesystem=mock_filesystem, bundle_dir=missing_bundle
        )

        with pytest.raises(NotImplementedError, match="IdeBundleExistsCheck.execute"):
            check.execute()

        # When implemented, failure result should have remediation:
        # remediation="Run 'forge build' to create the IDE bundle"
        # fix_command="forge build"
        # This proves the contract exists; developer fills in implementation.
