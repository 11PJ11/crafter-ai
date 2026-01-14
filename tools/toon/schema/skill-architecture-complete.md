# Skills Architecture - Complete Specification

## Executive Summary

This document consolidates all skill architecture decisions required to unblock Phase 1 steps (01-04, 01-05, 01-06).

**Critical Definitions**:
1. ✅ Skill data structure (DEFINED in skill-data-structure.md)
2. ✅ Skill markdown format (DEFINED in skill-markdown-format.md)
3. ✅ Trigger pattern semantics (THIS DOCUMENT)
4. ✅ Agent association model (THIS DOCUMENT)
5. ✅ Workflow integration requirements (THIS DOCUMENT)

---

## 1. Trigger Pattern Semantics

### Definition

Triggers are **regex patterns** that activate a skill when matched against task context.

### Pattern Matching Logic

```
Task Input: "Implement the login feature using outside-in TDD"

Skill: 'develop' with triggers=['implement.*', 'TDD', 'outside-in']
Evaluation:
  - Pattern 'implement.*' matches "Implement the login..." → MATCH
  - Pattern 'TDD' matches "outside-in TDD" → MATCH
  - Pattern 'outside-in' matches "outside-in" → MATCH

Result: Skill is ACTIVATED (OR logic: any match = activation)
```

### Pattern Matching Rules

1. **Case-Insensitive**: Patterns are matched case-insensitively
   ```
   Pattern: 'TDD'  matches:  'tdd', 'TDD', 'Tdd', 'tDD' ✓
   ```

2. **Partial Matching**: Patterns match anywhere in input (not just start/end)
   ```
   Pattern: 'implement.*'  matches:
     - "implement the feature" ✓
     - "I will implement X" ✓
     - "please implement Y" ✓
   ```

3. **OR Logic**: Multiple triggers = OR (activate if ANY pattern matches)
   ```
   triggers: ['refactor.*', 'simplify.*', 'optimize']

   "refactor this code" → ACTIVATE (pattern 0 matches)
   "simplify the logic" → ACTIVATE (pattern 1 matches)
   "optimize performance" → ACTIVATE (pattern 2 matches)
   "write more comments" → NO MATCH (no pattern matches)
   ```

4. **Character Escaping** in YAML:
   - Regex special chars DO NOT need escaping in TOON files (they're YAML values)
   - Example valid patterns:
     ```yaml
     triggers:
       - implement.*
       - refactor\s+\w+      # Whitespace handling
       - "test.*\(.*\)"       # Parentheses must be quoted
       - optimize|streamline  # OR operator in regex
     ```

### Validation

Parser MUST verify patterns are valid regex:
```python
import re

for pattern in triggers:
    try:
        re.compile(pattern, re.IGNORECASE)
    except re.error as e:
        raise ValidationError(f"Invalid trigger pattern '{pattern}': {e}")
```

### Pattern Examples

```yaml
# Example 1: TDD-related triggers
triggers:
  - implement.*
  - test.*driven
  - TDD
  - outside-in.*test

# Example 2: Refactoring triggers
triggers:
  - refactor
  - simplify.*code
  - optimize.*performance
  - mikado.*method

# Example 3: Documentation triggers
triggers:
  - document.*
  - write.*readme
  - api.*documentation
  - "spec.*\(.*\)"
```

---

## 2. Agent Association Model

### Cardinality Options

Skills support three binding modes:

### Mode 1: 1:1 (Single Agent)

**Definition**: Skill bound to exactly one agent

**Data Structure**:
```python
agent_association: str  # Single agent ID

# Example
agent_association: 'software-crafter'
```

**YAML Representation**:
```yaml
agent_association: software-crafter
```

**Semantics**:
- Skill is ONLY available to this agent
- Only this agent can invoke the skill
- Simple, clear responsibility

**Use Cases**:
- Skills specific to one agent's role
- Example: `'develop'` skill for software-crafter

### Mode 2: 1:N (One Skill → Multiple Agents)

**Definition**: Skill bound to multiple agents (any can invoke)

**Data Structure**:
```python
agent_association: List[str]  # Multiple agent IDs

# Example
agent_association: ['software-crafter', 'solution-architect']
```

**YAML Representation**:
```yaml
agent_association:
  - software-crafter
  - solution-architect
  - product-owner
```

**Semantics**:
- Skill is available to ALL listed agents
- Any listed agent can invoke the skill
- Useful for cross-agent workflows

**Use Cases**:
- Shared skills across multiple agents
- Example: `'review'` skill for software-crafter AND solution-architect
- Example: `'document'` skill for all agents

### Mode 3: N:M (Future Extension - Conditional Binding)

**Definition**: Skill with conditional agent access (future)

**Current Status**: NOT IMPLEMENTED (reserved for future)

**Data Structure** (future):
```python
agent_association: Dict[str, any]  # Conditional model

# Future example (not yet implemented)
agent_association: {
    'software-crafter': {'permission': 'full'},
    'solution-architect': {'permission': 'read-only'}
}
```

---

## 3. Workflow Integration Requirements

### Structure

```python
workflow_integration: Dict[str, any]  # Required fields:
{
    'wave': str,           # REQUIRED: nWave phase
    'phase': int,          # REQUIRED: Phase number (1-8)
    'context': Optional[str]  # OPTIONAL: Execution context
}
```

### Wave Values

Valid nWave phases:
- `'DISCUSS'`: Requirements gathering
- `'DESIGN'`: Architecture and design
- `'DEVELOP'`: Implementation (feature building)
- `'DISTILL'`: Acceptance testing and validation
- `'DELIVER'`: Deployment and release

### Phase Values

Phase numbers 1-8 (phase-specific meaning depends on wave):
- Example: DEVELOP wave phases = 1-8 of development TDD cycle
- Example: DESIGN wave phases = 1-8 of architecture phases

### Context Field

**Purpose**: Optional execution context/scope

**Values**: Free-form strings describing execution context
- `'TDD cycle'`: Indicates skill is used during TDD development
- `'refactoring improvement'`: Indicates skill relates to refactoring
- `'testing automation'`: Indicates skill relates to test automation

**Examples**:
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

workflow_integration={
    'wave': 'DELIVER',
    'phase': 7
    # context omitted if not relevant
}
```

### Parsing YAML

```yaml
workflow_integration:
  wave: DEVELOP
  phase: 3
  context: TDD cycle

# Parsed to Python dict:
{
    'wave': 'DEVELOP',
    'phase': 3,
    'context': 'TDD cycle'
}
```

### Validation Rules

Parser MUST enforce:
```python
# Required fields
assert 'wave' in workflow_integration, "Missing 'wave' field"
assert 'phase' in workflow_integration, "Missing 'phase' field"

# Wave validation
valid_waves = ['DISCUSS', 'DESIGN', 'DEVELOP', 'DISTILL', 'DELIVER']
assert workflow_integration['wave'] in valid_waves, \
    f"Invalid wave '{workflow_integration['wave']}'"

# Phase validation
assert isinstance(workflow_integration['phase'], int), \
    "Phase must be integer"
assert 1 <= workflow_integration['phase'] <= 8, \
    "Phase must be between 1 and 8"

# Context is optional
# (no validation needed if present)
```

---

## Summary Table

| Aspect | Definition | Status |
|--------|-----------|--------|
| **Skill Data Structure** | TypedDict with id, name, type, triggers, agent_association, workflow_integration | ✅ DEFINED |
| **Output Format** | SKILL.md with YAML frontmatter + sections | ✅ DEFINED |
| **Trigger Patterns** | Regex strings, case-insensitive, partial match, OR logic | ✅ DEFINED |
| **Pattern Validation** | YAML escaping rules, regex validation | ✅ DEFINED |
| **Agent Association (1:1)** | Single agent string | ✅ DEFINED |
| **Agent Association (1:N)** | List of agent strings | ✅ DEFINED |
| **Agent Association (N:M)** | Reserved for future extension | 📋 RESERVED |
| **Workflow Integration** | Dict with wave (str), phase (int), context (optional str) | ✅ DEFINED |
| **Wave Values** | DISCUSS, DESIGN, DEVELOP, DISTILL, DELIVER | ✅ DEFINED |
| **Phase Numbers** | 1-8 | ✅ DEFINED |
| **Context Field** | Optional free-form string | ✅ DEFINED |

---

## Impact on Phase 1 Steps

### Step 01-04: Create Skill Jinja2 Template

**Now Unblocked**:
- ✅ Skill data structure known → can write outer_test with proper data
- ✅ Skill output format defined → can validate template output
- ✅ Trigger pattern semantics clear → AC2 is measurable
- ✅ Agent association model defined → AC3 is measurable
- ✅ Workflow integration requirements defined → AC4 is measurable

**Acceptance Criteria** (now measurable):
1. Template produces valid YAML frontmatter with all required fields
2. Triggers rendered as YAML list with regex patterns properly escaped
3. Agent association rendered as string (1:1) or YAML list (1:N)
4. Workflow integration renders wave, phase, context fields
5. Output is valid SKILL.md format per skill-markdown-format.md

### Step 01-05: Create TOON Compiler

**Now Unblocked**:
- ✅ Knows expected skill template output structure
- ✅ Can route skill type to correct template
- ✅ Can validate output against type-specific schemas

### Step 01-06: Infrastructure Integration Tests

**Now Unblocked**:
- ✅ Can write integration tests with real skill data
- ✅ Can validate output against skill-markdown-format.md spec
- ✅ Can test trigger pattern rendering correctly

---

## Version History

- **v1.0** (2026-01-14): Complete skills architecture specification
  - Skill data structure with TypedDict
  - Skill markdown format with examples
  - Trigger pattern semantics (regex, OR logic, escaping)
  - Agent association models (1:1, 1:N, N:M reserved)
  - Workflow integration with wave/phase/context
  - All validation rules and examples
  - Unblocks Phase 1 steps 01-04, 01-05, 01-06
