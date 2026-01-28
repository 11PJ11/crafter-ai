# Platform Design Review Checklist

## Overview

Review checklist for platform-architect-reviewer (Atlas) to validate platform and delivery infrastructure designs before handoff to DISTILL wave.

---

## 🔴 **BLOCKING Issues - Must Fix Before Approval**

### CI/CD Pipeline

- [ ] **Pipeline completeness**
  - All required stages present (validate, test, security, build, deploy)
  - Quality gates defined with thresholds
  - Failure recovery documented

- [ ] **Security gates present**
  - SAST integrated in pipeline
  - Dependency scanning (SCA) integrated
  - Secret scanning in place

- [ ] **Rollback capability**
  - Rollback mechanism documented
  - Health checks defined
  - Recovery time estimated

### Infrastructure Security

- [ ] **Secrets management**
  - No secrets in code or state files
  - Secrets stored in approved vault/manager
  - OIDC for cloud authentication preferred

- [ ] **Access control**
  - Least privilege IAM policies
  - Network segmentation implemented
  - Encryption at rest and in transit

### Deployment Safety

- [ ] **Deployment approval**
  - Production deployment requires approval
  - Environment protection rules configured
  - Branch restrictions in place

- [ ] **Database migrations**
  - Migration strategy defined
  - Rollback capability for schema changes
  - Data consistency approach documented

### Observability Minimum

- [ ] **SLOs defined**
  - SLOs for critical user journeys
  - Error budget policy documented
  - Burn rate alerting configured

---

## 🟡 **MAJOR Issues - Should Fix, May Proceed with Mitigation**

### CI/CD Pipeline Quality

- [ ] **Build time optimization**
  - Target build time defined
  - Parallelization where possible
  - Caching strategy documented

- [ ] **Test coverage**
  - Coverage threshold defined
  - Coverage reporting configured
  - Trend tracking planned

### Observability Completeness

- [ ] **Golden signals coverage**
  - Latency metrics defined
  - Traffic metrics defined
  - Error rate metrics defined
  - Saturation metrics defined

- [ ] **Logging strategy**
  - Structured logging format
  - Correlation IDs for tracing
  - Log retention policy

- [ ] **Alerting quality**
  - SLO-based alerts preferred over threshold alerts
  - Escalation path documented
  - Runbooks linked to alerts

### Infrastructure Quality

- [ ] **IaC modularity**
  - Reusable modules defined
  - Environment-agnostic base modules
  - Module versioning strategy

- [ ] **Environment parity**
  - Dev/staging/prod consistency
  - Configuration differences documented
  - Drift detection planned

### DORA Metrics

- [ ] **Metrics measurability**
  - Deployment frequency trackable
  - Lead time measurable
  - Change failure rate trackable
  - MTTR measurable

---

## 🟢 **MINOR Issues - Nice to Have, Suggestions**

### Documentation

- [ ] **ADRs for key decisions**
  - Technology choices documented
  - Trade-offs explained
  - Alternatives considered

- [ ] **Runbooks for common operations**
  - Deployment runbook
  - Incident response runbook
  - Rollback runbook

### Advanced Patterns

- [ ] **Progressive delivery readiness**
  - Feature flags infrastructure
  - Canary analysis capability
  - A/B testing support

- [ ] **Chaos engineering readiness**
  - Failure injection points identified
  - Game day planning
  - Resilience testing approach

---

## Review Verdict

### ✅ APPROVED
- 0 BLOCKING issues
- <= 2 MAJOR issues with documented mitigation
- Action: Proceed to DISTILL wave

### ⚠️ CONDITIONAL
- 0 BLOCKING issues
- > 2 MAJOR issues
- Action: Fix MAJOR issues, re-review

### ❌ REJECTED
- >= 1 BLOCKING issues
- Action: Fix BLOCKING issues, full re-review required

---

## Reviewer Notes Template

```markdown
## Platform Design Review

**Reviewed by:** Atlas (platform-architect-reviewer)
**Date:** YYYY-MM-DD
**Verdict:** [APPROVED / CONDITIONAL / REJECTED]

### BLOCKING Issues Found
1. [Issue description and required fix]

### MAJOR Issues Found
1. [Issue description and mitigation]

### MINOR Issues / Suggestions
1. [Suggestion for improvement]

### Summary
[Overall assessment and recommendation]
```
