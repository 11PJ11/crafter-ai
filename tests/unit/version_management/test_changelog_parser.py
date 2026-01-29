"""
Unit tests for ChangelogParser - extract breaking changes from changelog.

Business behavior: Identify breaking changes in release notes.
"""

from nWave.core.version_management.changelog_parser import ChangelogParser


class TestChangelogParserShould:
    """Behavior specifications for changelog parsing logic."""

    def test_extract_breaking_changes_when_section_present(self):
        """Extract breaking changes when BREAKING CHANGES section exists."""
        parser = ChangelogParser()
        changelog = """
## BREAKING CHANGES
* feat!: redesign API endpoints - requires client migration
* feat!: remove deprecated features

## What's Changed
* feat: add new authentication system
* fix: resolve security vulnerability
"""

        breaking_changes = parser.extract_breaking_changes(changelog)

        assert len(breaking_changes) == 2, "Should extract 2 breaking changes"
        assert "redesign API endpoints" in breaking_changes[0]
        assert "remove deprecated features" in breaking_changes[1]

    def test_return_empty_list_when_no_breaking_changes(self):
        """Return empty list when no BREAKING CHANGES section."""
        parser = ChangelogParser()
        changelog = """
## What's Changed
* feat: add new feature
* fix: bug fix
"""

        breaking_changes = parser.extract_breaking_changes(changelog)

        assert (
            breaking_changes == []
        ), "Should return empty list when no breaking changes"

    def test_detect_breaking_changes_by_conventional_commits_marker(self):
        """Detect breaking changes using conventional commits ! marker."""
        parser = ChangelogParser()
        changelog = """
## What's Changed
* feat!: major API redesign
* feat: regular feature addition
* fix: bug fix
"""

        breaking_changes = parser.extract_breaking_changes(changelog)

        assert len(breaking_changes) >= 1, "Should detect feat! as breaking change"
        assert "API redesign" in breaking_changes[0]

    def test_handle_empty_changelog_gracefully(self):
        """Handle empty or None changelog without error."""
        parser = ChangelogParser()

        breaking_changes_empty = parser.extract_breaking_changes("")
        breaking_changes_none = parser.extract_breaking_changes(None)

        assert breaking_changes_empty == [], "Should handle empty string gracefully"
        assert breaking_changes_none == [], "Should handle None gracefully"
