# DW-DELIVER: Production Readiness Validation

**Wave**: DELIVER
**Agent**: Dakota (nw-devop)

## Overview

Validate production readiness and demonstrate business value delivery. Final wave in nWave (DISCOVER > DISCUSS > DESIGN > DISTILL > DEVELOP > DELIVER).

Dakota validates actual business value delivery, not just technical completion: functional completeness, operational excellence, performance, security, disaster recovery.

## Context Files Required

- src/\* - Implementation (from DEVELOP)
- tests/acceptance/\* - Acceptance tests (from DISTILL, validated in DEVELOP)
- tests/unit/\* - Unit tests (from DEVELOP)
- docs/feature/{feature-name}/design/architecture-design.md - Architecture (from DESIGN)

## Previous Artifacts (Wave Handoff)

- src/\* - Complete implementation (from DEVELOP)
- tests/acceptance/\* - All passing (from DEVELOP)
- tests/unit/\* - (from DEVELOP)
- docs/implementation/implementation-status.md - (from DEVELOP)

## Agent Invocation

@nw-devop

Execute \*validate-production-readiness for {feature-name}.

**Context Files:**

- src/\*
- tests/acceptance/\*
- tests/unit/\*
- docs/feature/{feature-name}/design/architecture-design.md
- docs/implementation/implementation-status.md

**Configuration:**

- deployment_target: staging | production
- environment: production-like
- monitoring_enabled: true
- stakeholder_demo: required

## Success Criteria

Refer to Dakota's quality gates in nWave/agents/nw-devop.md.

- [ ] All acceptance tests passing in production-like environment
- [ ] Production deployment completed successfully
- [ ] Stakeholder demonstrations successful
- [ ] Business outcome metrics collected
- [ ] Operational knowledge transfer completed

## Next Wave

**Handoff To**: Next feature iteration (return to DISCOVER) or project completion
**Deliverables**: See Dakota's handoff package specification in agent file

# Expected outputs:
# - docs/feature/{feature-name}/deliver/production-deployment.md
# - docs/feature/{feature-name}/deliver/stakeholder-feedback.md
# - docs/feature/{feature-name}/deliver/business-impact-report.md
