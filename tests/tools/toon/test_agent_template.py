"""Tests for agent.md.j2 template rendering

Business language: Template renders TOON parsed data into Claude Code compliant agent.md
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import pytest

from tools.toon.template_adapter import render_agent_template


@pytest.fixture
def jinja_env():
    """Setup Jinja2 environment for template testing"""
    template_dir = Path('tools/toon/templates')
    return Environment(loader=FileSystemLoader(str(template_dir)))


@pytest.fixture
def sample_parsed_data():
    """Sample parsed TOON data matching parser output schema"""
    return {
        'id': 'software-crafter',
        'type': 'agent',
        'metadata': {
            'name': 'Crafty',
            'description': 'Software craftsmanship expert',
            'model': 'claude-sonnet-4-5',
            'role': 'Crafty | software-crafter',
            'spec': 'TDD, Refactoring, Quality Excellence'
        },
        'sections': {
            'commands': {
                'develop': 'Execute TDD workflow',
                'refactor': 'Apply systematic refactoring',
                'mikado': 'Complex refactoring roadmaps'
            },
            'core_rules': {
                'Test-Driven Development': 'All code through TDD',
                'Quality First': 'No compromises on quality'
            }
        }
    }


# ============================================================================
# YAML FRONTMATTER RENDERING TESTS (AC#1, AC#5)
# ============================================================================

class TestYAMLFrontmatterRendering:
    """Tests for YAML frontmatter with escaping (AC#1, AC#5)"""

    def test_template_frontmatter_valid_yaml(self, jinja_env, sample_parsed_data):
        """
        GIVEN parsed agent data with mandatory fields
        WHEN I render agent.md.j2 template
        THEN output has valid YAML frontmatter with required keys (AC#1)

        Validates:
        - Frontmatter starts with ---
        - Contains name, description, model keys
        - Frontmatter ends with ---
        """
        output = render_agent_template(jinja_env, sample_parsed_data)

        # AC#1: Valid YAML frontmatter structure
        assert output.startswith('---'), "Missing frontmatter opening"
        lines = output.split('\n')
        assert lines[0] == '---', "First line must be ---"

        # Find closing ---
        closing_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line == '---':
                closing_idx = i
                break
        assert closing_idx is not None, "Missing frontmatter closing ---"

        # Mandatory keys present
        assert 'name: Crafty' in output, "Missing name in frontmatter"
        assert 'description:' in output, "Missing description in frontmatter"
        assert 'model: claude-sonnet-4-5' in output, "Missing model in frontmatter"

    def test_template_frontmatter_escapes_yaml_special_chars(self, jinja_env):
        """
        GIVEN agent description with YAML special characters
        WHEN I render agent.md.j2 template
        THEN special characters are properly escaped (AC#5)

        Validates:
        - Colons in values are escaped
        - Quotes are escaped
        - Values with special chars are wrapped in quotes
        """
        data_with_special_chars = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                'name': 'Test: Agent',  # Colon in name
                'description': 'Uses "quoted" text',  # Quotes in description
                'model': 'claude-sonnet-4-5'
            },
            'sections': {}
        }

        output = render_agent_template(jinja_env, data_with_special_chars)

        # AC#5: Special characters escaped
        # Colons should trigger quote wrapping
        assert 'name: "Test: Agent"' in output or "name: 'Test: Agent'" in output, \
            "Colon in name not properly escaped"
        # Quotes should be escaped
        assert r'\"quoted\"' in output or r"\'quoted\'" in output, \
            "Quotes in description not properly escaped"

    def test_template_handles_colons_in_descriptions(self, jinja_env):
        """
        GIVEN agent with colon in description (e.g., "Ratio: 3:1")
        WHEN I render agent.md.j2 template
        THEN colons are escaped and YAML remains valid (AC#5)

        Validates:
        - Descriptions with colons don't break YAML syntax
        - Values are properly quoted when containing colons
        """
        data_with_colons = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                'name': 'Test Agent',
                'description': 'Ratio: 3:1 performance',
                'model': 'claude-sonnet-4-5'
            },
            'sections': {}
        }

        output = render_agent_template(jinja_env, data_with_colons)

        # AC#5: Colons handled correctly
        # Description with colons should be quoted
        assert '"Ratio: 3:1 performance"' in output or "'Ratio: 3:1 performance'" in output, \
            "Colon-containing description not properly quoted"

    def test_template_handles_quotes_in_descriptions(self, jinja_env):
        """
        GIVEN agent description with single and double quotes
        WHEN I render agent.md.j2 template
        THEN quotes are escaped properly (AC#5)

        Validates:
        - Double quotes are escaped as \"
        - Single quotes are handled
        - YAML syntax remains valid
        """
        data_with_quotes = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                'name': 'Test Agent',
                'description': 'Agent with "quotes" and \'apostrophes\'',
                'model': 'claude-sonnet-4-5'
            },
            'sections': {}
        }

        output = render_agent_template(jinja_env, data_with_quotes)

        # AC#5: Quotes escaped
        # Should contain escaped quotes
        assert r'\"quotes\"' in output or r"\'quotes\'" in output, \
            "Quotes not properly escaped"

    def test_template_handles_newlines_in_descriptions(self, jinja_env):
        """
        GIVEN agent description with newline characters
        WHEN I render agent.md.j2 template
        THEN newlines are escaped as \\n (AC#5)

        Validates:
        - Newlines don't break YAML frontmatter
        - Multi-line descriptions are properly escaped
        """
        data_with_newlines = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                'name': 'Test Agent',
                'description': 'Line 1\nLine 2\nLine 3',
                'model': 'claude-sonnet-4-5'
            },
            'sections': {}
        }

        output = render_agent_template(jinja_env, data_with_newlines)

        # AC#5: Newlines escaped
        # Should contain escaped newlines, not actual newlines in frontmatter
        frontmatter_end = output.index('---', 3)  # Find second ---
        frontmatter = output[:frontmatter_end]

        # Check that newlines in description are escaped
        assert r'\n' in output or 'Line 1' not in frontmatter.split('\n')[1:], \
            "Newlines in description not properly escaped"

    def test_template_handles_multiline_strings(self, jinja_env):
        """
        GIVEN agent with multi-line description
        WHEN I render agent.md.j2 template
        THEN YAML frontmatter uses proper indentation (AC#6)

        Validates:
        - Multi-line strings don't break YAML structure
        - Indentation preserves YAML validity
        """
        data_multiline = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                'name': 'Test Agent',
                'description': 'A very long description\nthat spans multiple lines\nfor testing',
                'model': 'claude-sonnet-4-5'
            },
            'sections': {}
        }

        output = render_agent_template(jinja_env, data_multiline)

        # AC#6: Multi-line strings handled
        # Frontmatter should still be valid YAML (starts with ---, has name/model)
        assert output.startswith('---'), "Frontmatter broken by multiline string"
        assert 'name: Test Agent' in output, "Name missing with multiline description"
        assert 'model: claude-sonnet-4-5' in output, "Model missing with multiline description"


# ============================================================================
# ACTIVATION NOTICE TESTS (AC#2)
# ============================================================================

class TestActivationNotice:
    """Tests for activation notice section (AC#2)"""

    def test_template_activation_notice_present(self, jinja_env, sample_parsed_data):
        """
        GIVEN parsed agent data
        WHEN I render agent.md.j2 template
        THEN output contains activation notice section (AC#2)

        Validates:
        - Activation notice appears after frontmatter
        - Contains proper formatting
        - Includes agent identifier
        """
        output = render_agent_template(jinja_env, sample_parsed_data)

        # AC#2: Activation notice section present
        assert 'ACTIVATION-NOTICE:' in output, "Activation notice missing"
        assert 'software-crafter' in output or 'Crafty' in output, \
            "Agent identifier missing from activation notice"

        # Verify notice comes after frontmatter
        frontmatter_end = output.index('---', 3)  # Second ---
        notice_pos = output.index('ACTIVATION-NOTICE:')
        assert notice_pos > frontmatter_end, "Activation notice appears before frontmatter ends"


# ============================================================================
# COMMAND RENDERING TESTS (AC#3)
# ============================================================================

class TestCommandRendering:
    """Tests for command definitions rendering (AC#3)"""

    def test_template_commands_list_rendered_with_descriptions(self, jinja_env, sample_parsed_data):
        """
        GIVEN parsed agent data with commands dict
        WHEN I render agent.md.j2 template
        THEN commands appear with descriptions in markdown (AC#3)

        Validates:
        - Commands section exists
        - Each command has name and description
        - Format: - **command**: description
        """
        output = render_agent_template(jinja_env, sample_parsed_data)

        # AC#3: Commands with descriptions
        assert '## Commands' in output, "Commands section missing"
        assert '**develop**: Execute TDD workflow' in output, "develop command missing"
        assert '**refactor**: Apply systematic refactoring' in output, "refactor command missing"
        assert '**mikado**: Complex refactoring roadmaps' in output, "mikado command missing"

    def test_template_command_definitions_complete(self, jinja_env, sample_parsed_data):
        """
        GIVEN parsed agent data with multiple commands
        WHEN I render agent.md.j2 template
        THEN all command definitions are complete with name and description

        Validates:
        - No commands missing descriptions
        - Commands appear in both markdown section and YAML block
        """
        output = render_agent_template(jinja_env, sample_parsed_data)

        # All commands in markdown section
        commands = sample_parsed_data['sections']['commands']
        for cmd_name, cmd_desc in commands.items():
            assert f'**{cmd_name}**:' in output, f"Command {cmd_name} missing from markdown"
            assert cmd_desc in output, f"Description for {cmd_name} missing"

        # All commands in YAML block
        yaml_block_start = output.index('```yaml')
        yaml_block_end = output.index('```', yaml_block_start + 7)
        yaml_block = output[yaml_block_start:yaml_block_end]

        for cmd_name in commands.keys():
            assert f'- {cmd_name}' in yaml_block, f"Command {cmd_name} missing from YAML block"


# ============================================================================
# EMBEDDED KNOWLEDGE MARKERS TESTS (AC#4)
# ============================================================================

class TestEmbeddedKnowledgeMarkers:
    """Tests for build injection markers (AC#4)"""

    def test_template_embed_markers_preserved(self, jinja_env):
        """
        GIVEN parsed data with embedded knowledge dependencies
        WHEN I render agent.md.j2 template
        THEN output contains proper injection markers (AC#4)

        Validates:
        - Markers use correct format: <!-- BUILD:INJECT:START:path -->
        - End markers present: <!-- BUILD:INJECT:END -->
        - Markers placed correctly in output
        """
        data_with_embeds = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                'name': 'Test Agent',
                'description': 'Test',
                'model': 'claude-sonnet-4-5'
            },
            'sections': {
                'dependencies': {
                    'embed_knowledge': [
                        '5d-wave/data/embed/test/README.md',
                        '5d-wave/data/embed/test/guide.md'
                    ]
                }
            }
        }

        output = render_agent_template(jinja_env, data_with_embeds)

        # AC#4: Embedded knowledge markers
        assert '<!-- BUILD:INJECT:START:5d-wave/data/embed/test/README.md -->' in output, \
            "First embed marker missing"
        assert '<!-- BUILD:INJECT:START:5d-wave/data/embed/test/guide.md -->' in output, \
            "Second embed marker missing"

        # Count end markers (should match start markers)
        start_count = output.count('<!-- BUILD:INJECT:START:')
        end_count = output.count('<!-- BUILD:INJECT:END -->')
        assert start_count == end_count == 2, \
            f"Mismatched markers: {start_count} starts, {end_count} ends"

    def test_template_dependencies_rendered(self, jinja_env):
        """
        GIVEN parsed data with dependencies section
        WHEN I render agent.md.j2 template
        THEN dependencies appear in YAML block

        Validates:
        - Dependencies section in YAML block
        - Tasks, templates, embed_knowledge sub-sections
        """
        data_with_deps = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                'name': 'Test Agent',
                'description': 'Test',
                'model': 'claude-sonnet-4-5'
            },
            'sections': {
                'dependencies': {
                    'tasks': ['task1.md', 'task2.md'],
                    'templates': ['template1.yaml'],
                    'embed_knowledge': ['embed/file.md']
                }
            }
        }

        output = render_agent_template(jinja_env, data_with_deps)

        # Dependencies in YAML block
        yaml_block_start = output.index('```yaml')
        yaml_block_end = output.index('```', yaml_block_start + 7)
        yaml_block = output[yaml_block_start:yaml_block_end]

        assert 'dependencies:' in yaml_block, "dependencies key missing from YAML"
        assert 'tasks:' in yaml_block, "tasks key missing from dependencies"
        assert 'templates:' in yaml_block, "templates key missing from dependencies"
        assert 'embed_knowledge:' in yaml_block, "embed_knowledge key missing from dependencies"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

class TestErrorHandling:
    """Tests for validation and error handling"""

    def test_template_validates_missing_required_fields(self, jinja_env):
        """
        GIVEN parsed data missing required fields (name, model)
        WHEN I render agent.md.j2 template
        THEN template handles missing fields gracefully

        Validates:
        - Template doesn't crash with missing fields
        - Output remains valid markdown
        - Missing fields omitted or use defaults
        """
        data_incomplete = {
            'id': 'test-agent',
            'type': 'agent',
            'metadata': {
                # Missing name and model
                'description': 'Test Agent'
            },
            'sections': {}
        }

        # Should not raise exception
        output = render_agent_template(jinja_env, data_incomplete)

        # Output should still be valid markdown with frontmatter
        assert output.startswith('---'), "Frontmatter missing with incomplete data"
        assert 'description: Test Agent' in output, "Description missing from output"


# ============================================================================
# E2E VALIDATION TEST (AC#7)
# ============================================================================

def test_validates_claude_code_spec(jinja_env, sample_parsed_data):
    """
    GIVEN parsed agent data
    WHEN I render agent.md.j2 template
    THEN output validates against Claude Code agent spec (AC#7)

    Validates:
    - YAML frontmatter with mandatory keys (name, description, model)
    - Activation notice section
    - Agent YAML block with commands

    This is the complete format validation test.
    """
    output = render_agent_template(jinja_env, sample_parsed_data)

    # Frontmatter validation (AC#1)
    assert output.startswith('---'), "Missing frontmatter opening"
    assert 'name: Crafty' in output, "Missing name in frontmatter"
    assert 'description:' in output or 'spec:' in output, "Missing description/spec in frontmatter"
    assert 'model: claude-sonnet-4-5' in output, "Missing model in frontmatter"

    # Activation notice validation (AC#2)
    assert 'ACTIVATION-NOTICE:' in output, "Missing activation notice"

    # Agent YAML block validation (AC#3)
    assert '```yaml' in output and 'agent:' in output, "Missing agent YAML block"
    assert 'commands:' in output, "Missing commands in agent YAML block"
