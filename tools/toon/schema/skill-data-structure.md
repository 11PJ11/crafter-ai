# Skill Data Structure Specification

## Overview

Skills are workflow automation capabilities that trigger based on context patterns and bind to agents. This document defines the parsed skill data structure produced by the TOON parser (step 01-01).

## Skill Data Structure (TypedDict)

```python
from typing import TypedDict, Literal, List, Dict, Optional

class SkillData(TypedDict):
    """Parsed skill data structure from TOON parser.

    CRITICAL: All fields are REQUIRED unless marked Optional.
    Parser MUST validate and raise ValidationError if required fields missing.
    """

    # REQUIRED: Identity and metadata
    id: str  # Unique skill identifier (e.g., 'develop', 'refactor')
    name: str  # Human-readable skill name (e.g., 'TDD Development')
    type: Literal['skill']  # File type discriminator - always 'skill' for skills

    # REQUIRED: Core skill data
    triggers: List[str]  # Regex patterns that activate skill (YAML list format)
    agent_association: str | List[str]  # Agent ID(s) this skill binds to (1:1, 1:N, or N:M)

    # REQUIRED: Workflow integration
    workflow_integration: Dict[str, any]  # Integration metadata with required fields:
        # MUST contain:
        # - wave: str (nWave phase: DISCUSS, DESIGN, DEVELOP, DISTILL, DELIVER)
        # - phase: int (phase number within wave)
        # - context: Optional[str] (execution context/scope)

    # OPTIONAL: Extended metadata
    description: Optional[str]  # Skill description (max 500 chars)
    version: Optional[str]  # Skill version (semver format)
    metadata: Optional[Dict[str, any]]  # Additional metadata
```

## Field Definitions

### `id` (REQUIRED)
- Type: `str`
- Purpose: Unique skill identifier
- Constraints:
  - Must match pattern: `^[a-z_][a-z0-9_]*$` (lowercase, underscores, alphanumeric)
  - Must be unique across all skills in project
  - Used as directory name: `dist/skills/{id}/SKILL.md`
- Example: `'develop'`, `'refactor'`, `'tdd_cycle'`

### `name` (REQUIRED)
- Type: `str`
- Purpose: Human-readable skill name for UI/documentation
- Constraints:
  - Max 100 characters
  - Should be title case
  - Should be descriptive and concise
- Example: `'TDD Development'`, `'Code Refactoring'`

### `type` (REQUIRED)
- Type: `Literal['skill']`
- Purpose: File type discriminator for template selection
- Value: Must always be `'skill'` for skill files
- Note: Parser uses this field to route to skill template (01-02), not agent (01-02a) or command (01-03)

### `triggers` (REQUIRED)
- Type: `List[str]`
- Purpose: Regex patterns that activate/invoke the skill
- Constraints:
  - Must be non-empty list (at least 1 trigger required)
  - Each item must be valid regex pattern
  - Patterns are case-insensitive in execution
  - Special characters must be escaped for YAML
- Semantics:
  - Pattern matching happens against task description or user input
  - Multiple patterns = OR logic (skill activates if ANY pattern matches)
  - Patterns evaluated at runtime, not by template
- Examples:
  ```python
  triggers=['implement.*', 'coding.*', 'TDD', 'outside-in']
  triggers=['refactor.*', 'simplify', 'optimize']
  triggers=['document.*', 'write.*docs']
  ```

### `agent_association` (REQUIRED)
- Type: `str | List[str]`
- Purpose: Agent(s) that can execute this skill
- Cardinality:
  - 1:1 mode: Single agent ID string - `'software-crafter'`
  - 1:N mode: Multiple agents - `['software-crafter', 'solution-architect']`
  - N:M mode: Multi-agent binding with permissions (future extension)
- Semantics:
  - Skill is ONLY available to agents listed
  - At runtime, agent ID is checked against agent_association before execution
  - Multiple agents = skill available to all listed agents
- Constraints:
  - Must reference existing agent (validation deferred to runtime or integration test)
  - Case-sensitive (matches exact agent ID)
- Examples:
  ```python
  agent_association='software-crafter'
  agent_association=['software-crafter', 'solution-architect', 'product-owner']
  ```

### `workflow_integration` (REQUIRED)
- Type: `Dict[str, any]`
- Purpose: Integration metadata for nWave workflow system
- Required Sub-fields:
  ```python
  {
      'wave': str,  # nWave phase (DISCUSS, DESIGN, DEVELOP, DISTILL, DELIVER)
      'phase': int,  # Phase number within wave (1-8)
      'context': Optional[str]  # Execution context/scope (e.g., 'refactoring', 'testing')
  }
  ```
- Examples:
  ```python
  workflow_integration={
      'wave': 'DEVELOP',
      'phase': 3,
      'context': 'TDD cycle'
  }

  workflow_integration={
      'wave': 'DISTILL',
      'phase': 4,
      'context': 'acceptance testing'
  }
  ```

### `description` (OPTIONAL)
- Type: `Optional[str]`
- Purpose: Extended skill description for documentation
- Constraints: Max 500 characters
- Default: `None` (if missing, template uses empty string)

### `version` (OPTIONAL)
- Type: `Optional[str]`
- Purpose: Skill semantic version
- Format: Semver (X.Y.Z)
- Default: `None`

### `metadata` (OPTIONAL)
- Type: `Optional[Dict[str, any]]`
- Purpose: Additional skill metadata (extensible)
- Examples:
  - `{'tags': ['testing', 'automation']}`
  - `{'priority': 'high'}`
  - `{'max_concurrent': 2}`

## Parsing Examples

### Example 1: Simple Single-Agent Skill
```python
# Input TOON file content
id: develop
name: TDD Development
type: skill
triggers:
  - implement.*
  - TDD
  - outside-in
agent_association: software-crafter
workflow_integration:
  wave: DEVELOP
  phase: 3
  context: TDD cycle

# Parsed SkillData
{
    'id': 'develop',
    'name': 'TDD Development',
    'type': 'skill',
    'triggers': ['implement.*', 'TDD', 'outside-in'],
    'agent_association': 'software-crafter',
    'workflow_integration': {
        'wave': 'DEVELOP',
        'phase': 3,
        'context': 'TDD cycle'
    }
}
```

### Example 2: Multi-Agent Skill with Metadata
```python
# Input TOON file
id: refactor
name: Code Refactoring
type: skill
description: Systematic code refactoring using Mikado Method
triggers:
  - refactor.*
  - simplify.*
  - optimize
version: 1.2.0
agent_association:
  - software-crafter
  - solution-architect
workflow_integration:
  wave: DEVELOP
  phase: 5
  context: refactoring improvement
metadata:
  tags: [refactoring, optimization, design]
  priority: high

# Parsed SkillData
{
    'id': 'refactor',
    'name': 'Code Refactoring',
    'type': 'skill',
    'description': 'Systematic code refactoring using Mikado Method',
    'triggers': ['refactor.*', 'simplify.*', 'optimize'],
    'version': '1.2.0',
    'agent_association': ['software-crafter', 'solution-architect'],
    'workflow_integration': {
        'wave': 'DEVELOP',
        'phase': 5,
        'context': 'refactoring improvement'
    },
    'metadata': {
        'tags': ['refactoring', 'optimization', 'design'],
        'priority': 'high'
    }
}
```

## Validation Rules

Parser MUST enforce:

1. **REQUIRED fields present**: `id`, `name`, `type`, `triggers`, `agent_association`, `workflow_integration`
2. **Type validation**:
   - `type` must be exactly `'skill'`
   - `triggers` must be list (never string)
   - `agent_association` must be string or list of strings
   - `workflow_integration` must be dict with 'wave' and 'phase'
3. **Value validation**:
   - `id` matches pattern `^[a-z_][a-z0-9_]*$`
   - `triggers` non-empty (at least 1 pattern)
   - `triggers` items are valid regex patterns
   - `workflow_integration.wave` in ['DISCUSS', 'DESIGN', 'DEVELOP', 'DISTILL', 'DELIVER']
   - `workflow_integration.phase` in [1, 2, 3, 4, 5, 6, 7, 8]
4. **Uniqueness**: `id` must be unique across all skills
5. **Character escaping**: Special YAML characters in field values must be properly escaped

## Error Handling

Parser should raise `ValidationError` with context:
```python
# Example 1: Missing required field
ValidationError("Skill 'unknown-id': missing required field 'triggers'")

# Example 2: Invalid type
ValidationError("Skill 'develop': type='task' (expected 'skill')")

# Example 3: Invalid trigger pattern
ValidationError("Skill 'develop': trigger pattern '[invalid-regex' is not valid regex (error: unterminated character set)")

# Example 4: Invalid workflow_integration
ValidationError("Skill 'develop': workflow_integration.wave='unknown' (must be one of: DISCUSS, DESIGN, DEVELOP, DISTILL, DELIVER)")
```

## Integration Points

- **Parser Output**: Step 01-01 produces `TOONParserOutput`, converted to `SkillData` via mapping function
- **Template Input**: Step 01-04 Jinja2 template receives `SkillData` objects and renders to SKILL.md
- **Compiler**: Step 01-05 uses `type` field to route skill data to skill template
- **Integration Tests**: Step 01-06 validates parsed skill data matches schema before rendering

---

## TOONParserOutput → SkillData Mapping

### Overview

The TOON parser produces a generic `TOONParserOutput` structure. When `type='skill'`, this output
must be converted to the specialized `SkillData` structure before template rendering.

### Mapping Function

```python
from typing import Union, List, Dict, Any
from tools.toon.parser_schema import TOONParserOutput

def toon_output_to_skill_data(parser_output: TOONParserOutput) -> SkillData:
    """Convert generic TOONParserOutput to SkillData.

    Args:
        parser_output: Generic parser output with type='skill'

    Returns:
        SkillData: Specialized skill data structure

    Raises:
        ValueError: If type is not 'skill'
        ValidationError: If required skill fields are missing
    """
    if parser_output['type'] != 'skill':
        raise ValueError(
            f"Expected type='skill', got type='{parser_output['type']}'"
        )

    sections = parser_output['sections']
    metadata = parser_output['metadata']

    # Extract required fields
    skill_data: SkillData = {
        'id': parser_output['id'],
        'name': _extract_required(sections, 'name', metadata.get('name', '')),
        'type': 'skill',
        'triggers': _extract_triggers(sections),
        'agent_association': _extract_agent_association(sections),
        'workflow_integration': _extract_workflow_integration(sections),
    }

    # Add optional fields if present
    if 'description' in sections or 'description' in metadata:
        skill_data['description'] = sections.get(
            'description', metadata.get('description')
        )

    if 'version' in sections or 'version' in metadata:
        skill_data['version'] = sections.get(
            'version', metadata.get('version')
        )

    if 'metadata' in sections:
        skill_data['metadata'] = sections['metadata']

    return skill_data


def _extract_required(sections: Dict, key: str, fallback: str) -> str:
    """Extract required field with fallback."""
    value = sections.get(key, fallback)
    if not value:
        raise ValidationError(f"Missing required field: '{key}'")
    return value


def _extract_triggers(sections: Dict) -> List[str]:
    """Extract and validate trigger patterns."""
    triggers = sections.get('triggers', [])

    if not triggers:
        raise ValidationError("Skill must have at least one trigger pattern")

    if isinstance(triggers, str):
        triggers = [triggers]

    if not isinstance(triggers, list):
        raise ValidationError(
            f"triggers must be list, got {type(triggers).__name__}"
        )

    # Validate each pattern is valid regex
    for pattern in triggers:
        try:
            re.compile(pattern, re.IGNORECASE)
        except re.error as e:
            raise ValidationError(
                f"Invalid trigger pattern '{pattern}': {e}"
            )

    return triggers


def _extract_agent_association(sections: Dict) -> Union[str, List[str]]:
    """Extract agent association (1:1 or 1:N)."""
    assoc = sections.get('agent_association')

    if assoc is None:
        raise ValidationError("Missing required field: 'agent_association'")

    if isinstance(assoc, str):
        return assoc  # 1:1 mode

    if isinstance(assoc, list):
        if not assoc:
            raise ValidationError("agent_association list cannot be empty")
        return assoc  # 1:N mode

    raise ValidationError(
        f"agent_association must be str or list, got {type(assoc).__name__}"
    )


def _extract_workflow_integration(sections: Dict) -> Dict[str, Any]:
    """Extract and validate workflow integration."""
    wi = sections.get('workflow_integration')

    if wi is None:
        raise ValidationError("Missing required field: 'workflow_integration'")

    if not isinstance(wi, dict):
        raise ValidationError(
            f"workflow_integration must be dict, got {type(wi).__name__}"
        )

    # Validate required sub-fields
    if 'wave' not in wi:
        raise ValidationError(
            "workflow_integration missing required field: 'wave'"
        )

    if 'phase' not in wi:
        raise ValidationError(
            "workflow_integration missing required field: 'phase'"
        )

    # Validate wave value
    valid_waves = ['DISCUSS', 'DESIGN', 'DEVELOP', 'DISTILL', 'DELIVER']
    if wi['wave'] not in valid_waves:
        raise ValidationError(
            f"Invalid wave '{wi['wave']}', must be one of: {valid_waves}"
        )

    # Validate phase value
    if not isinstance(wi['phase'], int) or not (1 <= wi['phase'] <= 8):
        raise ValidationError(
            f"Invalid phase '{wi['phase']}', must be integer 1-8"
        )

    return wi
```

### Field Mapping Table

| TOONParserOutput | Location | SkillData | Notes |
|------------------|----------|-----------|-------|
| `id` | root | `id` | Direct mapping |
| `type` | root | `type` | Must be 'skill' |
| `metadata.name` | metadata | `name` (fallback) | Fallback if not in sections |
| `metadata.description` | metadata | `description` (fallback) | Optional |
| `metadata.version` | metadata | `version` (fallback) | Optional |
| `sections.name` | sections | `name` | Primary source |
| `sections.description` | sections | `description` | Optional |
| `sections.triggers` | sections | `triggers` | REQUIRED |
| `sections.agent_association` | sections | `agent_association` | REQUIRED |
| `sections.workflow_integration` | sections | `workflow_integration` | REQUIRED |
| `sections.version` | sections | `version` | Optional |
| `sections.metadata` | sections | `metadata` | Optional dict |

### TOON Skill File Format

For the mapping to work, TOON skill files must follow this structure:

```yaml
# TOON Skill File Format
id: develop
type: skill
name: TDD Development

triggers:
  - implement.*
  - TDD
  - outside-in

agent_association: software-crafter

workflow_integration:
  wave: DEVELOP
  phase: 3
  context: TDD cycle

# Optional fields
description: |
  Systematic test-driven development approach
  with outside-in TDD methodology

version: 1.0.0

metadata:
  tags: [testing, automation]
  priority: high
```

### Usage in Compiler

```python
# In compiler.py (step 01-05)
from tools.toon.parser import parse_toon_file
from tools.toon.schema.skill_mapping import toon_output_to_skill_data

def compile_skill(toon_file: str, output_dir: str) -> str:
    """Compile TOON skill file to SKILL.md."""
    # Step 1: Parse TOON file
    parser_output = parse_toon_file(toon_file)

    # Step 2: Validate and convert to SkillData
    if parser_output['type'] != 'skill':
        raise ValueError(f"Expected skill file, got {parser_output['type']}")

    skill_data = toon_output_to_skill_data(parser_output)

    # Step 3: Render template
    template = load_template('skill.md.j2')
    output = template.render(skill=skill_data)

    # Step 4: Write output
    output_path = f"{output_dir}/{skill_data['id']}/SKILL.md"
    write_file(output_path, output)

    return output_path
```

---

## Version History

- **v1.1** (2026-01-14): Opus review resolutions
  - Added TOONParserOutput → SkillData mapping function and validation
  - Added field mapping table for parser integration
  - Added TOON skill file format specification
  - Added compiler usage example

- **v1.0** (2026-01-14): Initial specification with basic skill structure, single/multi-agent binding, workflow integration
