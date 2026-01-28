"""
Unit tests for CoreContentIdentifier - nWave vs user content classification.

Business behavior: Identify nWave-prefixed content for safe update/preservation.

Classification Rules:
- ~/.claude/agents/nw/...     -> Core content (nWave managed)
- ~/.claude/commands/nw/...   -> Core content (nWave managed)
- ~/.claude/templates/nw/...  -> Core content (nWave managed)
- ~/.claude/agents/my-agent/  -> User content (preserved)
- ~/.claude/commands/my-cmd/  -> User content (preserved)
- ~/.claude/CLAUDE.md         -> User content (preserved)
"""

from nWave.core.versioning.domain.core_content_identifier import CoreContentIdentifier


class TestCoreContentIdentifierShould:
    """Behavior specifications for nWave content classification."""

    def test_nw_agents_is_core_content(self):
        """Paths under agents/nw/ are nWave core content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/agents/nw/software-crafter.md")

        assert result is True, "agents/nw/ paths should be classified as core content"

    def test_custom_agents_is_not_core_content(self):
        """Paths under agents/<custom>/ are user content, not nWave core."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/agents/my-custom-agent/agent.md")

        assert result is False, "agents/my-custom-agent/ should be user content"

    def test_nw_commands_is_core_content(self):
        """Paths under commands/nw/ are nWave core content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/commands/nw/develop.md")

        assert result is True, "commands/nw/ paths should be classified as core content"

    def test_custom_commands_is_not_core_content(self):
        """Paths under commands/<custom>/ are user content, not nWave core."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/commands/my-command/run.md")

        assert result is False, "commands/my-command/ should be user content"

    def test_nw_templates_is_core_content(self):
        """Paths under templates/nw/ are nWave core content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/templates/nw/step-template.yaml")

        assert result is True, "templates/nw/ paths should be classified as core content"

    def test_root_level_files_classification(self):
        """Root-level files like CLAUDE.md are user content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/CLAUDE.md")

        assert result is False, "Root-level CLAUDE.md should be user content"


class TestCoreContentIdentifierEdgeCases:
    """Edge case handling for content classification."""

    def test_nw_in_data_directory_is_core_content(self):
        """Paths under data/nw/ are nWave core content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/data/nw/research/topic.md")

        assert result is True, "data/nw/ paths should be classified as core content"

    def test_nested_nw_path_is_core_content(self):
        """Deeply nested paths under nw/ are still core content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/agents/nw/templates/sub/deep/file.yaml")

        assert result is True, "Deep nested paths under nw/ should be core content"

    def test_user_directory_with_nw_in_name_is_not_core(self):
        """User directory containing 'nw' substring but not 'nw/' prefix is user content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/agents/my-new-agent/file.md")

        assert result is False, "Directory containing 'new' is not core content"

    def test_absolute_path_with_nw_prefix_is_core_content(self):
        """Absolute paths with nw/ directory are core content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("/home/user/.claude/commands/nw/version.md")

        assert result is True, "Absolute paths with nw/ should be core content"

    def test_path_without_claude_prefix_handles_gracefully(self):
        """Paths without ~/.claude prefix should return False (not nWave managed)."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("/some/other/path/nw/file.md")

        assert result is False, "Paths outside ~/.claude are not core content"

    def test_nw_checklists_is_core_content(self):
        """Paths under checklists/nw/ are nWave core content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/checklists/nw/develop-wave.md")

        assert result is True, "checklists/nw/ paths should be core content"

    def test_user_config_file_is_not_core_content(self):
        """User configuration files at root level are user content."""
        identifier = CoreContentIdentifier()

        result = identifier.is_core_content("~/.claude/settings.json")

        assert result is False, "Root-level settings.json should be user content"
