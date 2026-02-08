---
description: 'Acceptance test creation and business validation [story-id] - Optional:
  --test-framework=[cucumber|specflow|pytest-bdd] --integration=[real-services|mocks]'
argument-hint: '[story-id] - Optional: --test-framework=[cucumber|specflow|pytest-bdd]
  --integration=[real-services|mocks]'
---

# DW-DISTILL: Acceptance Test Creation and Business Validation

**Wave**: DISTILL
**Agent**: Quinn (nw-acceptance-designer)

## Overview

Create E2E acceptance tests from requirements and architecture using Given-When-Then format. Produces executable specifications that bridge business requirements and technical implementation.

## Pre-flight

Ask the user before dispatching:

> Is this a **nWave core feature**, a **plugin feature**, or **bug testing**?

This determines test directory structure (Quinn handles the mapping).

## Context Files Required

- docs/feature/{feature-name}/discuss/requirements.md
- docs/feature/{feature-name}/discuss/user-stories.md
- docs/feature/{feature-name}/design/architecture-design.md
- docs/feature/{feature-name}/design/component-boundaries.md
- docs/feature/{feature-name}/design/technology-stack.md

## Agent Invocation

@nw-acceptance-designer

Execute \*create-acceptance-tests for {feature-name}.

**Context Files:**

- docs/feature/{feature-name}/discuss/requirements.md
- docs/feature/{feature-name}/discuss/user-stories.md
- docs/feature/{feature-name}/design/architecture-design.md
- docs/feature/{feature-name}/design/component-boundaries.md

**Configuration:**

- test_type: core | plugin | bug
- test_framework: specflow | cucumber | pytest-bdd
- interactive: moderate
- output_format: gherkin

## Success Criteria

- [ ] All user stories have corresponding acceptance tests
- [ ] Step methods call real production services (no mocks at acceptance level)
- [ ] One-at-a-time implementation strategy established (@skip/@pending tags)
- [ ] Tests exercise driving ports, not internal components (hexagonal boundary)
- [ ] Walking skeleton created first (features only; optional for bugs)
- [ ] Handoff package ready for software-crafter (DEVELOP wave)

## Next Wave

**Handoff To**: nw-software-crafter (DEVELOP wave)
**Deliverables**: Feature files, step definitions, test-scenarios.md, walking-skeleton.md

## Expected Outputs

```
tests/{test-type-path}/{feature-name}/acceptance/
├── walking-skeleton.feature
├── milestone-{N}-{description}.feature
├── integration-checkpoints.feature
└── steps/
    ├── conftest.py
    └── {domain}_steps.py

docs/feature/{feature-name}/distill/
├── test-scenarios.md
├── walking-skeleton.md
└── acceptance-review.md
```
