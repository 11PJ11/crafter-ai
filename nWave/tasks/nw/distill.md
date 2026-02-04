---
description: 'Acceptance test creation and business validation [story-id] - Optional:
  --test-framework=[cucumber|specflow|pytest-bdd] --integration=[real-services|mocks]'
argument-hint: '[story-id] - Optional: --test-framework=[cucumber|specflow|pytest-bdd]
  --integration=[real-services|mocks]'
---

# /distill Command

**Wave**: DISTILL
**Description**: Acceptance test creation and business validation

**Wave Progress**: 4/6
**Primary Agents**: acceptance-designer
**Expected Outputs**: acceptance_tests, test_scenarios

## Implementation
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

## Test Directory Structure

### IMPORTANT: Ask User for Feature Type

Before creating acceptance tests, the orchestrator MUST ask the user:

> "Is this a **nWave core feature**, a **plugin feature**, or **bug testing**?"

Based on the answer, use the appropriate directory structure.

### Option A: nWave Core Feature

For core nWave features (agents, commands, installer, etc.):

```
tests/nWave/<feature-name>/acceptance/
├── walking-skeleton.feature       # Minimal E2E path (implement FIRST)
├── milestone-1.feature            # Scenarios for milestone 1
├── milestone-2.feature            # Scenarios for milestone 2
├── ...
├── integration-checkpoints.feature # Cross-milestone validation
└── steps/
    ├── conftest.py                # Pytest fixtures and configuration
    ├── plugin_steps.py            # Plugin-related step definitions
    ├── installer_steps.py         # Installer-related step definitions
    ├── verification_steps.py      # Verification-related step definitions
    └── common_steps.py            # Shared step definitions
```

**Example**: For `plugin-architecture` feature:
```
tests/nWave/plugin-architecture/acceptance/
├── walking-skeleton.feature
├── milestone-1-infrastructure.feature
├── milestone-2-wrapper-plugins.feature
├── milestone-3-switchover.feature
├── milestone-4-des-plugin.feature
├── milestone-5-ecosystem.feature
├── milestone-6-deployment.feature
├── integration-checkpoints.feature
└── steps/
    ├── conftest.py
    ├── plugin_steps.py
    ├── installer_steps.py
    ├── registry_steps.py
    └── verification_steps.py
```

### Option B: Plugin Feature

For plugin-specific features (DES, mutation testing, etc.):

```
tests/plugins/<plugin-name>/<feature-name>/acceptance/
├── walking-skeleton.feature
├── milestone-1.feature
├── milestone-2.feature
├── ...
└── steps/
    ├── conftest.py
    ├── hook_steps.py              # Hook-related step definitions
    ├── validation_steps.py        # Validation-related step definitions
    ├── enforcement_steps.py       # Enforcement-related step definitions
    └── common_steps.py            # Shared step definitions
```

**Example**: For DES `hook-enforcement` feature:
```
tests/plugins/des/hook-enforcement/acceptance/
├── walking-skeleton.feature
├── milestone-1-pretask-hook.feature
├── milestone-2-validation.feature
├── milestone-3-enforcement.feature
└── steps/
    ├── conftest.py
    ├── hook_steps.py
    ├── validation_steps.py
    ├── enforcement_steps.py
    └── orchestrator_steps.py
```

### Option C: Bug Testing

For bug-specific acceptance tests (testing bugs before fixing them):

```
tests/bugs/<context>/<subcontext>/<feature>/acceptance/
├── bug-1-<description>.feature    # Test for bug 1
├── bug-2-<description>.feature    # Test for bug 2
├── bug-3-<description>.feature    # Test for bug 3
├── ...
└── steps/
    ├── conftest.py
    ├── common_steps.py            # Shared step definitions
    ├── <domain>_steps.py          # Domain-specific steps
    └── helpers.py                 # Utility functions
```

**Example**: For DES installation bugs:
```
tests/bugs/plugins/des/installation/acceptance/
├── walking-skeleton.feature       # OPTIONAL for bugs
├── bug-1-hook-idempotency.feature
├── bug-2-audit-logs-location.feature
├── bug-3-import-paths.feature
└── steps/
    ├── conftest.py
    ├── common_steps.py
    ├── hook_steps.py
    ├── audit_log_steps.py
    ├── import_path_steps.py
    └── helpers.py
```

**Key Differences for Bug Testing**:
- Walking skeleton is **OPTIONAL** (not required for bug tests)
- Tests should **FAIL when bugs are present** (current state)
- Tests should **PASS when bugs are fixed** (future state)
- Context hierarchy: `<context>/<subcontext>/<feature>` (e.g., `plugins/des/installation`)
- Feature files named: `bug-{N}-{description}.feature`

### File Naming Conventions

**Feature Files** (multiple per milestone):
- `walking-skeleton.feature` - Minimal E2E path (always first)
- `milestone-{N}-{description}.feature` - Scenarios grouped by milestone
- `integration-checkpoints.feature` - Cross-milestone validation scenarios
- `error-handling.feature` - Error path scenarios (optional, can be in milestone files)

**Step Definition Files** (multiple per domain):
- `conftest.py` - Pytest-bdd fixtures, hooks, and configuration
- `{domain}_steps.py` - Domain-specific step definitions
- `common_steps.py` - Shared/reusable step definitions

### Walking Skeleton Priority

**For Features (nWave core & plugins)**: The walking skeleton MUST be:
1. In a **separate file** (`walking-skeleton.feature`)
2. The **first file created**
3. The **first test implemented** (before any milestone scenarios)
4. **Minimal** - ONE scenario proving E2E path works

**For Bug Testing**: Walking skeleton is **OPTIONAL**
- May be useful to verify test infrastructure
- Not required if bugs are already well-isolated
- Focus on tests that fail when bugs are present

### Orchestrator Question Template

```
Before creating acceptance tests, please answer:

**Test Type**:
- [ ] nWave core feature (installer, agents, commands, etc.)
- [ ] Plugin feature (DES, mutation testing, etc.)
- [ ] Bug testing (acceptance tests for bugs before fixing)

If plugin feature:
- Plugin name: _____________
- Feature name: _____________

If bug testing:
- Context: _____________ (e.g., plugins, nWave, tools)
- Subcontext: _____________ (e.g., des, installer, cli)
- Feature: _____________ (e.g., installation, hooks, config)
- Walking skeleton needed? [ ] Yes [ ] No
```

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

## Expected Outputs

### For nWave Core Features

```
tests/nWave/{feature-name}/acceptance/
├── walking-skeleton.feature              # Minimal E2E (implement FIRST)
├── milestone-{N}-{description}.feature   # Per-milestone scenarios
├── integration-checkpoints.feature       # Cross-milestone validation
└── steps/
    ├── conftest.py                       # Fixtures and configuration
    └── {domain}_steps.py                 # Domain-specific steps
```

### For Plugin Features

```
tests/plugins/{plugin-name}/{feature-name}/acceptance/
├── walking-skeleton.feature              # Minimal E2E (implement FIRST)
├── milestone-{N}-{description}.feature   # Per-milestone scenarios
└── steps/
    ├── conftest.py                       # Fixtures and configuration
    └── {domain}_steps.py                 # Domain-specific steps
```

### For Bug Testing

```
tests/bugs/{context}/{subcontext}/{feature}/acceptance/
├── walking-skeleton.feature              # OPTIONAL for bugs
├── bug-{N}-{description}.feature         # One per bug
└── steps/
    ├── conftest.py                       # Fixtures and configuration
    ├── common_steps.py                   # Shared steps
    ├── {domain}_steps.py                 # Domain-specific steps
    └── helpers.py                        # Utility functions
```

### Documentation Artifacts (in docs/feature/)

```
docs/feature/{feature-name}/distill/
├── test-scenarios.md                     # Summary of all scenarios
├── walking-skeleton.md                   # Walking skeleton definition
└── acceptance-review.md                  # Review feedback and approval
```

### Implementation Order

1. **Walking Skeleton** - `walking-skeleton.feature` + minimal steps
2. **Milestone 1** - `milestone-1-*.feature` + domain steps
3. **Milestone 2** - `milestone-2-*.feature` + additional steps
4. ... (continue per milestone)
5. **Integration Checkpoints** - `integration-checkpoints.feature`
6. **Error Handling** - distributed in milestone files or separate

### Step Definition Organization

Group step definitions by **domain**, not by feature file:

```python
# steps/plugin_steps.py
@given('plugin infrastructure exists')
@given('AgentsPlugin is implemented')
@when('I register AgentsPlugin with the registry')

# steps/installer_steps.py
@given('nWave installer is at version "{version}"')
@when('I run install_nwave.py with full plugin installation')

# steps/verification_steps.py
@then('AgentsPlugin.verify() returns success')
@then('all plugins verify successfully')

# steps/common_steps.py (reusable across features)
@given('a clean installation directory exists')
@then('no errors are reported')
```

This organization enables step reuse across multiple feature files.
