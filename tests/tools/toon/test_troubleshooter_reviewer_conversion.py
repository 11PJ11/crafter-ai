"""Tests for troubleshooter-reviewer.md to TOON v3.0 conversion validation.

Step 04-02 acceptance criteria validation:
- TOON v3.0 file generated: nWave/agents/troubleshooter-reviewer.toon
- Schema validation passes
- All YAML keys preserved
- Zero syntax errors

Test approach follows troubleshooter conversion pattern as reference.
The troubleshooter-reviewer is a review-focused variant using Haiku model.
"""

import tempfile
from pathlib import Path

import pytest

from tools.toon.compiler import compile_toon
from tools.toon.parser import TOONParser

# Test constants
TOON_FILE = Path("nWave/agents/troubleshooter-reviewer.toon")
ORIGINAL_MD = Path("nWave/agents/troubleshooter-reviewer.md")

# Expected commands from original troubleshooter-reviewer.md
EXPECTED_COMMANDS = [
    "help",
    "investigate-problem",
    "analyze-system-failure",
    "investigate-recurring-issue",
    "analyze-performance-degradation",
    "investigate-integration-failure",
    "conduct-post-mortem",
    "validate-root-causes",
    "develop-prevention-strategy",
    "exit",
]

# Expected dependencies from original
EXPECTED_TASKS = [
    "dw/root-why.md",
]

EXPECTED_EMBED_PATHS = [
    "nWave/data/embed/troubleshooter/comprehensive-rca-methodologies.md",
]


class TestTOONFileExists:
    """Verify TOON file was created."""

    def test_toon_file_exists(self):
        """AC1: TOON v3.0 file generated."""
        assert TOON_FILE.exists(), f"TOON file not found: {TOON_FILE}"

    def test_original_md_preserved(self):
        """Original .md file kept for comparison until Phase 8."""
        assert ORIGINAL_MD.exists(), f"Original MD file should be preserved: {ORIGINAL_MD}"


class TestTOONMetadata:
    """Verify all agent metadata is present in TOON."""

    @pytest.fixture
    def parsed_toon(self):
        parser = TOONParser()
        with open(TOON_FILE, "r") as f:
            return parser.parse(f.read())

    def test_toon_has_agent_id(self, parsed_toon):
        """Agent ID is 'troubleshooter-reviewer'."""
        assert parsed_toon["id"] == "troubleshooter-reviewer"

    def test_toon_has_agent_type(self, parsed_toon):
        """Content type is 'agent'."""
        assert parsed_toon["type"] == "agent"

    def test_toon_has_version(self, parsed_toon):
        """TOON version is v3.0."""
        assert parsed_toon["toon_version"] == "v3.0"

    def test_toon_has_name_in_metadata(self, parsed_toon):
        """Metadata contains name 'Sage' from agent definition."""
        assert "name" in parsed_toon["metadata"]
        # Troubleshooter-reviewer uses same persona name 'Sage'
        assert parsed_toon["metadata"]["name"] in ["Sage", "Troubleshooter-Reviewer"]

    def test_toon_has_model_haiku(self, parsed_toon):
        """Metadata contains model 'haiku' - review variant uses cost-efficient model."""
        assert "model" in parsed_toon["metadata"]
        assert parsed_toon["metadata"]["model"] == "haiku"

    def test_toon_has_role_in_metadata(self, parsed_toon):
        """Metadata contains role with 'troubleshooter-reviewer'."""
        assert "role" in parsed_toon["metadata"]
        assert "troubleshooter-reviewer" in parsed_toon["metadata"]["role"]


class TestTOONCommands:
    """Verify all commands are present in TOON. AC3: All YAML keys preserved."""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    @pytest.fixture
    def parsed_toon(self, toon_content):
        parser = TOONParser()
        return parser.parse(toon_content)

    def test_commands_section_exists(self, parsed_toon):
        """Commands section exists in parsed TOON."""
        assert "commands" in parsed_toon["sections"]

    def test_all_commands_present(self, toon_content):
        """Verify each expected command is in the TOON file."""
        for command in EXPECTED_COMMANDS:
            assert (
                command in toon_content.lower()
            ), f"Command '{command}' missing from TOON"

    def test_help_command_present(self, toon_content):
        """Help command is present."""
        assert "- help:" in toon_content

    def test_investigate_problem_command_present(self, toon_content):
        """investigate-problem command is present."""
        assert "- investigate-problem:" in toon_content

    def test_exit_command_present(self, toon_content):
        """Exit command is present."""
        assert "- exit:" in toon_content


class TestTOONDependencies:
    """Verify all dependencies are present in TOON. AC3: All YAML keys preserved."""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    @pytest.fixture
    def parsed_toon(self, toon_content):
        parser = TOONParser()
        return parser.parse(toon_content)

    def test_dependencies_section_exists(self, parsed_toon):
        """Dependencies section exists."""
        assert "dependencies" in parsed_toon["sections"]

    def test_tasks_dependencies_present(self, toon_content):
        """Verify task dependencies are listed."""
        for task in EXPECTED_TASKS:
            assert task in toon_content, f"Task dependency '{task}' missing from TOON"

    def test_embed_knowledge_dependencies_present(self, toon_content):
        """Verify embed_knowledge paths are listed."""
        for path in EXPECTED_EMBED_PATHS:
            assert path in toon_content, f"Embed knowledge path '{path}' missing from TOON"


class TestTOONEmbeddedKnowledgeMarkers:
    """Verify BUILD:INJECT markers are preserved."""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    def test_build_inject_start_markers_present(self, toon_content):
        """Verify BUILD:INJECT:START markers are preserved."""
        assert "BUILD:INJECT:START" in toon_content

    def test_build_inject_end_markers_present(self, toon_content):
        """Verify BUILD:INJECT:END markers are preserved."""
        assert "BUILD:INJECT:END" in toon_content

    def test_rca_inject_marker_present(self, toon_content):
        """RCA methodologies inject marker present."""
        assert "BUILD:INJECT:START:nWave/data/embed/troubleshooter/comprehensive-rca-methodologies.md" in toon_content

    def test_critique_dimensions_inject_marker_present(self, toon_content):
        """Critique dimensions inject marker present."""
        assert "BUILD:INJECT:START:nWave/data/embed/troubleshooter/critique-dimensions.md" in toon_content

    def test_inject_markers_count(self, toon_content):
        """Verify expected number of BUILD:INJECT pairs."""
        start_count = toon_content.count("BUILD:INJECT:START")
        end_count = toon_content.count("BUILD:INJECT:END")
        assert start_count >= 2, f"Expected at least 2 START markers, found {start_count}"
        assert start_count == end_count, f"Mismatched START ({start_count}) and END ({end_count}) markers"


class TestTOONSchemaValidation:
    """AC2: Schema validation passes - Compiler accepts TOON syntax."""

    def test_compiler_accepts_toon_file(self):
        """TOON file compiles without errors."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Should not raise exception
            compile_toon(str(TOON_FILE), tmpdir)

            # Should produce output file
            output_files = list(Path(tmpdir).glob("*.md"))
            assert len(output_files) == 1, f"Expected 1 output file, got {len(output_files)}"

    def test_compiled_output_has_frontmatter(self):
        """Compiled output has YAML frontmatter."""
        with tempfile.TemporaryDirectory() as tmpdir:
            compile_toon(str(TOON_FILE), tmpdir)
            output_file = list(Path(tmpdir).glob("*.md"))[0]

            with open(output_file, "r") as f:
                content = f.read()

            assert content.startswith("---") or content.startswith("\n---")

    def test_compiled_output_has_name(self):
        """Compiled output includes agent name."""
        with tempfile.TemporaryDirectory() as tmpdir:
            compile_toon(str(TOON_FILE), tmpdir)
            output_file = list(Path(tmpdir).glob("*.md"))[0]

            with open(output_file, "r") as f:
                content = f.read()

            assert "name:" in content
            assert "troubleshooter-reviewer" in content.lower()


class TestTOONSyntaxErrors:
    """AC4: Zero syntax errors - parser handles file correctly."""

    @pytest.fixture
    def parsed_toon(self):
        parser = TOONParser()
        with open(TOON_FILE, "r") as f:
            return parser.parse(f.read())

    def test_parser_returns_valid_structure(self, parsed_toon):
        """Parser returns complete structure without errors."""
        assert parsed_toon is not None
        assert "id" in parsed_toon
        assert "type" in parsed_toon
        assert "metadata" in parsed_toon
        assert "sections" in parsed_toon

    def test_sections_not_empty(self, parsed_toon):
        """Sections are not empty."""
        assert len(parsed_toon["sections"]) > 0


class TestTOONCompleteness:
    """Verify TOON captures key knowledge sections from troubleshooter-reviewer.md."""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    def test_toyota_5_whys_preserved(self, toon_content):
        """Toyota 5 Whys methodology is captured."""
        assert "5_WHYS" in toon_content.upper() or "TOYOTA" in toon_content.upper()

    def test_investigation_framework_preserved(self, toon_content):
        """Investigation framework is captured."""
        assert "INVESTIGATION" in toon_content.upper()

    def test_problem_taxonomy_preserved(self, toon_content):
        """Problem taxonomy is captured."""
        assert "PROBLEM" in toon_content.upper()

    def test_analysis_methodology_preserved(self, toon_content):
        """Analysis methodology is captured."""
        assert "ANALYSIS" in toon_content.upper()

    def test_solution_framework_preserved(self, toon_content):
        """Solution framework is captured."""
        assert "SOLUTION" in toon_content.upper()

    def test_post_mortem_preserved(self, toon_content):
        """Post-mortem framework is captured."""
        assert "POST_MORTEM" in toon_content or "post-mortem" in toon_content.lower()

    def test_quality_framework_preserved(self, toon_content):
        """Quality framework is captured."""
        assert "QUALITY" in toon_content.upper()

    def test_collaboration_preserved(self, toon_content):
        """Collaboration patterns are captured."""
        assert "COLLABORATION" in toon_content.upper()


class TestTOONFormat:
    """Verify TOON follows v3.0 format conventions."""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    def test_has_toon_header(self, toon_content):
        """File has TOON v3.0 header."""
        assert "(TOON v3.0)" in toon_content

    def test_has_id_section(self, toon_content):
        """File has ## ID section."""
        assert "## ID" in toon_content

    def test_has_persona_section(self, toon_content):
        """File has ## PERSONA section."""
        assert "## PERSONA" in toon_content

    def test_has_core_principles_section(self, toon_content):
        """File has ## CORE_PRINCIPLES section."""
        assert "## CORE_PRINCIPLES" in toon_content

    def test_has_activation_section(self, toon_content):
        """File has ## ACTIVATION section."""
        assert "## ACTIVATION" in toon_content

    def test_has_commands_section(self, toon_content):
        """File has ## COMMANDS section."""
        assert "## COMMANDS" in toon_content

    def test_has_dependencies_section(self, toon_content):
        """File has ## DEPENDENCIES section."""
        assert "## DEPENDENCIES" in toon_content

    def test_has_metadata_section(self, toon_content):
        """File has ## METADATA section."""
        assert "## METADATA" in toon_content

    def test_uses_toon_symbols(self, toon_content):
        """File uses TOON symbols for implications."""
        # Check for arrow symbol (→) used in TOON format
        assert "→" in toon_content

    def test_has_toon_notes_footer(self, toon_content):
        """File has TOON_NOTES footer."""
        assert "TOON_NOTES:" in toon_content


class TestReviewerSpecificContent:
    """Verify reviewer-specific content is preserved."""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    def test_reviewer_role_mentioned(self, toon_content):
        """Review role is mentioned in the content."""
        content_lower = toon_content.lower()
        assert "review" in content_lower

    def test_haiku_model_in_description(self, toon_content):
        """Haiku model is mentioned for cost efficiency."""
        content_lower = toon_content.lower()
        assert "haiku" in content_lower

    def test_cost_efficient_mentioned(self, toon_content):
        """Cost-efficient operation is mentioned."""
        content_lower = toon_content.lower()
        assert "cost" in content_lower or "efficient" in content_lower
