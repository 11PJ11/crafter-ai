# DW-DISCUSS: Requirements Gathering and Business Analysis

**Wave**: DISCUSS
**Agent**: Riley (nw-product-owner)
**Command**: `/nw:discuss`

## Overview

Execute DISCUSS wave (wave 2 of 6) through collaborative requirements gathering, user story creation, and acceptance criteria definition. Establishes ATDD foundation for subsequent waves.

For greenfield projects (no src/ code, no docs/feature/ history), Riley proposes a Walking Skeleton as Feature 0 to validate architecture end-to-end before functional features.

## Context Files Required

- docs/project-brief.md - Project context and objectives
- docs/stakeholders.yaml - Stakeholder identification and roles
- docs/architecture/constraints.md - Technical and business constraints

## Previous Artifacts (Wave Handoff)

- docs/discovery/problem-validation.md - From DISCOVER wave
- docs/discovery/opportunity-tree.md - From DISCOVER wave
- docs/discovery/lean-canvas.md - From DISCOVER wave

## Agent Invocation

@nw-product-owner

Execute `/nw:discuss` for {feature-name}.

**Context Files:**

- docs/project-brief.md
- docs/stakeholders.yaml
- docs/architecture/constraints.md

**Configuration:**

- interactive: high
- output_format: markdown
- elicitation_depth: comprehensive

## Success Criteria

Refer to Riley's quality gates in nWave/agents/nw-product-owner.md.

- [ ] Requirements completeness score > 0.95
- [ ] Stakeholder consensus achieved
- [ ] All acceptance criteria testable
- [ ] Handoff accepted by solution-architect (DESIGN wave)

## Next Wave

**Handoff To**: nw-solution-architect (DESIGN wave)
**Deliverables**: See Riley's handoff package specification in agent file

# Expected outputs:
# - docs/feature/{feature-name}/discuss/requirements.md
# - docs/feature/{feature-name}/discuss/user-stories.md
# - docs/feature/{feature-name}/discuss/acceptance-criteria.md
# - docs/feature/{feature-name}/discuss/dor-checklist.md
