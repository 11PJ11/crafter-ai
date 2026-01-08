"""Unit tests for TOON parser - Walking Skeleton.

Business language: Parse TOON files into structured agent data.
"""
import pytest
from tools.toon.parser import TOONParser


def test_parser_extracts_agent_metadata_from_toon_id_section():
    """
    GIVEN TOON content with ID section containing role, spec, model
    WHEN parser processes the content
    THEN metadata contains extracted fields
    """
    toon_content = """# NOVEL EDITOR AGENT (TOON v1.0)
## ID
role: Aria | genre_editor
spec: fantasy/scifi/romantasy
model: evidence_based
"""

    parser = TOONParser()
    result = parser.parse(toon_content)

    assert result['metadata']['role'] == 'Aria | genre_editor'
    assert result['metadata']['spec'] == 'fantasy/scifi/romantasy'
    assert result['metadata']['model'] == 'evidence_based'
    assert result['metadata']['id'] == 'genre_editor'


def test_parser_identifies_toon_version_from_agent_header():
    """
    GIVEN TOON content with version in header
    WHEN parser processes the content
    THEN version is correctly detected
    """
    toon_content = """# NOVEL EDITOR AGENT (TOON v1.0)
"""

    parser = TOONParser()
    result = parser.parse(toon_content)

    assert result['toon_version'] == 'v1.0'


def test_parser_organizes_toon_content_into_named_sections():
    """
    GIVEN TOON content with multiple sections
    WHEN parser processes the content
    THEN sections are extracted and named correctly
    """
    toon_content = """# TEST AGENT (TOON v1.0)
## ID
role: test
## CORE_RULES
→ RULE_1: description
→ RULE_2: description
"""

    parser = TOONParser()
    result = parser.parse(toon_content)

    assert 'id' in result['sections']
    assert 'core_rules' in result['sections']


def test_parser_classifies_toon_file_as_agent_type():
    """
    GIVEN TOON content with AGENT in header
    WHEN parser processes the content
    THEN type is set to 'agent'
    """
    toon_content = """# NOVEL EDITOR AGENT (TOON v1.0)
"""

    parser = TOONParser()
    result = parser.parse(toon_content)

    assert result['type'] == 'agent'


def test_parser_handles_empty_toon_file_gracefully():
    """
    GIVEN empty TOON content
    WHEN parser processes the content
    THEN empty structure is returned
    """
    parser = TOONParser()
    result = parser.parse("")

    assert result['id'] == ''
    assert result['type'] == 'agent'
    assert result['metadata'] == {}
    assert result['sections'] == {}


def test_parser_handles_toon_file_without_version_marker():
    """
    GIVEN TOON content without version marker in header
    WHEN parser processes the content
    THEN version is set to 'unknown'
    """
    toon_content = """# LEGACY AGENT
## ID
role: Legacy | legacy-agent
"""

    parser = TOONParser()
    result = parser.parse(toon_content)

    assert result['toon_version'] == 'unknown'
    assert result['id'] == 'legacy-agent'
