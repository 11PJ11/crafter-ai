"""Tests for troubleshooter.md parsing - Step 03-01.

Validates that the troubleshooter agent MD file can be parsed and its structure extracted.

ACCEPTANCE CRITERIA:
1. MD file troubleshooter.md parsed without errors
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
TROUBLESHOOTER_MD_PATH = PROJECT_ROOT / "nWave" / "agents" / "troubleshooter.md"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def troubleshooter_content():
    """Load the troubleshooter.md file content."""
    assert TROUBLESHOOTER_MD_PATH.exists(), f"Troubleshooter agent not found: {TROUBLESHOOTER_MD_PATH}"
    return TROUBLESHOOTER_MD_PATH.read_text(encoding="utf-8")


@pytest.fixture
def md_parser():
    """Create MDAgentParser instance."""
    return MDAgentParser()


# ============================================================================
# TEST: TROUBLESHOOTER.MD PARSING - AC1: Parsed without errors
# ============================================================================


class TestTroubleshooterMdParsing:
    """Test troubleshooter.md can be parsed without errors."""

    def test_troubleshooter_md_file_exists(self):
        """
        GIVEN the nWave agents directory
        WHEN checking for troubleshooter.md
        THEN the file exists
        """
        assert TROUBLESHOOTER_MD_PATH.exists(), \
            f"troubleshooter.md not found at {TROUBLESHOOTER_MD_PATH}"

    def test_troubleshooter_md_parsed_without_errors(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing with MDAgentParser
        THEN no exceptions are raised

        AC1: MD file troubleshooter.md parsed without errors
        """
        # Should not raise any exceptions
        result = md_parser.parse(troubleshooter_content)

        # Should successfully parse
        assert result is not None, "Failed to parse troubleshooter.md"
        assert 'id' in result, "Parse result missing 'id' field"
        assert 'sections' in result, "Parse result missing 'sections' field"

    def test_troubleshooter_md_parse_file_method(self, md_parser):
        """
        GIVEN troubleshooter.md file path
        WHEN using parse_file method
        THEN file is parsed correctly with source_file set

        AC1: MD file troubleshooter.md parsed without errors
        """
        result = md_parser.parse_file(TROUBLESHOOTER_MD_PATH)

        assert result is not None, "Failed to parse troubleshooter.md via parse_file"
        assert result.get('source_file') == str(TROUBLESHOOTER_MD_PATH), \
            "source_file not set correctly"


# ============================================================================
# TEST: TROUBLESHOOTER.MD SECTIONS - AC2: All sections identified
# ============================================================================


class TestTroubleshooterMdSections:
    """Test all sections are identified and extracted."""

    def test_sections_contains_agent(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN agent section is present in sections

        AC2: All sections identified and extracted
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'agent' in sections, "Missing 'agent' section"

    def test_sections_contains_commands(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN commands section is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'commands' in sections, "Missing 'commands' section"

    def test_sections_contains_persona(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN persona section is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'persona' in sections, "Missing 'persona' section"

    def test_sections_contains_dependencies(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN dependencies section is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'dependencies' in sections, "Missing 'dependencies' section"

    def test_sections_contains_contract(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN contract section is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'contract' in sections, "Missing 'contract' section"

    def test_sections_contains_safety_framework(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN safety_framework section is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'safety_framework' in sections, "Missing 'safety_framework' section"

    def test_sections_contains_toyota_methodology(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN Toyota 5 Whys methodology section is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        # The section key from YAML might be toyota_methodology_framework
        assert 'toyota_methodology_framework' in sections, \
            "Missing 'toyota_methodology_framework' section"

    def test_sections_contains_investigation_framework(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN investigation_framework section is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        assert 'investigation_framework' in sections, \
            "Missing 'investigation_framework' section"


# ============================================================================
# TEST: TROUBLESHOOTER.MD OUTPUT STRUCTURE - AC3: Output contains expected fields
# ============================================================================


class TestTroubleshooterMdOutputStructure:
    """Test output JSON contains frontmatter, sections, commands."""

    def test_output_contains_agent_id(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN agent id is 'troubleshooter'

        AC3: Output JSON contains frontmatter, sections, commands
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        assert result.get('id') == 'troubleshooter', \
            f"Expected id 'troubleshooter', got '{result.get('id')}'"

    def test_output_contains_metadata_name(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN metadata contains name from frontmatter
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        metadata = result.get('metadata', {})
        assert metadata.get('name') == 'troubleshooter', \
            f"Expected metadata name 'troubleshooter', got '{metadata.get('name')}'"

    def test_output_contains_metadata_description(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN metadata contains description
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        metadata = result.get('metadata', {})
        assert 'description' in metadata, "Missing metadata.description"
        assert 'root cause' in metadata['description'].lower(), \
            "Description should mention root cause analysis"

    def test_output_agent_section_has_persona_name(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN agent section has persona name 'Sage'
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        agent_info = sections.get('agent', {})
        assert agent_info.get('name') == 'Sage', \
            f"Expected persona name 'Sage', got '{agent_info.get('name')}'"

    def test_output_contains_commands_list(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN commands list is present and non-empty
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        commands = sections.get('commands', [])

        assert isinstance(commands, list), "Commands should be a list"
        assert len(commands) > 0, "Commands list should not be empty"

    def test_output_contains_expected_commands(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN expected troubleshooter commands are present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        commands = sections.get('commands', [])

        # Convert command list to flat list of command names
        command_names = []
        for cmd in commands:
            if isinstance(cmd, dict):
                command_names.extend(cmd.keys())
            elif isinstance(cmd, str):
                # Handle simple string format
                command_names.append(cmd.split(':')[0].strip())

        expected_commands = [
            'help',
            'investigate-problem',
            'analyze-system-failure',
            'exit'
        ]
        for expected in expected_commands:
            assert expected in command_names, f"Missing expected command: {expected}"

    def test_output_contains_contract_section(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN contract section with inputs/outputs is present
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})
        contract = sections.get('contract', {})

        assert 'inputs' in contract, "Missing contract.inputs"
        assert 'outputs' in contract, "Missing contract.outputs"


# ============================================================================
# TEST: TROUBLESHOOTER.MD NO WARNINGS - AC4: No parsing warnings or errors
# ============================================================================


class TestTroubleshooterMdNoWarnings:
    """Test no parsing warnings or errors."""

    def test_parse_produces_no_errors(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN parse_errors is None or empty

        AC4: No parsing warnings or errors
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        parse_errors = result.get('parse_errors')
        assert parse_errors is None or len(parse_errors) == 0, \
            f"Parse errors found: {parse_errors}"

    def test_parse_produces_no_warnings(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN parse_warnings is None or empty
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        parse_warnings = result.get('parse_warnings')
        assert parse_warnings is None or len(parse_warnings) == 0, \
            f"Parse warnings found: {parse_warnings}"

    def test_all_top_level_sections_parsed_as_dict(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN all sections are properly structured (dict or list)
        """
        result = md_parser.parse(troubleshooter_content)

        assert result is not None
        sections = result.get('sections', {})

        for section_name, section_content in sections.items():
            # Sections should be dict, list, or string - not None
            assert section_content is not None, \
                f"Section '{section_name}' parsed as None"


# ============================================================================
# TEST: PARSED OUTPUT STRUCTURE (for step file output)
# ============================================================================


class TestTroubleshooterParsedOutputStructure:
    """Test the final parsed structure format for step file output."""

    def test_can_create_parsed_structure_json(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing and structuring output
        THEN a valid parsed structure JSON/object is produced

        This matches the step output requirement: "Parsed structure JSON/object"
        """
        result = md_parser.parse(troubleshooter_content)

        # Validate the output structure matches step requirements
        assert result.get('id') == 'troubleshooter'
        assert result.get('type') == 'agent'
        assert 'metadata' in result
        assert 'sections' in result

        # Verify specific troubleshooter sections
        sections = result['sections']
        assert 'agent' in sections
        assert 'commands' in sections
        assert 'contract' in sections

    def test_output_structure_contains_required_fields(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN all required output fields are present
        """
        result = md_parser.parse(troubleshooter_content)

        required_fields = ['id', 'type', 'metadata', 'sections', 'source_file',
                          'toon_version', 'raw_content', 'parse_errors', 'parse_warnings']

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"


# ============================================================================
# TEST: PERFORMANCE VALIDATION
# ============================================================================


class TestTroubleshooterMdParsePerformance:
    """Test parsing performance is acceptable."""

    def test_parse_completes_within_acceptable_time(self, md_parser, troubleshooter_content):
        """
        GIVEN troubleshooter.md content
        WHEN parsing
        THEN parse completes within reasonable time
        """
        start_time = time.time()
        result = md_parser.parse(troubleshooter_content)
        parse_time_ms = (time.time() - start_time) * 1000

        assert result is not None
        # Should parse within 500ms (generous limit for large files)
        assert parse_time_ms < 500, \
            f"Parse took {parse_time_ms:.2f}ms, expected < 500ms"

    def test_parse_file_completes_within_acceptable_time(self, md_parser):
        """
        GIVEN troubleshooter.md file path
        WHEN using parse_file method
        THEN parse completes within reasonable time
        """
        start_time = time.time()
        result = md_parser.parse_file(TROUBLESHOOTER_MD_PATH)
        parse_time_ms = (time.time() - start_time) * 1000

        assert result is not None
        # Should parse within 600ms (includes file read)
        assert parse_time_ms < 600, \
            f"Parse file took {parse_time_ms:.2f}ms, expected < 600ms"
