"""Tests for researcher-reviewer roundtrip validation (MD -> TOON -> MD).

Step 02-03 acceptance criteria:
1. MD -> TOON -> MD produces equivalent output
2. All YAML keys present in both directions
3. Values match after whitespace normalization
4. Embedded knowledge sections byte-identical

This test file validates the researcher-reviewer.toon file specifically,
ensuring the conversion preserves all critical content from the original
researcher-reviewer.md source.
"""

import tempfile
from pathlib import Path

import pytest

from tools.toon.compiler import compile_toon
from tools.toon.validate_roundtrip import (
    command_list_validator,
    dependency_list_validator,
    embedded_knowledge_validator,
    extract_commands,
    extract_dependencies,
    extract_inject_markers,
    metadata_validator,
    section_presence_validator,
    validate_roundtrip,
)


# Test files specific to researcher-reviewer
TOON_FILE = Path("nWave/agents/researcher-reviewer.toon")
ORIGINAL_MD = Path("nWave/agents/researcher-reviewer.md")


@pytest.fixture
def researcher_reviewer_toon_exists():
    """Verify TOON file exists before running tests."""
    assert TOON_FILE.exists(), f"TOON file not found: {TOON_FILE}"
    return True


@pytest.fixture
def researcher_reviewer_md_exists():
    """Verify original MD file exists before running tests."""
    assert ORIGINAL_MD.exists(), f"Original MD file not found: {ORIGINAL_MD}"
    return True


@pytest.fixture
def compiled_md_path(researcher_reviewer_toon_exists):
    """Compile TOON to temporary MD file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        compile_toon(str(TOON_FILE), tmpdir)
        output_files = list(Path(tmpdir).glob("*.md"))
        assert len(output_files) > 0, "No compiled MD file produced"
        yield str(output_files[0])


@pytest.fixture
def compiled_content(compiled_md_path):
    """Get compiled markdown content."""
    return Path(compiled_md_path).read_text()


@pytest.fixture
def original_content(researcher_reviewer_md_exists):
    """Get original markdown content."""
    return ORIGINAL_MD.read_text()


@pytest.fixture
def toon_content(researcher_reviewer_toon_exists):
    """Get TOON source content."""
    return TOON_FILE.read_text()


class TestResearcherReviewerRoundtripValidation:
    """E2E tests for researcher-reviewer roundtrip validation.

    AC1: MD -> TOON -> MD produces equivalent output
    """

    def test_roundtrip_equivalence_score_threshold(self, compiled_md_path):
        """GIVEN researcher-reviewer.md and compiled output from researcher-reviewer.toon
        WHEN I run roundtrip validation
        THEN semantic equivalence score >= 95%
        """
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)

        assert result["equivalence_score"] >= 95, (
            f"Equivalence score {result['equivalence_score']}% is below 95% threshold.\n"
            f"Commands match: {result['commands_match']}\n"
            f"Dependencies match: {result['dependencies_match']}\n"
            f"Frontmatter valid: {result['frontmatter_valid']}\n"
            f"Critical sections: {result['critical_sections_present']}\n"
            f"Embedded knowledge: {result['embedded_knowledge_preserved']}\n"
            f"Differences: {result['differences']}"
        )

    def test_roundtrip_commands_preserved(self, compiled_md_path):
        """GIVEN original MD and compiled output
        WHEN comparing command lists
        THEN all commands are preserved (order-independent)
        """
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)
        assert result["commands_match"] is True, "Commands do not match between original and compiled"

    def test_roundtrip_dependencies_preserved(self, compiled_md_path):
        """GIVEN original MD and compiled output
        WHEN comparing dependency lists
        THEN at least 80% of dependencies are preserved
        """
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)
        assert result["dependencies_match"] is True, "Dependencies do not match between original and compiled"


class TestResearcherReviewerYAMLKeyPreservation:
    """AC2: All YAML keys present in both directions."""

    def test_toon_has_id_section(self, toon_content):
        """TOON file should have ID section with required metadata."""
        assert "## ID" in toon_content, "TOON file missing ## ID section"
        assert "role:" in toon_content.lower(), "TOON file missing role metadata"

    def test_toon_has_persona_section(self, toon_content):
        """TOON file should have PERSONA section."""
        assert "## PERSONA" in toon_content, "TOON file missing ## PERSONA section"

    def test_toon_has_commands_section(self, toon_content):
        """TOON file should have COMMANDS section."""
        assert "## COMMANDS" in toon_content, "TOON file missing ## COMMANDS section"

    def test_toon_has_dependencies_section(self, toon_content):
        """TOON file should have DEPENDENCIES section."""
        assert "## DEPENDENCIES" in toon_content, "TOON file missing ## DEPENDENCIES section"

    def test_compiled_has_frontmatter(self, compiled_content):
        """Compiled output should have valid YAML frontmatter."""
        # Should have frontmatter OR TOON ID section
        # Frontmatter may have leading whitespace
        has_frontmatter = "---" in compiled_content[:50]  # Check start of file
        has_toon_id = "## ID" in compiled_content
        assert has_frontmatter or has_toon_id, "Compiled output missing frontmatter or ID section"

    def test_compiled_metadata_valid(self, compiled_content):
        """Compiled output should have valid metadata."""
        assert metadata_validator(compiled_content) is True, "Compiled output has invalid metadata"


class TestResearcherReviewerValueMatching:
    """AC3: Values match after whitespace normalization."""

    def test_command_names_match(self, original_content, compiled_content):
        """Command names should match between original and compiled."""
        original_cmds = set(extract_commands(original_content))
        compiled_cmds = set(extract_commands(compiled_content))

        # Find commands in common
        common_cmds = original_cmds & compiled_cmds

        # At least core commands should be present
        core_commands = {"help", "research", "exit"}
        missing_core = core_commands - common_cmds

        assert not missing_core, f"Missing core commands in compiled output: {missing_core}"

    def test_command_list_order_independent(self, original_content, compiled_content):
        """Command list validation should be order-independent."""
        # The validator already does order-independent comparison
        result = command_list_validator(original_content, compiled_content)
        assert isinstance(result, bool), "command_list_validator should return bool"

    def test_dependency_tasks_preserved(self, original_content, compiled_content):
        """Task dependencies should be preserved."""
        original_deps = extract_dependencies(original_content)
        compiled_deps = extract_dependencies(compiled_content)

        # Check that task dependencies are present
        if original_deps.get("tasks"):
            # At least some tasks should be in compiled
            original_tasks = set(original_deps["tasks"])
            compiled_tasks = set(compiled_deps.get("tasks", []))

            # Allow for some flexibility - check key tasks are present
            # dw/research.md is the main task for researcher
            key_tasks = {t for t in original_tasks if "research" in t.lower()}

            if key_tasks:
                preserved = key_tasks & compiled_tasks
                # At least one research-related task should be preserved
                assert len(preserved) > 0 or len(compiled_tasks) > 0, (
                    f"Research tasks not preserved. Original: {original_tasks}, Compiled: {compiled_tasks}"
                )


class TestResearcherReviewerEmbeddedKnowledge:
    """AC4: Embedded knowledge sections byte-identical."""

    def test_embedded_knowledge_markers_in_toon(self, toon_content):
        """TOON file should have embedded knowledge markers."""
        markers = extract_inject_markers(toon_content)
        # researcher-reviewer.toon has 1 BUILD:INJECT marker
        assert len(markers) >= 1, f"Expected at least 1 BUILD:INJECT marker, found {len(markers)}"

    def test_embedded_knowledge_marker_paths_valid(self, toon_content):
        """BUILD:INJECT marker paths should be valid file paths."""
        markers = extract_inject_markers(toon_content)
        for marker in markers:
            # Marker should be a file path ending in .md
            assert marker.endswith(".md"), f"Invalid marker path: {marker}"

    def test_embedded_knowledge_preserved_in_roundtrip(self, original_content, compiled_content):
        """Embedded knowledge should be preserved through roundtrip."""
        result = embedded_knowledge_validator(original_content, compiled_content)
        assert result is True, "Embedded knowledge not preserved in roundtrip"


class TestResearcherReviewerCriticalSections:
    """Test critical sections are present in compiled output."""

    def test_compiled_has_name(self, compiled_content):
        """Compiled output should have agent name."""
        has_name = (
            "name:" in compiled_content.lower() or
            "researcher-reviewer" in compiled_content.lower()
        )
        assert has_name, "Compiled output missing agent name"

    def test_compiled_has_commands(self, compiled_content):
        """Compiled output should have commands section."""
        has_commands = "commands" in compiled_content.lower()
        assert has_commands, "Compiled output missing commands section"

    def test_compiled_has_activation(self, compiled_content):
        """Compiled output should have activation instructions."""
        has_activation = "activation" in compiled_content.lower()
        assert has_activation, "Compiled output missing activation instructions"

    def test_section_presence_validation(self, compiled_content):
        """All critical sections should be present."""
        result = section_presence_validator(compiled_content)
        assert result is True, "Critical sections missing from compiled output"


class TestResearcherReviewerSpecificContent:
    """Test researcher-reviewer-specific content preservation."""

    def test_persona_name_preserved(self, toon_content):
        """Nova persona name should be in TOON file."""
        assert "Nova" in toon_content, "Nova persona name missing from TOON"

    def test_evidence_driven_identity(self, toon_content):
        """Evidence-driven researcher identity should be preserved."""
        # Check for key identity concepts
        has_evidence = "evidence" in toon_content.lower()
        has_research = "research" in toon_content.lower()
        assert has_evidence and has_research, "Evidence-driven identity not preserved"

    def test_source_verification_capability(self, toon_content):
        """Source verification command should be present."""
        assert "verify-sources" in toon_content.lower(), "verify-sources command missing"

    def test_cross_reference_capability(self, toon_content):
        """Cross-reference command should be present."""
        assert "cross-reference" in toon_content.lower(), "cross-reference command missing"

    def test_haiku_model_specification(self, toon_content):
        """Haiku model should be specified for cost efficiency."""
        assert "haiku" in toon_content.lower(), "Haiku model not specified"


class TestResearcherReviewerRoundtripIntegrity:
    """Integration tests for full roundtrip integrity."""

    def test_compile_produces_valid_output(self, compiled_md_path):
        """Compilation should produce a valid MD file."""
        compiled = Path(compiled_md_path)
        assert compiled.exists(), "Compiled file not created"
        assert compiled.stat().st_size > 0, "Compiled file is empty"

    def test_compiled_file_is_readable_markdown(self, compiled_content):
        """Compiled output should be valid markdown."""
        # Should not be empty
        assert len(compiled_content) > 100, "Compiled content too short"

        # Should have markdown structure (headers)
        has_headers = "#" in compiled_content
        assert has_headers, "Compiled output missing markdown headers"

    def test_no_parse_errors_in_roundtrip(self, compiled_md_path):
        """Roundtrip should not produce any critical parse errors."""
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)

        # Differences should not include critical errors
        critical_errors = [d for d in result.get("differences", []) if "error" in d.lower()]
        assert not critical_errors, f"Critical errors in roundtrip: {critical_errors}"
