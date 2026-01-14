"""
Test suite for Skill Jinja2 Template (Step 01-04).

Tests verify that skill.md.j2 template produces Claude Code compliant SKILL.md
output following the Anthropic Agent Skills specification.

Key requirements:
- YAML frontmatter with name (required) and description (required)
- Optional nWave metadata: wave, phase, agents, version
- Semantic matching via description (not regex triggers)
- Standard sections: When to Use, Guidelines, Examples
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
def skill_template(jinja_env):
    """Load the skill template."""
    return jinja_env.get_template("skill.md.j2")


@pytest.fixture
def develop_skill_data():
    """Example parsed skill data following Claude Code format."""
    return {
        "id": "develop",
        "type": "skill",
        "metadata": {
            "name": "develop",
            "description": "Use this skill when implementing features using test-driven development.\nActivates for: implementing features, TDD, outside-in testing, writing tests first, red-green-refactor cycle.",
            "wave": "DEVELOP",
            "phase": 3,
            "agents": ["software-crafter"],
            "version": "1.0.0",
        },
        "sections": {
            "when_to_use": [
                "Implementing new features",
                "Writing tests first (TDD approach)",
                "Red-green-refactor cycle",
                "Outside-in testing strategy",
            ],
            "guidelines": [
                "Start with a failing acceptance test (outer loop)",
                "Write failing unit tests (inner loop)",
                "Implement minimal code to pass",
                "Refactor for quality",
                "Repeat until acceptance test passes",
            ],
            "examples": [
                "Implement user authentication using TDD",
                "Add payment processing with outside-in tests",
                "Create REST API endpoint using red-green-refactor",
            ],
        },
        "source_file": "skills/develop.toon",
        "toon_version": "v3.0",
    }


class TestSkillFrontmatter:
    """Skill YAML frontmatter validation."""

    def test_frontmatter_has_required_fields(self, skill_template, develop_skill_data):
        """Frontmatter has name and description (required by Claude Code)."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        # Extract frontmatter
        lines = result.strip().split("\n")
        assert lines[0] == "---"
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)

        # Required fields per Claude Code spec
        assert "name" in frontmatter
        assert "description" in frontmatter
        assert frontmatter["name"] == "develop"
        assert "test-driven development" in frontmatter["description"]

    def test_frontmatter_valid_yaml(self, skill_template, develop_skill_data):
        """Frontmatter parses as valid YAML."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        # Should parse without error
        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter is not None

    def test_frontmatter_includes_optional_nwave_metadata(self, skill_template, develop_skill_data):
        """Optional nWave fields are included when provided."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        # Optional nWave metadata
        assert frontmatter.get("wave") == "DEVELOP"
        assert frontmatter.get("phase") == 3
        assert "software-crafter" in frontmatter.get("agents", [])
        assert frontmatter.get("version") == "1.0.0"


class TestSkillDescription:
    """Semantic description for Claude Code matching."""

    def test_description_is_semantic(self, skill_template, develop_skill_data):
        """Description enables semantic matching (not regex)."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        description = frontmatter["description"]

        # Should contain activation triggers as natural language
        assert "implementing features" in description.lower()
        assert "TDD" in description
        # Should NOT be regex patterns
        assert ".*" not in description
        assert "^" not in description


class TestSkillContent:
    """Skill markdown content sections."""

    def test_skill_title_present(self, skill_template, develop_skill_data):
        """Skill has H1 title after frontmatter."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        # Should have skill title
        assert "# " in result
        # Title should reference skill name or purpose
        assert "develop" in result.lower() or "TDD" in result

    def test_when_to_use_section(self, skill_template, develop_skill_data):
        """When to Use section is rendered."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        assert "## When to Use" in result or "When to Use" in result
        assert "Implementing new features" in result

    def test_guidelines_section(self, skill_template, develop_skill_data):
        """Guidelines section is rendered."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        assert "## Guidelines" in result or "Guidelines" in result
        assert "failing acceptance test" in result

    def test_examples_section(self, skill_template, develop_skill_data):
        """Examples section is rendered."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        assert "## Examples" in result or "Examples" in result
        assert "user authentication" in result


class TestClaudeCodeCompliance:
    """Claude Code Agent Skills specification compliance."""

    def test_no_regex_triggers(self, skill_template, develop_skill_data):
        """Output does not use regex triggers (Claude Code uses semantic matching)."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        # Should NOT have regex pattern indicators
        assert "triggers:" not in result.lower() or "activates for" in result.lower()
        # Description should be natural language, not regex
        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        if "triggers" in frontmatter:
            # If triggers exist, they should be converted to description
            assert False, "Triggers field should not exist - use description for semantic matching"

    def test_name_format_lowercase_hyphens(self, skill_template, develop_skill_data):
        """Name follows Claude Code format (lowercase, hyphens)."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        name = frontmatter["name"]
        # Should match Claude Code name pattern
        import re
        assert re.match(r'^[a-z][a-z0-9-]*$', name), f"Name '{name}' should be lowercase with hyphens"

    def test_description_minimum_length(self, skill_template, develop_skill_data):
        """Description is meaningful (min 50 chars per Claude Code spec)."""
        result = skill_template.render(
            metadata=develop_skill_data["metadata"],
            sections=develop_skill_data["sections"],
        )

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])
        frontmatter = yaml.safe_load(frontmatter_text)

        description = frontmatter["description"]
        assert len(description) >= 50, f"Description too short ({len(description)} chars)"


class TestMinimalSkill:
    """Minimal skill with only required fields."""

    def test_minimal_skill_renders(self, skill_template):
        """Skill with only required fields renders successfully."""
        data = {
            "metadata": {
                "name": "minimal-skill",
                "description": "A minimal skill for testing purposes with enough characters to meet the minimum length requirement.",
            },
            "sections": {},
        }
        result = skill_template.render(**data)

        assert "minimal-skill" in result
        lines = result.strip().split("\n")
        assert lines[0] == "---"

    def test_minimal_skill_valid_yaml(self, skill_template):
        """Minimal skill produces valid YAML frontmatter."""
        data = {
            "metadata": {
                "name": "minimal-skill",
                "description": "A minimal skill for testing purposes with enough characters to meet the minimum length requirement.",
            },
            "sections": {},
        }
        result = skill_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter["name"] == "minimal-skill"


class TestYAMLEscaping:
    """YAML special character escaping."""

    def test_colon_in_description(self, skill_template):
        """Description with colon is properly escaped."""
        data = {
            "metadata": {
                "name": "colon-test",
                "description": "Use when: implementing features with TDD. Activates for: testing, development.",
            },
            "sections": {},
        }
        result = skill_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)
        assert "Use when:" in frontmatter["description"]

    def test_multiline_description(self, skill_template):
        """Multi-line description is properly formatted."""
        data = {
            "metadata": {
                "name": "multiline-test",
                "description": "First line of description.\nSecond line with more details.\nThird line concludes.",
            },
            "sections": {},
        }
        result = skill_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter["description"] is not None

    def test_quotes_in_description(self, skill_template):
        """Description with quotes is properly escaped."""
        data = {
            "metadata": {
                "name": "quote-test",
                "description": 'Use for "advanced" development with \'special\' requirements.',
            },
            "sections": {},
        }
        result = skill_template.render(**data)

        lines = result.strip().split("\n")
        end_idx = lines[1:].index("---") + 1
        frontmatter_text = "\n".join(lines[1:end_idx])

        frontmatter = yaml.safe_load(frontmatter_text)
        assert frontmatter["description"] is not None
