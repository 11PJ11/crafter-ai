# DW-DESIGN: Architecture Design with Visual Representation

**Wave**: DESIGN
**Agent**: Morgan (nw-solution-architect)
**Command**: `*design-architecture`

## Overview

Execute DESIGN wave through architecture design, technology selection, and C4 visual representation. Transforms business requirements into technical architecture balancing business needs with quality attributes.

Morgan analyzes the existing codebase and evaluates open-source alternatives before designing new components. Integration-first mindset is part of the agent's methodology.

## Context Files Required

- docs/feature/{feature-name}/discuss/requirements.md - From DISCUSS wave
- docs/feature/{feature-name}/discuss/user-stories.md - From DISCUSS wave
- docs/feature/{feature-name}/discuss/domain-model.md - From DISCUSS wave
- docs/feature/{feature-name}/design/constraints.md - Technical and business constraints

## Agent Invocation

@nw-solution-architect

Execute \*design-architecture for {feature-name}.

**Context Files:**

- docs/feature/{feature-name}/discuss/requirements.md
- docs/feature/{feature-name}/discuss/user-stories.md
- docs/feature/{feature-name}/discuss/domain-model.md
- docs/feature/{feature-name}/design/constraints.md

**Configuration:**

- interactive: moderate
- output_format: markdown
- diagram_format: c4
- architecture: hexagonal

## Success Criteria

Refer to Morgan's quality gates in nWave/agents/nw-solution-architect.md.

- [ ] Existing system analyzed before design (codebase search performed)
- [ ] Integration points with existing components documented
- [ ] Reuse vs. new component decisions justified
- [ ] Architecture supports all business requirements
- [ ] Technology stack selected with clear rationale
- [ ] Component boundaries defined (hexagonal architecture)
- [ ] C4 diagrams complete and accessible
- [ ] Handoff accepted by acceptance-designer (DISTILL wave)

## Next Wave

**Handoff To**: acceptance-designer (DISTILL wave)
**Deliverables**: See Morgan's handoff package specification in agent file

# Expected outputs:
# - docs/feature/{feature-name}/design/architecture-design.md
# - docs/feature/{feature-name}/design/technology-stack.md
# - docs/feature/{feature-name}/design/component-boundaries.md
# - docs/feature/{feature-name}/design/data-models.md
# - docs/feature/{feature-name}/design/diagrams/*.svg
