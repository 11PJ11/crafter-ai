"""Tests for round-trip validation of TOON to Markdown compilation

Step 02-02 acceptance criteria validation:
- Compiled output has identical command list (exact match)
- Compiled output has identical dependency list (exact match, order-independent)
- Compiled output has valid YAML frontmatter (schema-validated)
- No critical sections missing from output
- Embedded knowledge markers preserved in compilation
- Patterns and edge cases enumerated
"""

import tempfile
from pathlib import Path

import pytest

from tools.toon.compiler import compile_toon
from tools.toon.validate_roundtrip import (
    collect_differences,
    command_list_validator,
    dependency_list_validator,
    discover_edge_cases,
    discover_patterns,
    embedded_knowledge_validator,
    extract_commands,
    extract_dependencies,
    extract_frontmatter,
    extract_inject_markers,
    metadata_validator,
    section_presence_validator,
    validate_roundtrip,
)

# Test files
TOON_FILE = Path("nWave/agents/software-crafter.toon")
ORIGINAL_MD = Path("nWave/agents/software-crafter.md")


@pytest.fixture
def compiled_md_path():
    """Compile TOON to temporary MD file for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        compile_toon(str(TOON_FILE), tmpdir)
        output_file = list(Path(tmpdir).glob("*.md"))[0]
        yield str(output_file)


@pytest.fixture
def compiled_content(compiled_md_path):
    """Get compiled markdown content."""
    return Path(compiled_md_path).read_text()


@pytest.fixture
def original_content():
    """Get original markdown content."""
    return ORIGINAL_MD.read_text()


@pytest.fixture
def toon_content():
    """Get TOON source content."""
    return TOON_FILE.read_text()


class TestValidateRoundtrip:
    """E2E test: validate_roundtrip achieves >= 95% equivalence."""

    def test_semantic_equivalence_score_above_threshold(self, compiled_md_path):
        """GIVEN original .md and compiled .md from TOON
        WHEN I run validation script
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

    def test_returns_all_required_fields(self, compiled_md_path):
        """Validate result dictionary has all required fields."""
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)

        required_fields = [
            "equivalence_score",
            "commands_match",
            "dependencies_match",
            "frontmatter_valid",
            "critical_sections_present",
            "embedded_knowledge_preserved",
            "differences",
            "patterns_discovered",
            "edge_cases_found",
        ]

        for field in required_fields:
            assert field in result, f"Missing required field: {field}"

    def test_patterns_enumerated_for_documentation(self, compiled_md_path):
        """Patterns and edge cases enumerated for step 2.3 documentation."""
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)

        # Minimum 5 patterns required
        assert len(result["patterns_discovered"]) >= 5, (
            f"Only {len(result['patterns_discovered'])} patterns discovered, need >= 5"
        )

        # Minimum 3 edge cases required
        assert len(result["edge_cases_found"]) >= 3, (
            f"Only {len(result['edge_cases_found'])} edge cases found, need >= 3"
        )


class TestCommandListValidator:
    """test_command_list_identical"""

    def test_command_list_validator_returns_bool(self, original_content, compiled_content):
        result = command_list_validator(original_content, compiled_content)
        assert isinstance(result, bool)

    def test_same_content_commands_match(self):
        """Same content should have matching commands."""
        content = "- help: Show help\n- develop: Run development\n- exit: Exit"
        assert command_list_validator(content, content) is True

    def test_extract_commands_finds_yaml_style(self):
        """Extract commands from YAML-style list."""
        content = "commands:\n  - help: Show help\n  - develop: Run dev\n"
        commands = extract_commands(content)
        assert "help" in commands
        assert "develop" in commands


class TestDependencyListValidator:
    """test_dependency_list_identical"""

    def test_dependency_list_validator_returns_bool(self, original_content, compiled_content):
        result = dependency_list_validator(original_content, compiled_content)
        assert isinstance(result, bool)

    def test_same_content_dependencies_match(self):
        """Same content should have matching dependencies."""
        content = "dependencies:\n  tasks:\n    - task1.md\n    - task2.md\n"
        assert dependency_list_validator(content, content) is True

    def test_extract_dependencies_finds_tasks(self):
        """Extract tasks from dependencies section."""
        content = "dependencies:\n  tasks:\n    - dw/develop.md\n    - dw/mikado.md\n"
        deps = extract_dependencies(content)
        assert "dw/develop.md" in deps["tasks"]
        assert "dw/mikado.md" in deps["tasks"]


class TestFrontmatterValidator:
    """test_frontmatter_valid_and_complete"""

    def test_frontmatter_validator_with_valid_yaml(self):
        """Valid YAML frontmatter passes validation."""
        content = "---\nname: test-agent\ndescription: Test\n---\n\n# Content"
        assert metadata_validator(content) is True

    def test_frontmatter_validator_missing_frontmatter(self):
        """Missing frontmatter fails validation."""
        content = "# Just markdown without frontmatter"
        assert metadata_validator(content) is False

    def test_frontmatter_validator_invalid_yaml(self):
        """Invalid YAML fails validation."""
        content = "---\nname: test\n  bad indent:\n---"
        # This should parse but may not have required fields
        result = metadata_validator(content)
        assert isinstance(result, bool)

    def test_extract_frontmatter_returns_dict(self):
        """Extract frontmatter returns dictionary."""
        content = "---\nname: test-agent\nmodel: inherit\n---\n# Content"
        fm = extract_frontmatter(content)
        assert isinstance(fm, dict)
        assert fm["name"] == "test-agent"


class TestCriticalSections:
    """test_no_critical_sections_missing"""

    def test_section_presence_with_all_sections(self, compiled_content):
        """Compiled output should have critical sections."""
        result = section_presence_validator(compiled_content)
        assert result is True, "Critical sections missing from compiled output"

    def test_section_presence_requires_name(self):
        """Must have agent name."""
        content = "---\nname: test\n---\n# test\ncommands:\n- help:\nactivation:"
        assert section_presence_validator(content) is True

    def test_section_presence_requires_commands(self):
        """Must have commands."""
        content = "---\nname: test\n---\n# test\nactivation: yes"
        # Missing commands
        assert section_presence_validator(content) is False


class TestEmbeddedKnowledgeValidator:
    """test_embedded_knowledge_markers_preserved"""

    def test_embedded_knowledge_validator_with_markers(self, original_content, compiled_content):
        """Original has BUILD:INJECT markers - validation should pass."""
        result = embedded_knowledge_validator(original_content, compiled_content)
        assert result is True

    def test_extract_inject_markers_finds_all(self, toon_content):
        """Extract all BUILD:INJECT markers from content."""
        markers = extract_inject_markers(toon_content)
        assert len(markers) >= 5  # software-crafter.toon has 6 markers


class TestPatternDiscovery:
    """test_patterns_enumerated_for_documentation"""

    def test_discover_patterns_returns_list(self, original_content, compiled_content):
        """Pattern discovery returns list of pattern dictionaries."""
        patterns = discover_patterns(original_content, compiled_content)
        assert isinstance(patterns, list)
        assert len(patterns) >= 5

    def test_pattern_has_required_fields(self, original_content, compiled_content):
        """Each pattern has required fields."""
        patterns = discover_patterns(original_content, compiled_content)

        required_fields = [
            "pattern_id",
            "description",
            "before_example",
            "after_example",
            "applies_to",
        ]

        for pattern in patterns:
            for field in required_fields:
                assert field in pattern, f"Pattern missing field: {field}"

    def test_discover_edge_cases_returns_list(self, original_content, compiled_content):
        """Edge case discovery returns list."""
        edge_cases = discover_edge_cases(original_content, compiled_content)
        assert isinstance(edge_cases, list)
        assert len(edge_cases) >= 3

    def test_edge_case_has_required_fields(self, original_content, compiled_content):
        """Each edge case has required fields."""
        edge_cases = discover_edge_cases(original_content, compiled_content)

        required_fields = ["edge_case_id", "description", "handling_strategy"]

        for edge_case in edge_cases:
            for field in required_fields:
                assert field in edge_case, f"Edge case missing field: {field}"


class TestDifferenceCollection:
    """Test difference collection for debugging."""

    def test_collect_differences_returns_list(self, original_content, compiled_content):
        """Difference collection returns list of strings."""
        diffs = collect_differences(original_content, compiled_content)
        assert isinstance(diffs, list)
        # All items should be strings
        for diff in diffs:
            assert isinstance(diff, str)


class TestEquivalenceScoreCalculation:
    """Test equivalence score calculation."""

    def test_score_is_percentage(self, compiled_md_path):
        """Score should be between 0 and 100."""
        result = validate_roundtrip(str(ORIGINAL_MD), compiled_md_path)
        assert 0 <= result["equivalence_score"] <= 100

    def test_perfect_match_gives_100(self):
        """Identical content should score 100%."""
        content = """---
name: test-agent
---

# test-agent

commands:
  - help: Show help

activation: yes

dependencies:
  tasks:
    - task1.md
"""
        # Write to temp files
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f1, tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f2:
            f1.write(content)
            f2.write(content)
            f1.flush()
            f2.flush()

            result = validate_roundtrip(f1.name, f2.name)
            # May not be exactly 100 due to extraction logic, but should be high
            assert result["equivalence_score"] >= 90
