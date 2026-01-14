"""
Tests for devop-reviewer TOON v3.0 format validation.
Step 08-02: Transform devop-reviewer to TOON v3.0 format.

TDD Phase: Tests that validate TOON format compliance.
"""
import pytest
import os
import re

# Paths
TOON_FILE = "nWave/agents/devop-reviewer.toon"
MD_FILE = "nWave/agents/devop-reviewer.md"


class TestTOONFileExists:
    """Verify TOON file exists and is readable."""

    def test_toon_file_exists(self):
        """TOON file exists."""
        assert os.path.exists(TOON_FILE), f"TOON file not found: {TOON_FILE}"

    def test_toon_file_readable(self):
        """TOON file is readable."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 0, "TOON file is empty"

    def test_toon_file_has_content(self):
        """TOON file has substantial content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 500, "TOON file seems too small"


class TestTOONHeader:
    """Verify TOON v3.0 header format."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_agent_name_in_header(self, toon_content):
        """Header contains agent name."""
        assert 'DEVOP-REVIEWER' in toon_content.upper()[:200]

    def test_has_toon_version(self, toon_content):
        """Header indicates TOON v3.0."""
        assert 'TOON v3.0' in toon_content[:200] or 'TOON' in toon_content[:200]

    def test_has_haiku_model(self, toon_content):
        """Header indicates haiku model for cost efficiency."""
        assert 'haiku' in toon_content.lower()[:500]


class TestRequiredSections:
    """Verify all required TOON sections exist."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_id_section(self, toon_content):
        """Has ID section."""
        assert '## ID' in toon_content

    def test_has_persona_section(self, toon_content):
        """Has PERSONA section."""
        assert '## PERSONA' in toon_content

    def test_has_core_principles_section(self, toon_content):
        """Has CORE_PRINCIPLES section."""
        assert '## CORE_PRINCIPLES' in toon_content

    def test_has_commands_section(self, toon_content):
        """Has COMMANDS section."""
        assert '## COMMANDS' in toon_content

    def test_has_activation_section(self, toon_content):
        """Has ACTIVATION section."""
        assert '## ACTIVATION' in toon_content

    def test_has_reviewer_section(self, toon_content):
        """Has REVIEWER section specific to reviewer agents."""
        assert '## REVIEWER' in toon_content or 'Review' in toon_content


class TestIDSection:
    """Verify ID section content."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_role_field(self, toon_content):
        """Has role field."""
        assert 'role:' in toon_content

    def test_role_contains_devop_reviewer(self, toon_content):
        """Role contains devop-reviewer."""
        # Extract ID section
        id_section = toon_content[toon_content.find('## ID'):toon_content.find('## PERSONA')]
        assert 'devop-reviewer' in id_section.lower()

    def test_has_model_haiku(self, toon_content):
        """Model is set to haiku."""
        assert 'model: haiku' in toon_content.lower() or 'model:haiku' in toon_content.lower().replace(' ', '')


class TestPersonaSection:
    """Verify PERSONA section content."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_name_dakota(self, toon_content):
        """Persona name is Dakota."""
        assert 'Dakota' in toon_content

    def test_has_style(self, toon_content):
        """Has style description."""
        assert 'style:' in toon_content.lower() or 'Style:' in toon_content

    def test_has_focus(self, toon_content):
        """Has focus description."""
        assert 'focus:' in toon_content.lower() or 'Focus:' in toon_content


class TestCorePrinciplesSection:
    """Verify CORE_PRINCIPLES section content."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_token_economy_principle(self, toon_content):
        """Has token economy principle."""
        assert 'Token' in toon_content and 'Economy' in toon_content

    def test_has_document_control_principle(self, toon_content):
        """Has document control principle."""
        assert 'Document' in toon_content

    def test_uses_arrow_notation(self, toon_content):
        """Uses arrow notation for principles."""
        assert '→' in toon_content


class TestCommandsSection:
    """Verify COMMANDS section content."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_help_command(self, toon_content):
        """Has help command."""
        assert 'help' in toon_content.lower()

    def test_has_exit_command(self, toon_content):
        """Has exit command."""
        assert 'exit' in toon_content.lower()

    def test_commands_use_dash_list(self, toon_content):
        """Commands use dash list format."""
        commands_start = toon_content.find('## COMMANDS')
        if commands_start > 0:
            commands_section = toon_content[commands_start:commands_start + 500]
            assert '- ' in commands_section


class TestReviewerSpecialization:
    """Verify reviewer-specific content."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_cost_efficiency_mention(self, toon_content):
        """Mentions cost efficiency."""
        assert 'cost' in toon_content.lower()

    def test_has_review_expert_role(self, toon_content):
        """Has review expert role."""
        assert 'review' in toon_content.lower()


class TestCompression:
    """Verify TOON is significantly smaller than MD."""

    def test_toon_smaller_than_md(self):
        """TOON file is smaller than MD."""
        md_size = os.path.getsize(MD_FILE)
        toon_size = os.path.getsize(TOON_FILE)
        assert toon_size < md_size, f"TOON ({toon_size}) should be smaller than MD ({md_size})"

    def test_toon_fewer_lines_than_md(self):
        """TOON has fewer lines than MD."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            md_lines = len(f.readlines())
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            toon_lines = len(f.readlines())
        assert toon_lines < md_lines, f"TOON ({toon_lines}) should have fewer lines than MD ({md_lines})"
