"""MD Agent Parser - Parse YAML-frontmatter Markdown agent files.

Parses agent specification files in Markdown format with:
- YAML frontmatter (---...---)
- Embedded YAML code blocks (```yaml...```)
- Inline YAML sections (without code block markers)
- Markdown content sections

Output matches TOONParserOutput schema for compatibility with template rendering.

Step: 02-01 - Parse researcher-reviewer.md
Step: 05-01 - Enhanced for illustrator.md inline YAML parsing
"""

import re
import yaml
from pathlib import Path
from typing import Any

from tools.toon.parser_schema import TOONParserOutput, TOONMetadata


class MDAgentParser:
    """Parser for Markdown agent specification files.

    Usage:
        parser = MDAgentParser()
        result = parser.parse(content)
        # or
        result = parser.parse_file(Path("agents/researcher-reviewer.md"))

    Output conforms to TOONParserOutput schema defined in parser_schema.py
    """

    def parse_file(self, file_path: Path) -> TOONParserOutput:
        """Parse MD agent file from path.

        Args:
            file_path: Path to .md agent file

        Returns:
            TOONParserOutput dictionary with id, type, metadata, sections
        """
        content = file_path.read_text(encoding="utf-8")
        result = self.parse(content)
        result["source_file"] = str(file_path)
        return result

    def parse(self, content: str) -> TOONParserOutput:
        """Parse MD content into structured dictionary.

        Args:
            content: Raw MD file content (string)

        Returns:
            TOONParserOutput dictionary with id, type, metadata, sections

        Behavior:
            - Empty content returns empty structure
            - YAML frontmatter extracted to metadata
            - Embedded YAML blocks extracted to sections
            - Markdown sections preserved
        """
        if not content or not content.strip():
            return self._create_empty_output()

        # Parse in stages
        frontmatter = self._extract_frontmatter(content)
        embedded_yaml = self._extract_embedded_yaml(content)
        metadata = self._build_metadata(frontmatter)
        sections = self._build_sections(embedded_yaml)
        agent_id = self._extract_id(metadata, sections)

        return {
            "id": agent_id,
            "type": "agent",
            "metadata": metadata,
            "sections": sections,
            "source_file": None,
            "toon_version": "md-agent",
            "raw_content": None,
            "parse_errors": None,
            "parse_warnings": None,
        }

    def _create_empty_output(self) -> TOONParserOutput:
        """Create empty parser output structure."""
        return {
            "id": "",
            "type": "agent",
            "metadata": {},
            "sections": {},
            "source_file": None,
            "toon_version": "md-agent",
            "raw_content": None,
            "parse_errors": None,
            "parse_warnings": None,
        }

    def _extract_frontmatter(self, content: str) -> dict[str, Any]:
        """Extract YAML frontmatter from content.

        Frontmatter format:
            ---
            name: agent-name
            description: Description
            model: model-name
            tools: [Read, Write]
            ---

        Returns:
            Parsed frontmatter as dict, or empty dict if not found
        """
        frontmatter_pattern = r"^---\s*\n(.*?)\n---"
        match = re.match(frontmatter_pattern, content, re.DOTALL)

        if match:
            try:
                return yaml.safe_load(match.group(1)) or {}
            except yaml.YAMLError:
                return {}
        return {}

    def _extract_embedded_yaml(self, content: str) -> dict[str, Any]:
        """Extract embedded YAML code blocks or inline YAML from content.

        Looks for:
            ```yaml
            key: value
            ```

        If no yaml code blocks found, falls back to inline YAML extraction
        (sections defined with key: at start of line without code block markers).

        Returns:
            Merged dict of all YAML blocks/sections
        """
        yaml_block_pattern = r"```yaml\s*\n(.*?)\n```"
        matches = re.findall(yaml_block_pattern, content, re.DOTALL)

        result: dict[str, Any] = {}
        for match in matches:
            try:
                parsed = yaml.safe_load(match)
                if isinstance(parsed, dict):
                    result.update(parsed)
            except yaml.YAMLError:
                # Fallback: extract top-level sections manually
                fallback = self._extract_sections_fallback(match)
                result.update(fallback)

        # If no yaml code blocks found, try inline YAML extraction
        if not result:
            result = self._extract_inline_yaml_sections(content)

        return result

    def _extract_inline_yaml_sections(self, content: str) -> dict[str, Any]:
        """Extract inline YAML sections from markdown content.

        For files like illustrator.md where YAML is inline without code block markers.
        Identifies top-level sections starting at column 0 (e.g., "agent:", "persona:")
        and extracts their content until the next top-level section or markdown heading.

        Handles special case where parent sections (agent:, persona:, pipeline:)
        have children at the same indentation level - these are grouped under the parent.

        Args:
            content: Full markdown content

        Returns:
            Dict with section names and parsed content
        """
        result: dict[str, Any] = {}

        # Remove frontmatter first
        content_without_frontmatter = re.sub(
            r"^---\s*\n.*?\n---\s*\n",
            "",
            content,
            flags=re.DOTALL
        )

        lines = content_without_frontmatter.split("\n")

        # Define known parent sections that have children
        # These are sections that appear as "section:" on their own line
        # followed by key: value pairs that belong to them
        known_parent_sections = {
            'agent', 'persona', 'pipeline', 'dependencies', 'elicitation',
            'handoff', 'review_criteria', 'toolchain_recommendations',
            'lip_sync_framework', 'export_framework'
        }

        # First pass: identify all section boundaries
        sections_found = self._identify_section_boundaries(
            lines, known_parent_sections
        )

        # Second pass: extract content for each section
        for section_name, (start_idx, end_idx) in sections_found.items():
            section_lines = lines[start_idx:end_idx]
            section_data = self._parse_inline_section(section_name, section_lines)
            if section_data is not None:
                result[section_name] = section_data

        return result

    def _identify_section_boundaries(
        self,
        lines: list[str],
        known_parent_sections: set[str]
    ) -> dict[str, tuple[int, int]]:
        """Identify start and end indices for each section.

        Args:
            lines: All lines of content
            known_parent_sections: Set of section names that have children

        Returns:
            Dict mapping section name to (start_idx, end_idx) of content lines
        """
        sections: dict[str, tuple[int, int]] = {}
        section_pattern = r"^([a-zA-Z_][a-zA-Z0-9_-]*):\s*(.*)$"

        current_section: str | None = None
        current_start: int = 0
        in_parent_section = False

        i = 0
        while i < len(lines):
            line = lines[i]

            # Markdown headings and HTML comments end current section
            if self._is_section_terminator(line):
                if current_section is not None:
                    sections[current_section] = (current_start, i)
                    current_section = None
                in_parent_section = False
                i += 1
                continue

            match = re.match(section_pattern, line)
            if match:
                section_name = match.group(1)
                inline_value = match.group(2).strip()

                # Handle known parent sections (e.g., agent:, persona:, pipeline:)
                if self._is_parent_section(section_name, inline_value, known_parent_sections):
                    if current_section is not None:
                        sections[current_section] = (current_start, i)
                    current_section = section_name
                    current_start = i + 1
                    in_parent_section = True

                elif not in_parent_section:
                    # Regular section (not child of parent)
                    if current_section is not None:
                        sections[current_section] = (current_start, i)
                    current_section = section_name
                    current_start = i + 1 if not inline_value else i
                    in_parent_section = False
                # else: child key of parent section - continue collecting

            i += 1

        # Save final section
        if current_section is not None:
            sections[current_section] = (current_start, len(lines))

        return sections

    def _is_section_terminator(self, line: str) -> bool:
        """Check if line terminates the current section.

        Markdown headings and HTML comments are section terminators.
        """
        return line.startswith("#") or line.startswith("<!--")

    def _is_parent_section(
        self,
        section_name: str,
        inline_value: str,
        known_parent_sections: set[str]
    ) -> bool:
        """Check if this is a known parent section with no inline value.

        Parent sections (like agent:, persona:, pipeline:) have children
        at the same indentation level.
        """
        return section_name in known_parent_sections and not inline_value

    def _parse_inline_section(
        self, section_name: str, content_lines: list[str]
    ) -> Any | None:
        """Parse an inline YAML section's content.

        Args:
            section_name: Name of the section (e.g., 'agent', 'persona')
            content_lines: Lines of content belonging to this section

        Returns:
            Parsed section data, or None if empty/invalid
        """
        if not content_lines:
            return None

        # Join lines and try to parse as YAML
        content = "\n".join(content_lines)

        # Skip empty content
        if not content.strip():
            return None

        # Try parsing as YAML first
        try:
            parsed = yaml.safe_load(content)
            if parsed is not None:
                return parsed
        except yaml.YAMLError:
            pass

        # Fall back to line-by-line extraction
        return self._extract_items_from_lines(content_lines, content)

    def _extract_sections_fallback(self, yaml_content: str) -> dict[str, Any]:
        """Extract top-level sections from malformed YAML.

        Uses regex to identify top-level keys (no leading whitespace, ending with :)
        and extract content until next top-level key.

        Args:
            yaml_content: YAML content that failed to parse

        Returns:
            Dict with section names and raw content
        """
        result: dict[str, Any] = {}

        # Find all top-level keys (no leading whitespace, word chars, colon)
        section_pattern = r"^([a-zA-Z_][a-zA-Z0-9_]*):\s*$"
        lines = yaml_content.split("\n")

        current_section = None
        current_content: list[str] = []

        for line in lines:
            match = re.match(section_pattern, line)
            if match:
                # Save previous section
                if current_section:
                    section_data = self._parse_section_content(current_content)
                    result[current_section] = section_data

                current_section = match.group(1)
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section and current_content:
            section_data = self._parse_section_content(current_content)
            result[current_section] = section_data

        return result

    def _parse_section_content(self, lines: list[str]) -> Any:
        """Parse section content into appropriate structure.

        Attempts YAML parsing first, falls back to line-by-line extraction.
        """
        content = "\n".join(lines)

        yaml_result = self._try_yaml_parse(content)
        if yaml_result is not None:
            return yaml_result

        return self._extract_items_from_lines(lines, content)

    def _try_yaml_parse(self, content: str) -> Any | None:
        """Attempt to parse content as YAML.

        Returns:
            Parsed YAML content, or None if parsing fails
        """
        try:
            parsed = yaml.safe_load(content)
            if parsed is not None:
                return parsed
        except yaml.YAMLError:
            pass
        return None

    def _extract_items_from_lines(self, lines: list[str], raw_content: str) -> Any:
        """Extract list items or key-value pairs from lines.

        Args:
            lines: Individual lines to process
            raw_content: Original content as fallback

        Returns:
            List of extracted items, or raw content if no items found
        """
        items = []
        for line in lines:
            stripped = line.strip()
            extracted = self._extract_item_from_line(stripped)
            if extracted:
                items.append(extracted)

        return items if items else raw_content.strip()

    def _extract_item_from_line(self, stripped_line: str) -> str | None:
        """Extract item from a single line.

        Handles:
            - List items: "- value" -> "value"
            - Key-value pairs: "key: value" -> "key: value"
            - Comments are ignored

        Returns:
            Extracted item string, or None if line should be skipped
        """
        if stripped_line.startswith("- "):
            return stripped_line[2:].strip()
        if ": " in stripped_line and not stripped_line.startswith("#"):
            return stripped_line
        return None

    def _build_metadata(self, frontmatter: dict[str, Any]) -> TOONMetadata:
        """Build metadata from frontmatter.

        Maps frontmatter fields to TOONMetadata fields.
        """
        metadata: TOONMetadata = {}

        if "name" in frontmatter:
            metadata["name"] = frontmatter["name"]
        if "description" in frontmatter:
            metadata["description"] = frontmatter["description"]
        if "model" in frontmatter:
            metadata["model"] = frontmatter["model"]
        if "tools" in frontmatter:
            metadata["spec"] = str(frontmatter["tools"])

        return metadata

    def _build_sections(self, embedded_yaml: dict[str, Any]) -> dict[str, Any]:
        """Build sections from embedded YAML.

        Returns:
            Dict mapping section names to section content
        """
        return embedded_yaml

    def _extract_id(
        self, metadata: TOONMetadata, sections: dict[str, Any]
    ) -> str:
        """Extract agent ID from metadata or sections.

        Priority:
        1. metadata['name']
        2. sections['agent']['id']
        3. Empty string

        Returns:
            Agent identifier string
        """
        if metadata.get("name"):
            return str(metadata["name"])

        if "agent" in sections and isinstance(sections["agent"], dict):
            if "id" in sections["agent"]:
                return str(sections["agent"]["id"])

        return ""
