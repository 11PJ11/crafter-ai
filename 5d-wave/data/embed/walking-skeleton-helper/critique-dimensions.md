# Walking Skeleton Quality Critique Dimensions
# For walking-skeleton-helper self-review mode

## Review Mode Activation

**Persona Shift**: From skeleton builder → independent minimalism reviewer
**Focus**: Validate minimal scope, verify E2E completeness, ensure deployment viability
**Mindset**: Challenge every feature - if not essential, remove it

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Scope Creep (Non-Minimal)

**Pattern**: Walking skeleton includes non-essential features

**Minimal Skeleton Should**:
- Implement single E2E user journey (simplest possible)
- Prove architecture works E2E
- Validate deployment pipeline
- NO business logic beyond minimal proof

**Scope Violations**:
- Multiple user journeys
- Business logic beyond "hello world" level
- UI polish, styling, multiple pages
- Complex data models

**Severity**: HIGH (defeats walking skeleton purpose)

**Recommendation**: Remove {feature} - not essential for E2E proof. Defer to later iteration.

---

## Critique Dimension 2: Incomplete E2E Path

**Pattern**: Skeleton doesn't actually go end-to-end

**Required E2E Components**:
- UI/Entry point (even if minimal)
- Application layer
- Domain layer
- Infrastructure/persistence
- Deployment to production-like environment

**Severity**: CRITICAL (doesn't prove architecture)

**Recommendation**: Add missing layer {layer} to complete E2E path

---

## Critique Dimension 3: Deployment Pipeline Not Validated

**Pattern**: Skeleton built but not deployed to production-like environment

**Required**:
- CI/CD pipeline configured
- Automated tests running
- Deployment to staging/production
- Smoke tests confirm E2E works in deployed environment

**Severity**: CRITICAL (deployment risk not validated)

**Recommendation**: Deploy to {environment}, run smoke tests, verify E2E path operational

---

## Review Output Format

```yaml
review_id: "skeleton_rev_{timestamp}"
reviewer: "walking-skeleton-helper (review mode)"

issues_identified:
  scope_creep:
    - issue: "Non-essential feature {feature} in skeleton"
      severity: "high"
      recommendation: "Remove {feature}, defer to later iteration"

  incomplete_e2e:
    - issue: "Missing {layer} in E2E path"
      severity: "critical"
      recommendation: "Add minimal {layer} to complete E2E"

  deployment_gaps:
    - issue: "Skeleton not deployed to {environment}"
      severity: "critical"
      recommendation: "Deploy and verify E2E path operational"

approval_status: "approved|rejected_pending_revisions"
```
