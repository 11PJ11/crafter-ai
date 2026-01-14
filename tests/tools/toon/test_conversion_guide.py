"""Tests for TOON Conversion Guide documentation quality

Step 02-03 acceptance criteria validation:
- README documents >= 15 TOON syntax features with before/after examples
- Every pattern from baseline/patterns/02-02-discovered-patterns.json is documented
- Examples are genericized (not software-crafter-specific)
- README includes decision tree for ambiguous conversions
- Version tracking mechanism for Phase 3 updates
"""

import json
import re
from pathlib import Path

import pytest

# File paths
README_PATH = Path("tools/toon/README.md")
PATTERNS_PATH = Path("baseline/patterns/02-02-discovered-patterns.json")


@pytest.fixture
def readme_content():
    """Load README content."""
    return README_PATH.read_text()


@pytest.fixture
def patterns_data():
    """Load discovered patterns data."""
    return json.loads(PATTERNS_PATH.read_text())


class TestReadmeExists:
    """Verify README file exists and is non-empty."""

    def test_readme_file_exists(self):
        assert README_PATH.exists(), f"README not found: {README_PATH}"

    def test_readme_is_not_empty(self, readme_content):
        assert len(readme_content) > 1000, "README is too short"


class TestSyntaxFeatures:
    """AC1: README documents >= 15 TOON syntax features with before/after examples."""

    def test_at_least_15_syntax_features(self, readme_content):
        """Count numbered syntax feature sections."""
        # Pattern matches "### N. Feature Name" or similar
        feature_pattern = r"###\s+\d+\.\s+[A-Z][a-zA-Z\s\(\)`→]+"
        matches = re.findall(feature_pattern, readme_content)
        assert len(matches) >= 15, (
            f"Only {len(matches)} syntax features found, need >= 15. "
            f"Found: {matches}"
        )

    def test_syntax_features_have_examples(self, readme_content):
        """Each syntax feature should have code examples."""
        # Find all numbered feature sections
        sections = re.split(r"###\s+\d+\.\s+", readme_content)
        features_with_examples = 0

        for section in sections[1:]:  # Skip content before first section
            if "```" in section:
                features_with_examples += 1

        assert features_with_examples >= 15, (
            f"Only {features_with_examples} features have code examples"
        )


class TestPatternDocumentation:
    """AC7: Every pattern from baseline/patterns/02-02-discovered-patterns.json is documented."""

    def test_all_patterns_documented(self, readme_content, patterns_data):
        """Verify each pattern ID appears in README."""
        patterns = patterns_data["patterns_discovered"]

        for pattern in patterns:
            pattern_id = pattern["pattern_id"]
            assert pattern_id in readme_content, (
                f"Pattern {pattern_id} not found in README"
            )

    def test_all_edge_cases_documented(self, readme_content, patterns_data):
        """Verify each edge case ID appears in README."""
        edge_cases = patterns_data["edge_cases_found"]

        for edge_case in edge_cases:
            edge_case_id = edge_case["edge_case_id"]
            assert edge_case_id in readme_content, (
                f"Edge case {edge_case_id} not found in README"
            )

    def test_pattern_count_matches(self, readme_content, patterns_data):
        """Verify pattern count in README matches discovered patterns."""
        expected_patterns = len(patterns_data["patterns_discovered"])
        expected_edge_cases = len(patterns_data["edge_cases_found"])

        # Check for coverage tracking section
        assert f"Patterns documented: {expected_patterns}/{expected_patterns}" in readme_content, (
            f"Pattern count mismatch in coverage tracking"
        )
        assert f"Edge cases documented: {expected_edge_cases}/{expected_edge_cases}" in readme_content, (
            f"Edge case count mismatch in coverage tracking"
        )


class TestGenericizedExamples:
    """AC9: Examples are genericized and portable (not software-crafter-specific)."""

    def test_no_software_crafter_paths(self, readme_content):
        """No software-crafter specific paths in examples."""
        # These patterns would indicate non-genericized examples
        forbidden_patterns = [
            r"nWave/agents/software-crafter\.md",
            r"nWave/agents/software-crafter\.toon",
            r"software-crafter/README\.md",
            r"software-crafter/mikado-method",
            r"software-crafter/outside-in-tdd",
        ]

        for pattern in forbidden_patterns:
            matches = re.findall(pattern, readme_content)
            # Allow in the statistics section but not in code examples
            code_blocks = re.findall(r"```[\s\S]*?```", readme_content)
            for block in code_blocks:
                assert pattern not in block, (
                    f"Found software-crafter specific path in code example: {pattern}"
                )

    def test_uses_generic_placeholders(self, readme_content):
        """Examples use generic placeholder names."""
        generic_patterns = [
            r"agent-name",
            r"path/to/",
            r"AgentName",
            r"PersonaName",
            r"Category Name",
        ]

        found_generic = 0
        for pattern in generic_patterns:
            if pattern in readme_content:
                found_generic += 1

        assert found_generic >= 3, (
            f"Only {found_generic} generic patterns found, expected >= 3"
        )


class TestDecisionTree:
    """AC: README includes decision tree for ambiguous conversions."""

    def test_decision_tree_section_exists(self, readme_content):
        """Decision tree section exists."""
        assert "## Decision Tree" in readme_content, (
            "Decision Tree section not found"
        )

    def test_decision_tree_has_branches(self, readme_content):
        """Decision tree has branching logic."""
        # Look for tree-like structure
        tree_indicators = [
            "├─",
            "└─",
            "Yes →",
            "No →",
        ]

        found = 0
        for indicator in tree_indicators:
            if indicator in readme_content:
                found += 1

        assert found >= 2, (
            f"Decision tree appears incomplete (found {found}/4 indicators)"
        )

    def test_decision_tree_references_patterns(self, readme_content):
        """Decision tree references pattern IDs."""
        # Find decision tree section by looking for the START marker and
        # the code block containing the flowchart
        tree_start = readme_content.find("## Decision Tree")
        assert tree_start != -1, "Could not find Decision Tree section"

        # Find the end of the decision tree (next major section)
        validation_start = readme_content.find("## Validation", tree_start)
        if validation_start == -1:
            tree_section = readme_content[tree_start:]
        else:
            tree_section = readme_content[tree_start:validation_start]

        # Check for pattern references (with parentheses as used in tree)
        pattern_refs = re.findall(r"\(PATTERN-\d{3}\)", tree_section)
        assert len(pattern_refs) >= 5, (
            f"Decision tree only references {len(pattern_refs)} patterns, need >= 5"
        )


class TestVersionTracking:
    """AC: Version tracking mechanism for Phase 3 updates."""

    def test_version_header_comment(self, readme_content):
        """README has version header comment."""
        assert "<!-- version:" in readme_content, (
            "Missing version header comment"
        )

    def test_last_updated_header(self, readme_content):
        """README has last_updated header."""
        assert "<!-- last_updated:" in readme_content, (
            "Missing last_updated header comment"
        )

    def test_version_history_section(self, readme_content):
        """Version history section exists."""
        assert "## Version History" in readme_content, (
            "Missing Version History section"
        )

    def test_update_protocol_documented(self, readme_content):
        """Update protocol for new patterns is documented."""
        assert "Update Protocol" in readme_content, (
            "Missing Update Protocol section"
        )

    def test_source_patterns_reference(self, readme_content):
        """Source patterns file is referenced."""
        assert "baseline/patterns/02-02-discovered-patterns.json" in readme_content, (
            "Missing reference to source patterns file"
        )


class TestBeforeAfterExamples:
    """AC: Before/after examples for patterns."""

    def test_patterns_have_before_after(self, readme_content):
        """Each pattern section has Before and After examples."""
        # Find all PATTERN sections
        pattern_sections = re.split(r"### PATTERN-\d{3}:", readme_content)

        patterns_with_both = 0
        for section in pattern_sections[1:]:  # Skip content before first pattern
            has_before = "**Before**" in section or "Before (Markdown)" in section
            has_after = "**After**" in section or "After (TOON)" in section

            if has_before and has_after:
                patterns_with_both += 1

        assert patterns_with_both >= 5, (
            f"Only {patterns_with_both} patterns have Before/After examples"
        )


class TestTOONCodeBlocksSyntax:
    """Verify TOON code blocks use correct syntax."""

    def test_toon_code_blocks_exist(self, readme_content):
        """TOON code blocks are present."""
        toon_blocks = re.findall(r"```toon", readme_content)
        assert len(toon_blocks) >= 10, (
            f"Only {len(toon_blocks)} TOON code blocks, need >= 10"
        )

    def test_toon_blocks_have_section_headers(self, readme_content):
        """TOON code blocks use ## section headers."""
        toon_blocks = re.findall(r"```toon\n([\s\S]*?)```", readme_content)

        blocks_with_headers = 0
        for block in toon_blocks:
            if "## " in block:
                blocks_with_headers += 1

        assert blocks_with_headers >= 5, (
            f"Only {blocks_with_headers} TOON blocks have section headers"
        )


class TestValidationSection:
    """Verify validation section exists with thresholds."""

    def test_validation_section_exists(self, readme_content):
        """Validation section exists."""
        assert "## Validation" in readme_content, (
            "Missing Validation section"
        )

    def test_acceptance_thresholds_documented(self, readme_content):
        """Acceptance thresholds are documented."""
        assert "Acceptance Thresholds" in readme_content, (
            "Missing Acceptance Thresholds"
        )
        assert ">= 95%" in readme_content, (
            "Missing 95% equivalence threshold"
        )


class TestQuickReference:
    """Verify quick reference section exists."""

    def test_quick_reference_exists(self, readme_content):
        """Quick reference section exists."""
        assert "## Quick Reference" in readme_content, (
            "Missing Quick Reference section"
        )

    def test_common_conversions_table(self, readme_content):
        """Common conversions table exists."""
        assert "Common Conversions" in readme_content, (
            "Missing Common Conversions table"
        )

    def test_symbol_reference_table(self, readme_content):
        """Symbol reference table exists."""
        assert "Symbol Reference" in readme_content, (
            "Missing Symbol Reference table"
        )
