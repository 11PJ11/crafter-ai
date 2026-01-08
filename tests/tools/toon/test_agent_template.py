"""Tests for agent.md.j2 template rendering

Business language: Template renders TOON parsed data into Claude Code compliant agent.md
"""
from pathlib import Path
from jinja2 import Environment, FileSystemLoader
import pytest


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


def test_activation_notice_present(jinja_env, sample_parsed_data):
    """
    GIVEN parsed agent data
    WHEN I render agent.md.j2 template
    THEN output contains activation notice section (AC#2)

    Validates:
    - Activation notice appears after frontmatter
    - Contains proper formatting with > blockquote
    - Includes agent name in notice
    """
    template = jinja_env.get_template('agent.md.j2')
    output = template.render(**sample_parsed_data)

    # AC#2: Activation notice section present
    assert '> **Agent Activated**:' in output, "Activation notice missing"
    assert 'Crafty' in output or 'software-crafter' in output, "Agent name missing from activation notice"


def test_agent_yaml_block_present(jinja_env, sample_parsed_data):
    """
    GIVEN parsed agent data with commands
    WHEN I render agent.md.j2 template
    THEN output contains agent YAML configuration block (AC#3)

    Validates:
    - YAML code block present (```yaml)
    - Contains 'agent:' top-level key
    - Commands rendered in YAML block
    """
    template = jinja_env.get_template('agent.md.j2')
    output = template.render(**sample_parsed_data)

    # AC#3: Agent YAML block with configuration
    assert '```yaml' in output, "YAML code block missing"
    assert 'agent:' in output, "agent: key missing from YAML block"
    assert 'commands:' in output, "commands: key missing from YAML block"


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
    template = jinja_env.get_template('agent.md.j2')
    output = template.render(**sample_parsed_data)

    # Frontmatter validation
    assert output.startswith('---'), "Missing frontmatter opening"
    assert 'name: Crafty' in output, "Missing name in frontmatter"
    assert 'description:' in output or 'spec:' in output, "Missing description/spec in frontmatter"
    assert 'model: claude-sonnet-4-5' in output, "Missing model in frontmatter"

    # Activation notice validation (AC#2)
    assert '> **Agent Activated**:' in output, "Missing activation notice"

    # Agent YAML block validation (AC#3)
    assert '```yaml' in output and 'agent:' in output, "Missing agent YAML block"
    assert 'commands:' in output, "Missing commands in agent YAML block"


def test_commands_rendered_as_list_in_yaml_block(jinja_env, sample_parsed_data):
    """
    GIVEN parsed agent data with multiple commands
    WHEN I render agent.md.j2 template
    THEN commands appear as list in YAML block

    Validates:
    - Commands listed under 'commands:' key
    - Each command appears in output
    """
    template = jinja_env.get_template('agent.md.j2')
    output = template.render(**sample_parsed_data)

    # Commands should be in YAML block
    assert 'develop' in output, "develop command missing"
    assert 'refactor' in output, "refactor command missing"
    assert 'mikado' in output, "mikado command missing"
