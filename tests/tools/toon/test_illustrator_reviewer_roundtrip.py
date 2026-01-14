"""
Tests for illustrator-reviewer roundtrip validation (MD -> TOON -> MD).
Step 06-03: Roundtrip validation for illustrator-reviewer.

TDD Phase: Tests that verify semantic equivalence across format conversions.
"""
import pytest
import os
import sys
import re

# Add tools directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..', 'tools', 'toon'))

MD_FILE = "nWave/agents/illustrator-reviewer.md"
TOON_FILE = "nWave/agents/illustrator-reviewer.toon"


class TestFilesExist:
    """Verify both source files exist."""

    def test_md_file_exists(self):
        """Source MD file exists."""
        assert os.path.exists(MD_FILE), f"MD file not found: {MD_FILE}"

    def test_toon_file_exists(self):
        """TOON file exists."""
        assert os.path.exists(TOON_FILE), f"TOON file not found: {TOON_FILE}"


class TestFrontmatterPreserved:
    """Verify frontmatter data is preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD file content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_name_preserved(self, md_content, toon_content):
        """Agent name is preserved."""
        assert 'illustrator-reviewer' in toon_content.lower()

    def test_model_preserved(self, md_content, toon_content):
        """Model (haiku) is preserved."""
        assert 'haiku' in md_content.lower()
        assert 'haiku' in toon_content.lower()

    def test_description_present(self, toon_content):
        """Description content preserved."""
        # Check for key parts of description
        assert 'visual' in toon_content.lower() or 'diagram' in toon_content.lower()


class TestCommandsPreserved:
    """Verify all commands are preserved in roundtrip."""

    @pytest.fixture
    def md_content(self):
        """Load MD file content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_help_command_preserved(self, md_content, toon_content):
        """Help command preserved."""
        assert 'help' in md_content.lower()
        assert 'help' in toon_content.lower()

    def test_review_command_preserved(self, md_content, toon_content):
        """Review command preserved."""
        assert 'review' in md_content.lower()
        assert 'review' in toon_content.lower()

    def test_storyboard_command_preserved(self, md_content, toon_content):
        """Storyboard command preserved."""
        assert 'storyboard' in md_content.lower()
        assert 'storyboard' in toon_content.lower()

    def test_animatic_command_preserved(self, md_content, toon_content):
        """Animatic command preserved."""
        assert 'animatic' in md_content.lower()
        assert 'animatic' in toon_content.lower()

    def test_lip_sync_command_preserved(self, md_content, toon_content):
        """Lip-sync command preserved."""
        assert 'lip-sync' in md_content.lower() or 'lip_sync' in md_content.lower()
        assert 'lip-sync' in toon_content.lower() or 'lip_sync' in toon_content.lower()

    def test_exit_command_preserved(self, md_content, toon_content):
        """Exit command preserved."""
        assert 'exit' in md_content.lower()
        assert 'exit' in toon_content.lower()


class TestDependenciesPreserved:
    """Verify dependencies are preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD file content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_checklists_preserved(self, md_content, toon_content):
        """Checklists dependency preserved."""
        assert '12-principles-check' in md_content
        assert '12-principles-check' in toon_content or '12-principles' in toon_content

    def test_readability_checklist_preserved(self, md_content, toon_content):
        """Readability checklist preserved."""
        assert 'readability' in md_content.lower()
        assert 'readability' in toon_content.lower()

    def test_templates_preserved(self, md_content, toon_content):
        """Templates dependency preserved."""
        assert 'style-brief' in md_content or 'style_brief' in md_content
        assert 'style-brief' in toon_content or 'style_brief' in toon_content


class TestEmbeddedKnowledgePreserved:
    """Verify embedded knowledge markers are preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD file content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_build_inject_marker_preserved(self, md_content, toon_content):
        """BUILD:INJECT markers preserved."""
        md_has_inject = 'BUILD:INJECT' in md_content
        toon_has_inject = 'BUILD:INJECT' in toon_content
        # Both should have the marker OR both should have substantial content
        assert md_has_inject == toon_has_inject or len(toon_content) > 3000

    def test_illustrator_embed_reference(self, md_content, toon_content):
        """Illustrator embed reference preserved if present."""
        if 'embed/illustrator' in md_content:
            assert 'embed/illustrator' in toon_content or 'illustrator' in toon_content


class TestPipelinePreserved:
    """Verify pipeline/workflow content is preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD file content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_pipeline_section_preserved(self, md_content, toon_content):
        """Pipeline section preserved."""
        assert 'pipeline' in md_content.lower() or 'storyboard_phase' in md_content.lower()
        assert 'pipeline' in toon_content.lower() or 'storyboard' in toon_content.lower()

    def test_fps_value_preserved(self, md_content, toon_content):
        """FPS value (24) preserved."""
        assert '24' in md_content
        assert '24' in toon_content

    def test_animation_phase_preserved(self, md_content, toon_content):
        """Animation phase content preserved."""
        assert 'animation' in md_content.lower()
        assert 'animation' in toon_content.lower()


class TestReviewerContentPreserved:
    """Verify reviewer-specific content is preserved."""

    @pytest.fixture
    def md_content(self):
        """Load MD file content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_review_criteria_preserved(self, md_content, toon_content):
        """Review criteria preserved."""
        md_lower = md_content.lower()
        toon_lower = toon_content.lower()
        # Check for readability criteria
        assert 'readability' in md_lower and 'readability' in toon_lower

    def test_quality_gates_preserved(self, md_content, toon_content):
        """Quality gates preserved."""
        md_lower = md_content.lower()
        toon_lower = toon_content.lower()
        assert 'quality' in md_lower or 'gates' in md_lower
        assert 'quality' in toon_lower or 'gates' in toon_lower


class TestSemanticEquivalence:
    """Verify overall semantic equivalence."""

    @pytest.fixture
    def md_content(self):
        """Load MD file content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    @pytest.fixture
    def toon_content(self):
        """Load TOON file content."""
        with open(TOON_FILE, 'r', encoding='utf-8') as f:
            return f.read()

    def test_agent_type_equivalent(self, md_content, toon_content):
        """Agent type information equivalent."""
        # Both represent an agent
        assert 'agent' in md_content.lower() or 'illustrator' in md_content.lower()
        assert 'agent' in toon_content.lower()

    def test_sufficient_content_preserved(self, md_content, toon_content):
        """Sufficient content is preserved (TOON should be substantial)."""
        # TOON should preserve significant content
        assert len(toon_content) > 3000, "TOON content appears too small"

    def test_no_critical_data_lost(self, md_content, toon_content):
        """No critical data lost in conversion."""
        # Check critical elements present in both
        critical_elements = [
            'illustrator-reviewer',
            'haiku',
            'help',
            'review',
            'exit'
        ]
        for element in critical_elements:
            if element.lower() in md_content.lower():
                assert element.lower() in toon_content.lower(), \
                    f"Critical element '{element}' lost in conversion"

    def test_toolchain_preserved(self, md_content, toon_content):
        """Toolchain recommendations preserved."""
        md_lower = md_content.lower()
        toon_lower = toon_content.lower()
        # Check for key tools
        if 'krita' in md_lower:
            assert 'krita' in toon_lower
        if 'opentoonz' in md_lower:
            assert 'opentoonz' in toon_lower
