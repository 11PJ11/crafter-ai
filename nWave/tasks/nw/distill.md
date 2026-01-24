# DW-DISTILL: Acceptance Test Creation and Business Validation

**Wave**: DISTILL
**Agent**: Quinn (acceptance-designer)
**Command**: `*create-acceptance-tests`

## Overview

Execute DISTILL wave of nWave methodology through creation of E2E acceptance tests informed by architectural design and component boundaries using Given-When-Then format for business validation.

Creates executable specifications that bridge business requirements and technical implementation, providing living documentation of system behavior.

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

1. **Read all requirements, user stories, and architecture files** and embed complete context inline
2. **Create a complete agent prompt** that includes:
   - Full requirements.md and user-stories.md content (inline, not paths)
   - Complete architecture design and component boundaries (inline)
   - BDD/Gherkin syntax specification and Given-When-Then format rules
   - Acceptance criteria transformation procedures
   - Step definition template patterns for production service integration
   - Test framework specifications (SpecFlow, Cucumber, pytest-bdd) with syntax examples
   - One-at-a-time implementation strategy procedures
   - All deliverable formats and test scenario structure
3. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
4. **Embed all acceptance test creation procedures** - agent executes directly, no command delegation

### Agent Prompt Must Contain

- Full requirements.md content (inline, not path reference)
- Complete user stories with acceptance criteria (inline)
- Full architecture design and component boundaries (inline)
- BDD/Gherkin syntax specification with complete syntax rules
- Given-When-Then scenario format with concrete examples
- Step definition implementation patterns (production service integration mandatory)
- Test framework selection procedure (with SpecFlow/Cucumber/pytest-bdd inline specifications)
- One-at-a-time feature implementation strategy (enable one scenario at a time using @skip/@pending/@ignore)
- Production service integration pattern for step methods (GetRequiredService pattern)
- Step method naming conventions and business language requirements
- Expected deliverables with file paths and content structure
- Quality gate criteria for acceptance test completeness and alignment

### What NOT to Include

- ❌ "Agent should invoke /nw:develop after acceptance tests created"
- ❌ "Use /nw:execute to run the acceptance tests"
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without full content embedded (agent needs requirements/design content inline)
- ❌ Test framework tool references without complete syntax specifications embedded

### Example: What TO Do

✅ "Create BDD acceptance tests from these requirements: [FULL REQUIREMENTS]"
✅ "Transform user stories to Gherkin scenarios following this syntax: [COMPLETE GIVEN-WHEN-THEN RULES WITH EXAMPLES]"
✅ "Implement step methods calling production services using this pattern: [PATTERN WITH SERVICE PROVIDER INJECTION EXAMPLE]"
✅ "Structure test scenarios following one-at-a-time strategy: [COMPLETE IMPLEMENTATION PROCEDURE]"
✅ "Provide these test deliverables: acceptance-tests.feature, step-definitions.{language}, test-scenarios.md"

## Context Files Required

- docs/feature/{feature-name}/discuss/requirements.md - (from DISCUSS wave)
- docs/feature/{feature-name}/discuss/user-stories.md - (from DISCUSS wave)
- docs/feature/{feature-name}/design/architecture-design.md - (from DESIGN wave)
- docs/feature/{feature-name}/design/component-boundaries.md - (from DESIGN wave)

## Previous Artifacts (Wave Handoff)

- docs/feature/{feature-name}/design/architecture-design.md - (from DESIGN wave)
- docs/feature/{feature-name}/design/technology-stack.md - (from DESIGN wave)
- docs/feature/{feature-name}/design/component-boundaries.md - (from DESIGN wave)

## Agent Invocation

@acceptance-designer

Execute \*create-acceptance-tests for {feature-name}.

**Context Files:**

- docs/feature/{feature-name}/discuss/requirements.md
- docs/feature/{feature-name}/discuss/user-stories.md
- docs/feature/{feature-name}/design/architecture-design.md
- docs/feature/{feature-name}/design/component-boundaries.md

**Previous Artifacts:**

- docs/feature/{feature-name}/design/architecture-design.md
- docs/feature/{feature-name}/design/technology-stack.md
- docs/feature/{feature-name}/design/component-boundaries.md

**Configuration:**

- interactive: moderate
- output_format: gherkin
- test_framework: specflow # or cucumber/pytest-bdd
- production_integration: mandatory

## Success Criteria

Refer to Quinn's quality gates in nWave/agents/acceptance-designer.md.

**Key Validations:**

- [ ] All user stories have acceptance tests
- [ ] Step methods call real production services
- [ ] One-at-a-time implementation strategy established
- [ ] Architecture-informed test structure respects component boundaries
- [ ] **Hexagonal boundary check passed (CM-A)** - see below
- [ ] Handoff accepted by software-crafter (DEVELOP wave)
- [ ] Layer 4 peer review approval obtained

## CM-A: Hexagonal Boundary Enforcement (MANDATORY)

**CRITICAL**: Acceptance tests MUST exercise driving ports, not internal components.

### The Problem This Solves

Acceptance tests written at the wrong boundary (internal components instead of driving ports) can:
- Pass 100% while the feature remains non-functional
- Create "Testing Theatre" - high metrics with false confidence
- Miss integration issues entirely

### Boundary Validation Criteria

**Acceptance tests MUST**:
1. Import entry-point modules (driving ports)
2. Exercise the system from user perspective
3. Verify observable system behavior

**Acceptance tests MUST NOT**:
1. Import internal components directly
2. Test implementation details instead of behavior
3. Bypass the system entry point

### Validation Check

```yaml
hexagonal_boundary_check:
  criterion: "Acceptance tests must exercise driving ports"

  validation:
    - "Tests import entry-point modules (e.g., DESOrchestrator, API client)"
    - "Tests do NOT import internal components directly"

  violation_examples:
    - "from des.validator import TemplateValidator"     # WRONG - internal component
    - "from internal.service import BusinessLogic"       # WRONG - internal component

  correct_examples:
    - "from des.orchestrator import DESOrchestrator"    # CORRECT - driving port
    - "from api.client import FeatureClient"            # CORRECT - driving port

  gate_failure:
    action: "REJECT acceptance tests"
    reason: "Tests at wrong boundary - would produce non-functional feature"
    required_fix: "Rewrite tests to invoke through system entry point"
```

### Review Question

Before finalizing acceptance tests, ask:

> "Do these tests import the USER-FACING ENTRY POINT, or do they directly instantiate internal components?"

If tests directly instantiate internal components (e.g., `validator = TemplateValidator()`), they are at the WRONG BOUNDARY and must be rewritten.

### Example: Correct vs Incorrect

**INCORRECT** (tests internal component):
```python
# tests/acceptance/test_validation.py
from des.validator import TemplateValidator  # WRONG - internal component

def test_validation_blocks_invalid_prompt():
    validator = TemplateValidator()  # WRONG - direct instantiation
    result = validator.validate_prompt(prompt)
    assert result.task_invocation_allowed == False
```

**CORRECT** (tests through driving port):
```python
# tests/acceptance/test_validation.py
from des.orchestrator import DESOrchestrator  # CORRECT - entry point

def test_validation_blocks_invalid_prompt():
    orchestrator = DESOrchestrator()  # CORRECT - system entry point
    result = orchestrator.render_prompt("/nw:execute", step_file="...")
    assert result["task_invocation_allowed"] == False
```

## Next Wave

**Handoff To**: software-crafter (DEVELOP wave)
**Deliverables**: See Quinn's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/feature/{feature-name}/distill/acceptance-tests.feature

# - docs/feature/{feature-name}/distill/step-definitions.{language}

# - docs/feature/{feature-name}/distill/test-scenarios.md
