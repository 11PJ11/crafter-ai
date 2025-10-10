---
agent-activation:
  required: true
  agent-id: skeleton-builder
  agent-name: "Skelly"
  agent-command: "*create-skeleton"
  auto-activate: true
---

# DW-SKELETON: Walking Skeleton E2E Automation

**Wave**: CROSS_WAVE (early DESIGN or DISTILL integration)
**Agent**: Skelly (skeleton-builder)
**Command**: `*create-skeleton`

## Overview

Execute Walking Skeleton methodology through minimal end-to-end implementation that validates architecture and reduces risk early in projects. Based on Alistair Cockburn's Walking Skeleton approach.

Implements thinnest possible slice through entire system to validate architecture, reduce integration risk, and establish automated deployment pipeline.

## Context Files Required

- docs/architecture/architecture-design.md - Architecture for skeleton validation
- docs/architecture/component-boundaries.md - Component structure
- docs/requirements/user-stories.md - Feature selection for skeleton

## Previous Artifacts (Wave Handoff)

- docs/architecture/architecture-design.md - (from DESIGN wave)
- docs/architecture/component-boundaries.md - (from DESIGN wave)

## Agent Invocation

@skeleton-builder

Execute \*create-skeleton for {feature-name}.

**Context Files:**

- docs/architecture/architecture-design.md
- docs/architecture/component-boundaries.md
- docs/requirements/user-stories.md

**Configuration:**

- depth: minimal # minimal/standard/comprehensive
- automated_deployment: true
- monitoring_integration: true

## Success Criteria

Refer to Skelly's quality gates in 5d-wave/agents/skeleton-builder.md.

**Key Validations:**

- [ ] End-to-end connectivity through all architectural layers
- [ ] Automated deployment pipeline operational
- [ ] Minimal business logic implemented (happy path only)
- [ ] Infrastructure validated (production-like)
- [ ] Monitoring and health checks active

## Next Wave

**Handoff To**: DISTILL or DEVELOP wave (skeleton provides foundation)
**Deliverables**: Minimal working system with deployment automation

# Expected outputs (reference only):

# - src/\* (minimal skeleton implementation)

# - .github/workflows/\* (CI/CD pipeline)

# - docs/skeleton/implementation-report.md
