# Skills Architecture - Claude Code Native Format

## Executive Summary

nWave skills follow the **Claude Code Agent Skills** specification from Anthropic for full ecosystem compatibility.

**Key Decision**: Adopt Claude Code native format (no custom nWave format).

**Critical Definitions**:
1. ✅ Skill data structure (DEFINED in skill-data-structure.md)
2. ✅ Skill markdown format (DEFINED in skill-markdown-format.md)
3. ✅ Runtime integration (DEFINED in skill-runtime-integration.md)
4. ✅ Semantic activation (THIS DOCUMENT)
5. ✅ nWave metadata extensions (THIS DOCUMENT)

---

## 1. Claude Code Skills Overview

### Official Specification

**Source**: [Anthropic Agent Skills](https://github.com/anthropics/skills)

### Core Concepts

1. **Skills are directories** containing a SKILL.md file
2. **YAML frontmatter** with `name` and `description` (required)
3. **Semantic matching** on description (no regex patterns)
4. **Automatic discovery** by Claude Code runtime
5. **Hot reload** support in Claude Code 2.1.0+

### Activation Flow

```
User Request
    ↓
Claude Code scans skill descriptions
    ↓
Semantic matching determines relevance
    ↓
Relevant skill content loaded into context
    ↓
Claude follows skill instructions
```

---

## 2. Skill Format

### Required Fields

| Field | Type | Purpose |
|-------|------|---------|
| `name` | string | Unique identifier (lowercase, hyphens) |
| `description` | string | Semantic matching for activation |

### Optional Fields (nWave Extensions)

| Field | Type | Purpose |
|-------|------|---------|
| `wave` | string | nWave phase (DISCUSS/DESIGN/DEVELOP/DISTILL/DELIVER) |
| `phase` | int | Phase number (1-8) |
| `agents` | list | Agent IDs for documentation |
| `version` | string | Skill version (semver) |

### SKILL.md Structure

```markdown
---
name: skill-name
description: |
  Clear description of what this skill does.
  Include when to use it and key activation terms.
wave: DEVELOP
phase: 3
agents:
  - software-crafter
version: 1.0.0
---

# Skill Title

[Instructions Claude follows when skill is active]

## When to Use
- Scenario 1
- Scenario 2

## Guidelines
1. Step 1
2. Step 2

## Examples
- Example request 1
- Example request 2
```

---

## 3. Semantic Activation (Description-Based)

### How It Works

Claude Code uses **semantic matching** on the `description` field:

1. All skill descriptions are loaded into Claude's system prompt
2. When user makes a request, Claude evaluates semantic similarity
3. Skills with relevant descriptions are loaded into context
4. Claude follows the skill instructions

### Writing Effective Descriptions

**DO**:
- Clearly state what the skill does
- List specific scenarios/keywords that should trigger activation
- Use natural language that matches how users would phrase requests

**DON'T**:
- Use vague descriptions
- Rely on regex patterns (not supported)
- Write technical jargon users wouldn't use

### Examples

```yaml
# GOOD - Clear activation triggers
description: |
  Use this skill when implementing features using test-driven development.
  Activates for: implementing features, TDD, outside-in testing,
  writing tests first, red-green-refactor cycle, unit testing.

# BAD - Too vague
description: |
  A development skill.

# GOOD - Specific scenarios
description: |
  Use this skill when refactoring code to improve quality.
  Activates for: refactoring, code cleanup, extract method, rename variable,
  Mikado method, simplifying code, reducing complexity.
```

### Migration from Regex Triggers

Old trigger patterns should be converted to semantic descriptions:

| Old Pattern | New Description |
|-------------|-----------------|
| `implement.*` | "Use when implementing features" |
| `TDD` | "Use for test-driven development (TDD)" |
| `refactor.*` | "Use when refactoring code" |
| `design.*arch` | "Use when designing architecture" |

---

## 4. nWave Workflow Integration

### Optional Metadata

nWave-specific fields are stored in YAML frontmatter but **ignored by Claude Code runtime**:

```yaml
---
name: develop
description: |
  Use when implementing features with TDD...
# nWave metadata (optional, for workflow orchestration)
wave: DEVELOP
phase: 3
agents:
  - software-crafter
---
```

### Phase Definitions

Each wave has 8 phases:

#### DEVELOP Wave Phases

| Phase | Name | Purpose |
|-------|------|---------|
| 1 | Outer Test (Red) | Write failing acceptance test |
| 2 | Inner Test (Red) | Write failing unit test |
| 3 | Implementation (Green) | Write minimal code to pass |
| 4 | Refactor (Blue) | Improve code quality |
| 5 | Integration | Integrate with codebase |
| 6 | Code Review | Peer review |
| 7 | Documentation | Update docs |
| 8 | Handoff | Package for testing |

#### Other Waves

See skill-runtime-integration.md for full phase definitions for:
- DISCUSS (Requirements gathering)
- DESIGN (Architecture)
- DISTILL (Acceptance testing)
- DELIVER (Deployment)

---

## 5. Directory Structure

### Claude Code Standard Location

```
project/
└── .claude/
    └── skills/
        ├── develop/
        │   └── SKILL.md
        ├── refactor/
        │   └── SKILL.md
        └── design-architecture/
            └── SKILL.md
```

### User-Level Skills

```
~/.claude/
└── skills/
    └── my-custom-skill/
        └── SKILL.md
```

---

## 6. Validation Rules

### Required Validation

```python
import re

def validate_skill(data: dict) -> bool:
    """Validate Claude Code skill format."""

    # Required: name
    if 'name' not in data:
        raise ValidationError("Missing 'name'")

    if not re.match(r'^[a-z][a-z0-9-]*$', data['name']):
        raise ValidationError(f"Invalid name: {data['name']}")

    # Required: description
    if 'description' not in data:
        raise ValidationError("Missing 'description'")

    if len(data['description']) < 50:
        raise ValidationError("Description too short (min 50 chars)")

    return True
```

### Optional nWave Validation

```python
def validate_nwave_metadata(data: dict) -> bool:
    """Validate optional nWave fields."""

    if 'wave' in data:
        valid = ['DISCUSS', 'DESIGN', 'DEVELOP', 'DISTILL', 'DELIVER']
        if data['wave'] not in valid:
            raise ValidationError(f"Invalid wave: {data['wave']}")

    if 'phase' in data:
        if not isinstance(data['phase'], int) or not (1 <= data['phase'] <= 8):
            raise ValidationError(f"Invalid phase: {data['phase']}")

    return True
```

---

## 7. Benefits of Native Format

| Aspect | Benefit |
|--------|---------|
| **Ecosystem** | Full Claude Code plugin/marketplace compatibility |
| **Discovery** | Automatic by Claude Code runtime |
| **Hot Reload** | Instant updates without restart |
| **Simplicity** | Single format to maintain |
| **Future-proof** | Aligned with Anthropic's official spec |
| **No Regex** | Semantic matching is more flexible and user-friendly |

---

## 8. Impact on Phase 1 Steps

### Step 01-04: Create Skill Jinja2 Template

**Requirements**:
- Generate Claude Code compatible SKILL.md
- Required fields: `name`, `description`
- Optional fields: `wave`, `phase`, `agents`, `version`
- Output to `.claude/skills/{name}/SKILL.md`

### Step 01-05: TOON Compiler

**Requirements**:
- Route `type='skill'` to skill template
- Write to `.claude/skills/` directory
- Validate output format

### Step 01-06: Integration Tests

**Requirements**:
- Validate SKILL.md follows Claude Code format
- Test YAML frontmatter parsing
- Verify semantic description quality

---

## Version History

- **v2.0** (2026-01-14): Aligned with Claude Code native format
  - Removed regex trigger patterns (replaced with semantic description)
  - Removed dual-format strategy
  - Removed agent association binding (skills available to all agents)
  - Simplified to `name` + `description` required fields
  - Added nWave metadata as optional extensions

- **v1.1** (2026-01-14): Added regex safeguards (superseded)

- **v1.0** (2026-01-14): Initial specification (superseded)
