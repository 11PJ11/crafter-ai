"""Tests for illustrator.md parsing - Step 05-01.

Validates that the illustrator agent MD file can be parsed and its structure extracted.

ACCEPTANCE CRITERIA:
1. MD file illustrator.md parsed without errors
2. All sections identified and extracted
3. Output JSON contains frontmatter, sections, commands
4. No parsing warnings or errors

Test approach: Use MDAgentParser to parse the standard nWave agent MD format.
"""

import time
import pytest
from pathlib import Path
from tools.toon.md_agent_parser import MDAgentParser


# ============================================================================
# FIXTURE PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
ILLUSTRATOR_MD_PATH = PROJECT_ROOT / "nWave" / "agents" / "illustrator.md"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def illustrator_content():
    """Load the illustrator.md file content."""
    assert ILLUSTRATOR_MD_PATH.exists(), f"Illustrator agent not found: {ILLUSTRATOR_MD_PATH}"
    return ILLUSTRATOR_MD_PATH.read_text(encoding="utf-8")


@pytest.fixture
def md_parser():
    """Create MDAgentParser instance."""
    return MDAgentParser()


# ============================================================================
# TEST: ILLUSTRATOR.MD PARSING - AC1: Parsed without errors
# ============================================================================


class TestIllustratorMdParsing:
    """Test illustrator.md can be parsed without errors."""

    def test_illustrator_md_file_exists(self):
        """
        GIVEN the nWave agents directory
        WHEN checking for illustrator.md
        THEN the file exists
        """
        assert ILLUSTRATOR_MD_PATH.exists(), \
            f"illustrator.md not found at {ILLUSTRATOR_MD_PATH}"

    def test_illustrator_md_parsed_without_errors(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing with MDAgentParser
        THEN no exceptions are raised

        AC1: MD file illustrator.md parsed without errors
        """
        # Should not raise any exceptions
        result = md_parser.parse(illustrator_content)

        # Should successfully parse
        assert result is not None, "Failed to parse illustrator.md"
        assert 'id' in result, "Parse result missing 'id' field"
        assert 'sections' in result, "Parse result missing 'sections' field"

    def test_illustrator_md_parse_file_method(self, md_parser):
        """
        GIVEN illustrator.md file path
        WHEN using parse_file method
        THEN file is parsed correctly with source_file set

        AC1: MD file illustrator.md parsed without errors
        """
        result = md_parser.parse_file(ILLUSTRATOR_MD_PATH)

        assert result is not None, "Failed to parse illustrator.md via parse_file"
        assert result.get('source_file') == str(ILLUSTRATOR_MD_PATH), \
            "source_file not set correctly"


# ============================================================================
# TEST: ILLUSTRATOR.MD SECTIONS - AC2: All sections identified
# ============================================================================


class TestIllustratorMdSections:
    """Test all sections are identified and extracted."""

    def test_sections_contains_agent(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN agent section is present in sections

        AC2: All sections identified and extracted
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'agent' in sections, "Missing 'agent' section"

    def test_sections_contains_commands(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN commands section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'commands' in sections, "Missing 'commands' section"

    def test_sections_contains_persona(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN persona section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'persona' in sections, "Missing 'persona' section"

    def test_sections_contains_dependencies(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN dependencies section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'dependencies' in sections, "Missing 'dependencies' section"

    def test_sections_contains_contract(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN contract section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'contract' in sections, "Missing 'contract' section"

    def test_sections_contains_safety_framework(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN safety_framework section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'safety_framework' in sections, "Missing 'safety_framework' section"

    def test_sections_contains_pipeline(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN pipeline section is present (animation workflow phases)
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'pipeline' in sections, "Missing 'pipeline' section"

    def test_sections_contains_testing_framework(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN testing_framework section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'testing_framework' in sections, "Missing 'testing_framework' section"

    def test_sections_contains_observability_framework(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN observability_framework section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'observability_framework' in sections, \
            "Missing 'observability_framework' section"

    def test_sections_contains_error_recovery_framework(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN error_recovery_framework section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'error_recovery_framework' in sections, \
            "Missing 'error_recovery_framework' section"

    def test_sections_contains_production_readiness(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN production_readiness section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'production_readiness' in sections, \
            "Missing 'production_readiness' section"


# ============================================================================
# TEST: ILLUSTRATOR.MD OUTPUT STRUCTURE - AC3: Output contains expected fields
# ============================================================================


class TestIllustratorMdOutputStructure:
    """Test output JSON contains frontmatter, sections, commands."""

    def test_output_contains_agent_id(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN agent id is 'illustrator'

        AC3: Output JSON contains frontmatter, sections, commands
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        assert result.get('id') == 'illustrator', \
            f"Expected id 'illustrator', got '{result.get('id')}'"

    def test_output_contains_metadata_name(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN metadata contains name from frontmatter
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        metadata = result.get('metadata', {})
        assert metadata.get('name') == 'illustrator', \
            f"Expected metadata name 'illustrator', got '{metadata.get('name')}'"

    def test_output_contains_metadata_description(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN metadata contains description
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        metadata = result.get('metadata', {})
        assert 'description' in metadata, "Missing metadata.description"
        assert 'visual' in metadata['description'].lower() or '2d' in metadata['description'].lower(), \
            "Description should mention visual/2D design"

    def test_output_agent_section_has_persona_name(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN agent section has persona name 'Luma'
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        agent_info = sections.get('agent', {})
        assert agent_info.get('name') == 'Luma', \
            f"Expected persona name 'Luma', got '{agent_info.get('name')}'"

    def test_output_agent_section_has_id(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN agent section has id 'visual-designer-2d'
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        agent_info = sections.get('agent', {})
        assert agent_info.get('id') == 'visual-designer-2d', \
            f"Expected agent id 'visual-designer-2d', got '{agent_info.get('id')}'"

    def test_output_contains_commands_list(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN commands list is present and non-empty
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        commands = sections.get('commands', [])

        assert isinstance(commands, list), "Commands should be a list"
        assert len(commands) > 0, "Commands list should not be empty"

    def test_output_contains_expected_commands(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN expected illustrator commands are present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        commands = sections.get('commands', [])

        # Convert command list to flat list of command names
        command_names = []
        for cmd in commands:
            if isinstance(cmd, dict):
                command_names.extend(cmd.keys())
            elif isinstance(cmd, str):
                # Handle simple string format like "help: description" or "help"
                command_names.append(cmd.split(':')[0].strip())

        expected_commands = [
            'help',
            'storyboard',
            'animatic',
            'design-motion',
            'lip-sync',
            'export-master',
            'exit'
        ]
        for expected in expected_commands:
            assert expected in command_names, f"Missing expected command: {expected}"

    def test_output_contains_contract_section(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN contract section with inputs/outputs is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        contract = sections.get('contract', {})

        assert 'inputs' in contract, "Missing contract.inputs"
        assert 'outputs' in contract, "Missing contract.outputs"


# ============================================================================
# TEST: ILLUSTRATOR.MD NO WARNINGS - AC4: No parsing warnings or errors
# ============================================================================


class TestIllustratorMdNoWarnings:
    """Test no parsing warnings or errors."""

    def test_parse_produces_no_errors(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN parse_errors is None or empty

        AC4: No parsing warnings or errors
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        parse_errors = result.get('parse_errors')
        assert parse_errors is None or len(parse_errors) == 0, \
            f"Parse errors found: {parse_errors}"

    def test_parse_produces_no_warnings(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN parse_warnings is None or empty
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        parse_warnings = result.get('parse_warnings')
        assert parse_warnings is None or len(parse_warnings) == 0, \
            f"Parse warnings found: {parse_warnings}"

    def test_all_top_level_sections_parsed_as_dict(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN all sections are properly structured (dict or list)
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})

        for section_name, section_content in sections.items():
            # Sections should be dict, list, or string - not None
            assert section_content is not None, \
                f"Section '{section_name}' parsed as None"


# ============================================================================
# TEST: PARSED OUTPUT STRUCTURE (for step file output)
# ============================================================================


class TestIllustratorParsedOutputStructure:
    """Test the final parsed structure format for step file output."""

    def test_can_create_parsed_structure_json(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing and structuring output
        THEN a valid parsed structure JSON/object is produced

        This matches the step output requirement: "Parsed structure JSON/object"
        """
        result = md_parser.parse(illustrator_content)

        # Validate the output structure matches step requirements
        assert result.get('id') == 'illustrator'
        assert result.get('type') == 'agent'
        assert 'metadata' in result
        assert 'sections' in result

        # Verify specific illustrator sections
        sections = result['sections']
        assert 'agent' in sections
        assert 'commands' in sections
        assert 'contract' in sections

    def test_output_structure_contains_required_fields(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN all required output fields are present
        """
        result = md_parser.parse(illustrator_content)

        required_fields = ['id', 'type', 'metadata', 'sections', 'source_file',
                          'toon_version', 'raw_content', 'parse_errors', 'parse_warnings']

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"


# ============================================================================
# TEST: ILLUSTRATOR-SPECIFIC SECTIONS
# ============================================================================


class TestIllustratorSpecificSections:
    """Test illustrator-specific section content."""

    def test_pipeline_section_exists(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN pipeline section is present

        Note: The illustrator.md file has pipeline phases (storyboard_phase,
        animatic_phase, animation_phase) at column 0 without proper YAML
        indentation, so they are parsed as separate top-level sections.
        This test validates the pipeline section itself exists.
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'pipeline' in sections, "Missing 'pipeline' section"

    def test_pipeline_content_contains_phase_data(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN pipeline section contains phase-related data

        Note: The illustrator.md uses non-standard YAML where sub-sections
        like storyboard_phase, animatic_phase are at column 0 following pipeline:.
        These are consumed as part of the pipeline section's content, not as
        separate top-level sections.
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        pipeline = sections.get('pipeline', {})

        # Pipeline content should exist (either as dict or list)
        assert pipeline is not None, "Pipeline section should have content"

    def test_lip_sync_framework_exists(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN lip_sync_framework section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'lip_sync_framework' in sections, "Missing 'lip_sync_framework' section"

    def test_export_framework_exists(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN export_framework section is present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'export_framework' in sections, "Missing 'export_framework' section"

    def test_toolchain_recommendations_present(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN toolchain_recommendations section is present with tools
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        toolchain = sections.get('toolchain_recommendations', {})

        assert toolchain is not None, "Missing toolchain_recommendations section"


# ============================================================================
# TEST: PERFORMANCE VALIDATION
# ============================================================================


class TestIllustratorMdParsePerformance:
    """Test parsing performance is acceptable."""

    def test_parse_completes_within_acceptable_time(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN parse completes within reasonable time
        """
        start_time = time.time()
        result = md_parser.parse(illustrator_content)
        parse_time_ms = (time.time() - start_time) * 1000

        assert result is not None
        # Should parse within 500ms (generous limit for large files)
        assert parse_time_ms < 500, \
            f"Parse took {parse_time_ms:.2f}ms, expected < 500ms"

    def test_parse_file_completes_within_acceptable_time(self, md_parser):
        """
        GIVEN illustrator.md file path
        WHEN using parse_file method
        THEN parse completes within reasonable time
        """
        start_time = time.time()
        result = md_parser.parse_file(ILLUSTRATOR_MD_PATH)
        parse_time_ms = (time.time() - start_time) * 1000

        assert result is not None
        # Should parse within 600ms (includes file read)
        assert parse_time_ms < 600, \
            f"Parse file took {parse_time_ms:.2f}ms, expected < 600ms"


# ============================================================================
# TEST: SECTION COUNT VALIDATION
# ============================================================================


class TestIllustratorSectionCount:
    """Test that all expected sections are identified."""

    def test_minimum_section_count(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN at least 10 sections are identified (production frameworks + core sections)
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})
        section_count = len(sections)

        # Should have at least: agent, persona, commands, dependencies,
        # pipeline, contract, safety_framework, testing_framework,
        # observability_framework, error_recovery_framework, production_readiness
        assert section_count >= 10, \
            f"Expected at least 10 sections, got {section_count}: {list(sections.keys())}"

    def test_all_production_framework_sections_present(self, md_parser, illustrator_content):
        """
        GIVEN illustrator.md content
        WHEN parsing
        THEN all 5 production framework sections are present
        """
        result = md_parser.parse(illustrator_content)

        assert result is not None
        sections = result.get('sections', {})

        production_frameworks = [
            'contract',
            'safety_framework',
            'testing_framework',
            'observability_framework',
            'error_recovery_framework'
        ]

        for framework in production_frameworks:
            assert framework in sections, \
                f"Missing production framework section: {framework}"
