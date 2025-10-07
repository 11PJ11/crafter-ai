---
agent-activation:
  required: true
  agent-id: business-analyst
  agent-name: "Riley"
  agent-command: "*gather-requirements"
  auto-activate: true
---

# DW-START: Initialize 5D-Wave Workflow

**Wave**: CROSS_WAVE (project initialization)
**Agent**: Riley (business-analyst)
**Command**: `*gather-requirements`

## Overview

Initialize 5D-Wave methodology workflow with project brief creation, stakeholder alignment, and workspace preparation for systematic feature development.

Establishes project foundation through context gathering, stakeholder identification, and success criteria definition before entering DISCUSS wave.

## Context Files Required

- None (project initialization creates initial context)

## Previous Artifacts (Wave Handoff)

- None (starting point for 5D-Wave methodology)

## Agent Invocation

@business-analyst

Execute *gather-requirements for project initialization.

**Context Files:**
- (none - will be created)

**Configuration:**
- template: greenfield  # greenfield/brownfield
- scope: small  # small/medium/large
- output_directory: docs/

## Success Criteria

Refer to Riley's quality gates in 5d-wave/agents/business-analyst.md (Project Initialization section).

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
