---
agent-activation:
  required: true
  agent-id: solution-architect
  agent-name: "Morgan"
  agent-command: "*design-architecture"
  auto-activate: true
---

# DW-DESIGN: Architecture Design with Visual Representation

**Wave**: DESIGN
**Agent**: Morgan (solution-architect)
**Command**: `*design-architecture`

## Overview

Execute DESIGN wave of nWave methodology through comprehensive architecture design, technology selection, and visual representation creation. Transforms business requirements into robust technical architecture balancing business needs with technical excellence.

Architecture serves business objectives while enabling quality attributes (performance, security, reliability, scalability).

## Context Files Required

- docs/requirements/requirements.md - (from DISCUSS wave)
- docs/requirements/user-stories.md - (from DISCUSS wave)
- docs/architecture/constraints.md - Technical and business constraints

## Previous Artifacts (Wave Handoff)

- docs/requirements/requirements.md - (from DISCUSS wave)
- docs/requirements/user-stories.md - (from DISCUSS wave)
- docs/requirements/domain-model.md - (from DISCUSS wave)

## Agent Invocation

@solution-architect

Execute \*design-architecture for {feature-name}.

**Context Files:**

- docs/requirements/requirements.md
- docs/requirements/user-stories.md
- docs/architecture/constraints.md

**Previous Artifacts:**

- docs/requirements/requirements.md
- docs/requirements/user-stories.md
- docs/requirements/domain-model.md

**Configuration:**

- interactive: moderate
- output_format: markdown
- diagram_format: c4
- architecture: hexagonal

## Success Criteria

Refer to Morgan's quality gates in nWave/agents/solution-architect.md.

**Key Validations:**

- [ ] Architecture supports all business requirements
- [ ] Technology stack selected with clear rationale
- [ ] Component boundaries defined (hexagonal architecture)
- [ ] Visual diagrams complete and accessible
- [ ] Handoff accepted by acceptance-designer (DISTILL wave)
- [ ] Layer 4 peer review approval obtained

## Next Wave

**Handoff To**: acceptance-designer (DISTILL wave)
**Deliverables**: See Morgan's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/architecture/architecture-design.md

# - docs/architecture/technology-stack.md

# - docs/architecture/component-boundaries.md

# - docs/architecture/diagrams/\*.svg
