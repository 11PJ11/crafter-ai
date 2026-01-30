"""
BoundaryRulesGenerator for scope-based file pattern generation.

This module extracts allowed file patterns from step file scope definitions,
ensuring agents can only modify files relevant to their assigned tasks.
"""

import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class BoundaryRulesGenerator:
    """
    Generate ALLOWED file patterns from step file scope.

    The generator reads step file scope field and extracts:
    - target_files: Implementation files to be modified
    - test_files: Test files for TDD workflow
    - allowed_patterns: Custom glob patterns
    - step file itself (implicitly allowed)

    If scope field is missing, defaults to generic patterns with WARNING log.
    """

    DEFAULT_PATTERNS = ["steps/**/*.json", "src/**/*", "tests/**/*"]

    def __init__(self, step_file_path: Path | str):
        """
        Initialize generator with step file path.

        Args:
            step_file_path: Path to step JSON file
        """
        self.step_file_path = Path(step_file_path)
        self._step_data = None

    def generate_allowed_patterns(self) -> list[str]:
        """
        Generate allowed file patterns from step scope.

        Returns:
            List of allowed file patterns including:
            - Step file path
            - target_files from scope
            - test_files from scope
            - allowed_patterns from scope
            - Default patterns if scope missing
        """
        self._load_step_file()

        patterns = []

        # Always include step file
        patterns.append(str(self.step_file_path))

        scope = self._step_data.get("scope")
        if not scope:
            logger.warning(
                f"Step file {self.step_file_path} missing scope field. "
                f"Using default patterns: {self.DEFAULT_PATTERNS}"
            )
            patterns.extend(self.DEFAULT_PATTERNS)
            return patterns

        # Add target files
        target_files = scope.get("target_files", [])
        patterns.extend(target_files)

        # Add test files
        test_files = scope.get("test_files", [])
        patterns.extend(test_files)

        # Add custom allowed patterns
        allowed_patterns = scope.get("allowed_patterns", [])
        patterns.extend(allowed_patterns)

        return patterns

    def _load_step_file(self) -> None:
        """Load step file JSON data."""
        if self._step_data is None:
            with open(self.step_file_path) as f:
                self._step_data = json.load(f)
