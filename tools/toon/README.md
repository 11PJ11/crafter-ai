# TOON Toolchain

<!-- version: 1.0.0 -->
<!-- last_updated: 2026-01-14 -->
<!-- source_patterns: baseline/patterns/02-02-discovered-patterns.json -->

> **TOON** (Terse Object Notation) v3.0 toolchain for converting nWave agents to Claude Code Plugin Marketplace format.

## Table of Contents

1. [Overview](#overview)
2. [Components](#components)
3. [Usage](#usage)
4. [TOON v3.0 Syntax Reference](#toon-v30-syntax-reference)
5. [Conversion Patterns](#conversion-patterns)
6. [Edge Cases](#edge-cases)
7. [Decision Tree](#decision-tree)
8. [Validation](#validation)
9. [Version History](#version-history)

---

## Overview

### What is TOON?

TOON (Terse Object Notation) is a compressed, token-efficient format for defining AI agents. It reduces token consumption while preserving semantic completeness.

### Key Benefits

| Benefit | Description |
|---------|-------------|
| **Token Efficiency** | 5-6x compression ratio vs verbose Markdown |
| **Structural Clarity** | Clear section hierarchy with `##` headers |
| **Machine Parseable** | Consistent format for automated processing |
| **Human Readable** | Intuitive syntax with minimal learning curve |

### Conversion Statistics (Pilot)

From the software-crafter pilot conversion:
- Original: 2562 lines, ~24,852 tokens
- TOON: 448 lines, ~4,360 tokens (estimated)
- Compression ratio: 5.7:1
- Sections converted: 18
- Commands preserved: 27
- Dependencies preserved: 16

---

## Components

| File | Purpose |
|------|---------|
| `parser.py` | Parses TOON v3.0 files into structured data |
| `parser_schema.py` | Output dataclass definitions |
| `compiler.py` | Orchestrates parse → template → output pipeline |
| `validate_roundtrip.py` | Validates semantic equivalence after conversion |
| `templates/agent.md.j2` | Jinja2 template for agent Markdown output |
| `templates/command.md.j2` | Jinja2 template for command output |
| `templates/skill.yaml.j2` | Jinja2 template for skill YAML output |

---

## Usage

### Basic Compilation

```python
from tools.toon.compiler import compile_toon

# Compile a TOON file to Claude Code agent format
compile_toon('nWave/agents/agent-name.toon', 'output/')
```

### Parse and Inspect

```python
from tools.toon.parser import TOONParser

parser = TOONParser()
with open('agent.toon', 'r') as f:
    data = parser.parse(f.read())

print(f"Agent ID: {data['id']}")
print(f"Type: {data['type']}")
print(f"Sections: {list(data['sections'].keys())}")
```

### Roundtrip Validation

```python
from tools.toon.validate_roundtrip import validate_roundtrip

result = validate_roundtrip('original.md', 'compiled.md')
print(f"Equivalence Score: {result['equivalence_score']}%")
print(f"Commands Match: {result['commands_match']}")
print(f"Dependencies Match: {result['dependencies_match']}")
```

---

## TOON v3.0 Syntax Reference

### 1. File Header Comment

**Purpose**: Identifies file type and provides brief description.

```toon
# AGENT-NAME (TOON v3.0)
# Use for [brief purpose description]
```

**Rules**:
- First line: Agent name in SCREAMING_SNAKE_CASE or KEBAB-CASE with version
- Second line: Brief `whenToUse` description

---

### 2. Section Headers (`##`)

**Purpose**: Define major sections.

```toon
## SECTION_NAME
content here
```

**Standard Sections** (in recommended order):

| Section | Required | Purpose |
|---------|----------|---------|
| `ID` | Yes | Agent identification and metadata |
| `PERSONA` | Yes | Agent personality and traits |
| `CORE_PRINCIPLES` | No | Guiding principles |
| `ACTIVATION` | Yes | Startup sequence |
| `COMMANDS` | Yes | Available commands |
| `DEPENDENCIES` | Yes | Required files and resources |
| `EMBEDDED_KNOWLEDGE` | No | BUILD:INJECT markers |
| `METADATA` | Yes | Version and capability info |

**Naming Convention**: SCREAMING_SNAKE_CASE for all section names.

---

### 3. Subsection Headers (`###`)

**Purpose**: Organize content within sections.

```toon
## COMMANDS

### Development Commands
- develop: Execute development workflow
- test: Run test suite

### Utility Commands
- help: Show available commands
- exit: End session
```

**Rules**:
- Use Title Case for subsection names
- Group related items logically
- Maximum nesting: 2 levels (`##` and `###`)

---

### 4. Key-Value Pairs

**Purpose**: Define metadata and properties.

```toon
## ID
role: AgentName | agent-id
title: Agent Title Description
icon: emoji-here
model: inherit
whenToUse: Brief description of when to use
```

**Formats**:
- Simple: `key: value`
- Compound: `key: value1 | value2` (pipe-separated alternatives)
- Multi-line: Use consistent indentation

---

### 5. Arrow Prefix (`→`)

**Purpose**: Emphasize principles, implications, or flow.

```toon
## CORE_PRINCIPLES
→ Quality First: Never compromise on quality
→ Test-Driven: All code must have tests first
→ Incremental: Small, focused, atomic changes
```

**Use Cases**:
- Core principles and values
- Implications and consequences
- Flow relationships and causality

---

### 6. List Items (`-`)

**Purpose**: Define commands, steps, or enumerations.

```toon
## ACTIVATION
- STEP 1: Read this file completely
- STEP 2: Adopt persona from ID section
- STEP 3: Greet user and display help

## COMMANDS
- help: Show numbered list of commands
- develop: Execute development workflow
```

**Patterns**:
- Commands: `- command-name: description`
- Steps: `- STEP N: action description`
- Dependencies: `- path/to/file.ext`

---

### 7. Nested YAML Structure

**Purpose**: Define hierarchical data.

```toon
## DEPENDENCIES
tasks:
  - path/to/task1.md
  - path/to/task2.md
templates:
  - template1.yaml
  - template2.yaml
checklists:
  - validation-checklist.md
data:
  - reference-data.md
embed_knowledge:
  - knowledge/topic1.md
  - knowledge/topic2.md
```

**Dependency Categories**:

| Category | Purpose |
|----------|---------|
| `tasks` | Task definitions loaded on command execution |
| `templates` | Output format templates |
| `checklists` | Validation and compliance checklists |
| `data` | Reference data files |
| `embed_knowledge` | Content injected at build time |

---

### 8. BUILD:INJECT Markers

**Purpose**: Mark locations for content injection at build time.

```toon
## EMBEDDED_KNOWLEDGE
<!-- BUILD:INJECT:START:path/to/knowledge-file.md -->
<!-- Content will be injected here at build time -->
<!-- BUILD:INJECT:END -->
```

**Rules**:
- Path is relative to project root
- START and END markers must be paired
- Content between markers is replaced during build
- List all paths in `dependencies.embed_knowledge`

---

### 9. Inline Metadata Separator (`|`)

**Purpose**: Combine related values compactly.

```toon
## METADATA
v: 3.0 | created: 2026-01-14
capabilities: Capability1 | Capability2 | Capability3
```

**Use Cases**:
- Version and date combinations
- Multiple capabilities or features
- Role and identifier combinations

---

### 10. Phase/Gate Definitions

**Purpose**: Define workflow phases with quality gates.

```toon
### Phase 1: PREPARE
→ Remove @skip from target test
→ Verify only 1 scenario enabled
gate: G1 - Exactly ONE test active
duration: 3-5 min

### Phase 2: RED_ACCEPTANCE
→ Run acceptance test - MUST fail
gate: G2 - Test fails for correct reason
valid_failures: LOGIC_NOT_IMPLEMENTED | MISSING_ENDPOINT
invalid_failures: CONNECTION_FAILED | TIMEOUT
duration: 3-5 min
```

**Standard Fields**:
- `gate`: Success criteria with identifier
- `duration`: Expected time range
- `valid_failures`: Acceptable failure categories
- `invalid_failures`: Unacceptable failures

---

### 11. Status Markers

**Purpose**: Indicate validation status.

```toon
## QUALITY_FRAMEWORK

### Commit Requirements
→ NEVER commit with failing tests
→ ALL tests must pass (100% required)
→ ALL quality gates must pass
```

**Symbol Reference**:

| Symbol | Meaning | Usage |
|--------|---------|-------|
| `✓` | Correct/passed | Validation lists |
| `✗` | Wrong/failed | Anti-patterns |
| `⚠️` | Warning/caution | Conditional items |
| `→` | Implies | Principles, flow |

---

### 12. Selection Criteria

**Purpose**: Define evaluation criteria with status.

```toon
## OPEN_SOURCE

### Required Checks
✓ License open source (MIT/Apache/BSD preferred)
✓ Active maintenance (commits within 6 months)
✓ Good community (> 100 stars)
✓ No critical security vulnerabilities

### Forbidden
✗ Packages with unclear licenses
✗ Paid/proprietary without approval
✗ Abandoned packages (> 2 years)
```

---

### 13. Collaboration Definitions

**Purpose**: Define agent handoffs.

```toon
## COLLABORATION

### Receives From
source_agent (WAVE_NAME): data1 | data2 | context

### Hands Off To
target_agent (WAVE_NAME): deliverable1 | deliverable2
```

**Format**: `agent_name (WAVE): item1 | item2 | item3`

---

### 14. Contract Specifications

**Purpose**: Define inputs, outputs, constraints.

```toon
## PRODUCTION_FRAMEWORKS

### Contract
inputs: user_request | context_files | configuration
outputs: artifacts (path/**/*) | documentation
allowed: File creation for necessary artifacts
forbidden: Unsolicited docs | deletion without approval
```

---

### 15. Symbol Legend (Footer)

**Purpose**: Document TOON-specific symbols.

```toon
---
TOON_NOTES:
- →=implies | ⟷=alternates | ≠=not_equal
- ✓=correct | ✗=wrong | ⚠️=warning
- L#=Level | G#=Gate | F#=Finding
```

---

## Conversion Patterns

These patterns are from `baseline/patterns/02-02-discovered-patterns.json`.

### PATTERN-001: YAML Frontmatter → ID Section

**Description**: Agent metadata in YAML frontmatter maps to TOON `## ID` section.

**Before** (Markdown):
```yaml
---
name: agent-name
description: Agent description text
model: inherit
---
```

**After** (TOON):
```toon
## ID
role: AgentName | agent-name
title: Agent Title Here
model: inherit
whenToUse: Agent description text
```

**Applies to**: All agents with metadata

---

### PATTERN-002: Commands List Format

**Description**: Commands list uses YAML list format with `-` prefix and colon separator.

**Before** (Markdown):
```yaml
commands:
  - help: Show numbered list of all available commands
  - develop: Execute main development workflow
```

**After** (TOON):
```toon
## COMMANDS

### Category Name
- help: Show numbered list of all available commands
- develop: Execute main development workflow
```

**Applies to**: All agents with commands

---

### PATTERN-003: Dependencies Structure

**Description**: Dependencies use nested YAML structure with category keys.

**Before** (Markdown):
```yaml
dependencies:
  tasks:
    - path/to/task1.md
    - path/to/task2.md
  templates:
    - template.yaml
```

**After** (TOON):
```toon
## DEPENDENCIES
tasks:
  - path/to/task1.md
  - path/to/task2.md
templates:
  - template.yaml
```

**Applies to**: All agents with dependencies

---

### PATTERN-004: Section Headers

**Description**: Section headers use `##` for major sections, `###` for subsections.

**Before** (Markdown):
```markdown
# Part 1: Methodology Topic
## Core Principles
```

**After** (TOON):
```toon
## METHODOLOGY_TOPIC

### Core Principles
```

**Applies to**: All multi-section agents

---

### PATTERN-005: Arrow Symbols for Flow

**Description**: TOON uses arrow symbols (`→`) for implies/flow relationships.

**Before** (Markdown):
```markdown
Step 1 leads to Step 2 which produces output
```

**After** (TOON):
```toon
Step 1 → Step 2 → output
```

**Applies to**: Flow descriptions and relationships

---

### PATTERN-006: Activation Instructions

**Description**: Activation instructions preserve step-based format with numbered steps.

**Before** (Markdown):
```yaml
activation-instructions:
  - STEP 1: Read this file
  - STEP 2: Adopt persona
```

**After** (TOON):
```toon
## ACTIVATION
- STEP 1: Read this file
- STEP 2: Adopt persona
```

**Applies to**: All agents with activation sequence

---

### PATTERN-007: Persona Definition

**Description**: Persona definition maps to dedicated PERSONA section.

**Before** (Markdown):
```yaml
persona:
  role: Master Specialist
  style: Methodical, test-driven
```

**After** (TOON):
```toon
## PERSONA
name: PersonaName
role: Master Specialist
style: Methodical, test-driven
```

**Applies to**: All agents with persona definitions

---

### PATTERN-008: Core Principles

**Description**: Core principles use arrow symbol (`→`) prefix for emphasis.

**Before** (Markdown):
```yaml
core_principles:
  - Token Economy: Minimize tokens
  - Document Control: Only necessary docs
```

**After** (TOON):
```toon
## CORE_PRINCIPLES
→ Token Economy: Minimize tokens
→ Document Control: Only necessary docs
```

**Applies to**: All agents with principle lists

---

## Edge Cases

### EDGE-001: Embedded Knowledge with BUILD:INJECT

**Description**: Embedded knowledge with BUILD:INJECT markers requires preservation.

**Handling Strategy**: Preserve `BUILD:INJECT` markers verbatim in `EMBEDDED_KNOWLEDGE` section.

**Format**:
```toon
## EMBEDDED_KNOWLEDGE
<!-- BUILD:INJECT:START:path/to/file.md -->
<!-- Content will be injected here at build time -->
<!-- BUILD:INJECT:END -->
```

**Rules**:
- Use HTML comment format exactly as shown
- START path must be relative to project root
- START and END markers must be paired
- All paths should also appear in `dependencies.embed_knowledge`

---

### EDGE-002: Multi-Part Structure

**Description**: Large agents with multi-part structure (`Part 1`, `Part 2`, etc.) containing extensive methodology.

**Handling Strategy**: Consolidate into semantic sections. Map `Part N: Topic` to `## TOPIC` section. Preserve critical methodology content, compress verbose explanations.

**Example**:
```markdown
# Part 1: TDD Methodology
## Overview
...

# Part 2: Refactoring Approach
## Principles
...
```

Becomes:
```toon
## TDD_METHODOLOGY
### Overview
...

## REFACTORING_APPROACH
### Principles
...
```

---

### EDGE-003: Embedded YAML Code Blocks

**Description**: Embedded YAML code blocks within markdown (` ```yaml ... ``` `).

**Handling Strategy**: Extract YAML content and convert to TOON section format. Remove code fences, preserve key-value structure.

**Before**:
````markdown
```yaml
config:
  setting1: value1
  setting2: value2
```
````

**After**:
```toon
### Configuration
setting1: value1
setting2: value2
```

---

### EDGE-004: Nested Dict Values in Frontmatter

**Description**: YAML frontmatter with nested dict values (e.g., `agent.customization`).

**Handling Strategy**: Flatten to TOON key-value pairs. Use dot notation (e.g., `agent.customization`) or create nested sections.

**Before**:
```yaml
---
agent:
  customization:
    theme: dark
---
```

**After** (Option 1 - Flatten):
```toon
## ID
agent.customization.theme: dark
```

**After** (Option 2 - Subsection):
```toon
## CUSTOMIZATION
theme: dark
```

---

### EDGE-005: Unicode Symbols

**Description**: Unicode symbols (emojis, arrows) in content require UTF-8 handling.

**Handling Strategy**: Preserve Unicode symbols - TOON format supports UTF-8. Emojis and arrows pass through unchanged.

**Supported Symbols**:

| Symbol | Meaning | Example |
|--------|---------|---------|
| → | implies | `A → B` |
| ⟷ | alternates | `X ⟷ Y` |
| ≠ | not equal | `A ≠ B` |
| ✓ | correct | `✓ Valid` |
| ✗ | wrong | `✗ Invalid` |
| ⚠️ | warning | `⚠️ Caution` |

---

### EDGE-006: Deeply Nested YAML

**Description**: Production framework sections with deeply nested YAML structures.

**Handling Strategy**: Create subsections using `###` headers. Flatten complex nesting to 2 levels maximum: `## SECTION` / `### SUBSECTION`.

**Before**:
```yaml
production:
  safety:
    input:
      validation: schema
      sanitization: enabled
    output:
      filtering: guardrails
```

**After**:
```toon
## PRODUCTION_FRAMEWORKS

### Safety
input_validation: schema
input_sanitization: enabled
output_filtering: guardrails
```

---

## Decision Tree

Use this flowchart when encountering ambiguous conversion scenarios:

```
START: Analyzing source content
│
├─ Is it YAML frontmatter (---...---)?
│  ├─ Yes → Convert to ## ID section (PATTERN-001)
│  └─ No → Continue
│
├─ Is it a commands list?
│  ├─ Yes → Create ## COMMANDS with ### categories (PATTERN-002)
│  └─ No → Continue
│
├─ Is it a dependencies block?
│  ├─ Yes → Create ## DEPENDENCIES with nested YAML (PATTERN-003)
│  └─ No → Continue
│
├─ Is it a `# Part N:` section header?
│  ├─ Yes → Convert to ## TOPIC_NAME (PATTERN-004)
│  └─ No → Continue
│
├─ Is it activation/startup instructions?
│  ├─ Yes → Create ## ACTIVATION with STEP format (PATTERN-006)
│  └─ No → Continue
│
├─ Is it a persona definition?
│  ├─ Yes → Create ## PERSONA with name/role/style (PATTERN-007)
│  └─ No → Continue
│
├─ Is it a list of principles/values?
│  ├─ Yes → Create ## CORE_PRINCIPLES with → prefix (PATTERN-008)
│  └─ No → Continue
│
├─ Does it contain BUILD:INJECT markers?
│  ├─ Yes → Preserve in ## EMBEDDED_KNOWLEDGE (EDGE-001)
│  └─ No → Continue
│
├─ Is it embedded ` ```yaml ``` ` block?
│  ├─ Yes → Extract and convert to section (EDGE-003)
│  └─ No → Continue
│
├─ Is it deeply nested YAML (>2 levels)?
│  ├─ Yes → Flatten to max 2 levels (EDGE-006)
│  └─ No → Continue
│
├─ Is it a flow/process description?
│  ├─ Yes → Use → arrows (PATTERN-005)
│  └─ No → Continue
│
└─ Default: Create appropriate ## SECTION_NAME with content
```

### Ambiguity Resolution Rules

1. **Unclear section name**: Use most specific semantic name
   - ❌ `## SECTION_1`
   - ✓ `## QUALITY_FRAMEWORK`

2. **Content belongs to multiple sections**: Place in most relevant, reference from others

3. **Compression loses meaning**: Preserve full content over token savings

4. **Inconsistent format**: Standardize to TOON conventions

5. **Unknown category**: Create new `## CUSTOM_SECTION`

---

## Validation

### Compiler Validation

```bash
# Compile and validate TOON file
python -c "
from tools.toon.compiler import compile_toon
compile_toon('path/to/file.toon', '/tmp/out')
print('Compilation successful')
"

# Parse and inspect structure
python -c "
from tools.toon.parser import TOONParser
data = TOONParser().parse(open('file.toon').read())
print(f'ID: {data[\"id\"]}')
print(f'Type: {data[\"type\"]}')
print(f'Sections: {list(data[\"sections\"].keys())}')
"
```

### Required Checks

- [ ] File compiles without errors
- [ ] All sections have valid `## SECTION_NAME` headers
- [ ] ID section contains: `role`, `title`, `model`
- [ ] COMMANDS section lists all commands
- [ ] DEPENDENCIES section lists all required files
- [ ] BUILD:INJECT markers are paired (START/END)
- [ ] METADATA section has version info

### Roundtrip Validation

```python
from tools.toon.validate_roundtrip import validate_roundtrip

result = validate_roundtrip('original.md', 'compiled.md')

# Check thresholds
assert result['equivalence_score'] >= 95, f"Score: {result['equivalence_score']}"
assert result['commands_match'] == True
assert result['dependencies_match'] == True
assert result['frontmatter_valid'] == True
assert result['critical_sections_present'] == True
```

### Acceptance Thresholds

| Metric | Threshold |
|--------|-----------|
| Equivalence Score | >= 95% |
| Commands Match | 100% |
| Dependencies Preserved | >= 80% |
| Frontmatter Valid | Yes |
| Critical Sections Present | Yes |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-01-14 | Initial release: 8 patterns, 6 edge cases, 15 syntax features |

### Update Protocol

When discovering new patterns during Phase 3 batch migration:

1. Add pattern to `baseline/patterns/02-02-discovered-patterns.json`
2. Document in this README under Conversion Patterns
3. Increment version: MINOR for new patterns, PATCH for clarifications
4. Update `last_updated` and `version` in header comments

### Coverage Tracking

- Patterns documented: 8/8 (from baseline/patterns/02-02-discovered-patterns.json)
- Edge cases documented: 6/6 (from baseline/patterns/02-02-discovered-patterns.json)
- Syntax features: 15/15

---

## Quick Reference

### Common Conversions

| Source Pattern | TOON Pattern |
|----------------|--------------|
| `---\nname: x\n---` | `## ID\nrole: Name \| x` |
| `# Part N: Topic` | `## TOPIC` |
| `commands:\n  - cmd:` | `## COMMANDS\n- cmd:` |
| `leads to` | `→` |
| `- principle:` | `→ principle:` |
| ` ```yaml ``` ` | Extract to section |

### Symbol Reference

| Symbol | Purpose | Example |
|--------|---------|---------|
| `##` | Major section | `## COMMANDS` |
| `###` | Subsection | `### Utilities` |
| `→` | Implies/flow | `→ Principle` |
| `\|` | Separator | `A \| B` |
| `-` | List item | `- command:` |
| `✓` | Correct | `✓ Valid` |
| `✗` | Wrong | `✗ Invalid` |

---

*TOON Toolchain - Part of the nWave AI-Craft Framework*
