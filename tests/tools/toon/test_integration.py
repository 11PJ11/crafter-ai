"""Integration Tests for TOON Toolchain (Step 01-06).

End-to-end tests validating the complete pipeline:
    parse TOON → template selection → rendering → output validation

CRITICAL POLICY: NO MOCKS - All tests use real implementations.

Tests cover:
- Full pipeline E2E with real TOON file
- Error propagation (parser errors, template errors)
- Type-specific output validation (agent/command/skill schemas)

Test fixture: agents/novel-editor-chatgpt-toon.txt (TOON v1.0 format)
"""

import pytest
import yaml
import tempfile
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

from tools.toon.parser import TOONParser
from tools.toon.compiler import compile_toon
from tools.toon.template_adapter import adapt_for_template, render_agent_template


# ============================================================================
# FIXTURE PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
FIXTURE_PATH = PROJECT_ROOT / "agents" / "novel-editor-chatgpt-toon.txt"
TEMPLATE_DIR = PROJECT_ROOT / "tools" / "toon" / "templates"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def novel_editor_content():
    """Load the novel-editor TOON file content."""
    assert FIXTURE_PATH.exists(), f"Test fixture not found: {FIXTURE_PATH}"
    return FIXTURE_PATH.read_text(encoding="utf-8")


@pytest.fixture
def parser():
    """Create a real TOON parser instance."""
    return TOONParser()


@pytest.fixture
def jinja_env():
    """Create Jinja2 environment with real templates."""
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture
def temp_output_dir():
    """Create temporary directory for output files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


# ============================================================================
# TEST: FULL PIPELINE E2E
# ============================================================================


class TestIntegrationFullPipeline:
    """E2E test: parse → template selection → rendering → output."""

    def test_full_pipeline_parses_novel_editor_successfully(
        self, parser, novel_editor_content
    ):
        """Parser successfully processes the novel-editor TOON file."""
        result = parser.parse(novel_editor_content)

        # Parser produces valid output structure
        assert result is not None
        assert "id" in result
        assert "type" in result
        assert "metadata" in result
        assert "sections" in result

    def test_full_pipeline_detects_agent_type(self, parser, novel_editor_content):
        """Parser correctly identifies the content as agent type."""
        result = parser.parse(novel_editor_content)

        assert result["type"] == "agent"

    def test_full_pipeline_extracts_metadata(self, parser, novel_editor_content):
        """Parser extracts metadata from TOON header and ID section."""
        result = parser.parse(novel_editor_content)
        metadata = result["metadata"]

        # Metadata should contain name and version
        assert "name" in metadata or result["id"], "Agent should have name or id"
        assert "version" in metadata or result.get("toon_version"), "Version should be detected"

    def test_full_pipeline_extracts_sections(self, parser, novel_editor_content):
        """Parser extracts content sections from TOON file."""
        result = parser.parse(novel_editor_content)
        sections = result["sections"]

        # Novel-editor TOON has multiple sections
        assert len(sections) > 0, "Should extract at least one section"

        # Check for expected sections (based on fixture content)
        expected_sections = ["id", "core_rules", "4_scenarios", "metadata"]
        found_sections = [s.lower() for s in sections.keys()]

        # At least some expected sections should be present
        matching = sum(1 for s in expected_sections if any(s in f for f in found_sections))
        assert matching > 0, f"Expected some of {expected_sections}, found {found_sections}"

    def test_full_pipeline_compiles_to_output_file(
        self, temp_output_dir
    ):
        """Compiler produces output file from TOON input."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        # Output file should exist
        output_files = list(Path(temp_output_dir).glob("*.md"))
        assert len(output_files) == 1, f"Expected 1 output file, found {len(output_files)}"

    def test_full_pipeline_output_is_valid_markdown(self, temp_output_dir):
        """Compiled output is valid Markdown content."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        output_file = next(Path(temp_output_dir).glob("*.md"))
        content = output_file.read_text(encoding="utf-8")

        # Basic markdown validation: has content, starts reasonably
        assert len(content) > 100, "Output should have substantial content"
        # Should start with YAML frontmatter (---)
        assert content.strip().startswith("---"), "Agent output should start with YAML frontmatter"


# ============================================================================
# TEST: ERROR PROPAGATION - PARSER ERRORS
# ============================================================================


class TestIntegrationErrorPropagationParserErrors:
    """Test error handling for parser failures."""

    def test_parser_handles_empty_content_gracefully(self, parser):
        """Parser handles empty content without crashing."""
        result = parser.parse("")

        # Should return empty structure, not raise exception
        assert result is not None
        assert result["id"] == ""
        assert result["type"] == "agent"  # Default type
        assert result["metadata"] == {}
        assert result["sections"] == {}

    def test_parser_handles_none_content_gracefully(self, parser):
        """Parser handles None content without crashing."""
        # This tests the defensive programming of the parser
        result = parser.parse(None)

        assert result is not None
        assert "id" in result

    def test_parser_handles_malformed_toon_gracefully(self, parser):
        """Parser handles malformed TOON without raising exceptions."""
        malformed_content = """
        This is not valid TOON format
        Just random text without sections
        No ## headers, no key: value pairs
        """
        result = parser.parse(malformed_content)

        # Should parse best-effort without exceptions
        assert result is not None
        assert "id" in result
        assert "sections" in result

    def test_parser_handles_unicode_content(self, parser):
        """Parser handles unicode characters correctly."""
        unicode_content = """# UNICODE AGENT (TOON v1.0)
## ID
role: Test | unicode_test
spec: αβγδ | émojis 🚀 | 日本語

## RULES
→ Support unicode: αβγδ
→ Emojis: 🎯 ✅ ❌
→ Symbols: « » — – °
"""
        result = parser.parse(unicode_content)

        assert result is not None
        assert result["type"] == "agent"
        # Unicode should be preserved
        assert "unicode" in str(result).lower() or "αβγδ" in str(result)


# ============================================================================
# TEST: ERROR PROPAGATION - TEMPLATE ERRORS
# ============================================================================


class TestIntegrationErrorPropagationTemplateErrors:
    """Test error handling for template failures."""

    def test_compiler_handles_missing_input_file(self, temp_output_dir):
        """Compiler fails gracefully when input file doesn't exist."""
        with pytest.raises(FileNotFoundError):
            compile_toon("/nonexistent/path/file.toon", temp_output_dir)

    def test_compiler_handles_invalid_output_directory(self):
        """Compiler creates output directory if it doesn't exist."""
        with tempfile.TemporaryDirectory() as tmpdir:
            nested_output = Path(tmpdir) / "nested" / "deep" / "output"

            # Should not raise - compiler creates directories
            compile_toon(str(FIXTURE_PATH), str(nested_output))

            # Verify output was created
            output_files = list(nested_output.glob("*.md"))
            assert len(output_files) == 1

    def test_template_adapter_handles_empty_parser_output(self):
        """Template adapter handles empty parser output gracefully."""
        empty_output = {
            "id": "",
            "type": "agent",
            "metadata": {},
            "sections": {},
        }

        # Should not raise
        template_data = adapt_for_template(empty_output)

        assert template_data is not None
        assert "metadata_safe" in template_data
        assert "commands_typed" in template_data

    def test_template_adapter_handles_missing_sections(self):
        """Template adapter handles parser output with missing sections."""
        partial_output = {
            "id": "test-agent",
            "type": "agent",
            "metadata": {"name": "Test Agent"},
            # No sections key
        }

        template_data = adapt_for_template(partial_output)

        assert template_data is not None
        assert template_data["commands_typed"] == []


# ============================================================================
# TEST: OUTPUT VALIDATION - AGENT SCHEMA
# ============================================================================


class TestIntegrationOutputValidationAgentSchema:
    """Validate agent output follows Claude Code agent.md schema."""

    def test_agent_output_has_yaml_frontmatter(self, temp_output_dir):
        """Agent output includes YAML frontmatter section."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        output_file = next(Path(temp_output_dir).glob("*.md"))
        content = output_file.read_text(encoding="utf-8")

        # Extract frontmatter
        assert content.strip().startswith("---")
        parts = content.split("---", 2)
        assert len(parts) >= 3, "Should have opening and closing ---"

        # Parse frontmatter as YAML
        frontmatter_text = parts[1]
        frontmatter = yaml.safe_load(frontmatter_text)

        assert frontmatter is not None

    def test_agent_output_frontmatter_has_name(self, temp_output_dir):
        """Agent frontmatter includes name field."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        output_file = next(Path(temp_output_dir).glob("*.md"))
        content = output_file.read_text(encoding="utf-8")

        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])

        assert "name" in frontmatter, "Frontmatter must have 'name' field"
        assert frontmatter["name"], "Name should not be empty"

    def test_agent_output_has_content_after_frontmatter(self, temp_output_dir):
        """Agent output has markdown content after frontmatter."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        output_file = next(Path(temp_output_dir).glob("*.md"))
        content = output_file.read_text(encoding="utf-8")

        parts = content.split("---", 2)
        assert len(parts) == 3, "Should have frontmatter and content"

        body = parts[2].strip()
        assert len(body) > 0, "Should have content after frontmatter"

    def test_agent_output_has_title_heading(self, temp_output_dir):
        """Agent output has H1 title heading."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        output_file = next(Path(temp_output_dir).glob("*.md"))
        content = output_file.read_text(encoding="utf-8")

        parts = content.split("---", 2)
        body = parts[2]

        # Should have at least one # heading
        assert "# " in body, "Agent output should have heading"


# ============================================================================
# TEST: OUTPUT VALIDATION - COMMAND SCHEMA
# ============================================================================


class TestIntegrationOutputValidationCommandSchema:
    """Validate command output follows command.md schema."""

    @pytest.fixture
    def command_toon_content(self):
        """Create minimal command TOON content for testing.

        Note: Content must not contain 'AGENT' substring as parser checks
        for 'AGENT' before 'COMMAND' in type detection priority.
        """
        return """# DEVELOP COMMAND (TOON v1.0)
## ID
role: develop | develop
spec: command

## METADATA
name: develop
description: Execute DEVELOP wave
parent: software-crafter
version: v1.0

## PARAMETERS
- feature-description: string (required)

## RETURNS
type: object
"""

    def test_command_parses_as_command_type(self, parser, command_toon_content):
        """Parser identifies command TOON as command type."""
        result = parser.parse(command_toon_content)

        assert result["type"] == "command"

    def test_command_template_renders_with_frontmatter(
        self, jinja_env, parser, command_toon_content
    ):
        """Command template renders with YAML frontmatter."""
        parsed = parser.parse(command_toon_content)
        template_data = adapt_for_template(parsed)

        # Add required command template context
        # Note: template expects 'parent_agent' key
        template_data["metadata"]["name"] = template_data["metadata"].get("name", "test-command")
        template_data["metadata"]["parent_agent"] = template_data["metadata"].get(
            "parent_agent",
            template_data["metadata"].get("parent", "test-crafter")
        )

        template = jinja_env.get_template("command.md.j2")
        output = template.render(**template_data)

        # Validate frontmatter
        assert output.strip().startswith("---")
        parts = output.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])

        assert "name" in frontmatter
        assert "parent_agent" in frontmatter


# ============================================================================
# TEST: OUTPUT VALIDATION - SKILL SCHEMA
# ============================================================================


class TestIntegrationOutputValidationSkillSchema:
    """Validate skill output follows SKILL.md schema."""

    @pytest.fixture
    def skill_toon_content(self):
        """Create minimal skill TOON content for testing."""
        return """# TDD SKILL (TOON v1.0)
## ID
role: tdd | tdd-skill
spec: skill

## METADATA
name: develop
description: Use this skill when implementing features using test-driven development. Activates for implementing features, TDD, outside-in testing, writing tests first.
wave: DEVELOP
phase: 3

## WHEN_TO_USE
- Implementing new features
- Writing tests first
- Red-green-refactor cycle

## GUIDELINES
- Start with failing test
- Write minimal code to pass
- Refactor for quality
"""

    def test_skill_parses_as_skill_type(self, parser, skill_toon_content):
        """Parser identifies skill TOON as skill type."""
        result = parser.parse(skill_toon_content)

        assert result["type"] == "skill"

    def test_skill_template_renders_with_frontmatter(
        self, jinja_env, parser, skill_toon_content
    ):
        """Skill template renders with YAML frontmatter."""
        parsed = parser.parse(skill_toon_content)
        template_data = adapt_for_template(parsed)

        # Ensure required fields for skill template
        template_data["metadata"]["name"] = template_data["metadata"].get("name", "test-skill")
        template_data["metadata"]["description"] = template_data["metadata"].get(
            "description",
            "A test skill for validation purposes. Activates for testing and validation scenarios."
        )

        template = jinja_env.get_template("skill.md.j2")
        output = template.render(**template_data)

        # Validate frontmatter
        assert output.strip().startswith("---")
        parts = output.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])

        # Required Claude Code fields
        assert "name" in frontmatter
        assert "description" in frontmatter

    def test_skill_output_description_minimum_length(
        self, jinja_env, parser, skill_toon_content
    ):
        """Skill description meets minimum length requirement (50 chars)."""
        parsed = parser.parse(skill_toon_content)
        template_data = adapt_for_template(parsed)

        template_data["metadata"]["name"] = "develop"
        template_data["metadata"]["description"] = template_data["metadata"].get(
            "description",
            "Use this skill when implementing features using test-driven development. Activates for implementing features, TDD, outside-in testing."
        )

        template = jinja_env.get_template("skill.md.j2")
        output = template.render(**template_data)

        parts = output.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])

        description = frontmatter.get("description", "")
        assert len(description) >= 50, f"Description must be at least 50 chars, got {len(description)}"


# ============================================================================
# TEST: VERSION COMPATIBILITY
# ============================================================================


class TestIntegrationVersionCompatibility:
    """Test TOON version detection and handling."""

    def test_parser_detects_v1_0_version(self, parser, novel_editor_content):
        """Parser detects TOON v1.0 from header."""
        result = parser.parse(novel_editor_content)

        # novel-editor-chatgpt-toon.txt uses v1.0
        assert result.get("toon_version") == "v1.0"

    def test_parser_detects_v3_0_version(self, parser):
        """Parser detects TOON v3.0 from header."""
        v3_content = """# TEST AGENT (TOON v3.0)
## ID
role: Test Agent | test_agent
"""
        result = parser.parse(v3_content)

        assert result.get("toon_version") == "v3.0"

    def test_parser_handles_unknown_version(self, parser):
        """Parser handles content without version gracefully."""
        no_version_content = """# TEST AGENT
## ID
role: Test | test
"""
        result = parser.parse(no_version_content)

        assert result.get("toon_version") == "unknown"


# ============================================================================
# TEST: FULL E2E COMPILATION
# ============================================================================


class TestIntegrationE2ECompilation:
    """Complete end-to-end compilation tests."""

    def test_novel_editor_compiles_to_valid_agent_md(self, temp_output_dir):
        """Novel-editor TOON compiles to valid Claude Code agent.md format."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        output_file = next(Path(temp_output_dir).glob("*.md"))
        content = output_file.read_text(encoding="utf-8")

        # 1. Has YAML frontmatter
        assert content.strip().startswith("---")

        # 2. Frontmatter is valid YAML
        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])
        assert frontmatter is not None

        # 3. Has required agent fields
        assert "name" in frontmatter

        # 4. Has markdown body
        body = parts[2].strip()
        assert len(body) > 0

        # 5. Output file has correct naming
        assert output_file.stem in ["aria", "genre-editor", "novel-editor", "genre_editor"]

    def test_compilation_preserves_agent_identity(self, temp_output_dir):
        """Compilation preserves agent identity from source TOON."""
        compile_toon(str(FIXTURE_PATH), temp_output_dir)

        output_file = next(Path(temp_output_dir).glob("*.md"))
        content = output_file.read_text(encoding="utf-8")

        parts = content.split("---", 2)
        frontmatter = yaml.safe_load(parts[1])

        # Agent identity should be preserved
        # Novel-editor has name "Novel Editor" or similar
        name = frontmatter.get("name", "").lower()
        assert any(
            term in name for term in ["novel", "editor", "aria", "genre"]
        ), f"Agent identity not preserved. Got name: {frontmatter.get('name')}"
