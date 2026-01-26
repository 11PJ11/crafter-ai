"""
ChangelogParser - extract breaking changes from release notes.

Business capability: Identify breaking changes in GitHub release changelog.
"""

import re
from typing import List, Optional


class ChangelogParser:
    """Parses GitHub release changelog to extract breaking changes."""

    def extract_breaking_changes(self, changelog: Optional[str]) -> List[str]:
        """
        Extract breaking changes from changelog text.

        Detection strategies (in priority order):
        1. BREAKING CHANGES section - if present, use only this
        2. Conventional commits with ! marker (feat!, fix!) - fallback

        Args:
            changelog: Changelog text from GitHub release, or None

        Returns:
            List of breaking change descriptions (empty if none found)
        """
        if not changelog:
            return []

        # Strategy 1: Extract from BREAKING CHANGES section (priority)
        breaking_section_changes = self._extract_from_breaking_section(changelog)

        if breaking_section_changes:
            return breaking_section_changes

        # Strategy 2: Find conventional commits with ! marker (fallback)
        conventional_commits_breaking = self._extract_from_conventional_commits(
            changelog
        )

        return conventional_commits_breaking

    def _extract_from_breaking_section(self, changelog: str) -> List[str]:
        """
        Extract changes from BREAKING CHANGES section.

        Looks for:
        ## BREAKING CHANGES
        * change 1
        * change 2

        Returns:
            List of breaking change descriptions (without feat!/fix! prefixes)
        """
        changes = []

        # Find BREAKING CHANGES section
        pattern = r'##\s*BREAKING\s+CHANGES\s*\n((?:\*.*\n?)+)'
        matches = re.finditer(pattern, changelog, re.IGNORECASE)

        for match in matches:
            section_content = match.group(1)

            # Extract bullet points, remove conventional commit markers
            bullet_pattern = r'\*\s*(?:\w+!:\s*)?(.+)'
            bullets = re.findall(bullet_pattern, section_content)

            changes.extend([bullet.strip() for bullet in bullets])

        return changes

    def _extract_from_conventional_commits(self, changelog: str) -> List[str]:
        """
        Extract breaking changes marked with ! in conventional commits.

        Looks for: feat!, fix!, etc.

        Returns:
            List of breaking change descriptions
        """
        changes = []

        # Find conventional commits with ! marker
        pattern = r'\*\s*\w+!:\s*(.+)'
        matches = re.findall(pattern, changelog)

        changes.extend([match.strip() for match in matches])

        return changes
