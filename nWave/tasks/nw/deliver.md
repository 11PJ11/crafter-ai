# DW-DELIVER: Production Readiness Validation and Stakeholder Demonstration

**Wave**: DELIVER
**Agent**: Dakota (devop)
**Command**: `*validate-production-readiness`

## Overview

Execute DELIVER wave of nWave methodology through comprehensive feature completion validation, production deployment, and stakeholder demonstration of business value delivery.

Validates actual business value delivery, not just technical completion: functional completeness, operational excellence, performance validation, security compliance, disaster recovery.

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

1. **Read all implementation and test artifacts** and embed complete validation context inline
2. **Create a complete agent prompt** that includes:
   - Full implementation status and completion metrics (inline)
   - Complete test results: acceptance tests, unit tests, integration tests (inline)
   - Architecture documentation and component boundaries (inline)
   - Production environment specifications and deployment procedures (inline)
   - Validation checklist and acceptance criteria (inline)
   - Smoke test definitions and monitoring setup procedures (inline)
   - Rollback procedures and failure scenarios (inline)
   - Stakeholder communication templates (inline)
3. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
4. **Embed all production validation procedures** - agent executes directly, no command delegation

### Agent Prompt Must Contain

- Full implementation status documentation (inline, not path reference)
- Complete test results: acceptance test summary, unit test coverage, integration test results (inline)
- Architecture design and component boundaries (inline)
- Production environment specifications (infrastructure, configurations, dependencies)
- Deployment procedures and sequencing steps
- Validation checklist with acceptance criteria for each item
- Smoke test definitions and expected results
- Monitoring setup procedures and health check specifications
- Performance baseline requirements and validation methods
- Security compliance checklist and validation procedures
- Disaster recovery and rollback procedures
- Stakeholder communication procedures and feedback collection
- Business impact metrics and success measurement procedures
- Expected deliverables with file paths and content structure
- Quality gate criteria for production readiness

### What NOT to Include

- ❌ "Agent should invoke /nw:finalize after deployment"
- ❌ "Use /nw:execute to run validation tests"
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without full content embedded (agent needs specs, test results inline)
- ❌ External CI/CD tool references without complete procedure specifications embedded

### Example: What TO Do

✅ "Validate production readiness using these acceptance criteria: [FULL CRITERIA AND VALIDATION PROCEDURES]"
✅ "Execute smoke tests following this definition: [COMPLETE TEST SPECIFICATIONS WITH EXPECTED RESULTS]"
✅ "Deploy to staging environment following this procedure: [COMPLETE DEPLOYMENT STEPS WITH SEQUENCING]"
✅ "Verify monitoring setup following this checklist: [COMPLETE MONITORING SPECIFICATIONS]"
✅ "Collect stakeholder feedback using this template: [COMPLETE FEEDBACK STRUCTURE]"
✅ "Provide these delivery outputs: production-deployment.md, stakeholder-feedback.md, business-impact-report.md"

## Delivery as Fresh Instance Validation

The deliver command invokes a new agent instance that validates production readiness. This instance reads completed implementation files, reviews all accumulated documentation (architecture, test results, review feedback), executes validation scenarios in production-like environments, and produces delivery artifacts. The instance does not rely on prior session memory. All context needed for delivery validation comes from persistent artifacts: implementation files, documentation, test records, and deployment configurations.

## Context Files Required

- src/\* - (from DEVELOP wave)
- tests/acceptance/\* - (from DISTILL wave, validated in DEVELOP)
- tests/unit/\* - (from DEVELOP wave)
- docs/feature/{feature-name}/design/architecture-design.md - (from DESIGN wave)

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
- docs/feature/{feature-name}/design/architecture-design.md

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

# - docs/feature/{feature-name}/deliver/production-deployment.md

# - docs/feature/{feature-name}/deliver/stakeholder-feedback.md

# - docs/feature/{feature-name}/deliver/business-impact-report.md
