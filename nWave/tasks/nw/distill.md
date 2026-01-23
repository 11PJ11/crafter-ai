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
- [ ] Handoff accepted by software-crafter (DEVELOP wave)
- [ ] Layer 4 peer review approval obtained

## Next Wave

**Handoff To**: software-crafter (DEVELOP wave)
**Deliverables**: See Quinn's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/feature/{feature-name}/distill/acceptance-tests.feature

# - docs/feature/{feature-name}/distill/step-definitions.{language}

# - docs/feature/{feature-name}/distill/test-scenarios.md
