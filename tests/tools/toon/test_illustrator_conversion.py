"""Tests for illustrator.md to TOON v3.0 conversion validation.

Step 05-02 acceptance criteria validation:
- TOON v3.0 file generated: nWave/agents/illustrator.toon
- Schema validation passes
- All YAML keys preserved
- Zero syntax errors

Test approach follows troubleshooter conversion pattern as reference.
"""

import tempfile
from pathlib import Path

import pytest

from tools.toon.compiler import compile_toon
from tools.toon.parser import TOONParser

# Test constants
TOON_FILE = Path("nWave/agents/illustrator.toon")
ORIGINAL_MD = Path("nWave/agents/illustrator.md")

# Expected commands from original illustrator.md
EXPECTED_COMMANDS = [
    "help",
    "discover-style",
    "storyboard",
    "animatic",
    "design-motion",
    "lip-sync",
    "cleanup-inkpaint",
    "export-master",
    "toolchain",
    "review",
    "exit",
]

# Expected checklist dependencies from original
EXPECTED_CHECKLISTS = [
    "12-principles-check.md",
    "readability-pass.md",
    "lip-sync-pass.md",
    "export-specs.md",
]

# Expected template dependencies from original
EXPECTED_TEMPLATES = [
    "style-brief.yaml",
    "shot-card.md",
    "x-sheet.csv",
    "timing-chart.svg",
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
        """Agent ID is 'illustrator'."""
        assert parsed_toon["id"] == "illustrator"

    def test_toon_has_agent_type(self, parsed_toon):
        """Content type is 'agent'."""
        assert parsed_toon["type"] == "agent"

    def test_toon_has_version(self, parsed_toon):
        """TOON version is v3.0."""
        assert parsed_toon["toon_version"] == "v3.0"

    def test_toon_has_name_in_metadata(self, parsed_toon):
        """Metadata contains persona name 'Luma'."""
        assert "name" in parsed_toon["metadata"]
        # Parser extracts name from 'role: Luma | illustrator' or similar
        assert parsed_toon["metadata"]["name"] in ["Luma", "Illustrator"]

    def test_toon_has_model_in_metadata(self, parsed_toon):
        """Metadata contains model 'inherit'."""
        assert "model" in parsed_toon["metadata"]
        assert parsed_toon["metadata"]["model"] == "inherit"

    def test_toon_has_role_in_metadata(self, parsed_toon):
        """Metadata contains role with 'illustrator' or 'visual-designer-2d'."""
        assert "role" in parsed_toon["metadata"]
        role_lower = parsed_toon["metadata"]["role"].lower()
        assert "illustrator" in role_lower or "visual" in role_lower or "designer" in role_lower


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

    def test_storyboard_command_present(self, toon_content):
        """storyboard command is present."""
        assert "- storyboard:" in toon_content

    def test_animatic_command_present(self, toon_content):
        """animatic command is present."""
        assert "- animatic:" in toon_content

    def test_lip_sync_command_present(self, toon_content):
        """lip-sync command is present."""
        assert "- lip-sync:" in toon_content

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

    def test_checklist_dependencies_present(self, toon_content):
        """Verify checklist dependencies are listed."""
        for checklist in EXPECTED_CHECKLISTS:
            assert checklist in toon_content, f"Checklist dependency '{checklist}' missing from TOON"

    def test_template_dependencies_present(self, toon_content):
        """Verify template dependencies are listed."""
        for template in EXPECTED_TEMPLATES:
            assert template in toon_content, f"Template dependency '{template}' missing from TOON"


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

    def test_critique_dimensions_inject_marker_present(self, toon_content):
        """Critique dimensions inject marker present."""
        assert "BUILD:INJECT:START:nWave/data/embed/illustrator/critique-dimensions.md" in toon_content

    def test_inject_markers_count(self, toon_content):
        """Verify expected number of BUILD:INJECT pairs."""
        start_count = toon_content.count("BUILD:INJECT:START")
        end_count = toon_content.count("BUILD:INJECT:END")
        assert start_count >= 1, f"Expected at least 1 START marker, found {start_count}"
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
            assert "illustrator" in content.lower()


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
    """Verify TOON captures key knowledge sections from illustrator.md."""

    @pytest.fixture
    def toon_content(self):
        with open(TOON_FILE, "r") as f:
            return f.read()

    def test_pipeline_framework_preserved(self, toon_content):
        """Pipeline framework is captured."""
        assert "PIPELINE" in toon_content.upper()

    def test_animation_phases_preserved(self, toon_content):
        """Animation phases are captured (storyboard, animatic, animation)."""
        assert "storyboard" in toon_content.lower()
        assert "animatic" in toon_content.lower()
        assert "animation" in toon_content.lower()

    def test_lip_sync_framework_preserved(self, toon_content):
        """Lip sync framework is captured."""
        assert "LIP_SYNC" in toon_content or "lip-sync" in toon_content.lower()

    def test_export_framework_preserved(self, toon_content):
        """Export framework is captured."""
        assert "EXPORT" in toon_content.upper()

    def test_toolchain_recommendations_preserved(self, toon_content):
        """Toolchain recommendations are captured."""
        assert "TOOLCHAIN" in toon_content.upper()

    def test_review_criteria_preserved(self, toon_content):
        """Review criteria (12 principles) are captured."""
        assert "12" in toon_content and "principles" in toon_content.lower()

    def test_quality_gates_preserved(self, toon_content):
        """Quality gates are captured."""
        assert "quality" in toon_content.lower() and "gate" in toon_content.lower()

    def test_contract_preserved(self, toon_content):
        """Contract section is captured."""
        assert "CONTRACT" in toon_content.upper()

    def test_safety_framework_preserved(self, toon_content):
        """Safety framework is captured."""
        assert "SAFETY" in toon_content.upper()

    def test_testing_framework_preserved(self, toon_content):
        """Testing framework is captured."""
        assert "TESTING" in toon_content.upper()

    def test_observability_framework_preserved(self, toon_content):
        """Observability framework is captured."""
        assert "OBSERVABILITY" in toon_content.upper()

    def test_error_recovery_framework_preserved(self, toon_content):
        """Error recovery framework is captured."""
        assert "ERROR_RECOVERY" in toon_content or "error_recovery" in toon_content.lower()

    def test_production_readiness_preserved(self, toon_content):
        """Production readiness is captured."""
        assert "PRODUCTION_READINESS" in toon_content or "production_readiness" in toon_content.lower()


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


class TestTOONSizeReduction:
    """Verify TOON achieves reasonable size reduction from original MD."""

    def test_toon_smaller_than_original(self):
        """TOON file should be smaller than original MD."""
        toon_size = TOON_FILE.stat().st_size
        original_size = ORIGINAL_MD.stat().st_size

        # Allow for reasonable reduction (TOON should be smaller)
        # Note: With all the production frameworks, reduction may be modest
        assert toon_size < original_size, \
            f"TOON ({toon_size} bytes) should be smaller than original ({original_size} bytes)"

    def test_toon_line_count(self):
        """TOON file should have reasonable line count."""
        with open(TOON_FILE, "r") as f:
            line_count = len(f.readlines())

        # Should be a reasonable size (not too small, not excessively large)
        assert line_count >= 200, f"TOON file seems too small: {line_count} lines"
        assert line_count <= 1500, f"TOON file seems too large: {line_count} lines"
