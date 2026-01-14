"""
Tests for illustrator-reviewer.md parsing and structure extraction.
Step 06-01: Parse illustrator-reviewer.md and validate structure extraction.

TDD Phase: RED - Tests that verify parsing functionality.
"""
import pytest
import os
import yaml
import json

# Paths
MD_FILE = "nWave/agents/illustrator-reviewer.md"
PARSED_OUTPUT = "docs/feature/toon-agent-conversion/parsed/illustrator-reviewer-parsed.yaml"


class TestMDFileExists:
    """Verify source MD file exists and is readable."""

    def test_md_file_exists(self):
        """AC1: MD file illustrator-reviewer.md exists."""
        assert os.path.exists(MD_FILE), f"Source file not found: {MD_FILE}"

    def test_md_file_not_empty(self):
        """Source file has content."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        assert len(content) > 1000, "Source file appears too small"

    def test_md_file_has_yaml_frontmatter(self):
        """Source file starts with YAML frontmatter."""
        with open(MD_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        # Check for frontmatter markers
        assert content.strip().startswith('---') or 'id:' in content[:500], \
            "File should have YAML frontmatter"


class TestParsedOutputExists:
    """Verify parsed output file is created."""

    def test_parsed_output_exists(self):
        """Parsed output YAML file exists."""
        assert os.path.exists(PARSED_OUTPUT), f"Parsed output not found: {PARSED_OUTPUT}"

    def test_parsed_output_valid_yaml(self):
        """Parsed output is valid YAML."""
        with open(PARSED_OUTPUT, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        assert data is not None, "Parsed output is empty or invalid YAML"


class TestParsedStructure:
    """Verify parsed structure contains required sections."""

    @pytest.fixture
    def parsed_data(self):
        """Load parsed YAML data."""
        with open(PARSED_OUTPUT, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_has_agent_id(self, parsed_data):
        """AC3: Parsed data contains agent ID."""
        assert 'id' in parsed_data or 'agent_id' in parsed_data, \
            "Parsed output must contain agent ID"

    def test_has_agent_type(self, parsed_data):
        """Parsed data contains agent type."""
        assert 'type' in parsed_data, "Parsed output must contain type"

    def test_agent_type_is_agent(self, parsed_data):
        """Agent type should be 'agent'."""
        assert parsed_data.get('type') == 'agent', "Type should be 'agent'"

    def test_has_version(self, parsed_data):
        """Parsed data contains version."""
        assert 'version' in parsed_data, "Parsed output must contain version"

    def test_has_model_optimization(self, parsed_data):
        """Parsed data contains model optimization (reviewer uses Haiku)."""
        model = parsed_data.get('model_optimization') or parsed_data.get('model')
        assert model is not None, "Reviewer agent must specify model optimization"

    def test_model_is_haiku(self, parsed_data):
        """Reviewer agent should be optimized for Haiku model."""
        model = parsed_data.get('model_optimization') or parsed_data.get('model')
        assert model is not None and 'haiku' in str(model).lower(), \
            "Reviewer agent should use Haiku model"

    def test_has_sections(self, parsed_data):
        """AC2: All sections identified and extracted."""
        assert 'sections' in parsed_data or 'content_sections' in parsed_data, \
            "Parsed output must contain sections"

    def test_has_dependencies(self, parsed_data):
        """Parsed data contains dependencies."""
        deps = parsed_data.get('dependencies') or parsed_data.get('requires')
        # Dependencies might be empty list, which is fine
        assert deps is not None or 'dependencies' in str(parsed_data), \
            "Parsed output should have dependencies field"


class TestContentExtraction:
    """Verify content is correctly extracted."""

    @pytest.fixture
    def parsed_data(self):
        """Load parsed YAML data."""
        with open(PARSED_OUTPUT, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_has_purpose_section(self, parsed_data):
        """Purpose/overview section extracted."""
        sections = parsed_data.get('sections') or parsed_data.get('content_sections') or {}
        section_names = str(sections).lower()
        assert 'purpose' in section_names or 'overview' in section_names or 'description' in section_names, \
            "Should have purpose/overview section"

    def test_has_review_capabilities(self, parsed_data):
        """Review capabilities extracted (specific to reviewer agents)."""
        content = str(parsed_data).lower()
        assert 'review' in content, "Reviewer agent should have review-related content"

    def test_has_quality_criteria(self, parsed_data):
        """Quality criteria for review extracted."""
        content = str(parsed_data).lower()
        assert 'quality' in content or 'criteria' in content or 'check' in content, \
            "Reviewer should have quality criteria"


class TestEmbeddedKnowledge:
    """Verify embedded knowledge sections are preserved."""

    @pytest.fixture
    def parsed_data(self):
        """Load parsed YAML data."""
        with open(PARSED_OUTPUT, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_embedded_knowledge_preserved(self, parsed_data):
        """BUILD:INJECT markers or embedded knowledge preserved."""
        content = str(parsed_data)
        # Check for either BUILD:INJECT markers or substantial content
        has_inject = 'BUILD:INJECT' in content or 'INJECT' in content
        has_substantial_content = len(content) > 5000
        assert has_inject or has_substantial_content, \
            "Embedded knowledge should be preserved"


class TestParsingQuality:
    """Verify parsing quality - no errors or warnings."""

    @pytest.fixture
    def parsed_data(self):
        """Load parsed YAML data."""
        with open(PARSED_OUTPUT, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_no_parsing_errors(self, parsed_data):
        """AC4: No parsing errors in output."""
        errors = parsed_data.get('parsing_errors') or parsed_data.get('errors')
        assert not errors, f"Parsing errors detected: {errors}"

    def test_no_parsing_warnings(self, parsed_data):
        """AC4: No parsing warnings in output."""
        warnings = parsed_data.get('parsing_warnings') or parsed_data.get('warnings')
        # Warnings might be empty list which is fine
        if warnings:
            assert len(warnings) == 0, f"Parsing warnings detected: {warnings}"

    def test_content_not_truncated(self, parsed_data):
        """Content should not be truncated."""
        content = str(parsed_data)
        assert 'truncated' not in content.lower() or 'not truncated' in content.lower(), \
            "Content appears to be truncated"


class TestReviewerSpecificFields:
    """Test reviewer-specific agent fields."""

    @pytest.fixture
    def parsed_data(self):
        """Load parsed YAML data."""
        with open(PARSED_OUTPUT, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)

    def test_reviewer_role_defined(self, parsed_data):
        """Reviewer role is clearly defined."""
        content = str(parsed_data).lower()
        assert 'reviewer' in content, "Reviewer role should be defined"

    def test_has_review_checklist_or_criteria(self, parsed_data):
        """Should have review checklist or criteria."""
        content = str(parsed_data).lower()
        assert 'checklist' in content or 'criteria' in content or 'check' in content, \
            "Reviewer should have checklist or criteria"

    def test_illustrator_domain_reference(self, parsed_data):
        """Should reference illustrator domain knowledge."""
        content = str(parsed_data).lower()
        assert 'diagram' in content or 'visual' in content or 'illustration' in content, \
            "Should reference illustrator domain"
