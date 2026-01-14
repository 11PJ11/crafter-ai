"""
Edge case tests for Command Jinja2 Template (Step 01-03).

Tests cover:
- AC5: Null/missing fields handling
- AC6: YAML special character escaping
- AC7: Multi-line command documentation
- AC8: Command namespace collision prevention
- AC10: Embedded knowledge marker preservation
"""

import pytest
import yaml
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

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


class TestNullFieldHandling:
    """AC5: Template handles null/missing fields gracefully."""

    def test_missing_description(self, command_template):
        """Template renders without description."""
        data = {
            "metadata": {
                "name": "minimal-command",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        assert "minimal-command" in result
        assert "test-agent" in result
        # Should not crash

    def test_missing_parameters(self, command_template):
        """Template renders without parameters section."""
        data = {
            "metadata": {
                "name": "no-params",
                "description": "Command without parameters",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        assert "no-params" in result
        # Parameters section should be absent or empty
        assert "no-params" in result

    def test_missing_returns(self, command_template):
        """Template renders without returns section."""
        data = {
            "metadata": {
                "name": "no-returns",
                "description": "Command without returns",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        assert "no-returns" in result

    def test_missing_prerequisites(self, command_template):
        """Template renders without prerequisites section."""
        data = {
            "metadata": {
                "name": "no-prereqs",
                "description": "Command without prerequisites",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        assert "no-prereqs" in result

    def test_empty_sections(self, command_template):
        """Template handles empty sections dict."""
        data = {
            "metadata": {
                "name": "empty-sections",
                "description": "Command with empty sections",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        # Should produce valid output
        assert "---" in result
        assert "empty-sections" in result

    def test_null_parameter_description(self, command_template):
        """Template handles parameter with null description."""
        data = {
            "metadata": {
                "name": "null-param-desc",
                "description": "Command with null param description",
                "parent_agent": "test-agent",
                "parameters": [
                    {
                        "name": "param1",
                        "type": "string",
                        "required": True,
                        "description": None,
                    }
                ],
            },
            "sections": {},
        }
        result = command_template.render(**data)

        assert "param1" in result
        # Should not crash on None description


class TestYAMLSpecialCharacterEscaping:
    """AC6: Template properly escapes YAML special characters."""

    def test_colon_in_description(self, command_template):
        """Description with colon is properly escaped."""
        data = {
            "metadata": {
                "name": "colon-test",
                "description": "Validate: configuration settings",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        # Extract and parse frontmatter
        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        # Should parse without error
        frontmatter = yaml.safe_load(frontmatter_text)
        assert "Validate" in frontmatter["description"]
        assert "configuration" in frontmatter["description"]

    def test_quotes_in_description(self, command_template):
        """Description with quotes is properly escaped."""
        data = {
            "metadata": {
                "name": "quote-test",
                "description": 'Run "special" command with \'options\'',
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        # Should parse without error
        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter["description"] is not None

    def test_hash_at_start(self, command_template):
        """Description starting with # is properly escaped."""
        data = {
            "metadata": {
                "name": "hash-test",
                "description": "#1 priority command",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)
        assert "#1" in frontmatter["description"]

    def test_ampersand_in_name(self, command_template):
        """Special YAML characters in values are escaped."""
        data = {
            "metadata": {
                "name": "ampersand-test",
                "description": "&reference anchor test",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter["description"] is not None

    def test_bracket_in_description(self, command_template):
        """Description with brackets is properly escaped."""
        data = {
            "metadata": {
                "name": "bracket-test",
                "description": "[Optional] Command {with} brackets",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)
        assert "[Optional]" in frontmatter["description"]


class TestMultiLineDocumentation:
    """AC7: Template handles multi-line command documentation."""

    def test_multiline_description(self, command_template):
        """Multi-line description is properly formatted."""
        data = {
            "metadata": {
                "name": "multiline-test",
                "description": "First line of description\nSecond line continues here\nThird line ends it",
                "parent_agent": "test-agent",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        # Should parse without error
        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter["description"] is not None

    def test_multiline_prerequisite(self, command_template):
        """Multi-line prerequisites are handled."""
        data = {
            "metadata": {
                "name": "multiline-prereq",
                "description": "Command with multi-line prereqs",
                "parent_agent": "test-agent",
            },
            "sections": {
                "prerequisites": [
                    "First prerequisite\nwith continuation",
                    "Second prerequisite",
                ]
            },
        }
        result = command_template.render(**data)

        assert "First prerequisite" in result
        assert "Second prerequisite" in result


class TestCommandNamespaceCollision:
    """AC8: Template namespaces commands to prevent name collisions."""

    def test_command_has_parent_agent_context(self, command_template):
        """Commands include parent agent context for namespacing."""
        data = {
            "metadata": {
                "name": "validate",
                "description": "Generic validate command",
                "parent_agent": "software-crafter",
            },
            "sections": {},
        }
        result = command_template.render(**data)

        # Frontmatter should include parent_agent for namespacing
        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        assert frontmatter["parent_agent"] == "software-crafter"

    def test_different_parent_agents_same_command_name(self, command_template):
        """Same command name with different parents produces different context."""
        data1 = {
            "metadata": {
                "name": "validate",
                "description": "Validate for software-crafter",
                "parent_agent": "software-crafter",
            },
            "sections": {},
        }
        data2 = {
            "metadata": {
                "name": "validate",
                "description": "Validate for product-owner",
                "parent_agent": "product-owner",
            },
            "sections": {},
        }

        result1 = command_template.render(**data1)
        result2 = command_template.render(**data2)

        # Both should render successfully
        assert "software-crafter" in result1
        assert "product-owner" in result2

        # They should be different
        assert result1 != result2


class TestEmbeddedKnowledgeMarkerPreservation:
    """AC10: Template preserves embedded knowledge injection markers."""

    def test_embed_markers_preserved(self, command_template):
        """Embed markers are preserved in output."""
        data = {
            "metadata": {
                "name": "embed-test",
                "description": "Command with embedded knowledge",
                "parent_agent": "test-agent",
            },
            "sections": {
                "embed_knowledge": [
                    "path/to/knowledge.md",
                    "another/knowledge.yaml",
                ]
            },
        }
        result = command_template.render(**data)

        # Should contain build injection markers
        assert "BUILD:INJECT:START" in result or "EMBEDDED KNOWLEDGE" in result

    def test_embed_markers_with_typed_markers(self, command_template):
        """Typed embed markers are preserved."""
        data = {
            "metadata": {
                "name": "typed-embed",
                "description": "Command with typed markers",
                "parent_agent": "test-agent",
            },
            "sections": {},
            "embed_markers": [
                {
                    "start_marker": "<!-- BUILD:INJECT:START:custom-knowledge.md -->",
                    "end_marker": "<!-- BUILD:INJECT:END -->",
                }
            ],
        }
        result = command_template.render(**data)

        assert "custom-knowledge.md" in result


class TestValidYAMLOutput:
    """Additional YAML output validation tests."""

    def test_complex_metadata_produces_valid_yaml(self, command_template):
        """Complex metadata still produces valid YAML frontmatter."""
        data = {
            "metadata": {
                "name": "complex-command",
                "description": "A complex: command with 'quotes' and \"double quotes\"",
                "parent_agent": "test-agent",
                "version": "v3.0",
                "parameters": [
                    {
                        "name": "complex-param",
                        "type": "object",
                        "required": True,
                        "description": "Parameter with: special chars",
                    }
                ],
                "returns": {
                    "type": "object",
                    "properties": {
                        "result": {"type": "string"},
                    },
                },
            },
            "sections": {
                "prerequisites": ["prereq: with colon"],
                "success_criteria": ["criterion: with 'special' chars"],
            },
        }
        result = command_template.render(**data)

        # Extract frontmatter
        lines = result.strip().split("\n")
        assert lines[0] == "---"
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        # Should parse without error
        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter["name"] == "complex-command"
        assert frontmatter["parent_agent"] == "test-agent"
