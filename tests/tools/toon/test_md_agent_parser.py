"""Unit tests for MD Agent parser - Parse YAML-frontmatter Markdown files.

Business language: Parse MD agent files (YAML frontmatter + embedded YAML) into structured data.

Step: 02-01 - Parse researcher-reviewer.md
"""
import pytest
from pathlib import Path


class TestMDAgentParserAcceptance:
    """Acceptance tests for MD agent parser (step 02-01)"""

    def test_parse_researcher_reviewer_md_without_errors(self):
        """
        GIVEN researcher-reviewer.md file path
        WHEN MDAgentParser processes the file
        THEN no parsing errors occur and valid structure returned

        AC#1: MD file parsed without errors
        """
        from tools.toon.md_agent_parser import MDAgentParser

        parser = MDAgentParser()
        result = parser.parse_file(Path("nWave/agents/researcher-reviewer.md"))

        assert result is not None, "Parser returned None"
        assert "id" in result, "Missing 'id' in result"
        assert "type" in result, "Missing 'type' in result"
        assert "metadata" in result, "Missing 'metadata' in result"
        assert "sections" in result, "Missing 'sections' in result"

    def test_parse_researcher_reviewer_md_identifies_all_sections(self):
        """
        GIVEN researcher-reviewer.md file with multiple sections
        WHEN MDAgentParser processes the file
        THEN all sections are identified and extracted

        AC#2: All sections identified and extracted
        """
        from tools.toon.md_agent_parser import MDAgentParser

        parser = MDAgentParser()
        result = parser.parse_file(Path("nWave/agents/researcher-reviewer.md"))

        # Expected sections from researcher-reviewer.md
        expected_sections = [
            "agent",
            "commands",
            "dependencies",
            "contract",
            "safety_framework",
            "testing_framework",
            "observability_framework",
            "error_recovery_framework",
        ]

        for section in expected_sections:
            assert section in result["sections"], f"Missing section: {section}"

    def test_parse_researcher_reviewer_md_extracts_frontmatter(self):
        """
        GIVEN researcher-reviewer.md file with YAML frontmatter
        WHEN MDAgentParser processes the file
        THEN frontmatter is extracted into metadata

        AC#3: Output JSON contains frontmatter
        """
        from tools.toon.md_agent_parser import MDAgentParser

        parser = MDAgentParser()
        result = parser.parse_file(Path("nWave/agents/researcher-reviewer.md"))

        # Frontmatter fields from researcher-reviewer.md
        assert result["metadata"].get("name") == "researcher-reviewer"
        assert "description" in result["metadata"]
        assert result["metadata"].get("model") == "haiku"

    def test_parse_researcher_reviewer_md_extracts_commands(self):
        """
        GIVEN researcher-reviewer.md file with commands section
        WHEN MDAgentParser processes the file
        THEN commands are extracted into result

        AC#3: Output JSON contains commands
        """
        from tools.toon.md_agent_parser import MDAgentParser

        parser = MDAgentParser()
        result = parser.parse_file(Path("nWave/agents/researcher-reviewer.md"))

        assert "commands" in result["sections"]
        commands = result["sections"]["commands"]

        # Expected commands from researcher-reviewer.md
        expected_commands = [
            "help",
            "research",
            "verify-sources",
            "cross-reference",
            "synthesize-findings",
            "cite-sources",
            "ask-clarification",
            "create-embed",
            "exit",
        ]

        for cmd in expected_commands:
            assert any(
                cmd in str(c) for c in (commands if isinstance(commands, list) else [commands])
            ), f"Missing command: {cmd}"

    def test_parse_researcher_reviewer_md_no_warnings_or_errors(self):
        """
        GIVEN researcher-reviewer.md file
        WHEN MDAgentParser processes the file
        THEN no parsing warnings or errors are recorded

        AC#4: No parsing warnings or errors
        """
        from tools.toon.md_agent_parser import MDAgentParser

        parser = MDAgentParser()
        result = parser.parse_file(Path("nWave/agents/researcher-reviewer.md"))

        # Check for error indicators
        assert result.get("parse_errors") is None or len(result.get("parse_errors", [])) == 0
        assert result.get("parse_warnings") is None or len(result.get("parse_warnings", [])) == 0


class TestMDAgentParserUnit:
    """Unit tests for MD agent parser components"""

    def test_parser_exists(self):
        """
        GIVEN tools/toon/md_agent_parser.py exists
        WHEN importing MDAgentParser
        THEN import succeeds
        """
        from tools.toon.md_agent_parser import MDAgentParser

        assert MDAgentParser is not None

    def test_parser_handles_empty_content(self):
        """
        GIVEN empty content string
        WHEN MDAgentParser.parse() is called
        THEN returns empty structure without errors
        """
        from tools.toon.md_agent_parser import MDAgentParser

        parser = MDAgentParser()
        result = parser.parse("")

        assert result["id"] == ""
        assert result["type"] == "agent"
        assert result["metadata"] == {}
        assert result["sections"] == {}

    def test_parser_extracts_yaml_frontmatter(self):
        """
        GIVEN content with YAML frontmatter
        WHEN MDAgentParser.parse() is called
        THEN frontmatter fields are extracted to metadata
        """
        from tools.toon.md_agent_parser import MDAgentParser

        content = """---
name: test-agent
description: Test description
model: sonnet
tools: [Read, Write]
---

# test-agent

Content here.
"""
        parser = MDAgentParser()
        result = parser.parse(content)

        assert result["metadata"]["name"] == "test-agent"
        assert result["metadata"]["description"] == "Test description"
        assert result["metadata"]["model"] == "sonnet"

    def test_parser_extracts_embedded_yaml_block(self):
        """
        GIVEN content with embedded YAML code block
        WHEN MDAgentParser.parse() is called
        THEN YAML block content is parsed into sections
        """
        from tools.toon.md_agent_parser import MDAgentParser

        content = """---
name: test-agent
---

# test-agent

```yaml
agent:
  id: test-agent
  title: Test Agent

commands:
  - help: Show help
  - exit: Exit agent
```
"""
        parser = MDAgentParser()
        result = parser.parse(content)

        assert "agent" in result["sections"]
        assert result["sections"]["agent"]["id"] == "test-agent"
        assert "commands" in result["sections"]
