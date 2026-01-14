# Skill Runtime Integration - Claude Code Native Format

## Executive Summary

nWave skills adopt the **Claude Code native Agent Skills format** for full compatibility with the Claude Code ecosystem.

**Decision**: Single format aligned with Claude Code specification (no custom nWave format).

---

## 1. Claude Code Agent Skills Format

### Official Specification

**Source**: [Anthropic Agent Skills](https://github.com/anthropics/skills), [Engineering Blog](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)

### SKILL.md Structure

```markdown
---
name: skill-name
description: |
  A clear description of what this skill does and when to use it.
  Claude uses this description for semantic matching to determine
  when to activate the skill.
---

# Skill Title

[Instructions that Claude follows when skill is active]

## Guidelines
- Guideline 1
- Guideline 2

## Examples
- Example usage 1
- Example usage 2
```

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Unique skill identifier (lowercase, hyphens) |
| `description` | string | What the skill does and when to use it |

### Optional Fields (nWave Extensions)

These fields are **optional** and used internally by nWave for workflow orchestration:

| Field | Type | Description |
|-------|------|-------------|
| `wave` | string | nWave phase (DISCUSS/DESIGN/DEVELOP/DISTILL/DELIVER) |
| `phase` | int | Phase number (1-8) |
| `agents` | list | Agent IDs that can use this skill |
| `version` | string | Skill version (semver) |

---

## 2. Activation Mechanism

### Claude Code Semantic Matching

Claude Code uses **semantic matching** on the `description` field:

1. User makes a request
2. Claude reads all skill descriptions from system prompt
3. Claude determines which skills are relevant based on semantic similarity
4. Relevant skills are loaded into context

**No regex patterns**. The `description` field must clearly explain:
- What the skill does
- When it should be activated
- Key trigger terms users might mention

### Writing Effective Descriptions

```yaml
# GOOD - Clear activation triggers in description
description: |
  Use this skill when implementing features using test-driven development (TDD).
  Activates for: implementing features, writing tests first, outside-in TDD,
  red-green-refactor cycle, unit testing, integration testing.

# BAD - Vague description
description: |
  A skill for development tasks.
```

---

## 3. Directory Structure

### Skill Location

Skills are placed in standard Claude Code locations:

```
project/
├── .claude/
│   └── skills/
│       ├── develop/
│       │   └── SKILL.md
│       ├── refactor/
│       │   └── SKILL.md
│       └── research/
│           └── SKILL.md
```

### User-Level Skills

```
~/.claude/
└── skills/
    └── my-custom-skill/
        └── SKILL.md
```

---

## 4. Complete Example

### TOON Source → Claude Code SKILL.md

**Input** (TOON skill definition):
```yaml
id: develop
name: TDD Development
description: |
  Systematic test-driven development for implementing features.
  Use when: implementing features, TDD, outside-in testing,
  red-green-refactor, writing tests first.
wave: DEVELOP
phase: 3
agents:
  - software-crafter
version: 1.0.0
```

**Output** (`.claude/skills/develop/SKILL.md`):
```markdown
---
name: develop
description: |
  Systematic test-driven development for implementing features.
  Use when: implementing features, TDD, outside-in testing,
  red-green-refactor, writing tests first.
wave: DEVELOP
phase: 3
agents:
  - software-crafter
version: 1.0.0
---

# TDD Development Skill

This skill guides systematic test-driven development using the outside-in TDD methodology.

## When to Use

- Implementing new features
- Writing tests first (TDD approach)
- Red-green-refactor cycle
- Outside-in testing strategy

## Guidelines

1. Start with a failing acceptance test (outer loop)
2. Write failing unit tests (inner loop)
3. Implement minimal code to pass
4. Refactor for quality
5. Repeat until acceptance test passes

## TDD Cycle

1. **Red**: Write a failing test
2. **Green**: Write minimal code to pass
3. **Blue**: Refactor for quality

## Integration with nWave

- **Wave**: DEVELOP
- **Phase**: 3 (Implementation)
- **Agent**: software-crafter
```

---

## 5. Migration from Trigger Patterns

### Converting Triggers to Description

Old trigger patterns are converted to semantic description:

| Old (Triggers) | New (Description) |
|----------------|-------------------|
| `implement.*` | "Use when implementing features" |
| `TDD` | "Use for test-driven development (TDD)" |
| `outside-in` | "Use for outside-in testing approach" |
| `refactor.*` | "Use when refactoring code" |

### Conversion Example

**Before** (trigger-based):
```yaml
triggers:
  - implement.*
  - TDD
  - outside-in
  - test.*first
```

**After** (description-based):
```yaml
description: |
  Use this skill when implementing features using test-driven development.
  Activates for: implementing features, TDD, outside-in testing,
  writing tests first, red-green-refactor cycle.
```

---

## 6. Runtime Consumer

### Claude Code Native Runtime

The runtime consumer is **Claude Code itself**:

1. **Discovery**: Claude Code scans `.claude/skills/` at startup
2. **Loading**: Skill names and descriptions loaded into system prompt
3. **Matching**: Claude semantically matches user requests to skills
4. **Activation**: Relevant skill content loaded into context
5. **Execution**: Claude follows skill instructions

### Hot Reload

Claude Code 2.1.0+ supports hot reload:
- New/updated skills available immediately
- No session restart required

---

## 7. nWave Workflow Integration

### Optional Metadata

nWave-specific fields (`wave`, `phase`, `agents`) are:
- **Stored in YAML frontmatter** (Claude Code ignores unknown fields)
- **Used by nWave orchestrator** for workflow sequencing
- **Transparent to Claude Code runtime**

### Example with nWave Metadata

```yaml
---
name: design-architecture
description: |
  Architecture design skill for creating system designs.
  Use when: designing architecture, creating diagrams,
  defining components, planning system structure.
# nWave metadata (optional, ignored by Claude Code)
wave: DESIGN
phase: 2
agents:
  - solution-architect
version: 1.0.0
---

# Architecture Design Skill

[Skill content...]
```

---

## 8. Validation Rules

### Required Validation

```python
def validate_skill(skill_data: dict) -> bool:
    """Validate skill follows Claude Code format."""
    # Required fields
    if 'name' not in skill_data:
        raise ValidationError("Missing required field: 'name'")

    if 'description' not in skill_data:
        raise ValidationError("Missing required field: 'description'")

    # Name format: lowercase, hyphens
    if not re.match(r'^[a-z][a-z0-9-]*$', skill_data['name']):
        raise ValidationError(
            f"Invalid name '{skill_data['name']}': "
            "must be lowercase with hyphens"
        )

    # Description must be meaningful
    if len(skill_data['description']) < 50:
        raise ValidationError(
            "Description too short. Must clearly explain "
            "what skill does and when to use it."
        )

    return True
```

### Optional nWave Validation

```python
def validate_nwave_metadata(skill_data: dict) -> bool:
    """Validate optional nWave metadata if present."""
    if 'wave' in skill_data:
        valid_waves = ['DISCUSS', 'DESIGN', 'DEVELOP', 'DISTILL', 'DELIVER']
        if skill_data['wave'] not in valid_waves:
            raise ValidationError(f"Invalid wave: {skill_data['wave']}")

    if 'phase' in skill_data:
        if not isinstance(skill_data['phase'], int) or not (1 <= skill_data['phase'] <= 8):
            raise ValidationError(f"Invalid phase: {skill_data['phase']}")

    return True
```

---

## 9. Benefits of Native Format

| Aspect | Benefit |
|--------|---------|
| **Ecosystem** | Full compatibility with Claude Code plugins and marketplace |
| **Discovery** | Automatic discovery by Claude Code runtime |
| **Hot Reload** | Instant updates without restart |
| **Simplicity** | Single format to maintain |
| **Future-proof** | Aligned with Anthropic's official specification |

---

## Version History

- **v2.0** (2026-01-14): Simplified to Claude Code native format only
  - Removed dual-format strategy
  - Adopted Claude Code `name` + `description` as required fields
  - Trigger patterns converted to semantic descriptions
  - nWave metadata as optional fields

- **v1.0** (2026-01-14): Initial dual-format specification (superseded)
