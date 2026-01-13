# Command vs Agent Structural Differences

**Purpose**: Clarify structural and semantic differences between TOON agent and command files.
**Audience**: Template developers (step 01-02, 01-03), parser maintainers, QA reviewers
**Created**: 2026-01-13
**Coordinates with**: `parser_output.json` schema

---

## Quick Reference

| Aspect | Agent | Command |
|--------|-------|---------|
| **Type** | `type: "agent"` | `type: "command"` |
| **Purpose** | Define autonomous actor | Define invocable operation |
| **Activation** | Auto-activated by context | Explicitly invoked via `/command` |
| **Metadata** | name, id, role, spec, model | name, description, parent_agent, parameters, returns |
| **Sections** | core_rules, commands, dependencies, persona | prerequisites, workflow, success_criteria |

---

## Metadata Fields

### Agent Metadata
```typescript
{
  name: string           // Display name (e.g., "Crafty")
  id: string             // Identifier (e.g., "software-crafter")
  role: string           // Role description
  spec: string           // Specialization domain
  model: string          // Model configuration
  version: string        // TOON version
  description: string    // Brief description
}
```

### Command Metadata
```typescript
{
  name: string           // Command name (e.g., "develop")
  description: string    // What command does
  parent_agent: string   // Owner agent (e.g., "software-crafter")
  version: string        // TOON version
  parameters: [{         // Input parameters (agents don't have this)
    name: string
    type: string
    required: boolean
    description: string
  }]
  returns: {             // Return value spec (agents don't have this)
    type: string
    properties: {...}
  }
}
```

**KEY DIFFERENCE**: Commands have `parameters` and `returns` (like functions), agents have `role` and `spec` (like personas).

---

## Section Content

### Agent Sections (Common)
- **core_rules**: Fundamental operational rules
- **commands**: List of commands this agent can execute
- **dependencies**: Tasks and templates this agent requires
- **persona**: Role, style, communication patterns

**Example**:
```yaml
sections:
  core_rules:
    evidence_only: "Cite source for all claims"
    no_quant_claims: "No metrics without data"
  commands:
    - develop
    - refactor
    - mikado
  dependencies:
    tasks: [nw/develop.md, nw/mikado.md]
  persona:
    role: "Master Software Crafter"
    style: "Methodical, test-driven"
```

### Command Sections (Common)
- **prerequisites**: What must be true before command runs
- **workflow**: Sequence of steps command executes
- **success_criteria**: How to know command succeeded

**Example**:
```yaml
sections:
  prerequisites:
    - baseline approved
    - roadmap approved
  workflow:
    steps:
      - Validate baseline
      - Execute all steps
      - Finalize
  success_criteria:
    - All tests passing
    - All commits created
```

**KEY DIFFERENCE**: Commands define workflows (operational), agents define personas (behavioral).

---

## Template Rendering Implications

### Agent Template (01-02)
**Renders**:
- YAML frontmatter with `name`, `description`, `model`
- Activation notice section
- Agent YAML block with `commands`, `dependencies`, `persona`

**Does NOT render**:
- Parameters specification
- Returns specification
- Workflow steps

### Command Template (01-03)
**Renders**:
- Command invocation header with name, purpose
- Parent agent reference
- Parameters specification (input)
- Returns specification (output)
- Prerequisites checklist

**Does NOT render**:
- Persona configuration
- Core rules
- Activation notice (commands are explicitly invoked, not auto-activated)

---

## Validation Rules

### Agent Output Validation (from schema)
```json
{
  "required_frontmatter_keys": ["name", "description", "model"],
  "required_sections": ["activation_notice", "agent_yaml_block"],
  "agent_yaml_required_keys": ["commands", "dependencies", "persona"]
}
```

### Command Output Validation (from schema)
```json
{
  "required_frontmatter_keys": ["name", "description", "parent_agent"],
  "required_sections": ["invocation_header", "parameters_spec", "returns_spec"],
  "no_persona_section": true,
  "no_auto_activation": true
}
```

---

## Common Mistakes to Avoid

### ❌ WRONG: Treating commands like agents
```yaml
# Command file with agent-style metadata
## ID: develop
name: Develop Command
role: Development Orchestrator    # ❌ Commands don't have roles
persona:                          # ❌ Commands don't have personas
  style: "Systematic"
```

### ✅ CORRECT: Command with proper metadata
```yaml
## ID: develop
name: develop
description: Execute DEVELOP wave with 11-phase TDD
parent_agent: software-crafter     # ✓ Commands have parent agent
parameters:                        # ✓ Commands have parameters
  - name: feature-description
    type: string
```

### ❌ WRONG: Agent with command-style metadata
```yaml
## ID: software-crafter
name: Software Crafter
parent_agent: devop               # ❌ Agents don't have parent agents
parameters:                       # ❌ Agents don't have parameters
  - name: task
```

### ✅ CORRECT: Agent with proper metadata
```yaml
## ID: software-crafter
name: Crafty
role: Master Software Crafter     # ✓ Agents have roles
spec: TDD, Refactoring            # ✓ Agents have specializations
persona:                          # ✓ Agents have personas
  style: "Methodical, test-driven"
```

---

## Test Data Examples

See `parser_output.json` examples section for complete parsed data structures:
- Example 1: Agent (software-crafter)
- Example 2: Command (develop)

---

## References

- **Parser schema**: `tools/toon/schema/parser_output.json`
- **Parser implementation**: `tools/toon/parser.py`
- **Step 01-01**: TOON Parser Core
- **Step 01-02**: Agent Jinja2 Template
- **Step 01-03**: Command Jinja2 Template
