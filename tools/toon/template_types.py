"""Domain types for TOON template rendering

Level 4 Refactoring: Type-Driven Design with Business Types

Business concepts:
- AgentTemplateData: Complete template input (replaces raw dict)
- YAMLSafeValue: Automatically escaped YAML values (replaces string + escape logic)
- AgentCommand: Command with name and description (replaces dict entries)
- EmbeddedKnowledgeMarker: Build injection marker (replaces string template)
- AgentMetadata: Agent identity and configuration (enhances TOONMetadata)

Type system goals:
1. Invalid states non-representable (e.g., command without name)
2. Type constructors validate business rules
3. Business language throughout (Agent, Command, not dict, str)
4. Compile-time guarantees through frozen dataclasses
"""

from dataclasses import dataclass
from typing import TypedDict, Required, NotRequired


# ============================================================================
# DOMAIN TYPE 1: YAML-Safe Value (replaces escape_yaml_value logic)
# ============================================================================

@dataclass(frozen=True)
class YAMLSafeValue:
    """YAML-safe value with automatic escaping

    Business concept: String value that is guaranteed safe for YAML frontmatter

    Type guarantee: Once constructed, value is always properly escaped
    No need to call escape function - type ensures safety

    Escapes:
    - Colons (:) in values
    - Quotes (single and double)
    - Newlines (\n)
    - Hash (#) at start
    - Ampersand (&), Asterisk (*), Brackets, Braces
    """
    raw_value: str | None

    @property
    def yaml_safe(self) -> str:
        """Returns YAML-safe representation for frontmatter rendering

        Called by template: {{ yaml_value.yaml_safe }}
        """
        if self.raw_value is None:
            return "null"

        value = self.raw_value

        # Check if escaping needed
        needs_escape = (
            ':' in value or
            '"' in value or
            "'" in value or
            '\n' in value or
            value.startswith('#') or
            value.startswith('&') or
            value.startswith('*') or
            value.startswith('[') or
            value.startswith('{')
        )

        if needs_escape:
            # Escape quotes and newlines, wrap in double quotes
            escaped = value.replace('"', '\\"').replace('\n', '\\n')
            return f'"{escaped}"'

        return value


# ============================================================================
# DOMAIN TYPE 2: Agent Command (replaces dict with cmd: desc)
# ============================================================================

@dataclass(frozen=True)
class AgentCommand:
    """Agent command with name and description

    Business concept: Agent capability invoked by user via command

    Type guarantee: Command always has name and description
    Invalid state non-representable: Cannot create command without both

    Examples:
    - AgentCommand("develop", "Execute TDD workflow")
    - AgentCommand("refactor", "Apply systematic refactoring")
    """
    name: str
    description: str

    def __post_init__(self):
        """Validate business rules at construction"""
        if not self.name or not self.name.strip():
            raise ValueError("Command name cannot be empty")
        if not self.description or not self.description.strip():
            raise ValueError("Command description cannot be empty")


# ============================================================================
# DOMAIN TYPE 3: Embedded Knowledge Marker (replaces string templates)
# ============================================================================

@dataclass(frozen=True)
class EmbeddedKnowledgeMarker:
    """Build injection marker for embedded knowledge

    Business concept: Placeholder for build-time content injection

    Type guarantee: Marker always has valid file path
    Format: <!-- BUILD:INJECT:START:path/to/file.md -->

    Examples:
    - EmbeddedKnowledgeMarker("5d-wave/data/embed/agent/README.md")
    - Renders to: <!-- BUILD:INJECT:START:5d-wave/data/embed/agent/README.md -->
    """
    file_path: str

    def __post_init__(self):
        """Validate business rules at construction"""
        if not self.file_path or not self.file_path.strip():
            raise ValueError("Embedded knowledge file path cannot be empty")

    @property
    def start_marker(self) -> str:
        """Build injection start marker"""
        return f"<!-- BUILD:INJECT:START:{self.file_path} -->"

    @property
    def end_marker(self) -> str:
        """Build injection end marker"""
        return "<!-- BUILD:INJECT:END -->"


# ============================================================================
# DOMAIN TYPE 4: Agent Metadata (enhanced TOONMetadata with validation)
# ============================================================================

class AgentMetadata(TypedDict, total=False):
    """Agent identity and configuration metadata

    Business concept: Agent identity (name, ID, role) and runtime config (model)

    Enhanced from TOONMetadata with explicit required/optional distinction
    All fields optional at type level (depend on TOON file content)
    """
    name: NotRequired[str]  # Agent display name
    id: NotRequired[str]  # Agent identifier
    role: NotRequired[str]  # Agent role description
    spec: NotRequired[str]  # Specialization domain
    model: NotRequired[str]  # Model configuration
    version: NotRequired[str]  # TOON version
    description: NotRequired[str]  # Brief description


# ============================================================================
# DOMAIN TYPE 5: Agent Template Data (replaces raw dict input)
# ============================================================================

class AgentTemplateData(TypedDict):
    """Complete input data for agent template rendering

    Business concept: All information needed to render agent.md from TOON

    Type guarantee: Template receives validated, structured input
    Replaces: Passing raw dict with implicit structure

    Structure matches TOON parser output (parser_schema.TOONParserOutput)
    """
    # Core identification (required)
    id: Required[str]
    type: Required[str]  # 'agent', 'command', 'skill'

    # Agent metadata (optional fields handled by AgentMetadata)
    metadata: Required[AgentMetadata]

    # Structured sections (commands, dependencies, persona, etc.)
    sections: Required[dict]

    # Source information (optional)
    source_file: NotRequired[str | None]
    toon_version: NotRequired[str]
    raw_content: NotRequired[str | None]


# ============================================================================
# HELPER FUNCTIONS: Construct domain types from parser output
# ============================================================================

def create_commands_from_dict(commands_dict: dict[str, str]) -> list[AgentCommand]:
    """Convert commands dict to list of AgentCommand domain types

    Business logic: Transform parser output into domain model

    Args:
        commands_dict: Dict mapping command names to descriptions
                      Example: {"develop": "Execute TDD", "refactor": "Apply refactoring"}

    Returns:
        List of AgentCommand instances

    Raises:
        ValueError: If command name or description empty
    """
    return [
        AgentCommand(name=name, description=desc)
        for name, desc in commands_dict.items()
    ]


def create_embed_markers(embed_paths: list[str]) -> list[EmbeddedKnowledgeMarker]:
    """Convert embed file paths to EmbeddedKnowledgeMarker domain types

    Business logic: Transform parser output into domain model

    Args:
        embed_paths: List of file paths for embedded knowledge
                    Example: ["5d-wave/data/embed/agent/README.md"]

    Returns:
        List of EmbeddedKnowledgeMarker instances

    Raises:
        ValueError: If file path empty
    """
    return [
        EmbeddedKnowledgeMarker(file_path=path)
        for path in embed_paths
    ]


def escape_yaml_value(value: str | None) -> YAMLSafeValue:
    """Create YAMLSafeValue domain type from raw string

    Business logic: Ensure string is safe for YAML frontmatter

    Args:
        value: Raw string value (may contain YAML special characters)

    Returns:
        YAMLSafeValue with automatic escaping
    """
    return YAMLSafeValue(raw_value=value)
