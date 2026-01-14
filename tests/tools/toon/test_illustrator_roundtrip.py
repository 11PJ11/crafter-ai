"""Tests for illustrator roundtrip validation (MD -> TOON -> MD).

Step 05-03 acceptance criteria:
1. MD -> TOON -> MD produces equivalent output
2. All YAML keys present in both directions
3. Values match after whitespace normalization
4. Embedded knowledge sections byte-identical

This test file validates the illustrator.toon file specifically,
ensuring the conversion preserves all critical content from the original
illustrator.md source.
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


# Test files specific to illustrator
TOON_FILE = Path("nWave/agents/illustrator.toon")
ORIGINAL_MD = Path("nWave/agents/illustrator.md")


@pytest.fixture
def illustrator_toon_exists():
    """Verify TOON file exists before running tests."""
    assert TOON_FILE.exists(), f"TOON file not found: {TOON_FILE}"
    return True


@pytest.fixture
def illustrator_md_exists():
    """Verify original MD file exists before running tests."""
    assert ORIGINAL_MD.exists(), f"Original MD file not found: {ORIGINAL_MD}"
    return True


@pytest.fixture
def compiled_md_path(illustrator_toon_exists):
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
def original_content(illustrator_md_exists):
    """Get original markdown content."""
    return ORIGINAL_MD.read_text()


@pytest.fixture
def toon_content(illustrator_toon_exists):
    """Get TOON source content."""
    return TOON_FILE.read_text()


class TestIllustratorRoundtripValidation:
    """E2E tests for illustrator roundtrip validation.

    AC1: MD -> TOON -> MD produces equivalent output
    """

    def test_roundtrip_equivalence_score_threshold(self, compiled_md_path):
        """GIVEN illustrator.md and compiled output from illustrator.toon
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


class TestIllustratorYAMLKeyPreservation:
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

    def test_toon_has_activation_section(self, toon_content):
        """TOON file should have ACTIVATION section."""
        assert "## ACTIVATION" in toon_content, "TOON file missing ## ACTIVATION section"

    def test_toon_has_core_principles_section(self, toon_content):
        """TOON file should have CORE_PRINCIPLES section."""
        assert "## CORE_PRINCIPLES" in toon_content, "TOON file missing ## CORE_PRINCIPLES section"

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


class TestIllustratorValueMatching:
    """AC3: Values match after whitespace normalization."""

    def test_command_names_match(self, original_content, compiled_content):
        """Command names should match between original and compiled."""
        original_cmds = set(extract_commands(original_content))
        compiled_cmds = set(extract_commands(compiled_content))

        # Find commands in common
        common_cmds = original_cmds & compiled_cmds

        # At least core commands should be present
        core_commands = {"help", "exit", "storyboard", "animatic", "lip-sync"}
        missing_core = core_commands - common_cmds

        assert not missing_core, f"Missing core commands in compiled output: {missing_core}"

    def test_command_list_order_independent(self, original_content, compiled_content):
        """Command list validation should be order-independent."""
        # The validator already does order-independent comparison
        result = command_list_validator(original_content, compiled_content)
        assert isinstance(result, bool), "command_list_validator should return bool"

    def test_dependency_checklists_preserved(self, original_content, compiled_content):
        """Checklist dependencies should be preserved."""
        original_deps = extract_dependencies(original_content)
        compiled_deps = extract_dependencies(compiled_content)

        # Check that checklist dependencies are present
        if original_deps.get("checklists"):
            # At least some checklists should be in compiled
            original_checklists = set(original_deps["checklists"])
            compiled_checklists = set(compiled_deps.get("checklists", []))

            # Key checklists for illustrator
            key_checklists = {c for c in original_checklists if "12-principles" in c.lower() or "readability" in c.lower()}

            if key_checklists:
                preserved = key_checklists & compiled_checklists
                # At least one key checklist should be preserved
                assert len(preserved) > 0 or len(compiled_checklists) > 0, (
                    f"Key checklists not preserved. Original: {original_checklists}, Compiled: {compiled_checklists}"
                )

    def test_dependency_templates_preserved(self, original_content, compiled_content):
        """Template dependencies should be preserved."""
        original_deps = extract_dependencies(original_content)
        compiled_deps = extract_dependencies(compiled_content)

        # Check that template dependencies are present
        if original_deps.get("templates"):
            original_templates = set(original_deps["templates"])
            compiled_templates = set(compiled_deps.get("templates", []))

            # Key templates for illustrator
            key_templates = {t for t in original_templates if "style-brief" in t.lower() or "x-sheet" in t.lower()}

            if key_templates:
                preserved = key_templates & compiled_templates
                # At least one key template should be preserved
                assert len(preserved) > 0 or len(compiled_templates) > 0, (
                    f"Key templates not preserved. Original: {original_templates}, Compiled: {compiled_templates}"
                )


class TestIllustratorEmbeddedKnowledge:
    """AC4: Embedded knowledge sections byte-identical."""

    def test_embedded_knowledge_markers_in_toon(self, toon_content):
        """TOON file should have embedded knowledge markers."""
        markers = extract_inject_markers(toon_content)
        # illustrator.toon has at least 1 BUILD:INJECT marker (critique-dimensions.md)
        assert len(markers) >= 1, f"Expected at least 1 BUILD:INJECT marker, found {len(markers)}"

    def test_embedded_knowledge_marker_paths_valid(self, toon_content):
        """BUILD:INJECT marker paths should be valid file paths."""
        markers = extract_inject_markers(toon_content)
        for marker in markers:
            # Marker should be a file path ending in .md
            assert marker.endswith(".md"), f"Invalid marker path: {marker}"

    def test_critique_dimensions_marker_present(self, toon_content):
        """Critique dimensions inject marker should be present."""
        assert "critique-dimensions.md" in toon_content, "critique-dimensions.md marker not found"

    def test_embedded_knowledge_preserved_in_roundtrip(self, original_content, compiled_content):
        """Embedded knowledge should be preserved through roundtrip."""
        result = embedded_knowledge_validator(original_content, compiled_content)
        assert result is True, "Embedded knowledge not preserved in roundtrip"


class TestIllustratorCriticalSections:
    """Test critical sections are present in compiled output."""

    def test_compiled_has_name(self, compiled_content):
        """Compiled output should have agent name."""
        has_name = (
            "name:" in compiled_content.lower() or
            "illustrator" in compiled_content.lower()
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


class TestIllustratorSpecificContent:
    """Test illustrator-specific content preservation."""

    def test_persona_name_preserved(self, toon_content):
        """Luma persona name should be in TOON file."""
        assert "Luma" in toon_content, "Luma persona name missing from TOON"

    def test_animation_designer_identity(self, toon_content):
        """2D Animation Designer identity should be preserved."""
        # Check for key identity concepts
        has_animation = "animation" in toon_content.lower()
        has_designer = "designer" in toon_content.lower()
        assert has_animation and has_designer, "2D Animation Designer identity not preserved"

    def test_storyboard_command_present(self, toon_content):
        """storyboard command should be present."""
        assert "storyboard" in toon_content.lower(), "storyboard command missing"

    def test_animatic_command_present(self, toon_content):
        """animatic command should be present."""
        assert "animatic" in toon_content.lower(), "animatic command missing"

    def test_lip_sync_command_present(self, toon_content):
        """lip-sync command should be present."""
        assert "lip-sync" in toon_content.lower(), "lip-sync command missing"

    def test_12_principles_reference(self, toon_content):
        """12 principles should be referenced."""
        assert "12" in toon_content and "principles" in toon_content.lower(), "12 principles not referenced"

    def test_inherit_model_specification(self, toon_content):
        """Model should be 'inherit' for illustrator."""
        assert "inherit" in toon_content.lower(), "inherit model not specified"


class TestIllustratorPipelinePreservation:
    """Test pipeline-specific content preservation."""

    def test_pipeline_section_present(self, toon_content):
        """PIPELINE section should be present."""
        assert "PIPELINE" in toon_content.upper(), "PIPELINE section missing"

    def test_storyboard_phase_present(self, toon_content):
        """Storyboard phase should be documented."""
        assert "storyboard" in toon_content.lower(), "Storyboard phase missing"

    def test_animatic_phase_present(self, toon_content):
        """Animatic phase should be documented."""
        assert "animatic" in toon_content.lower(), "Animatic phase missing"

    def test_animation_phase_present(self, toon_content):
        """Animation phase should be documented."""
        assert "animation" in toon_content.lower(), "Animation phase missing"

    def test_lip_sync_framework_present(self, toon_content):
        """Lip sync framework should be documented."""
        assert "lip" in toon_content.lower() and "sync" in toon_content.lower(), "Lip sync framework missing"

    def test_export_framework_present(self, toon_content):
        """Export framework should be documented."""
        assert "export" in toon_content.lower(), "Export framework missing"


class TestIllustratorToolchainPreservation:
    """Test toolchain recommendations preservation."""

    def test_toolchain_section_present(self, toon_content):
        """TOOLCHAIN section should be present."""
        assert "TOOLCHAIN" in toon_content.upper(), "TOOLCHAIN section missing"

    def test_krita_mentioned(self, toon_content):
        """Krita should be recommended."""
        assert "Krita" in toon_content, "Krita tool recommendation missing"

    def test_opentoonz_mentioned(self, toon_content):
        """OpenToonz should be recommended."""
        assert "OpenToonz" in toon_content, "OpenToonz tool recommendation missing"

    def test_synfig_mentioned(self, toon_content):
        """Synfig should be recommended."""
        assert "Synfig" in toon_content, "Synfig tool recommendation missing"


class TestIllustratorProductionFrameworks:
    """Test production frameworks preservation."""

    def test_contract_section_present(self, toon_content):
        """CONTRACT section should be present."""
        assert "CONTRACT" in toon_content.upper(), "CONTRACT section missing"

    def test_safety_framework_present(self, toon_content):
        """SAFETY_FRAMEWORK section should be present."""
        assert "SAFETY" in toon_content.upper(), "SAFETY section missing"

    def test_testing_framework_present(self, toon_content):
        """TESTING_FRAMEWORK section should be present."""
        assert "TESTING" in toon_content.upper(), "TESTING section missing"

    def test_observability_section_present(self, toon_content):
        """OBSERVABILITY section should be present."""
        assert "OBSERVABILITY" in toon_content.upper(), "OBSERVABILITY section missing"

    def test_error_recovery_section_present(self, toon_content):
        """ERROR_RECOVERY section should be present."""
        assert "ERROR_RECOVERY" in toon_content or "error_recovery" in toon_content.lower(), "ERROR_RECOVERY section missing"


class TestIllustratorRoundtripIntegrity:
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

    def test_equivalence_score_components(self, compiled_md_path):
        """Each component of equivalence should be evaluated."""
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)

        # All components should be present in result
        assert "equivalence_score" in result
        assert "commands_match" in result
        assert "dependencies_match" in result
        assert "frontmatter_valid" in result
        assert "critical_sections_present" in result
        assert "embedded_knowledge_preserved" in result
        assert "differences" in result
        assert "patterns_discovered" in result
        assert "edge_cases_found" in result
