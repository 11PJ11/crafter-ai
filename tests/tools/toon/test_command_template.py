"""
Test suite for Command Jinja2 Template (Step 01-03).

Tests verify that command.md.j2 template produces Claude Code compliant output
with proper command-specific metadata (NOT agent metadata).

Key differences from agent template:
- Commands have parameters/returns (agents have role/spec)
- Commands have parent_agent (agents don't)
- Commands have prerequisites/workflow (agents have persona/core_rules)
- Commands are explicitly invoked, NOT auto-activated
"""

import pytest
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

# Test data directory
TEMPLATE_DIR = Path(__file__).parent.parent.parent.parent / "tools" / "toon" / "templates"


@pytest.fixture
def jinja_env():
    """Create Jinja2 environment for template testing."""
    return Environment(
        loader=FileSystemLoader(str(TEMPLATE_DIR)),
        trim_blocks=True,
        lstrip_blocks=True,
    )


@pytest.fixture
def command_template(jinja_env):
    """Load the command template."""
    return jinja_env.get_template("command.md.j2")


@pytest.fixture
def develop_command_data():
    """Example parsed command data from parser - develop command."""
    return {
        "id": "develop",
        "type": "command",
        "metadata": {
            "name": "develop",
            "description": "Execute complete DEVELOP wave with 11-phase TDD",
            "parent_agent": "software-crafter",
            "version": "v3.0",
            "parameters": [
                {
                    "name": "feature-description",
                    "type": "string",
                    "required": True,
                    "description": "Natural language description of feature to develop",
                }
            ],
            "returns": {
                "type": "object",
                "properties": {
                    "success": {"type": "boolean"},
                    "commits": {"type": "integer"},
                    "evolution_doc": {"type": "string"},
                },
            },
        },
        "sections": {
            "prerequisites": [
                "baseline approved",
                "roadmap approved",
                "all step files reviewed",
            ],
            "workflow": {
                "steps": [
                    "Validate baseline",
                    "Execute all steps with TDD",
                    "Finalize and archive",
                ]
            },
            "success_criteria": [
                "All tests passing",
                "All commits created",
                "Evolution document generated",
            ],
        },
        "source_file": "commands/develop.toon",
        "toon_version": "v3.0",
    }


class TestCommandInvocationHeader:
    """AC1: Template produces command invocation header (NOT agent-activation header)."""

    def test_command_invocation_header_present(self, command_template, develop_command_data):
        """Command has invocation header with name and purpose."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # Should have command invocation header, NOT activation notice
        assert "# develop" in result or "# /develop" in result
        assert "Execute complete DEVELOP wave" in result
        # Should NOT have agent activation notice
        assert "ACTIVATION-NOTICE" not in result
        assert "This file contains your full agent" not in result

    def test_no_auto_activation_notice(self, command_template, develop_command_data):
        """Commands are explicitly invoked, NOT auto-activated."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        assert "auto-activat" not in result.lower()
        assert "ACTIVATION-NOTICE" not in result


class TestParentAgentReference:
    """AC2: Template includes parent agent reference."""

    def test_parent_agent_in_frontmatter(self, command_template, develop_command_data):
        """Parent agent appears in YAML frontmatter."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # Extract frontmatter
        lines = result.strip().split("\n")
        assert lines[0] == "---"
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        assert "parent_agent" in frontmatter
        assert frontmatter["parent_agent"] == "software-crafter"

    def test_parent_agent_reference_in_body(self, command_template, develop_command_data):
        """Parent agent is mentioned in command body."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        assert "software-crafter" in result


class TestParametersSpecification:
    """AC3 (revised): Template includes parameter specifications."""

    def test_parameters_section_present(self, command_template, develop_command_data):
        """Parameters section is rendered."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        assert "Parameters" in result or "## Parameters" in result or "parameters:" in result.lower()

    def test_parameter_details_rendered(self, command_template, develop_command_data):
        """Parameter name, type, and description are rendered."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        assert "feature-description" in result
        assert "string" in result.lower()
        # Description should appear somewhere
        assert "Natural language" in result or "feature" in result.lower()


class TestReturnsSpecification:
    """Template includes returns specification."""

    def test_returns_section_present(self, command_template, develop_command_data):
        """Returns section is rendered."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        assert "Returns" in result or "## Returns" in result or "returns:" in result.lower()

    def test_return_properties_rendered(self, command_template, develop_command_data):
        """Return properties are rendered."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # At least one of the return properties should appear
        assert any(prop in result for prop in ["success", "commits", "evolution_doc"])


class TestPrerequisitesSection:
    """AC3 (original): Template includes command prerequisites."""

    def test_prerequisites_rendered_as_checklist(self, command_template, develop_command_data):
        """Prerequisites are rendered as markdown checklist."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # Should have prerequisites as checklist items
        assert "baseline approved" in result
        assert "roadmap approved" in result
        # Could be either checklist format
        has_checklist_format = (
            "- [ ]" in result
            or "- baseline" in result.lower()
            or "* baseline" in result.lower()
        )
        assert has_checklist_format or "Prerequisites" in result


class TestSuccessCriteriaSection:
    """AC4: Template renders success criteria as markdown checklist."""

    def test_success_criteria_rendered(self, command_template, develop_command_data):
        """Success criteria section is rendered."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        assert "Success" in result or "success_criteria" in result.lower()

    def test_success_criteria_as_checklist(self, command_template, develop_command_data):
        """Success criteria are in checklist format."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # Success criteria items should appear
        assert "All tests passing" in result
        assert "All commits created" in result


class TestYAMLOutput:
    """AC6: Template properly escapes YAML special characters."""

    def test_output_is_valid_yaml_frontmatter(self, command_template, develop_command_data):
        """Generated output has valid YAML frontmatter."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # Extract frontmatter
        lines = result.strip().split("\n")
        assert lines[0] == "---", "Must start with YAML frontmatter delimiter"

        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line == "---":
                end_idx = i
                break

        assert end_idx is not None, "Must have closing frontmatter delimiter"
        frontmatter_text = "\n".join(lines[1:end_idx])

        # Should parse without error
        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter is not None
        assert "name" in frontmatter
        assert "description" in frontmatter

    def test_frontmatter_required_fields(self, command_template, develop_command_data):
        """Frontmatter has all required fields for commands."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # Extract frontmatter
        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        # Required for commands per schema
        assert "name" in frontmatter
        assert "description" in frontmatter
        assert "parent_agent" in frontmatter


class TestClaudeCodeSpecCompliance:
    """AC9: Generated command.md files validate against Claude Code specification."""

    def test_validates_claude_code_command_spec(self, command_template, develop_command_data):
        """Output matches Claude Code command specification."""
        result = command_template.render(
            metadata=develop_command_data["metadata"],
            sections=develop_command_data["sections"],
        )

        # Must have valid frontmatter
        lines = result.strip().split("\n")
        assert lines[0] == "---"

        # Must have command-specific sections, NOT agent sections
        assert "ACTIVATION-NOTICE" not in result
        assert "agent:" not in result.lower() or "parent_agent" in result.lower()

        # Must have command invocation pattern
        assert "/develop" in result or "# develop" in result

        # Should NOT have agent-specific content
        assert "persona:" not in result.lower()
        assert "core_rules:" not in result.lower()
