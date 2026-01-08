"""TOON Parser Output Schema

This module defines the TypedDict structure for TOON parser output.

Coordinated with step 01-02 (Jinja2 template) requirements:
- Template needs: id, role metadata, commands, dependencies, persona configuration
- Schema supports TOON v3.0 format
- All TOON symbols (→, ⟷, ≠, ✓, ✗, ⚠️) converted to normalized forms

TOON v3.0 Symbols:
- → (U+2192): implies, leads to
- ⟷ (U+27F7): alternates, bidirectional
- ≠ (U+2260): not equal
- ✓ (U+2713): correct, checkmark
- ✗ (U+2717): wrong, X mark
- ⚠️ (U+26A0): warning

Parser guarantees:
- All sections parsed into structured dicts
- Metadata extracted from header and ID section
- Commands, dependencies, and persona sections normalized
- TOON symbols preserved or converted based on context
"""

from typing import TypedDict, Any, Literal, Required, NotRequired


class TOONMetadata(TypedDict, total=False):
    """Agent metadata from header and ID section

    Required fields: None (all metadata fields are optional since they depend on TOON file content)

    NotRequired fields explicitly marked for type checker clarity.
    """
    name: NotRequired[str]  # Agent display name (e.g., "Crafty", "Aria")
    id: NotRequired[str]  # Agent identifier (e.g., "software-crafter", "novel-editor")
    role: NotRequired[str]  # Agent role description
    spec: NotRequired[str]  # Specialization or domain
    model: NotRequired[str]  # Model configuration or requirements
    version: NotRequired[str]  # TOON format version (v1.0, v3.0)
    description: NotRequired[str]  # Brief description from header


class TOONSection(TypedDict, total=False):
    """Generic section content (key-value pairs, lists, nested structures)"""
    # Dynamic keys based on section content
    # Can contain: str, list, dict, or nested TOONSection


class TOONParserOutput(TypedDict):
    """Complete parser output structure for TOON agent files

    This is the contract between step 01-01 (parser) and step 01-02 (Jinja2 template).
    """
    # Core identification
    id: str  # Agent unique identifier (required)
    type: Literal['agent', 'command', 'skill']  # Content type for template selection

    # Metadata (from header and ID section)
    metadata: TOONMetadata

    # Structured content sections
    sections: dict[str, Any]  # All parsed sections (commands, rules, scenarios, etc.)

    # Source information
    source_file: str | None  # Original file path (if available)
    toon_version: str  # Detected TOON version (v1.0, v3.0)

    # Raw content (for debugging/validation)
    raw_content: str | None  # Original unparsed content (optional)


# Example parser output (documenting expected structure):
EXAMPLE_PARSER_OUTPUT: TOONParserOutput = {
    'id': 'software-crafter',
    'type': 'agent',
    'metadata': {
        'name': 'Crafty',
        'id': 'software-crafter',
        'role': 'Master Software Crafter',
        'spec': 'TDD, Refactoring, Quality',
        'model': 'claude-sonnet-4.5',
        'version': 'v3.0',
        'description': 'Unified Software Craftsmanship Specialist'
    },
    'sections': {
        'core_rules': {
            'evidence_only': 'Cite source for all claims',
            'no_quant_claims': 'No percentages/metrics without data',
            'confidence': 'HIGH/MED/LOW with justification'
        },
        'commands': [
            'develop',
            'refactor',
            'mikado'
        ],
        'dependencies': {
            'tasks': ['dw/develop.md', 'dw/mikado.md'],
            'templates': ['develop-outside-in-tdd.yaml']
        },
        'persona': {
            'role': 'Master Software Crafter',
            'style': 'Methodical, test-driven, quality-obsessed'
        }
    },
    'source_file': 'agents/software-crafter.toon',
    'toon_version': 'v3.0',
    'raw_content': None
}
