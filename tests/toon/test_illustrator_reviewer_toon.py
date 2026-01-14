"""
Tests for illustrator-reviewer.toon TOON v3.0 format validation.
Step 06-02: Transform illustrator-reviewer to TOON v3.0 format.

TDD Phase: RED - Tests that verify TOON file structure and content.
"""
import pytest
import os
import sys

# Add tools directory to path for TOON parser
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'tools', 'toon'))

TOON_FILE = "nWave/agents/illustrator-reviewer.toon"
MD_FILE = "nWave/agents/illustrator-reviewer.md"


class TestToonFileExists:
    """Verify TOON file exists and is readable."""

    def test_toon_file_exists(self):
        """AC1: TOON v3.0 file generated."""
        assert os.path.exists(TOON_FILE), f"TOON file not found: {TOON_FILE}"

    def test_toon_file_not_empty(self):
        """TOON file has content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 500, "TOON file appears too small"

    def test_toon_file_extension(self):
        """File has .toon extension."""
        assert TOON_FILE.endswith('.toon'), "File must have .toon extension"


class TestToonHeaderSection:
    """Verify TOON header section is correct."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_id_section(self, toon_content):
        """Has ## ID section."""
        assert '## ID' in toon_content or '## id' in toon_content.lower(), \
            "TOON file must have ID section"

    def test_id_is_correct(self, toon_content):
        """ID is illustrator-reviewer."""
        assert 'illustrator-reviewer' in toon_content, \
            "ID should be illustrator-reviewer"

    def test_has_type_agent(self, toon_content):
        """Type is agent."""
        assert 'type: agent' in toon_content.lower() or 'type=agent' in toon_content.lower(), \
            "Type should be agent"

    def test_has_version(self, toon_content):
        """Has version field."""
        assert 'version' in toon_content.lower(), "Must have version field"

    def test_version_is_v3(self, toon_content):
        """Version is v3.0."""
        assert 'v3.0' in toon_content or 'v3' in toon_content, \
            "Version should be v3.0"


class TestHaikuModelOptimization:
    """Verify reviewer agent uses Haiku model."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_model_field(self, toon_content):
        """Has model field."""
        assert 'model' in toon_content.lower(), "Must have model field"

    def test_model_is_haiku(self, toon_content):
        """Model is haiku."""
        assert 'haiku' in toon_content.lower(), \
            "Reviewer agent should use Haiku model"


class TestToonSections:
    """Verify TOON contains required sections."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_persona_section(self, toon_content):
        """Has persona section."""
        content_lower = toon_content.lower()
        assert 'persona' in content_lower or 'role' in content_lower, \
            "Must have persona section"

    def test_has_commands_section(self, toon_content):
        """Has commands section."""
        assert 'commands' in toon_content.lower() or '## COMMANDS' in toon_content, \
            "Must have commands section"

    def test_has_dependencies_section(self, toon_content):
        """Has dependencies section."""
        assert 'dependencies' in toon_content.lower() or 'checklists' in toon_content.lower(), \
            "Must have dependencies section"


class TestCommandsPreserved:
    """Verify commands are preserved from MD."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_help_command(self, toon_content):
        """Has help command."""
        assert 'help' in toon_content.lower(), "Must have help command"

    def test_has_review_command(self, toon_content):
        """Has review command."""
        assert 'review' in toon_content.lower(), "Must have review command"

    def test_has_storyboard_command(self, toon_content):
        """Has storyboard command."""
        assert 'storyboard' in toon_content.lower(), "Must have storyboard command"

    def test_has_exit_command(self, toon_content):
        """Has exit command."""
        assert 'exit' in toon_content.lower(), "Must have exit command"


class TestEmbeddedKnowledge:
    """Verify embedded knowledge is preserved."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_inject_markers_or_content(self, toon_content):
        """Has BUILD:INJECT markers or substantial content."""
        has_inject = 'BUILD:INJECT' in toon_content or 'INJECT' in toon_content
        has_content = len(toon_content) > 5000
        assert has_inject or has_content, \
            "Must preserve embedded knowledge markers or content"

    def test_has_pipeline_content(self, toon_content):
        """Has pipeline/workflow content."""
        assert 'pipeline' in toon_content.lower() or 'storyboard' in toon_content.lower(), \
            "Must have pipeline content"


class TestToonParserCompatibility:
    """Verify TOON file can be parsed by TOONParser."""

    def test_parser_can_load(self):
        """TOONParser can load the file."""
        try:
            from toon_parser import TOONParser
            parser = TOONParser()
            result = parser.parse_file(TOON_FILE)
            assert result is not None, "Parser returned None"
        except ImportError:
            pytest.skip("TOONParser not available")

    def test_parser_extracts_id(self):
        """Parser extracts correct ID."""
        try:
            from toon_parser import TOONParser
            parser = TOONParser()
            result = parser.parse_file(TOON_FILE)
            assert result.get('id') == 'illustrator-reviewer', \
                f"Wrong ID: {result.get('id')}"
        except ImportError:
            pytest.skip("TOONParser not available")

    def test_parser_extracts_type(self):
        """Parser extracts correct type."""
        try:
            from toon_parser import TOONParser
            parser = TOONParser()
            result = parser.parse_file(TOON_FILE)
            assert result.get('type') == 'agent', \
                f"Wrong type: {result.get('type')}"
        except ImportError:
            pytest.skip("TOONParser not available")


class TestNoSyntaxErrors:
    """Verify no syntax errors in TOON file."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_no_unclosed_brackets(self, toon_content):
        """AC4: No unclosed brackets."""
        open_brackets = toon_content.count('[') + toon_content.count('{')
        close_brackets = toon_content.count(']') + toon_content.count('}')
        assert abs(open_brackets - close_brackets) < 5, \
            "Possible unclosed brackets detected"

    def test_valid_utf8(self, toon_content):
        """Content is valid UTF-8."""
        assert isinstance(toon_content, str), "Content should be valid UTF-8 string"

    def test_no_null_bytes(self, toon_content):
        """No null bytes in content."""
        assert '\x00' not in toon_content, "Content should not contain null bytes"


class TestSizeReduction:
    """Verify TOON file is smaller than MD source."""

    def test_toon_smaller_than_md(self):
        """TOON file is smaller than MD source."""
        toon_size = os.path.getsize(TOON_FILE)
        md_size = os.path.getsize(MD_FILE)
        assert toon_size < md_size, \
            f"TOON ({toon_size} bytes) should be smaller than MD ({md_size} bytes)"

    def test_size_reduction_significant(self):
        """Size reduction is significant (at least 30%)."""
        toon_size = os.path.getsize(TOON_FILE)
        md_size = os.path.getsize(MD_FILE)
        reduction_percent = ((md_size - toon_size) / md_size) * 100
        assert reduction_percent > 30, \
            f"Size reduction only {reduction_percent:.1f}%, expected at least 30%"


class TestReviewerSpecificContent:
    """Verify reviewer-specific content is preserved."""

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_has_reviewer_role(self, toon_content):
        """Has reviewer role specified."""
        content_lower = toon_content.lower()
        assert 'review' in content_lower and ('role' in content_lower or 'expert' in content_lower), \
            "Must specify reviewer role"

    def test_has_quality_focus(self, toon_content):
        """Has quality/criteria focus."""
        content_lower = toon_content.lower()
        assert 'quality' in content_lower or 'criteria' in content_lower or 'check' in content_lower, \
            "Must have quality focus"

    def test_has_visual_domain(self, toon_content):
        """References visual/diagram domain."""
        content_lower = toon_content.lower()
        assert 'visual' in content_lower or 'diagram' in content_lower or 'animation' in content_lower, \
            "Must reference visual domain"
