# Skill Data Structure Specification

## Overview

Skills are Claude Code Agent Skills that follow the official Anthropic specification. This document defines the parsed skill data structure for the TOON compiler.

**Format**: Claude Code native Agent Skills format with optional nWave extensions.

---

## Skill Data Structure (TypedDict)

```python
from typing import TypedDict, List, Optional

class SkillData(TypedDict, total=False):
    """Parsed skill data structure following Claude Code format.

    REQUIRED fields: name, description
    OPTIONAL fields: wave, phase, agents, version, content
    """

    # REQUIRED: Claude Code standard fields
    name: str  # Skill identifier (lowercase, hyphens: "develop", "refactor")
    description: str  # What skill does and when to use it (semantic matching)

    # OPTIONAL: nWave workflow metadata
    wave: Optional[str]  # nWave phase: DISCUSS, DESIGN, DEVELOP, DISTILL, DELIVER
    phase: Optional[int]  # Phase number (1-8)
    agents: Optional[List[str]]  # Agent IDs that can use this skill

    # OPTIONAL: Versioning
    version: Optional[str]  # Skill version (semver format)

    # OPTIONAL: Skill content
    content: Optional[str]  # Markdown content (instructions, guidelines, examples)
```

---

## Field Definitions

### `name` (REQUIRED)

- **Type**: `str`
- **Purpose**: Unique skill identifier for Claude Code discovery
- **Format**: Lowercase letters, numbers, hyphens only
- **Pattern**: `^[a-z][a-z0-9-]*$`
- **Examples**: `develop`, `refactor`, `design-architecture`, `tdd-implementation`

### `description` (REQUIRED)

- **Type**: `str`
- **Purpose**: Semantic matching for skill activation
- **Minimum length**: 50 characters
- **Content must include**:
  - What the skill does
  - When to use it
  - Key trigger terms users might mention

**Good description example**:
```yaml
description: |
  Use this skill when implementing features using test-driven development (TDD).
  Activates for: implementing features, writing tests first, outside-in TDD,
  red-green-refactor cycle, unit testing, integration testing.
```

**Bad description example**:
```yaml
description: A skill for development.  # Too vague, no activation triggers
```

### `wave` (OPTIONAL)

- **Type**: `Optional[str]`
- **Purpose**: nWave workflow phase assignment
- **Valid values**: `DISCUSS`, `DESIGN`, `DEVELOP`, `DISTILL`, `DELIVER`
- **Note**: Ignored by Claude Code runtime, used by nWave orchestrator

### `phase` (OPTIONAL)

- **Type**: `Optional[int]`
- **Purpose**: Phase number within wave
- **Valid values**: 1-8
- **Note**: Ignored by Claude Code runtime, used by nWave orchestrator

### `agents` (OPTIONAL)

- **Type**: `Optional[List[str]]`
- **Purpose**: Agent IDs that should use this skill
- **Examples**: `['software-crafter']`, `['solution-architect', 'software-crafter']`
- **Note**: Informational only; Claude Code skills are available to all agents

### `version` (OPTIONAL)

- **Type**: `Optional[str]`
- **Purpose**: Skill version tracking
- **Format**: Semver (X.Y.Z)
- **Examples**: `1.0.0`, `2.1.3`

### `content` (OPTIONAL)

- **Type**: `Optional[str]`
- **Purpose**: Full markdown content for the skill
- **Includes**: Instructions, guidelines, examples, references

---

## Parsing Examples

### Example 1: Minimal Skill (Required Fields Only)

```yaml
name: develop
description: |
  Use this skill when implementing features using test-driven development.
  Activates for: implementing features, TDD, outside-in testing,
  writing tests first, red-green-refactor cycle.
```

**Parsed SkillData**:
```python
{
    'name': 'develop',
    'description': 'Use this skill when implementing features using test-driven development.\nActivates for: implementing features, TDD, outside-in testing,\nwriting tests first, red-green-refactor cycle.'
}
```

### Example 2: Full Skill with nWave Metadata

```yaml
name: refactor
description: |
  Use this skill when refactoring code to improve quality.
  Activates for: refactoring, simplifying code, optimizing,
  Mikado method, extract method, rename variable.
wave: DEVELOP
phase: 4
agents:
  - software-crafter
  - solution-architect
version: 1.2.0
```

**Parsed SkillData**:
```python
{
    'name': 'refactor',
    'description': 'Use this skill when refactoring code to improve quality.\nActivates for: refactoring, simplifying code, optimizing,\nMikado method, extract method, rename variable.',
    'wave': 'DEVELOP',
    'phase': 4,
    'agents': ['software-crafter', 'solution-architect'],
    'version': '1.2.0'
}
```

---

## Validation Rules

### Required Field Validation

```python
import re

def validate_skill(skill_data: dict) -> bool:
    """Validate skill follows Claude Code format."""

    # 1. Required: name
    if 'name' not in skill_data:
        raise ValidationError("Missing required field: 'name'")

    name = skill_data['name']
    if not re.match(r'^[a-z][a-z0-9-]*$', name):
        raise ValidationError(
            f"Invalid name '{name}': must be lowercase with hyphens only"
        )

    # 2. Required: description
    if 'description' not in skill_data:
        raise ValidationError("Missing required field: 'description'")

    description = skill_data['description']
    if len(description) < 50:
        raise ValidationError(
            f"Description too short ({len(description)} chars). "
            "Must clearly explain what skill does and when to use it (min 50 chars)."
        )

    return True
```

### Optional Field Validation

```python
def validate_optional_fields(skill_data: dict) -> bool:
    """Validate optional nWave metadata if present."""

    # wave validation
    if 'wave' in skill_data:
        valid_waves = ['DISCUSS', 'DESIGN', 'DEVELOP', 'DISTILL', 'DELIVER']
        if skill_data['wave'] not in valid_waves:
            raise ValidationError(
                f"Invalid wave '{skill_data['wave']}'. "
                f"Must be one of: {valid_waves}"
            )

    # phase validation
    if 'phase' in skill_data:
        phase = skill_data['phase']
        if not isinstance(phase, int) or not (1 <= phase <= 8):
            raise ValidationError(
                f"Invalid phase '{phase}'. Must be integer 1-8."
            )

    # agents validation
    if 'agents' in skill_data:
        agents = skill_data['agents']
        if not isinstance(agents, list):
            raise ValidationError("agents must be a list")
        if not all(isinstance(a, str) for a in agents):
            raise ValidationError("agents must be list of strings")

    # version validation (semver)
    if 'version' in skill_data:
        version = skill_data['version']
        if not re.match(r'^\d+\.\d+\.\d+$', version):
            raise ValidationError(
                f"Invalid version '{version}'. Must be semver (X.Y.Z)."
            )

    return True
```

---

## TOON Skill File Format

TOON skill files use YAML format:

```yaml
# Required fields
name: skill-name
description: |
  Detailed description of what the skill does.
  Include when to use it and key activation terms.

# Optional nWave metadata
wave: DEVELOP
phase: 3
agents:
  - software-crafter
version: 1.0.0

# Optional content (can also be in separate section)
content: |
  # Skill Title

  Instructions and guidelines...

  ## Examples
  - Example 1
  - Example 2
```

---

## Output Format: SKILL.md

The compiler generates Claude Code compatible SKILL.md:

```markdown
---
name: skill-name
description: |
  Detailed description...
wave: DEVELOP
phase: 3
agents:
  - software-crafter
version: 1.0.0
---

# Skill Title

[Content from skill definition or generated template]

## Guidelines
...

## Examples
...
```

---

## Integration Points

- **Parser Output**: Step 01-01 produces `SkillData` objects
- **Template Input**: Step 01-04 Jinja2 template receives `SkillData` and renders SKILL.md
- **Compiler**: Step 01-05 routes `type='skill'` to skill template
- **Output Location**: `.claude/skills/{name}/SKILL.md`

---

## Migration from Old Format

### Field Mapping

| Old Field | New Field | Conversion |
|-----------|-----------|------------|
| `id` | `name` | Direct (ensure lowercase, hyphens) |
| `triggers` | `description` | Convert patterns to semantic text |
| `agent_association` | `agents` | Rename, keep as list |
| `workflow_integration.wave` | `wave` | Flatten to top-level |
| `workflow_integration.phase` | `phase` | Flatten to top-level |

### Trigger Conversion Example

**Old**:
```yaml
triggers:
  - implement.*
  - TDD
  - outside-in
```

**New**:
```yaml
description: |
  Use this skill when implementing features using TDD.
  Activates for: implementing features, TDD, outside-in testing.
```

---

## Version History

- **v2.0** (2026-01-14): Aligned with Claude Code native format
  - Changed required fields to `name` and `description`
  - Removed `triggers` (converted to semantic description)
  - Renamed `agent_association` to `agents`
  - Flattened `workflow_integration` to `wave` and `phase`
  - Simplified validation rules

- **v1.1** (2026-01-14): Added TOONParserOutput mapping (superseded)

- **v1.0** (2026-01-14): Initial specification (superseded)
