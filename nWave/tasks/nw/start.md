---
agent-activation:
  required: true
  agent-id: product-owner
  agent-name: "Riley"
  agent-command: "*gather-requirements"
  auto-activate: true
---

# DW-START: Initialize nWave Workflow

**Wave**: CROSS_WAVE (project initialization)
**Agent**: Riley (product-owner)
**Command**: `*gather-requirements`

## Overview

Initialize nWave methodology workflow with project brief creation, stakeholder alignment, and workspace preparation for systematic feature development.

Establishes project foundation through context gathering, stakeholder identification, and success criteria definition before entering DISCUSS wave.

## Context Files Required

- None (project initialization creates initial context)

## Previous Artifacts (Wave Handoff)

- None (starting point for nWave methodology)

## Agent Invocation

@product-owner

Execute \*gather-requirements for project initialization.

**Context Files:**

- (none - will be created)

**Configuration:**

- template: greenfield # greenfield/brownfield
- scope: small # small/medium/large
- output_directory: docs/

## Success Criteria

Refer to Riley's quality gates in nWave/agents/product-owner.md (Project Initialization section).

**Key Validations:**

- [ ] Project brief created and validated
- [ ] Stakeholders identified and roles defined
- [ ] Success criteria established
- [ ] Workspace structure prepared
- [ ] Ready to proceed to DISCUSS wave

## Next Wave

**Handoff To**: DISCUSS wave (formal requirements gathering)
**Deliverables**: Project brief and workspace foundation

# Expected outputs (reference only):

# - docs/project-brief.md

# - docs/stakeholders.yaml

# - docs/architecture/constraints.md
