---
agent-activation:
  required: true
  agent-id: acceptance-designer
  agent-name: "Quinn"
  agent-command: "*create-acceptance-tests"
  auto-activate: true
---

# DW-DISTILL: Acceptance Test Creation and Business Validation

**Wave**: DISTILL
**Agent**: Quinn (acceptance-designer)
**Command**: `*create-acceptance-tests`

## Overview

Execute DISTILL wave of 5D-Wave methodology through creation of E2E acceptance tests informed by architectural design and component boundaries using Given-When-Then format for business validation.

Creates executable specifications that bridge business requirements and technical implementation, providing living documentation of system behavior.

## Context Files Required

- docs/requirements/requirements.md - (from DISCUSS wave)
- docs/requirements/user-stories.md - (from DISCUSS wave)
- docs/architecture/architecture-design.md - (from DESIGN wave)
- docs/architecture/component-boundaries.md - (from DESIGN wave)

## Previous Artifacts (Wave Handoff)

- docs/architecture/architecture-design.md - (from DESIGN wave)
- docs/architecture/technology-stack.md - (from DESIGN wave)
- docs/architecture/component-boundaries.md - (from DESIGN wave)

## Agent Invocation

@acceptance-designer

Execute *create-acceptance-tests for {feature-name}.

**Context Files:**
- docs/requirements/requirements.md
- docs/requirements/user-stories.md
- docs/architecture/architecture-design.md
- docs/architecture/component-boundaries.md

**Previous Artifacts:**
- docs/architecture/architecture-design.md
- docs/architecture/technology-stack.md
- docs/architecture/component-boundaries.md

**Configuration:**
- interactive: moderate
- output_format: gherkin
- test_framework: specflow  # or cucumber/pytest-bdd
- production_integration: mandatory

## Success Criteria

Refer to Quinn's quality gates in 5d-wave/agents/acceptance-designer.md.

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
# - tests/acceptance/acceptance-tests.feature
# - tests/acceptance/step-definitions.cs
# - docs/testing/test-scenarios.md
