# Skill Markdown Output Format Specification

## Overview

This document specifies the SKILL.md format following the **Claude Code Agent Skills** specification from Anthropic.

**Reference**: [Anthropic Agent Skills](https://github.com/anthropics/skills)

---

## File Structure

SKILL.md files follow the Claude Code native format:

```markdown
---
name: skill-name
description: |
  Clear description of what this skill does and when to use it.
  Claude uses this for semantic matching to activate the skill.
---

# Skill Title

[Instructions that Claude follows when skill is active]

## When to Use

- Scenario 1
- Scenario 2

## Guidelines

1. Guideline 1
2. Guideline 2

## Examples

- Example usage 1
- Example usage 2
```

---

## YAML Frontmatter

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `name` | string | Skill identifier (lowercase, hyphens only) |
| `description` | string | What the skill does and when to use it |

### Optional Fields (nWave Extensions)

| Field | Type | Description |
|-------|------|-------------|
| `wave` | string | nWave phase (DISCUSS/DESIGN/DEVELOP/DISTILL/DELIVER) |
| `phase` | int | Phase number (1-8) |
| `agents` | list | Agent IDs that can use this skill |
| `version` | string | Skill version (semver) |

### Frontmatter Example

```yaml
---
name: develop
description: |
  Use this skill when implementing features using test-driven development.
  Activates for: implementing features, TDD, outside-in testing,
  writing tests first, red-green-refactor cycle.
wave: DEVELOP
phase: 3
agents:
  - software-crafter
version: 1.0.0
---
```

---

## Content Sections

### Skill Title (H1)

```markdown
# TDD Development Skill
```

- Required
- Should be descriptive and match skill purpose

### When to Use (H2)

```markdown
## When to Use

- Implementing new features
- Writing tests first (TDD approach)
- Red-green-refactor cycle
```

- Recommended
- Lists scenarios when skill should activate
- Reinforces semantic matching triggers

### Guidelines (H2)

```markdown
## Guidelines

1. Start with a failing acceptance test
2. Write failing unit tests
3. Implement minimal code to pass
4. Refactor for quality
```

- Recommended
- Step-by-step instructions Claude follows
- Numbered for clarity

### Examples (H2)

```markdown
## Examples

- "Implement user authentication using TDD"
- "Add a new API endpoint with tests first"
```

- Optional
- Shows example user requests that activate skill
- Helps Claude understand usage context

### Additional Sections

Add any sections relevant to the skill:

```markdown
## Technical Details
...

## Integration Notes
...

## References
- [External Resource](url)
```

---

## Complete Example

### Input (SkillData)

```python
{
    'name': 'develop',
    'description': 'Use this skill when implementing features using test-driven development.\nActivates for: implementing features, TDD, outside-in testing.',
    'wave': 'DEVELOP',
    'phase': 3,
    'agents': ['software-crafter'],
    'version': '1.0.0',
    'content': '...'
}
```

### Output (SKILL.md)

```markdown
---
name: develop
description: |
  Use this skill when implementing features using test-driven development.
  Activates for: implementing features, TDD, outside-in testing.
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

## Examples

- "Implement user authentication using TDD"
- "Add payment processing with outside-in tests"
- "Create REST API endpoint using red-green-refactor"

## References

- [Outside-In TDD Methodology](nWave/data/embed/software-crafter/outside-in-tdd-methodology.md)
```

---

## YAML Escaping Rules

### String Values

```yaml
# Simple strings - no quotes needed
name: develop

# Strings with special chars - use quotes
description: "Value with: colons"

# Multiline strings - use pipe
description: |
  Line 1
  Line 2
  Line 3
```

### Special Characters

| Character | Handling |
|-----------|----------|
| `:` | Quote the value: `"value: here"` |
| `#` | Quote the value: `"value # here"` |
| `'` | Use double quotes: `"it's"` |
| `"` | Escape: `"He said \"hello\""` |
| `|` | Use as multiline indicator at end |

---

## Validation Rules

Template output MUST:

1. **Valid YAML frontmatter**: Parseable by any YAML parser
2. **Required fields present**: `name` and `description`
3. **Name format**: Lowercase, hyphens only (`^[a-z][a-z0-9-]*$`)
4. **Description length**: Minimum 50 characters
5. **Valid Markdown**: Parseable without syntax errors
6. **Proper escaping**: Special characters escaped in YAML

### Validation Code

```python
import yaml
import re

def validate_skill_md(content: str) -> bool:
    """Validate SKILL.md follows Claude Code format."""

    # Extract frontmatter
    if not content.startswith('---'):
        raise ValidationError("Must start with YAML frontmatter (---)")

    parts = content.split('---', 2)
    if len(parts) < 3:
        raise ValidationError("Invalid frontmatter format")

    frontmatter_yaml = parts[1]
    markdown_content = parts[2]

    # Parse YAML
    try:
        data = yaml.safe_load(frontmatter_yaml)
    except yaml.YAMLError as e:
        raise ValidationError(f"Invalid YAML: {e}")

    # Required fields
    if 'name' not in data:
        raise ValidationError("Missing required field: 'name'")

    if 'description' not in data:
        raise ValidationError("Missing required field: 'description'")

    # Name format
    if not re.match(r'^[a-z][a-z0-9-]*$', data['name']):
        raise ValidationError(
            f"Invalid name '{data['name']}': must be lowercase with hyphens"
        )

    # Description length
    if len(data['description']) < 50:
        raise ValidationError("Description must be at least 50 characters")

    return True
```

---

## Directory Structure

Skills are output to Claude Code standard location:

```
.claude/
└── skills/
    ├── develop/
    │   └── SKILL.md
    ├── refactor/
    │   └── SKILL.md
    └── design-architecture/
        └── SKILL.md
```

---

## Template Requirements

The Jinja2 template (step 01-04) must:

1. Generate valid YAML frontmatter with `name` and `description`
2. Include optional nWave fields if provided
3. Generate markdown content with H1 title
4. Include "When to Use" section from description keywords
5. Generate "Guidelines" section if instructions provided
6. Properly escape all YAML special characters
7. Output valid Markdown

---

## Version History

- **v2.0** (2026-01-14): Aligned with Claude Code native format
  - Simplified to `name` + `description` required fields
  - Removed custom sections (Activation Notice, Raw Triggers)
  - Added standard Claude Code sections (When to Use, Guidelines, Examples)
  - Updated directory structure to `.claude/skills/`

- **v1.0** (2026-01-14): Initial specification (superseded)
