# Skill Markdown Output Format Specification

## Overview

This document specifies the format of SKILL.md files produced by the Skill Jinja2 template (step 01-04). These files are the compiled output that integrate skills into the nWave framework.

## File Structure

SKILL.md files follow this structure:

```markdown
---
skill_id: <skill_id>
name: <skill_name>
agent_association: <agent_id | [agent_ids]>
wave: <DISCUSS|DESIGN|DEVELOP|DISTILL|DELIVER>
phase: <1-8>
triggers:
  - <trigger_pattern>
  - <trigger_pattern>
---

# Activation Notice

This is a **skill** artifact for the nWave framework.

- **Activation**: Automatically triggered when patterns match
- **Scope**: Bound to agent(s): `<agent_id(s)>`
- **Context**: Wave `<WAVE>` / Phase `<phase>`

---

## Trigger Patterns

Skill activates when any pattern matches task context:

- `<trigger_1>`
- `<trigger_2>`
- `<trigger_3>`
(one per line, as regex strings)

---

## Skill Metadata

```yaml
skill_id: <skill_id>
name: <skill_name>
description: |
  <skill_description>
version: <version | omitted if not provided>
agent_association: <agent_id | [agent_ids]>
trigger_count: <number_of_triggers>
workflow_integration:
  wave: <DISCUSS|DESIGN|DEVELOP|DISTILL|DELIVER>
  phase: <1-8>
  context: <execution_context | omitted>
```

---

## Additional Metadata (if provided)

```yaml
metadata:
  <key>: <value>
  <key>: <value>
```

---

## Raw Trigger Patterns (for direct matching)

<list_trigger_patterns_as_yaml_array>
```
```yaml
triggers:
  - <trigger_1>
  - <trigger_2>
```
```

---

```

## Detailed Sections

### YAML Frontmatter (Lines 1-N)

**Purpose**: Machine-readable skill metadata

**Fields** (all REQUIRED):
- `skill_id`: Skill identifier (matches `SkillData.id`)
- `name`: Human-readable skill name
- `agent_association`: Agent ID(s) (string or YAML list)
- `wave`: nWave phase (DISCUSS, DESIGN, DEVELOP, DISTILL, DELIVER)
- `phase`: Phase number (1-8)
- `triggers`: YAML list of trigger patterns

**Fields** (OPTIONAL):
- `description`: Skill description (only if provided in SkillData)
- `version`: Semantic version (only if provided in SkillData)
- `metadata`: Additional metadata dict (only if provided in SkillData)

**YAML Escaping Rules**:
- String values with special characters MUST be quoted: `"value: with: colons"`
- Colons in YAML must be escaped or quoted: `key: "value: here"` or `"key:value"`
- Double quotes inside strings must be escaped: `"He said \"hello\""`
- List items are on separate lines with `-` prefix
- Multiline strings use `|` or `>` YAML syntax

**Example**:
```yaml
---
skill_id: develop
name: TDD Development
agent_association: software-crafter
wave: DEVELOP
phase: 3
triggers:
  - implement.*
  - TDD
  - outside-in
description: |
  Systematic test-driven development approach
version: 1.0.0
metadata:
  tags: [testing, automation]
  priority: high
---
```

### Activation Notice Section

**Purpose**: Human-readable documentation of skill activation

**Format**:
```markdown
# Activation Notice

This is a **skill** artifact for the nWave framework.

- **Activation**: Automatically triggered when patterns match
- **Scope**: Bound to agent(s): `<agent_id(s)>`
- **Context**: Wave `<WAVE>` / Phase `<phase>`
```

**Rules**:
- Always use header `# Activation Notice`
- Always include "This is a **skill** artifact..." statement
- **Activation** line explains skill is pattern-triggered
- **Scope** lists agent(s) with backticks around agent ID(s)
- **Context** shows wave and phase numbers

**Examples**:
```markdown
# Activation Notice

This is a **skill** artifact for the nWave framework.

- **Activation**: Automatically triggered when patterns match
- **Scope**: Bound to agent(s): `software-crafter`
- **Context**: Wave `DEVELOP` / Phase `3`
```

Multi-agent version:
```markdown
# Activation Notice

This is a **skill** artifact for the nWave framework.

- **Activation**: Automatically triggered when patterns match
- **Scope**: Bound to agent(s): `software-crafter`, `solution-architect`
- **Context**: Wave `DEVELOP` / Phase `5`
```

### Trigger Patterns Section

**Purpose**: Human-readable documentation of activation patterns

**Format**:
```markdown
## Trigger Patterns

Skill activates when any pattern matches task context:

- `<trigger_1>`
- `<trigger_2>`
- `<trigger_3>`
(one per line, as regex strings)
```

**Rules**:
- Always use header `## Trigger Patterns`
- Introductory text explains patterns are OR logic (any match = activation)
- List each pattern as markdown list item with backticks
- Patterns are regex strings, not evaluated in markdown
- Last line "(one per line, as regex strings)" clarifies format
- Special regex characters are NOT escaped in markdown (they're already escaped in YAML)

**Examples**:
```markdown
## Trigger Patterns

Skill activates when any pattern matches task context:

- `implement.*`
- `TDD`
- `outside-in`
(one per line, as regex strings)
```

### Skill Metadata Section

**Purpose**: Machine-readable skill data in YAML format

**Format**:
```yaml
## Skill Metadata

\`\`\`yaml
skill_id: <skill_id>
name: <skill_name>
description: |
  <skill_description>
version: <version>
agent_association: <agent_id | [agent_ids]>
trigger_count: <number>
workflow_integration:
  wave: <WAVE>
  phase: <number>
  context: <context>
\`\`\`
```

**Rules**:
- Always use header `## Skill Metadata`
- Enclose in Markdown triple backticks with `yaml` language tag
- Include all fields from SkillData
- `description`: Use YAML multiline syntax if present: `description: |` followed by indented text
- `trigger_count`: Integer count of triggers (useful for debugging/monitoring)
- `workflow_integration`: Nested YAML structure with wave, phase, context (context omitted if not in SkillData)
- Omit optional fields if not provided in SkillData (description, version, metadata)

**Example**:
```yaml
## Skill Metadata

\`\`\`yaml
skill_id: develop
name: TDD Development
description: |
  Systematic test-driven development approach
  with outside-in TDD methodology
version: 1.0.0
agent_association: software-crafter
trigger_count: 3
workflow_integration:
  wave: DEVELOP
  phase: 3
  context: TDD cycle
\`\`\`
```

### Additional Metadata Section

**Conditions**: Only if `metadata` field exists in SkillData

**Purpose**: Extension point for future metadata

**Format**:
```yaml
## Additional Metadata

\`\`\`yaml
metadata:
  tags: [tag1, tag2, tag3]
  priority: high
  custom_field: custom_value
\`\`\`
```

**Rules**:
- Only included if `metadata` dict present in SkillData
- Use header `## Additional Metadata`
- Render complete metadata dict as YAML

### Raw Trigger Patterns Section

**Purpose**: Machine-readable trigger list for runtime pattern matching

**Format**:
```markdown
## Raw Trigger Patterns (for direct matching)

\`\`\`yaml
triggers:
  - <trigger_1>
  - <trigger_2>
  - <trigger_3>
\`\`\`
```

**Rules**:
- Use header `## Raw Trigger Patterns (for direct matching)`
- List triggers as YAML array
- Each pattern on separate line with `-` prefix
- Patterns are exact copies from SkillData.triggers (no transformation)
- YAML escaping already applied from frontmatter

**Example**:
```markdown
## Raw Trigger Patterns (for direct matching)

\`\`\`yaml
triggers:
  - implement.*
  - TDD
  - "outside-in.*task"
\`\`\`
```

## Complete Example

### Input (SkillData)
```python
{
    'id': 'develop',
    'name': 'TDD Development',
    'type': 'skill',
    'description': 'Systematic test-driven development approach\nwith outside-in TDD methodology',
    'triggers': ['implement.*', 'TDD', 'outside-in'],
    'version': '1.0.0',
    'agent_association': 'software-crafter',
    'workflow_integration': {
        'wave': 'DEVELOP',
        'phase': 3,
        'context': 'TDD cycle'
    },
    'metadata': {
        'tags': ['testing', 'automation'],
        'priority': 'high'
    }
}
```

### Output (SKILL.md)
```markdown
---
skill_id: develop
name: TDD Development
agent_association: software-crafter
wave: DEVELOP
phase: 3
triggers:
  - implement.*
  - TDD
  - outside-in
description: |
  Systematic test-driven development approach
  with outside-in TDD methodology
version: 1.0.0
metadata:
  tags: [testing, automation]
  priority: high
---

# Activation Notice

This is a **skill** artifact for the nWave framework.

- **Activation**: Automatically triggered when patterns match
- **Scope**: Bound to agent(s): `software-crafter`
- **Context**: Wave `DEVELOP` / Phase `3`

---

## Trigger Patterns

Skill activates when any pattern matches task context:

- `implement.*`
- `TDD`
- `outside-in`
(one per line, as regex strings)

---

## Skill Metadata

\`\`\`yaml
skill_id: develop
name: TDD Development
description: |
  Systematic test-driven development approach
  with outside-in TDD methodology
version: 1.0.0
agent_association: software-crafter
trigger_count: 3
workflow_integration:
  wave: DEVELOP
  phase: 3
  context: TDD cycle
\`\`\`

---

## Additional Metadata

\`\`\`yaml
metadata:
  tags: [testing, automation]
  priority: high
\`\`\`

---

## Raw Trigger Patterns (for direct matching)

\`\`\`yaml
triggers:
  - implement.*
  - TDD
  - outside-in
\`\`\`
```

## Multi-Agent Skill Example

### Output (Multi-Agent SKILL.md)
```markdown
---
skill_id: refactor
name: Code Refactoring
agent_association:
  - software-crafter
  - solution-architect
wave: DEVELOP
phase: 5
triggers:
  - refactor.*
  - simplify.*
  - optimize
description: |
  Systematic code refactoring using Mikado Method
version: 1.2.0
metadata:
  priority: high
---

# Activation Notice

This is a **skill** artifact for the nWave framework.

- **Activation**: Automatically triggered when patterns match
- **Scope**: Bound to agent(s): `software-crafter`, `solution-architect`
- **Context**: Wave `DEVELOP` / Phase `5`

[rest of sections same as above]
```

## Validation Rules for Template

Template MUST verify:

1. **Frontmatter validity**: All required fields present and valid YAML
2. **YAML escaping**: Special characters properly escaped (colons, quotes, etc.)
3. **Trigger list**: Non-empty, each item is string
4. **Agent association**: String or valid YAML list of strings
5. **Activation notice**: Contains required lines in correct order
6. **Trigger patterns section**: Lists all triggers with backticks
7. **Metadata section**: Valid YAML if included
8. **Output is valid Markdown**: Parses without syntax errors

## Error Messages

Template should error on:
- Missing required frontmatter fields
- Invalid YAML in frontmatter
- Empty trigger list
- Malformed agent_association

## Version History

- **v1.0** (2026-01-14): Initial specification with frontmatter, sections, YAML escaping rules
