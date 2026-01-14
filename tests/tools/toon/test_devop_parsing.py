"""
Tests for devop.md parsing and structure extraction.
Step 07-01: Parse devop.md and validate structure extraction.

TDD Phase: RED - Tests written before implementation.
"""
import pytest
import os
import yaml
import re

# Paths
MD_FILE = "nWave/agents/devop.md"
PARSED_OUTPUT = "docs/feature/toon-agent-conversion/parsed/devop-parsed.yaml"


class TestMDFileExists:
    """Verify source file exists and is readable."""

    def test_md_file_exists(self):
        """MD source file exists."""
        assert os.path.exists(MD_FILE), f"MD file not found: {MD_FILE}"

    def test_md_file_readable(self):
        """MD file is readable."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 0, "MD file is empty"

    def test_md_file_has_content(self):
        """MD file has substantial content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 5000, "MD file too small for agent definition"


class TestFrontmatterParsing:
    """Test YAML frontmatter extraction."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_yaml_frontmatter(self, md_content):
        """File starts with YAML frontmatter."""
        assert md_content.startswith('---'), "File should start with YAML frontmatter"

    def test_frontmatter_has_name(self, md_content):
        """Frontmatter contains name field."""
        assert 'name:' in md_content[:500], "Frontmatter should contain name field"

    def test_frontmatter_has_description(self, md_content):
        """Frontmatter contains description field."""
        assert 'description:' in md_content[:1000], "Frontmatter should contain description"

    def test_frontmatter_name_is_devop(self, md_content):
        """Frontmatter name is devop."""
        match = re.search(r'name:\s*(\S+)', md_content[:500])
        assert match, "Could not find name field"
        assert match.group(1) == 'devop', f"Name should be devop, got {match.group(1)}"


class TestAgentBlockParsing:
    """Test internal agent YAML block extraction."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_agent_section(self, md_content):
        """File contains agent section."""
        assert 'agent:' in md_content, "File should contain agent section"

    def test_agent_has_name(self, md_content):
        """Agent section has name field."""
        # Look for agent name in YAML block
        assert re.search(r'agent:\s*\n\s+name:', md_content), "Agent should have name"

    def test_agent_has_id(self, md_content):
        """Agent section has id field."""
        assert re.search(r'\s+id:\s*devop', md_content), "Agent should have id: devop"

    def test_agent_has_title(self, md_content):
        """Agent section has title field."""
        assert re.search(r'\s+title:', md_content), "Agent should have title"

    def test_agent_has_icon(self, md_content):
        """Agent section has icon field."""
        assert re.search(r'\s+icon:', md_content), "Agent should have icon"


class TestPersonaParsing:
    """Test persona section extraction."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_persona_section(self, md_content):
        """File contains persona section."""
        assert 'persona:' in md_content, "File should contain persona section"

    def test_persona_has_role(self, md_content):
        """Persona has role field."""
        assert re.search(r'persona:\s*\n\s+role:', md_content), "Persona should have role"

    def test_persona_has_style(self, md_content):
        """Persona has style field."""
        assert 'style:' in md_content, "Persona should have style"


class TestCommandsParsing:
    """Test commands section extraction."""

    @pytest.fixture
    def md_content(self):
        """Load MD content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_commands_section(self, md_content):
        """File contains commands section."""
        assert 'commands:' in md_content, "File should contain commands section"

    def test_has_help_command(self, md_content):
        """File has help command."""
        assert re.search(r'-\s+name:\s*help', md_content.lower()) or \
               re.search(r'\*help', md_content), "Should have help command"

    def test_has_exit_command(self, md_content):
        """File has exit command."""
        assert 'exit' in md_content.lower(), "Should have exit command"


class TestParsedOutputExists:
    """Verify parsed output is generated."""

    def test_parsed_yaml_exists(self):
        """Parsed YAML output exists."""
        assert os.path.exists(PARSED_OUTPUT), f"Parsed output not found: {PARSED_OUTPUT}"


class TestParsedOutputStructure:
    """Verify parsed output has correct structure."""

    @pytest.fixture
    def parsed_data(self):
        """Load parsed YAML data."""
        with open(PARSED_OUTPUT, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_has_frontmatter(self, parsed_data):
        """Parsed data has frontmatter section."""
        assert 'frontmatter' in parsed_data, "Should have frontmatter section"

    def test_has_agent(self, parsed_data):
        """Parsed data has agent section."""
        assert 'agent' in parsed_data, "Should have agent section"

    def test_has_persona(self, parsed_data):
        """Parsed data has persona section."""
        assert 'persona' in parsed_data, "Should have persona section"

    def test_has_commands(self, parsed_data):
        """Parsed data has commands section."""
        assert 'commands' in parsed_data, "Should have commands section"

    def test_frontmatter_name_correct(self, parsed_data):
        """Frontmatter name is devop."""
        assert parsed_data['frontmatter'].get('name') == 'devop'

    def test_agent_id_correct(self, parsed_data):
        """Agent id is devop."""
        assert parsed_data['agent'].get('id') == 'devop'
