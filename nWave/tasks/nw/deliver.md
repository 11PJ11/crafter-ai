---
agent-activation:
  required: true
  agent-id: devop
  agent-name: "Dakota"
  agent-command: "*validate-production-readiness"
  auto-activate: true
---

# DW-DELIVER: Production Readiness Validation and Stakeholder Demonstration

**Wave**: DELIVER
**Agent**: Dakota (devop)
**Command**: `*validate-production-readiness`

## Overview

Execute DELIVER wave of nWave methodology through comprehensive feature completion validation, production deployment, and stakeholder demonstration of business value delivery.

Validates actual business value delivery, not just technical completion: functional completeness, operational excellence, performance validation, security compliance, disaster recovery.

## Context Files Required

- src/\* - (from DEVELOP wave)
- tests/acceptance/\* - (from DISTILL wave, validated in DEVELOP)
- tests/unit/\* - (from DEVELOP wave)
- docs/architecture/architecture-design.md - (from DESIGN wave)

## Previous Artifacts (Wave Handoff)

- src/\* - (from DEVELOP wave)
- tests/acceptance/\* - (from DEVELOP wave, all passing)
- tests/unit/\* - (from DEVELOP wave)
- docs/implementation/implementation-status.md - (from DEVELOP wave)

## Agent Invocation

@devop

Execute \*validate-production-readiness for {feature-name}.

**Context Files:**

- src/\*
- tests/acceptance/\*
- tests/unit/\*
- docs/architecture/architecture-design.md

**Previous Artifacts:**

- src/\* (complete implementation)
- tests/acceptance/\* (all passing)
- tests/unit/\*
- docs/implementation/implementation-status.md

**Configuration:**

- deployment_target: staging # or production
- environment: production-like
- monitoring_enabled: true
- stakeholder_demo: required

## Success Criteria

Refer to Dakota's quality gates in nWave/agents/devop.md.

**Key Validations:**

- [ ] All acceptance tests passing in production-like environment
- [ ] Production deployment completed successfully
- [ ] Stakeholder demonstrations successful
- [ ] Business outcome metrics collected
- [ ] Operational knowledge transfer completed
- [ ] nWave methodology cycle completed successfully

## Next Wave

**Handoff To**: Next feature iteration (return to DISCUSS) or project completion

**Deliverables**: See Dakota's handoff package specification in agent file

# Expected outputs (reference only):

# - docs/demo/production-deployment.md

# - docs/demo/stakeholder-feedback.md

# - docs/demo/business-impact-report.md
