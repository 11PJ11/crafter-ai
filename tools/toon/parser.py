"""TOON Parser Core Implementation

Parses TOON (Terse Object Notation) files into structured Python dictionaries.

Supports TOON v3.0 format with backward compatibility for v1.0.

TOON Format Features:
- Section headers: ## SECTION_NAME
- Key-value pairs: key: value
- Lists: - item or key:\n  - item
- Nested structures: indentation-based
- TOON symbols: →, ⟷, ≠, ✓, ✗, ⚠️
- Comments: # comment (inline or standalone)

Implementation Strategy:
- Level 1 Refactoring: Clear naming for parse methods
- Level 2 Refactoring: Extract section parsers from monolithic function
- Level 3 Refactoring: Separate lexer from parser responsibility
"""

import re
from typing import Any
from tools.toon.parser_schema import TOONParserOutput, TOONMetadata


class TOONParser:
    """Parser for TOON (Terse Object Notation) format files

    Usage:
        parser = TOONParser()
        result = parser.parse(toon_content)

    Output conforms to TOONParserOutput schema defined in parser_schema.py
    """

    # TOON symbols and their semantic meanings
    TOON_SYMBOLS = {
        '→': 'implies',
        '⟷': 'alternates',
        '≠': 'not_equal',
        '✓': 'correct',
        '✗': 'wrong',
        '⚠️': 'warning',
    }

    def parse(self, content: str) -> TOONParserOutput:
        """Parse TOON content into structured dictionary

        Args:
            content: Raw TOON file content (string)

        Returns:
            TOONParserOutput dictionary with id, type, metadata, sections

        Behavior:
            - Empty content returns empty structure
            - Malformed content parses best-effort (no exceptions)
            - Comments stripped from values
            - TOON symbols preserved in content
            - Version detected from header (TOON v1.0/v3.0)
        """
        if not content or not content.strip():
            return self._create_empty_output()

        # Parse in stages (separation of concerns)
        lines = self._preprocess_content(content)
        version = self._detect_version(content)
        metadata = self._extract_metadata(lines, content)
        sections = self._parse_sections(lines)
        agent_id = self._extract_id(metadata, sections)
        content_type = self._determine_type(content)

        return {
            'id': agent_id,
            'type': content_type,
            'metadata': metadata,
            'sections': sections,
            'source_file': None,  # Set by caller if needed
            'toon_version': version,
            'raw_content': None,  # Optional for debugging
        }

    def _create_empty_output(self) -> TOONParserOutput:
        """Create empty parser output structure"""
        return {
            'id': '',
            'type': 'agent',
            'metadata': {},
            'sections': {},
            'source_file': None,
            'toon_version': 'unknown',
            'raw_content': None,
        }

    def _preprocess_content(self, content: str) -> list[str]:
        """Preprocess content into clean lines

        Removes:
        - Standalone comment lines
        - Empty lines (consolidated)

        Preserves:
        - Section markers (## SECTION)
        - Content lines with inline comments stripped
        - Indentation
        """
        lines = []
        for line in content.split('\n'):
            # Skip standalone comments (but preserve ## section markers)
            if line.strip().startswith('#') and not line.strip().startswith('##'):
                continue

            # Strip inline comments (but not from header)
            if '#' in line and not line.strip().startswith('##'):
                # Keep everything before first # that's not a section marker
                parts = line.split('#')
                line = parts[0].rstrip()

            if line.strip():  # Keep non-empty lines
                lines.append(line)

        return lines

    def _detect_version(self, content: str) -> str:
        """Detect TOON version from header

        Looks for: # AGENT NAME (TOON v3.0) or (TOON v1.0)

        Returns:
            Version string: 'v1.0', 'v3.0', or 'unknown'
        """
        version_match = re.search(r'\(TOON\s+(v\d+\.\d+)\)', content)
        if version_match:
            return version_match.group(1)
        return 'unknown'

    def _extract_metadata(self, lines: list[str], full_content: str) -> TOONMetadata:
        """Extract metadata from header and ID section

        Metadata Sources:
        - Header: First line (# AGENT NAME (TOON vX.X))
        - Second line: Description
        - ID section: role, spec, model fields

        Returns:
            TOONMetadata dict with name, id, role, spec, model, version, description
        """
        metadata: TOONMetadata = {}

        # Extract from header (first line)
        header_match = re.search(r'^#\s+([A-Z\s]+AGENT).*\(TOON\s+(v\d+\.\d+)\)', full_content)
        if header_match:
            agent_name_raw = header_match.group(1).strip()
            # Extract just the name part before "AGENT"
            name_parts = agent_name_raw.replace(' AGENT', '').strip().split()
            if name_parts:
                # Convert "NOVEL EDITOR" -> "Novel Editor"
                metadata['name'] = ' '.join(name_parts).title()
            metadata['version'] = header_match.group(2)

        # Extract description (second line if it's a comment)
        description_match = re.search(r'^#[^#](.+)$', full_content, re.MULTILINE)
        if description_match:
            desc_line = description_match.group(1).strip()
            # Skip if it looks like the header line
            if 'TOON v' not in desc_line and 'AGENT' not in desc_line.upper():
                metadata['description'] = desc_line

        # Extract from ID section
        in_id_section = False
        for line in lines:
            if line.strip().startswith('## ID'):
                in_id_section = True
                continue
            elif line.strip().startswith('##'):
                in_id_section = False
                continue

            if in_id_section and ':' in line:
                key, value = self._parse_key_value(line)
                if key == 'role':
                    metadata['role'] = value
                    # Extract id from role if pattern: "Name | id_name"
                    if '|' in value:
                        parts = value.split('|')
                        if len(parts) >= 2:
                            metadata['id'] = parts[1].strip()
                            if not metadata.get('name'):
                                metadata['name'] = parts[0].strip()
                elif key == 'spec':
                    metadata['spec'] = value
                elif key == 'model':
                    metadata['model'] = value

        return metadata

    def _parse_sections(self, lines: list[str]) -> dict[str, Any]:
        """Parse content into structured sections

        Sections identified by: ## SECTION_NAME

        Each section contains:
        - Key-value pairs (key: value)
        - Lists (- item or key:\n  - subitem)
        - Nested structures (indentation-based)

        Returns:
            Dict mapping section names (lowercase) to section content
        """
        sections: dict[str, Any] = {}
        current_section = None
        current_content: list[str] = []

        for line in lines:
            # Section header
            if line.strip().startswith('##') and not line.strip().startswith('###'):
                # Save previous section
                if current_section:
                    sections[current_section] = self._parse_section_content(current_content)

                # Start new section
                section_name = line.strip()[2:].strip().lower()
                # Remove inline comments from section name
                if '#' in section_name:
                    section_name = section_name.split('#')[0].strip()
                current_section = section_name
                current_content = []
            elif current_section:
                current_content.append(line)

        # Save last section
        if current_section:
            sections[current_section] = self._parse_section_content(current_content)

        return sections

    def _parse_section_content(self, lines: list[str]) -> dict[str, Any] | list[str] | str:
        """Parse content within a section

        Detects structure type:
        - List: Lines starting with - or containing nested lists
        - Dict: Lines containing key: value
        - Mixed: Combination of both

        Returns:
            dict[str, Any]: For key-value or mixed sections
            list[str]: For list-only sections
            str: For plain text sections
        """
        if not lines:
            return {}

        # Check structure type
        has_lists = any(line.strip().startswith('-') for line in lines)
        has_key_values = any(':' in line and not line.strip().startswith('-') for line in lines)

        if has_key_values and not has_lists:
            return self._parse_key_value_section(lines)
        elif has_lists and not has_key_values:
            return self._parse_list_section(lines)
        elif has_key_values and has_lists:
            return self._parse_mixed_section(lines)
        else:
            # Plain text content
            return '\n'.join(line.strip() for line in lines)

    def _parse_key_value_section(self, lines: list[str]) -> dict[str, Any]:
        """Parse section with key: value pairs"""
        result = {}
        current_key = None
        current_value_lines: list[str] = []

        for line in lines:
            if ':' in line and not line.strip().startswith('-'):
                # Save previous key-value
                if current_key:
                    result[current_key] = self._join_multiline_value(current_value_lines)

                # Parse new key-value
                key, value = self._parse_key_value(line)
                current_key = key
                current_value_lines = [value] if value else []
            elif current_key and line.strip():
                # Continuation of previous value (multiline)
                current_value_lines.append(line.strip())

        # Save last key-value
        if current_key:
            result[current_key] = self._join_multiline_value(current_value_lines)

        return result

    def _parse_list_section(self, lines: list[str]) -> list[Any]:
        """Parse section with list items (- item)"""
        items = []
        for line in lines:
            if line.strip().startswith('-'):
                item = line.strip()[1:].strip()  # Remove leading -
                items.append(item)
        return items

    def _parse_mixed_section(self, lines: list[str]) -> dict[str, Any]:
        """Parse section with mixed key-value and nested lists

        Example:
            dependencies:
              tasks:
                - task1.md
                - task2.md
              templates:
                - template1.yaml
        """
        result = {}
        current_key = None
        current_items: list[str] = []
        indent_level = 0

        for line in lines:
            stripped = line.strip()

            # Key with nested list
            if ':' in line and not stripped.startswith('-'):
                # Save previous key's list
                if current_key and current_items:
                    result[current_key] = current_items
                    current_items = []

                # Parse key
                key, value = self._parse_key_value(line)
                current_key = key

                # If value exists inline, store it
                if value:
                    result[key] = value
                    current_key = None  # Reset since value was inline
            elif stripped.startswith('-') and current_key:
                # List item under current key
                item = stripped[1:].strip()
                current_items.append(item)
            elif stripped.startswith('-'):
                # Standalone list item (no parent key)
                item = stripped[1:].strip()
                if 'items' not in result:
                    result['items'] = []
                result['items'].append(item)

        # Save last key's list
        if current_key and current_items:
            result[current_key] = current_items

        return result

    def _parse_key_value(self, line: str) -> tuple[str, str]:
        """Parse a key: value line

        Returns:
            Tuple of (key, value) with whitespace stripped
        """
        parts = line.split(':', 1)
        key = parts[0].strip()
        # Remove leading - if present
        key = key.lstrip('-').strip()

        value = parts[1].strip() if len(parts) > 1 else ''
        return (key, value)

    def _join_multiline_value(self, lines: list[str]) -> str:
        """Join multiline value into single string

        Preserves structure but removes excess whitespace
        """
        if not lines:
            return ''
        if len(lines) == 1:
            return lines[0]
        # Join with space for readability
        return ' '.join(line.strip() for line in lines if line.strip())

    def _extract_id(self, metadata: TOONMetadata, sections: dict[str, Any]) -> str:
        """Extract agent ID from metadata or sections

        Priority:
        1. metadata['id'] (from ID section role field)
        2. sections['id']['id'] (explicit id field)
        3. Generated from name (lowercase, hyphenated)
        4. Empty string

        Returns:
            Agent identifier string
        """
        # Check metadata first
        if metadata.get('id'):
            return metadata['id']

        # Check ID section
        if 'id' in sections and isinstance(sections['id'], dict):
            if 'id' in sections['id']:
                return sections['id']['id']

        # Generate from name
        if metadata.get('name'):
            return metadata['name'].lower().replace(' ', '-')

        return ''

    def _determine_type(self, content: str) -> str:
        """Determine content type from file content

        Type Detection:
        - 'agent': Contains AGENT in header or has persona/commands sections
        - 'command': Contains COMMAND in header
        - 'skill': Contains SKILL in header

        Returns:
            Content type: 'agent', 'command', or 'skill'
        """
        content_upper = content.upper()

        if 'AGENT' in content_upper:
            return 'agent'
        elif 'COMMAND' in content_upper:
            return 'command'
        elif 'SKILL' in content_upper:
            return 'skill'

        # Default to agent
        return 'agent'
