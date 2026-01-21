# Layer 4 for Users

**Version**: 1.2.81
**Date**: 2026-01-21
**Status**: Production Ready

Manual review workflows via CLI and interactive mode.

**Prerequisites**: ai-craft CLI installed.

**Related Docs**:
- [API Reference](../reference/layer-4-api-reference.md) (contracts)
- [For Developers](layer-4-for-developers.md) (code)
- [For CI/CD](layer-4-for-cicd.md) (pipelines)

---

## Quick Start

Request a peer review:

```bash
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --interactive
```

---

## Basic Review Request

### Step 1: Run Review Command

```bash
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --interactive
```

### Step 2: Read Output

```
Initiating Layer 4 Peer Review...
Reviewer: business-analyst-reviewer (Scout)
Artifact: docs/requirements/requirements.md

Analyzing artifact for bias, completeness, clarity, testability...

Review Complete
Issues Identified: 8 (2 critical, 3 high, 3 medium, 0 low)
Approval Status: rejected_pending_revisions

Review saved to: reviews/rev_20251006_152330_requirements.yaml

Next Steps:
1. Review feedback: cat reviews/rev_20251006_152330_requirements.yaml
2. Address critical and high issues
3. Re-submit: ai-craft review --artifact docs/requirements/requirements.md --iteration 2
```

---

## Review Specific Dimensions

Focus review on specific areas:

```bash
# Review only for bias detection
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --dimensions bias

# Review for completeness and testability
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --dimensions completeness,testability
```

### Available Dimensions

| Dimension | Description |
|-----------|-------------|
| `bias` | Confirmation bias detection |
| `completeness` | Missing scenarios/stakeholders |
| `clarity` | Vague requirements |
| `testability` | Measurable acceptance criteria |

---

## Interactive Review Mode

Let the CLI guide you through options:

```bash
ai-craft review --interactive
```

**Prompts**:
```
? Select artifact to review:
  > docs/requirements/requirements.md
    docs/architecture/architecture.md
    tests/acceptance/checkout.feature

? Select reviewer:
  > business-analyst-reviewer (Scout) - Requirements quality
    solution-architect-reviewer (Atlas) - Architecture quality
    acceptance-designer-reviewer (Sentinel) - Test quality

? Review dimensions (select all that apply):
  [x] Confirmation Bias Detection
  [x] Completeness Validation
  [x] Clarity Assessment
  [x] Testability Verification

Initiating review...
```

---

## Interpreting Review Feedback

### View Feedback File

```bash
cat reviews/rev_20251006_152330_requirements.yaml
```

### Key Sections

**1. Strengths** - What's done well:
```yaml
strengths:
  - "Clear business context with quantitative goal (45% -> 25% cart abandonment)"
  - "Well-structured user stories with persona-based format"
```

**2. Critical Issues** - Must fix:
```yaml
issues_identified:
  completeness_gaps:
    - issue: "Performance requirement 'System should be fast' is vague"
      severity: "critical"
      recommendation: "Quantify: 'API responds within 2s (p95)'"
```

**3. Recommendations** - Prioritized actions:
```yaml
recommendations:
  1: "CRITICAL: Quantify performance requirements"
  2: "CRITICAL: Add error handling scenarios"
  3: "HIGH: Re-elicit deployment constraints"
```

**4. Approval Status** - What happens next:
```yaml
approval_status: "rejected_pending_revisions"
next_steps: |
  Address critical and high severity issues before DESIGN wave handoff.
```

---

## Revision and Re-Submission

### Step 1: Address Feedback

Edit your artifact to fix issues:

```bash
vim docs/requirements/requirements.md
```

### Step 2: Re-Submit (Iteration 2)

```bash
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --iteration 2 \
  --revision-notes revision_notes_v1_to_v2.md
```

### Step 3: Check Result

```
Re-review (Iteration 2)...

Review Complete
Critical Issues Resolved: 2/2 (100%)
High Issues Resolved: 3/3 (100%)

APPROVED
Handoff Ready: Yes
Next Agent: solution-architect
```

---

## Understanding Iteration Limits

**Maximum 2 iterations**:
- **Iteration 1**: Initial review, you revise
- **Iteration 2**: Re-review, approve or escalate

### If Not Approved After 2 Iterations

```
Max iterations exceeded (2/2)
Unresolved Critical Issues: 1
- Performance requirement still vague after revision

Escalation Required
Created escalation ticket: ESC-2025-10-06-001
Assigned to: Human Facilitator (John Smith)
Recommendation: Schedule stakeholder workshop to clarify requirements

Escalation report: escalations/ESC-2025-10-06-001.yaml
```

---

## Choosing the Right Reviewer

| Artifact Type | Reviewer | Focus |
|--------------|----------|-------|
| Requirements | business-analyst-reviewer | Bias, completeness, testability |
| Architecture | solution-architect-reviewer | ADR quality, feasibility |
| Acceptance tests | acceptance-designer-reviewer | Happy path bias, GWT quality |
| Code | software-crafter-reviewer | Implementation bias, complexity |
| Research | knowledge-researcher-reviewer | Source credibility, evidence |

---

## Common Workflows

### Pre-Handoff Review

Before handing off to the next wave:

```bash
# After DISCUSS wave, before DESIGN
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --fail-on-critical
```

### Quick Bias Check

Fast check for common biases:

```bash
ai-craft review \
  --artifact docs/architecture/architecture.md \
  --reviewer solution-architect-reviewer \
  --dimensions bias \
  --quick
```

### Full Quality Audit

Comprehensive review of all dimensions:

```bash
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --dimensions bias,completeness,clarity,testability \
  --verbose
```

---

## Troubleshooting

### Reviewer Not Found

**Error**: `Reviewer agent 'business-analyst-reviewer' not found`

**Fix**:
```bash
# Check available reviewers
ls -1 $AI_CRAFT_REVIEWERS_DIR/

# Verify specific reviewer
cat $AI_CRAFT_REVIEWERS_DIR/business-analyst-reviewer.md

# Re-install if missing
./scripts/install-ai-craft.sh
```

### Review Takes Too Long

**Error**: `Warning: Review timed out after 300 seconds`

**Fix**:
```bash
export REVIEWER_TIMEOUT_SECONDS="600"  # 10 minutes
ai-craft review --artifact ...
```

### No Feedback Returned

**Error**: Review completes but file is empty

**Fix**: Use verbose mode:
```bash
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --verbose \
  --debug
```

---

## Debugging Commands

```bash
# Enable verbose logging
ai-craft review --artifact ... --verbose --debug

# Check Layer 4 status
ai-craft status --layer 4

# Validate reviewer agent
ai-craft validate-agent business-analyst-reviewer

# Test reviewer without changes
ai-craft test-reviewer business-analyst-reviewer --dry-run
```

---

**Last Updated**: 2026-01-21
**Type**: How-to Guide
**Purity**: 95%+
