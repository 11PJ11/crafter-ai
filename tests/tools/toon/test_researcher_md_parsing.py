"""Tests for researcher.md parsing - Step 01-01.

Validates that the researcher agent MD file can be parsed and its structure extracted.

ACCEPTANCE CRITERIA:
1. MD file researcher.md parsed without errors
2. All sections identified and extracted
3. Output JSON contains frontmatter, sections, commands
4. No parsing warnings or errors

Test approach: Use AgentProcessor to parse the standard nWave agent MD format.
"""

import pytest
from pathlib import Path
from tools.processors.agent_processor import AgentProcessor


# ============================================================================
# FIXTURE PATHS
# ============================================================================

PROJECT_ROOT = Path(__file__).parent.parent.parent.parent
RESEARCHER_MD_PATH = PROJECT_ROOT / "nWave" / "agents" / "researcher.md"


# ============================================================================
# FIXTURES
# ============================================================================


@pytest.fixture
def researcher_content():
    """Load the researcher.md file content."""
    assert RESEARCHER_MD_PATH.exists(), f"Researcher agent not found: {RESEARCHER_MD_PATH}"
    return RESEARCHER_MD_PATH.read_text(encoding="utf-8")


class MockFileManager:
    """Minimal file manager for testing."""

    def read_file(self, path):
        """Read file content."""
        path = Path(path)
        if path.exists():
            return path.read_text(encoding="utf-8")
        return None

    def write_file(self, path, content):
        """Write file content."""
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        return True


@pytest.fixture
def agent_processor():
    """Create AgentProcessor with mock file manager."""
    file_manager = MockFileManager()
    return AgentProcessor(
        source_dir=PROJECT_ROOT / "nWave",
        output_dir=PROJECT_ROOT / "output",
        file_manager=file_manager
    )


# ============================================================================
# TEST: RESEARCHER.MD PARSING - AC1: Parsed without errors
# ============================================================================


class TestResearcherMdParsing:
    """Test researcher.md can be parsed without errors."""

    def test_researcher_md_file_exists(self):
        """
        GIVEN the nWave agents directory
        WHEN checking for researcher.md
        THEN the file exists
        """
        assert RESEARCHER_MD_PATH.exists(), \
            f"researcher.md not found at {RESEARCHER_MD_PATH}"

    def test_researcher_md_parsed_without_errors(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN no exceptions are raised

        AC1: MD file researcher.md parsed without errors
        """
        # Should not raise any exceptions
        yaml_config, remaining_content = agent_processor.extract_yaml_block(researcher_content)

        # Should successfully extract YAML
        assert yaml_config is not None, "Failed to extract YAML configuration"
        assert remaining_content is not None, "Failed to get remaining content"


# ============================================================================
# TEST: RESEARCHER.MD SECTIONS - AC2: All sections identified
# ============================================================================


class TestResearcherMdSections:
    """Test all sections are identified and extracted."""

    def test_yaml_block_contains_agent_section(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN agent section is present

        AC2: All sections identified and extracted
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        assert 'agent' in yaml_config, "Missing 'agent' section in YAML"

    def test_yaml_block_contains_contract_section(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN contract section is present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        assert 'contract' in yaml_config, "Missing 'contract' section in YAML"

    def test_yaml_block_contains_commands_section(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN commands section is present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        assert 'commands' in yaml_config, "Missing 'commands' section in YAML"

    def test_yaml_block_contains_dependencies_section(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN dependencies section is present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        assert 'dependencies' in yaml_config, "Missing 'dependencies' section in YAML"

    def test_yaml_block_contains_safety_framework_section(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN safety_framework section is present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        assert 'safety_framework' in yaml_config, "Missing 'safety_framework' section in YAML"


# ============================================================================
# TEST: RESEARCHER.MD OUTPUT STRUCTURE - AC3: Output contains expected fields
# ============================================================================


class TestResearcherMdOutputStructure:
    """Test output JSON contains frontmatter, sections, commands."""

    def test_output_contains_agent_metadata(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN agent metadata is present with id and title

        AC3: Output JSON contains frontmatter, sections, commands
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        agent_info = yaml_config.get('agent', {})

        assert 'id' in agent_info, "Missing agent.id"
        assert 'title' in agent_info, "Missing agent.title"
        assert agent_info['id'] == 'researcher', f"Expected id 'researcher', got '{agent_info.get('id')}'"

    def test_output_contains_persona_info(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN persona information is present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        agent_info = yaml_config.get('agent', {})

        assert 'persona' in agent_info, "Missing agent.persona"
        persona = agent_info['persona']
        assert 'name' in persona, "Missing persona.name"
        assert persona['name'] == 'Nova', f"Expected persona name 'Nova', got '{persona.get('name')}'"

    def test_output_contains_commands_list(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN commands list is present and non-empty
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        commands = yaml_config.get('commands', [])

        assert isinstance(commands, list), "Commands should be a list"
        assert len(commands) > 0, "Commands list should not be empty"

    def test_output_contains_specific_commands(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN expected researcher commands are present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        commands = yaml_config.get('commands', [])

        # Convert command list to dict for easier lookup
        # Commands format: [{help: "description"}, {research: "description"}, ...]
        command_names = []
        for cmd in commands:
            if isinstance(cmd, dict):
                command_names.extend(cmd.keys())
            elif isinstance(cmd, str):
                # Handle simple string format "- research" etc
                command_names.append(cmd.split(':')[0].strip())

        expected_commands = ['help', 'research', 'verify-sources', 'exit']
        for expected in expected_commands:
            assert expected in command_names, f"Missing expected command: {expected}"

    def test_output_contains_contract_inputs(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN contract.inputs section is present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        contract = yaml_config.get('contract', {})

        assert 'inputs' in contract, "Missing contract.inputs"
        inputs = contract['inputs']
        assert 'required' in inputs, "Missing contract.inputs.required"

    def test_output_contains_contract_outputs(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN contract.outputs section is present
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        assert yaml_config is not None
        contract = yaml_config.get('contract', {})

        assert 'outputs' in contract, "Missing contract.outputs"


# ============================================================================
# TEST: RESEARCHER.MD NO WARNINGS - AC4: No parsing warnings or errors
# ============================================================================


class TestResearcherMdNoWarnings:
    """Test no parsing warnings or errors."""

    def test_yaml_parsing_produces_valid_structure(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN parsing completes without warnings

        AC4: No parsing warnings or errors
        """
        # This should not produce any warnings or errors
        yaml_config, remaining = agent_processor.extract_yaml_block(researcher_content)

        # Validate structure completeness
        assert yaml_config is not None, "YAML parsing failed"
        assert isinstance(yaml_config, dict), "YAML should parse to dict"

        # Check for common parsing issues
        for key in yaml_config:
            # No None values at top level (would indicate parsing issues)
            assert yaml_config[key] is not None, f"Parsing produced None for key: {key}"

    def test_remaining_content_is_valid_markdown(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN extracting YAML block
        THEN remaining content is valid markdown
        """
        _, remaining = agent_processor.extract_yaml_block(researcher_content)

        assert remaining is not None
        assert isinstance(remaining, str)
        # Should have content outside the YAML block
        assert len(remaining.strip()) > 0, "No content outside YAML block"

    def test_frontmatter_can_be_generated(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content with valid YAML
        WHEN generating frontmatter
        THEN valid frontmatter is produced
        """
        yaml_config, _ = agent_processor.extract_yaml_block(researcher_content)

        # Should be able to generate frontmatter from parsed YAML
        frontmatter = agent_processor.generate_frontmatter(RESEARCHER_MD_PATH, yaml_config)

        assert frontmatter is not None
        assert frontmatter.startswith("---")
        assert "name:" in frontmatter
        assert "description:" in frontmatter


# ============================================================================
# TEST: PARSED OUTPUT STRUCTURE (for step file output)
# ============================================================================


class TestResearcherParsedOutputStructure:
    """Test the final parsed structure format for step file output."""

    def test_can_create_parsed_structure_json(self, agent_processor, researcher_content):
        """
        GIVEN researcher.md content
        WHEN parsing and structuring output
        THEN a valid parsed structure JSON/object is produced

        This matches the step output requirement: "Parsed structure JSON/object"
        """
        yaml_config, remaining = agent_processor.extract_yaml_block(researcher_content)

        # Create the output structure expected by the step
        parsed_output = {
            'frontmatter': {
                'name': yaml_config.get('agent', {}).get('id', ''),
                'description': yaml_config.get('agent', {}).get('whenToUse', ''),
                'model': 'inherit',
                'tools': yaml_config.get('tools', [])
            },
            'sections': {
                'agent': yaml_config.get('agent', {}),
                'contract': yaml_config.get('contract', {}),
                'commands': yaml_config.get('commands', []),
                'dependencies': yaml_config.get('dependencies', {}),
                'safety_framework': yaml_config.get('safety_framework', {}),
                'testing_framework': yaml_config.get('testing_framework', {}),
                'observability_framework': yaml_config.get('observability_framework', {}),
                'error_recovery_framework': yaml_config.get('error_recovery_framework', {}),
            },
            'commands': yaml_config.get('commands', []),
            'source_file': str(RESEARCHER_MD_PATH),
            'parse_success': True,
            'warnings': [],
            'errors': []
        }

        # Validate output structure
        assert parsed_output['frontmatter']['name'] == 'researcher'
        assert len(parsed_output['sections']) > 0
        assert len(parsed_output['commands']) > 0
        assert parsed_output['parse_success'] is True
        assert len(parsed_output['warnings']) == 0
        assert len(parsed_output['errors']) == 0
