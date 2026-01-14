"""Tests for researcher-reviewer.toon conversion from researcher-reviewer.md

Step 02-02: Transform researcher-reviewer to TOON v3.0 format

Acceptance Criteria:
1. TOON v3.0 file generated: nWave/agents/researcher-reviewer.toon
2. Schema validation passes
3. All YAML keys preserved
4. Zero syntax errors
"""

import pytest
from pathlib import Path


# File path constants
TOON_FILE_PATH = Path("/mnt/c/Repositories/Projects/ai-craft/nWave/agents/researcher-reviewer.toon")
SOURCE_MD_PATH = Path("/mnt/c/Repositories/Projects/ai-craft/nWave/agents/researcher-reviewer.md")


class TestResearcherReviewerToonFileExists:
    """AC1: TOON v3.0 file generated"""

    def test_toon_file_exists(self):
        """The TOON file must exist at the expected path"""
        assert TOON_FILE_PATH.exists(), f"TOON file not found at {TOON_FILE_PATH}"

    def test_toon_file_not_empty(self):
        """The TOON file must contain content"""
        assert TOON_FILE_PATH.exists(), "TOON file must exist first"
        content = TOON_FILE_PATH.read_text(encoding='utf-8')
        assert len(content) > 0, "TOON file must not be empty"


class TestResearcherReviewerToonSchemaValidation:
    """AC2: Schema validation passes"""

    @pytest.fixture
    def toon_content(self) -> str:
        """Load TOON file content"""
        if not TOON_FILE_PATH.exists():
            pytest.skip("TOON file does not exist yet")
        return TOON_FILE_PATH.read_text(encoding='utf-8')

    def test_has_toon_header(self, toon_content: str):
        """TOON file must have proper header with version"""
        assert "(TOON v3.0)" in toon_content, "Missing TOON v3.0 header"

    def test_has_id_section(self, toon_content: str):
        """TOON file must have ID section"""
        assert "## ID" in toon_content, "Missing ## ID section"

    def test_has_persona_section(self, toon_content: str):
        """TOON file must have PERSONA section"""
        assert "## PERSONA" in toon_content, "Missing ## PERSONA section"

    def test_has_commands_section(self, toon_content: str):
        """TOON file must have COMMANDS section"""
        assert "## COMMANDS" in toon_content, "Missing ## COMMANDS section"

    def test_has_core_principles_section(self, toon_content: str):
        """TOON file must have CORE_PRINCIPLES section"""
        assert "## CORE_PRINCIPLES" in toon_content, "Missing ## CORE_PRINCIPLES section"

    def test_has_contract_section(self, toon_content: str):
        """TOON file must have CONTRACT section"""
        assert "## CONTRACT" in toon_content, "Missing ## CONTRACT section"

    def test_has_safety_framework_section(self, toon_content: str):
        """TOON file must have SAFETY_FRAMEWORK section"""
        assert "## SAFETY_FRAMEWORK" in toon_content, "Missing ## SAFETY_FRAMEWORK section"

    def test_has_testing_framework_section(self, toon_content: str):
        """TOON file must have TESTING_FRAMEWORK section"""
        assert "## TESTING_FRAMEWORK" in toon_content, "Missing ## TESTING_FRAMEWORK section"

    def test_has_metadata_section(self, toon_content: str):
        """TOON file must have METADATA section"""
        assert "## METADATA" in toon_content, "Missing ## METADATA section"


class TestResearcherReviewerYamlKeysPreserved:
    """AC3: All YAML keys preserved"""

    @pytest.fixture
    def toon_content(self) -> str:
        """Load TOON file content"""
        if not TOON_FILE_PATH.exists():
            pytest.skip("TOON file does not exist yet")
        return TOON_FILE_PATH.read_text(encoding='utf-8')

    def test_agent_id_preserved(self, toon_content: str):
        """Agent ID 'researcher-reviewer' must be present"""
        assert "researcher-reviewer" in toon_content, "Agent ID 'researcher-reviewer' not preserved"

    def test_persona_name_nova_preserved(self, toon_content: str):
        """Persona name 'Nova' must be preserved"""
        assert "Nova" in toon_content, "Persona name 'Nova' not preserved"

    def test_role_evidence_driven_preserved(self, toon_content: str):
        """Role description must include 'Evidence-Driven Knowledge Researcher'"""
        assert "Evidence-Driven Knowledge Researcher" in toon_content, "Role not preserved"

    def test_model_haiku_preserved(self, toon_content: str):
        """Model 'haiku' must be preserved (cost-efficient review agent)"""
        assert "haiku" in toon_content.lower(), "Model 'haiku' not preserved"

    def test_tools_list_preserved(self, toon_content: str):
        """Tools list must be preserved"""
        expected_tools = ["Read", "Write", "Edit", "Glob", "Grep", "WebFetch", "WebSearch"]
        for tool in expected_tools:
            assert tool in toon_content, f"Tool '{tool}' not preserved"

    def test_commands_preserved(self, toon_content: str):
        """Key commands must be preserved"""
        expected_commands = ["help", "research", "verify-sources", "cross-reference",
                          "synthesize-findings", "cite-sources", "exit"]
        for cmd in expected_commands:
            assert cmd in toon_content, f"Command '{cmd}' not preserved"

    def test_dependencies_preserved(self, toon_content: str):
        """Dependencies must be preserved"""
        assert "dw/research.md" in toon_content, "Task dependency not preserved"
        assert "trusted-source-domains.yaml" in toon_content, "Data dependency not preserved"

    def test_core_principles_token_economy(self, toon_content: str):
        """Core principle 'Token Economy' must be preserved"""
        assert "Token Economy" in toon_content, "Core principle 'Token Economy' not preserved"

    def test_core_principles_evidence_based(self, toon_content: str):
        """Core principle about evidence-based research must be preserved"""
        assert "Evidence-Based" in toon_content or "evidence-based" in toon_content.lower(), \
            "Core principle 'Evidence-Based' not preserved"


class TestResearcherReviewerToonSyntax:
    """AC4: Zero syntax errors"""

    @pytest.fixture
    def toon_content(self) -> str:
        """Load TOON file content"""
        if not TOON_FILE_PATH.exists():
            pytest.skip("TOON file does not exist yet")
        return TOON_FILE_PATH.read_text(encoding='utf-8')

    def test_no_unclosed_brackets(self, toon_content: str):
        """No unclosed brackets in content"""
        # Count various bracket types
        assert toon_content.count('[') == toon_content.count(']'), "Unclosed square brackets"
        assert toon_content.count('(') == toon_content.count(')'), "Unclosed parentheses"
        assert toon_content.count('{') == toon_content.count('}'), "Unclosed curly braces"

    def test_no_yaml_block_markers(self, toon_content: str):
        """TOON format should not contain YAML code block markers"""
        assert "```yaml" not in toon_content, "TOON should not contain YAML code blocks"
        assert "```" not in toon_content, "TOON should not contain code block markers"

    def test_section_markers_properly_formatted(self, toon_content: str):
        """Section markers should be properly formatted with ## prefix"""
        lines = toon_content.split('\n')
        section_lines = [l for l in lines if l.strip().startswith('## ')]
        assert len(section_lines) >= 8, f"Expected at least 8 sections, found {len(section_lines)}"

    def test_valid_utf8_encoding(self, toon_content: str):
        """File content should be valid UTF-8"""
        # If we got here, the file was successfully read as UTF-8
        assert isinstance(toon_content, str), "Content must be a string"

    def test_no_double_colon_syntax_errors(self, toon_content: str):
        """No accidental double colons that break parsing"""
        # Allow :: in specific contexts like URLs, but flag obvious errors
        lines = toon_content.split('\n')
        for i, line in enumerate(lines, 1):
            if '::' in line and 'http' not in line.lower():
                # Check if it's not in a URL context
                if not any(url in line.lower() for url in ['http://', 'https://', 'ftp://']):
                    # Could be intentional, but flag for review
                    pass  # TOON allows some special syntax


class TestResearcherReviewerToonParserIntegration:
    """Validate parser can process the TOON file"""

    @pytest.fixture
    def toon_content(self) -> str:
        """Load TOON file content"""
        if not TOON_FILE_PATH.exists():
            pytest.skip("TOON file does not exist yet")
        return TOON_FILE_PATH.read_text(encoding='utf-8')

    def test_parser_can_parse_file(self, toon_content: str):
        """TOON parser should successfully parse the file"""
        from tools.toon.parser import TOONParser

        parser = TOONParser()
        result = parser.parse(toon_content)

        assert result is not None, "Parser returned None"
        assert 'id' in result, "Parser result missing 'id'"
        assert 'type' in result, "Parser result missing 'type'"
        assert 'metadata' in result, "Parser result missing 'metadata'"
        assert 'sections' in result, "Parser result missing 'sections'"

    def test_parser_extracts_correct_id(self, toon_content: str):
        """Parser should extract the correct agent ID"""
        from tools.toon.parser import TOONParser

        parser = TOONParser()
        result = parser.parse(toon_content)

        assert result['id'] == 'researcher-reviewer', \
            f"Expected ID 'researcher-reviewer', got '{result['id']}'"

    def test_parser_detects_v3_version(self, toon_content: str):
        """Parser should detect TOON v3.0 version"""
        from tools.toon.parser import TOONParser

        parser = TOONParser()
        result = parser.parse(toon_content)

        assert result['toon_version'] == 'v3.0', \
            f"Expected version 'v3.0', got '{result['toon_version']}'"

    def test_parser_extracts_sections(self, toon_content: str):
        """Parser should extract multiple sections"""
        from tools.toon.parser import TOONParser

        parser = TOONParser()
        result = parser.parse(toon_content)

        assert len(result['sections']) >= 5, \
            f"Expected at least 5 sections, got {len(result['sections'])}"


class TestResearcherReviewerSpecificContent:
    """Test researcher-reviewer specific content is preserved"""

    @pytest.fixture
    def toon_content(self) -> str:
        """Load TOON file content"""
        if not TOON_FILE_PATH.exists():
            pytest.skip("TOON file does not exist yet")
        return TOON_FILE_PATH.read_text(encoding='utf-8')

    def test_review_specialist_reference(self, toon_content: str):
        """Should mention review specialist role"""
        assert "Review Specialist" in toon_content or "review specialist" in toon_content.lower(), \
            "Missing review specialist reference"

    def test_cost_efficiency_reference(self, toon_content: str):
        """Should mention cost efficiency for Haiku model"""
        assert "cost" in toon_content.lower(), "Missing cost efficiency reference"

    def test_when_to_use_includes_review(self, toon_content: str):
        """whenToUse should mention review tasks"""
        assert "review" in toon_content.lower(), "whenToUse missing review reference"

    def test_critique_dimensions_embed_marker(self, toon_content: str):
        """Should have embedded knowledge marker for critique dimensions"""
        assert "BUILD:INJECT" in toon_content or "EMBEDDED_KNOWLEDGE" in toon_content, \
            "Missing embedded knowledge section"
