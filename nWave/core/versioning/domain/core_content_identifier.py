"""
CoreContentIdentifier - nWave vs user content classification.

Business capability: Identify nWave-managed content for safe updates.

Classification Rules:
- Paths with '/nw/' directory segment are nWave core content
- User content (custom agents, commands, root-level files) is preserved during updates
- Only paths within ~/.claude/ structure are considered for classification
"""

import re
from typing import Pattern


class CoreContentIdentifier:
    """
    Classifies content as nWave-managed (core) or user-managed (preserved).

    Core content lives under 'nw/' prefixed directories:
    - ~/.claude/agents/nw/...
    - ~/.claude/commands/nw/...
    - ~/.claude/templates/nw/...
    - ~/.claude/data/nw/...
    - ~/.claude/checklists/nw/...

    User content is everything else within ~/.claude/:
    - ~/.claude/agents/my-custom-agent/...
    - ~/.claude/commands/my-command/...
    - ~/.claude/CLAUDE.md
    """

    # Pattern to detect nw/ directory segment in path
    _NW_DIRECTORY_PATTERN: Pattern[str] = re.compile(r"/nw/")

    # Pattern to detect valid ~/.claude/ structure
    _CLAUDE_DIR_PATTERN: Pattern[str] = re.compile(r"(^~?/.*)?\.claude/")

    def is_core_content(self, path: str) -> bool:
        """
        Determine if path represents nWave-managed core content.

        Core content is identified by the presence of '/nw/' directory
        segment within a valid ~/.claude/ structure.

        Args:
            path: File or directory path to classify

        Returns:
            True if path is nWave core content, False if user content
        """
        if not self._is_within_claude_structure(path):
            return False

        return self._has_nw_directory_segment(path)

    def _is_within_claude_structure(self, path: str) -> bool:
        """Check if path is within ~/.claude/ directory structure."""
        return bool(self._CLAUDE_DIR_PATTERN.search(path))

    def _has_nw_directory_segment(self, path: str) -> bool:
        """Check if path contains '/nw/' directory segment."""
        return bool(self._NW_DIRECTORY_PATTERN.search(path))
