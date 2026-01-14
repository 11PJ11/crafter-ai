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

- **Parser Output**: Step 01-01 produces `SkillData` objects
- **Template Input**: Step 01-04 Jinja2 template receives `SkillData` objects and renders to SKILL.md
- **Compiler**: Step 01-05 uses `type` field to route skill data to skill template
- **Integration Tests**: Step 01-06 validates parsed skill data matches schema before rendering

## Version History

- **v1.0** (2026-01-14): Initial specification with basic skill structure, single/multi-agent binding, workflow integration
