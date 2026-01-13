# Agent Template Expected Output Examples

**Purpose**: Define expected output structure for agent.md.j2 template (step 01-02)
**Resolves**: Critical issues C1 (incomplete reference) and C4 (embedded knowledge spec)
**Audience**: Template developers, QA reviewers
**Created**: 2026-01-13

---

## Complete Agent Output Structure

### Example 1: Software Crafter Agent

```markdown
# Software Crafter Agent

<!-- version: 1.0.0 -->

**Agent**: Master software craftsmanship specialist with expertise in TDD, refactoring, and systematic quality improvement.

## ⚡ Agent Activation

This agent is automatically available when you need software craftsmanship expertise.

**Auto-activation triggers**:
- Questions about TDD, refactoring, or code quality
- Requests for systematic development workflows
- Complex refactoring challenges

**Manual invocation**: `@software-crafter` (in conversation context)

---

## Agent Configuration

```yaml
agent:
  name: "Crafty"
  id: "software-crafter"
  model: "claude-sonnet-4.5"
  description: "Unified Software Craftsmanship Specialist"
  role: "Master Software Crafter"
  specialization: "TDD, Refactoring, Quality"

commands:
  - name: "develop"
    description: "Execute complete DEVELOP wave with 11-phase TDD"
  - name: "refactor"
    description: "Apply systematic refactoring using Mikado Method"
  - name: "mikado"
    description: "Create refactoring roadmap for complex changes"

dependencies:
  tasks:
    - "nw/develop.md"
    - "nw/refactor.md"
    - "nw/mikado.md"
  templates:
    - "develop-outside-in-tdd.yaml"
    - "mikado-method-progressive-refactoring.yaml"

persona:
  role: "Master Software Crafter"
  style: "Methodical, test-driven, quality-obsessed"
  communication: "Clear, evidence-based, professional"
  values:
    - "Tests MUST pass before commit"
    - "Quality saves time, money, lives"
    - "Evidence over assumptions"

core_rules:
  evidence_only: "Cite source for all claims"
  no_quant_claims: "No percentages/metrics without measurement"
  confidence_levels: "HIGH/MED/LOW with justification"
```

---

<!-- BUILD:INJECT:START:data/embed/software-crafter/outside-in-tdd-methodology.md -->
## Outside-In TDD Methodology

[Content injected here by build process]
<!-- BUILD:INJECT:END:data/embed/software-crafter/outside-in-tdd-methodology.md -->

<!-- BUILD:INJECT:START:data/embed/software-crafter/refactoring-patterns-catalog.md -->
## Refactoring Patterns Catalog

[Content injected here by build process]
<!-- BUILD:INJECT:END:data/embed/software-crafter/refactoring-patterns-catalog.md -->

---

*This agent was generated from TOON source by AI-Craft nWave framework*
```

---

## YAML Frontmatter Requirements

**Mandatory keys** (from schema validation rules):
- `name`: Agent display name
- `description`: Brief description (1-2 sentences)
- `model`: Claude model specification

**Example**:
```yaml
---
name: "Software Crafter"
description: "Master software craftsmanship specialist with expertise in TDD, refactoring, and systematic quality improvement."
model: "claude-sonnet-4.5"
---
```

---

## Activation Notice Structure

**Purpose**: Explain how agent is activated (auto vs manual)

**Required elements**:
1. Section header: `## ⚡ Agent Activation`
2. Brief description
3. Auto-activation triggers (bullet list)
4. Manual invocation syntax

**Template**:
```markdown
## ⚡ Agent Activation

This agent is automatically available when you need {domain} expertise.

**Auto-activation triggers**:
- {trigger 1}
- {trigger 2}
- {trigger 3}

**Manual invocation**: `@{agent-id}` (in conversation context)
```

---

## Agent YAML Block Structure

**Purpose**: Define agent configuration in structured YAML

**Required top-level keys** (from validation rules):
- `agent`: Metadata (name, id, model, description, role, specialization)
- `commands`: List of command definitions
- `dependencies`: Tasks and templates required
- `persona`: Role, style, communication, values

**Optional keys**:
- `core_rules`: Fundamental operational rules
- `workflows`: Predefined workflows
- `knowledge_domains`: Areas of expertise

**Example**:
```yaml
agent:
  name: "Agent Name"
  id: "agent-id"
  model: "claude-sonnet-4.5"
  description: "Brief description"
  role: "Role title"
  specialization: "Domain areas"

commands:
  - name: "command1"
    description: "What command does"
  - name: "command2"
    description: "What command does"

dependencies:
  tasks: ["task1.md", "task2.md"]
  templates: ["template1.yaml"]

persona:
  role: "Role title"
  style: "Communication style"
  communication: "Tone and approach"
  values:
    - "Core value 1"
    - "Core value 2"
```

---

## Embedded Knowledge Injection Markers

**Purpose**: Mark locations where build process should inject content files

**Marker format** (EXACT syntax):
```markdown
<!-- BUILD:INJECT:START:relative/path/to/file.md -->
{Content injected here by compiler at build time}
<!-- BUILD:INJECT:END:relative/path/to/file.md -->
```

**Rules**:
1. **Exact format**: `BUILD:INJECT:START:path` and `BUILD:INJECT:END:path`
2. **Path must match** in START and END markers
3. **Relative path** from `nWave/data/embed/{agent-id}/` directory
4. **Markers preserved** in template output, content injected by compiler
5. **Whitespace**: No leading/trailing spaces in comment tags

**Valid examples**:
```markdown
<!-- BUILD:INJECT:START:outside-in-tdd-methodology.md -->
<!-- BUILD:INJECT:END:outside-in-tdd-methodology.md -->

<!-- BUILD:INJECT:START:refactoring-patterns-catalog.md -->
<!-- BUILD:INJECT:END:refactoring-patterns-catalog.md -->

<!-- BUILD:INJECT:START:critique-dimensions.md -->
<!-- BUILD:INJECT:END:critique-dimensions.md -->
```

**Invalid examples** (will fail validation):
```markdown
<!-- BUILD:INJECT:outside-in-tdd.md -->         ❌ Missing START/END
<!-- BUILD:INJECT START: file.md -->            ❌ Wrong separator
<!-- BUILD:INJECT:START:file.md-->              ❌ Missing space before -->
<!--BUILD:INJECT:START:file.md -->              ❌ Missing space after <!--
<!-- BUILD:INJECT:START:/absolute/path.md -->   ❌ Absolute path
```

**Placement**:
- After agent YAML block
- Before footer
- One section per knowledge domain
- Maintain document flow and readability

---

## YAML Special Character Escaping

**Critical**: YAML parsers fail on unescaped special characters in strings.

**Characters requiring escaping**:
- `:` (colon) → Use quotes: `"Description: with colon"`
- `"` (double quote) → Escape: `"Description with \"quotes\""`
- `'` (single quote in single-quoted string) → Escape: `'Description with ''quotes'''`
- `\n` (newline) → Use literal block scalar `|` or folded scalar `>`

**Examples**:

### ❌ WRONG (will break YAML parsing):
```yaml
description: This is a description: with colon
command: Validate: configuration and report
note: He said "hello"
```

### ✅ CORRECT:
```yaml
description: "This is a description: with colon"
command: "Validate: configuration and report"
note: 'He said "hello"'
# OR for multiline:
description: |
  This is a multiline description
  with proper YAML formatting
```

---

## Multiline String Handling

**Use literal block scalar (`|`) for multiline content**:

```yaml
description: |
  First line of description
  Second line of description
  Third line of description
```

**Use folded scalar (`>`) for long paragraphs**:

```yaml
description: >
  This is a very long description that would wrap
  across multiple lines but should be treated as
  a single paragraph when rendered.
```

---

## Validation Checklist (step 01-02 acceptance criteria)

When template renders, output MUST satisfy:

- [ ] ✓ Valid YAML frontmatter with keys: `name`, `description`, `model`
- [ ] ✓ Activation notice section present with structure defined above
- [ ] ✓ Agent YAML block with keys: `agent`, `commands`, `dependencies`, `persona`
- [ ] ✓ All YAML special characters properly escaped (no parse errors)
- [ ] ✓ Multiline strings use `|` or `>` syntax
- [ ] ✓ Embedded knowledge markers match exact format: `<!-- BUILD:INJECT:START:path -->`
- [ ] ✓ Command definitions include both `name` and `description`
- [ ] ✓ No missing required fields (template handles gracefully or errors clearly)

---

## References

- **Parser output schema**: `tools/toon/schema/parser_output.json`
- **Command vs Agent differences**: `tools/toon/schema/command-vs-agent-differences.md`
- **Step 01-02**: Agent Jinja2 Template
- **Validation rules**: See `parser_output.json` → `validationRules.agent_output`
