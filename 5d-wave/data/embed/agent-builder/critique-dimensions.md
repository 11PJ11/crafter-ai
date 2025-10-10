# Agent Quality Critique Dimensions
# For agent-builder self-review mode

## Review Mode Activation

**Persona Shift**: From agent creator → independent agent specification reviewer
**Focus**: Validate template compliance, verify framework completeness, ensure safety
**Mindset**: Challenge agent design - assume unsafe until proven otherwise

**CRITICAL OUTPUT REQUIREMENT**: Return complete YAML feedback to calling agent for display to user.

---

## Critique Dimension 1: Template Compliance

**Pattern**: Agent specification deviates from AGENT_TEMPLATE.yaml

**Required Sections**:
- Input/Output contract
- Safety framework (validation + security)
- 4-layer testing
- Observability
- Error recovery

**Severity**: CRITICAL (non-compliant agent, production risk)

**Recommendation**: Add missing section {section} per AGENT_TEMPLATE.yaml specification

---

## Critique Dimension 2: Safety Framework Gaps

**Pattern**: Missing input validation, security checks, or error handling

**Required Safety**:
- Input validation (type, range, format)
- Security validation (auth, sanitization, rate limiting)
- Error handling with graceful degradation
- Circuit breakers for external dependencies

**Severity**: CRITICAL (security vulnerability, production failures)

**Recommendation**: Implement {safety control} to protect against {risk}

---

## Critique Dimension 3: Testing Framework Incomplete

**Pattern**: Missing test layers or insufficient coverage

**Required 4 Layers**:
- Layer 1: Unit tests (agent logic)
- Layer 2: Integration tests (dependencies)
- Layer 3: Adversarial tests (security, edge cases)
- Layer 4: Peer review validation

**Severity**: HIGH (untested agent, quality risk)

**Recommendation**: Add {test layer} with coverage for {scenarios}

---

## Review Output Format

```yaml
review_id: "agent_rev_{timestamp}"
reviewer: "agent-builder (review mode)"

issues_identified:
  template_compliance:
    - issue: "Missing {section} from AGENT_TEMPLATE"
      severity: "critical"
      recommendation: "Add {section} per template specification"

  safety_gaps:
    - issue: "No input validation for {parameter}"
      severity: "critical"
      recommendation: "Validate {parameter} type/range/format"

  testing_incomplete:
    - issue: "Missing {test layer}"
      severity: "high"
      recommendation: "Add {test layer} covering {scenarios}"

approval_status: "approved|rejected_pending_revisions"
```
