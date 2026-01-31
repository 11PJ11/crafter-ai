"""
ScopeValidator - Post-Execution Scope Validation

Validates that agent modifications stay within step scope by comparing
git diff output against allowed file patterns from step file.

Business Context:
Prevents agents from "helpfully" modifying files outside assigned step scope,
catching unauthorized changes before merge to prevent release delays.

Domain Language:
- allowed_patterns: Glob patterns defining in-scope files
- out_of_scope_files: Files modified that don't match allowed patterns
- scope violation: Modification of file outside allowed patterns
- validation_skipped: Git command unavailable, validation not performed
"""

import json
import logging
import subprocess
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path
from typing import List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class ScopeValidationResult:
    """
    Result of post-execution scope validation.

    Attributes:
        has_violations: True if out-of-scope files were modified
        out_of_scope_files: List of files modified outside allowed patterns
        violation_message: Human-readable description of violations
        violation_severity: Severity level (WARNING)
        validation_skipped: True if git command unavailable
        reason: Explanation when validation_skipped=True
    """

    has_violations: bool
    out_of_scope_files: List[str] = field(default_factory=list)
    violation_message: str = ""
    violation_severity: str = "WARNING"
    validation_skipped: bool = False
    reason: str = ""


class ScopeValidator:
    """
    Validates agent modifications stay within step scope.

    Uses git diff to detect modified files and compares against
    allowed patterns from step file scope definition.

    Error Handling:
    - Subprocess timeout (5 seconds) prevents hanging
    - CalledProcessError caught and logged
    - On git failure: returns validation_skipped=True
    """

    def __init__(self):
        """Initialize ScopeValidator."""
        self.git_timeout = 5  # seconds

    def validate_scope(
        self,
        step_file_path: str,
        project_root: Path,
        git_diff_files: Optional[List[str]] = None,
    ) -> ScopeValidationResult:
        """
        Validate modified files against allowed patterns.

        Args:
            step_file_path: Path to step file containing scope definition
            project_root: Project root directory (for logging context)
            git_diff_files: Optional list of modified files (if provided, skips git diff)

        Returns:
            ScopeValidationResult with violation details

        Business Logic:
        1. Load allowed patterns from step file
        2. Get modified files from git diff (or use provided list)
        3. Compare each modified file against allowed patterns
        4. Report violations for out-of-scope modifications
        """
        # Load allowed patterns from step file
        allowed_patterns = self._load_allowed_patterns(step_file_path)

        # Get modified files (from git or parameter)
        if git_diff_files is None:
            modified_files_result = self._get_modified_files_from_git()
            modified_files, error_reason = modified_files_result
            if modified_files is None:
                # Git command failed - return validation skipped
                return ScopeValidationResult(
                    has_violations=False,
                    validation_skipped=True,
                    reason=error_reason,
                )
        else:
            modified_files = git_diff_files

        # Check each modified file against allowed patterns
        out_of_scope_files = []
        for modified_file in modified_files:
            if not modified_file.strip():
                continue  # Skip empty lines

            # Step file is implicitly allowed (agent must update phase outcomes)
            if modified_file == step_file_path:
                continue  # Skip pattern matching for step file

            if not self._file_matches_any_pattern(modified_file, allowed_patterns):
                out_of_scope_files.append(modified_file)

        # Build result
        if out_of_scope_files:
            violation_message = self._build_violation_message(out_of_scope_files)
            return ScopeValidationResult(
                has_violations=True,
                out_of_scope_files=out_of_scope_files,
                violation_message=violation_message,
                violation_severity="WARNING",
            )
        else:
            return ScopeValidationResult(has_violations=False)

    def _load_allowed_patterns(self, step_file_path: str) -> List[str]:
        """
        Load allowed file patterns from step file.

        Args:
            step_file_path: Path to step file JSON

        Returns:
            List of glob patterns (e.g., **/UserRepository*)
        """
        with open(step_file_path, "r") as f:
            step_data = json.load(f)

        scope = step_data.get("scope", {})
        allowed_patterns = scope.get("allowed_patterns", [])

        return allowed_patterns

    def _get_modified_files_from_git(self) -> Tuple[Optional[List[str]], str]:
        """
        Execute git diff to get modified files.

        Returns:
            Tuple of (modified files list, error reason) or (None, reason) if git command failed

        Error Handling:
        - TimeoutExpired: Log ERROR, return (None, "Git command timeout")
        - CalledProcessError: Log ERROR, return (None, "Git command unavailable in environment")
        """
        try:
            result = subprocess.run(
                ["git", "diff", "--name-only", "HEAD"],
                capture_output=True,
                timeout=self.git_timeout,
                check=True,
                text=True,
            )
            modified_files = result.stdout.strip().split("\n")
            return (modified_files, "")

        except subprocess.TimeoutExpired:
            logger.error("Git diff timed out after %d seconds", self.git_timeout)
            return (None, "Git command timeout")

        except subprocess.CalledProcessError as e:
            logger.error("Git diff failed: %s", e)
            return (None, "Git command unavailable in environment")

    def _file_matches_any_pattern(
        self, file_path: str, allowed_patterns: List[str]
    ) -> bool:
        """
        Check if file matches any allowed pattern.

        Args:
            file_path: Path to check (e.g., src/services/OrderService.py)
            allowed_patterns: List of glob patterns (e.g., **/UserRepository*)

        Returns:
            True if file matches at least one pattern
        """
        for pattern in allowed_patterns:
            if fnmatch(file_path, pattern):
                return True
        return False

    def _build_violation_message(self, out_of_scope_files: List[str]) -> str:
        """
        Build human-readable violation message.

        Args:
            out_of_scope_files: List of files modified outside scope

        Returns:
            Formatted violation message including file names
        """
        file_count = len(out_of_scope_files)
        if file_count == 1:
            return f"Scope violation: {out_of_scope_files[0]} modified outside allowed patterns"
        else:
            files_list = ", ".join(out_of_scope_files)
            return f"Scope violations: {file_count} files modified outside allowed patterns: {files_list}"
