"""
Tests for devop.toon TOON v3.0 format validation.
Step 07-02: Transform devop to TOON v3.0 format.

TDD Phase: RED - Tests written before implementation.
"""
import pytest
import os
import re

# Paths
TOON_FILE = "nWave/agents/devop.toon"
MD_FILE = "nWave/agents/devop.md"


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

    def test_toon_file_substantial(self):
        """TOON file has substantial content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 2000, "TOON file too small"


class TestTOONHeader:
    """Verify TOON file has correct header structure."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_agent_header_comment(self, toon_content):
        """Has agent header comment."""
        assert '# DEVOP AGENT' in toon_content.upper() or 'devop' in toon_content.lower()[:200]

    def test_has_toon_version(self, toon_content):
        """Has TOON v3.0 version indicator."""
        assert 'TOON v3.0' in toon_content or 'v3.0' in toon_content


class TestIDSection:
    """Verify ID section structure."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_id_section(self, toon_content):
        """Has ## ID section."""
        assert '## ID' in toon_content

    def test_has_role(self, toon_content):
        """Has role field."""
        assert re.search(r'role:\s*\S', toon_content)

    def test_role_contains_devop(self, toon_content):
        """Role contains devop."""
        assert 'devop' in toon_content.lower()

    def test_has_title(self, toon_content):
        """Has title field."""
        assert re.search(r'title:\s*\S', toon_content)

    def test_has_icon(self, toon_content):
        """Has icon field."""
        assert re.search(r'icon:\s*\S', toon_content)

    def test_has_model(self, toon_content):
        """Has model field."""
        assert re.search(r'model:\s*\S', toon_content)


class TestPersonaSection:
    """Verify PERSONA section structure."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_persona_section(self, toon_content):
        """Has ## PERSONA section."""
        assert '## PERSONA' in toon_content

    def test_has_persona_name(self, toon_content):
        """Has name in persona."""
        assert 'Dakota' in toon_content

    def test_has_persona_role(self, toon_content):
        """Has role in persona."""
        assert 'Feature Completion' in toon_content or 'Production Readiness' in toon_content


class TestCorePrinciplesSection:
    """Verify CORE_PRINCIPLES section structure."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_core_principles_section(self, toon_content):
        """Has ## CORE_PRINCIPLES section."""
        assert '## CORE_PRINCIPLES' in toon_content

    def test_has_token_economy_principle(self, toon_content):
        """Has Token Economy principle."""
        assert 'Token' in toon_content and 'Economy' in toon_content or \
               'token' in toon_content.lower()


class TestCommandsSection:
    """Verify COMMANDS section structure."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_commands_section(self, toon_content):
        """Has ## COMMANDS section."""
        assert '## COMMANDS' in toon_content

    def test_has_help_command(self, toon_content):
        """Has help command."""
        assert 'help' in toon_content.lower()

    def test_has_exit_command(self, toon_content):
        """Has exit command."""
        assert 'exit' in toon_content.lower()

    def test_has_validate_completion_command(self, toon_content):
        """Has validate-completion command."""
        assert 'validate-completion' in toon_content.lower() or \
               'validate completion' in toon_content.lower()

    def test_has_orchestrate_deployment_command(self, toon_content):
        """Has orchestrate-deployment command."""
        assert 'orchestrate-deployment' in toon_content.lower() or \
               'orchestrate deployment' in toon_content.lower()


class TestActivationSection:
    """Verify ACTIVATION section structure."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_activation_section(self, toon_content):
        """Has ## ACTIVATION section."""
        assert '## ACTIVATION' in toon_content


class TestDependenciesSection:
    """Verify DEPENDENCIES section structure."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_dependencies_section(self, toon_content):
        """Has ## DEPENDENCIES section."""
        assert '## DEPENDENCIES' in toon_content or 'DEPENDENCIES' in toon_content


class TestTOONSyntax:
    """Verify TOON syntax correctness."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_no_yaml_block_markers(self, toon_content):
        """No ```yaml block markers (TOON uses plain format)."""
        # TOON should not have large YAML code blocks
        yaml_blocks = re.findall(r'```yaml[\s\S]*?```', toon_content)
        # Small examples OK, large blocks not
        for block in yaml_blocks:
            assert len(block) < 500, "TOON should not have large YAML blocks"

    def test_uses_arrow_notation(self, toon_content):
        """Uses arrow notation for principles."""
        # TOON v3.0 uses → for principles
        assert '→' in toon_content or '->' in toon_content or \
               re.search(r'^\s*-\s+\w', toon_content, re.MULTILINE)


class TestContentCompleteness:
    """Verify all key content from MD is preserved in TOON."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_devop_id_preserved(self, toon_content):
        """devop ID preserved."""
        assert 'devop' in toon_content.lower()

    def test_dakota_name_preserved(self, toon_content):
        """Dakota name preserved."""
        assert 'Dakota' in toon_content

    def test_deliver_wave_mentioned(self, toon_content):
        """DELIVER wave mentioned."""
        assert 'DELIVER' in toon_content

    def test_rocket_icon_preserved(self, toon_content):
        """Rocket icon preserved."""
        assert '\U0001F680' in toon_content or 'rocket' in toon_content.lower()
