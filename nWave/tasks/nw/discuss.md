---
agent-activation:
  required: true
  agent-id: product-owner
  agent-name: "Riley"
  agent-command: "*gather-requirements"
  auto-activate: true
---

# DW-DISCUSS: Requirements Gathering and Business Analysis

**Wave**: DISCUSS
**Agent**: Riley (product-owner)
**Command**: `*gather-requirements`

## Overview

Execute DISCUSS wave of nWave methodology through comprehensive requirements gathering, stakeholder collaboration, and business analysis. Establishes ATDD foundation (Customer-Developer-Tester collaboration) for all subsequent waves.

The DISCUSS wave creates shared understanding between stakeholders, developers, and testers through collaborative requirements elicitation, user story creation, and acceptance criteria definition.

## Context Files Required

- docs/project-brief.md - Project context and objectives
- docs/stakeholders.yaml - Stakeholder identification and roles
- docs/architecture/constraints.md - Technical and business constraints

## Previous Artifacts (Wave Handoff)

- None (DISCUSS is the first wave in nWave)

## Agent Invocation

@product-owner

Execute \*gather-requirements for {feature-name}.

**Context Files:**

- docs/project-brief.md
- docs/stakeholders.yaml
- docs/architecture/constraints.md

**Configuration:**

- interactive: high
- output_format: markdown
- elicitation_depth: comprehensive

## Success Criteria

Refer to Riley's quality gates in nWave/agents/product-owner.md.

**Key Validations:**

- [ ] Requirements completeness score > 0.95
- [ ] Stakeholder consensus achieved
- [ ] All acceptance criteria testable
- [ ] Handoff accepted by solution-architect (DESIGN wave)
- [ ] Layer 4 peer review approval obtained

## Next Wave

**Handoff To**: solution-architect (DESIGN wave)
**Deliverables**: See Riley's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/requirements/requirements.md

# - docs/requirements/user-stories.md

# - docs/requirements/acceptance-criteria.md
