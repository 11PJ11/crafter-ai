"""Pre-flight check for IDE bundle existence.

Verifies that the IDE bundle directory (dist/ide/) exists and contains
content before the install phase begins. If missing or empty, returns
a BLOCKING failure with remediation to run 'forge build'.

This check uses a class (not a function like other checks) because it
requires injected dependencies: a FileSystemPort and a bundle directory path.
"""

from __future__ import annotations

from pathlib import Path

from crafter_ai.installer.domain.check_result import CheckResult, CheckSeverity
from crafter_ai.installer.domain.ide_bundle_constants import (
    AGENTS_SUBDIR,
    COMMANDS_SUBDIR,
)
from crafter_ai.installer.ports.filesystem_port import FileSystemPort

CHECK_ID = "ide-bundle-exists"
CHECK_NAME = "IDE Bundle Exists"
REMEDIATION = "Run 'forge build' to create the IDE bundle"
FIX_COMMAND = "forge build"


class IdeBundleExistsCheck:
    """Pre-flight check for IDE bundle existence in dist/ide/.

    Returns BLOCKING failure if dist/ide/ is missing or empty,
    with remediation to run 'forge build'.
    """

    def __init__(self, filesystem: FileSystemPort, bundle_dir: Path) -> None:
        self._filesystem = filesystem
        self._bundle_dir = bundle_dir

    def execute(self) -> CheckResult:
        """Check whether the IDE bundle exists and has content.

        Returns:
            CheckResult with pass/fail, component counts, and remediation.
        """
        if not self._filesystem.exists(self._bundle_dir):
            return self._blocking_failure(
                f"IDE bundle not found at {self._bundle_dir}"
            )

        contents = self._filesystem.list_dir(self._bundle_dir)
        if not contents:
            return self._blocking_failure(
                f"IDE bundle at {self._bundle_dir} is empty"
            )

        agent_count = self._count_items_in(AGENTS_SUBDIR)
        command_count = self._count_items_in(COMMANDS_SUBDIR)

        return CheckResult(
            id=CHECK_ID,
            name=CHECK_NAME,
            passed=True,
            severity=CheckSeverity.BLOCKING,
            message=f"IDE bundle found: {agent_count} agents, {command_count} commands",
        )

    def _count_items_in(self, subdir: str) -> int:
        """Count items in a bundle subdirectory, returning 0 if it doesn't exist."""
        subdir_path = self._bundle_dir / subdir
        if not self._filesystem.exists(subdir_path):
            return 0
        return len(self._filesystem.list_dir(subdir_path))

    def _blocking_failure(self, message: str) -> CheckResult:
        """Create a BLOCKING failure result with standard remediation."""
        return CheckResult(
            id=CHECK_ID,
            name=CHECK_NAME,
            passed=False,
            severity=CheckSeverity.BLOCKING,
            message=message,
            remediation=REMEDIATION,
            fixable=True,
            fix_command=FIX_COMMAND,
        )
