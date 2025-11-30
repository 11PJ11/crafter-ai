# How to Ensure Reviewers Are Invoked - Complete Guide

**Version**: 1.0
**Date**: 2025-10-06
**Status**: Production Ready

---

## Executive Summary

**Reviewer agents** are Layer 4 Adversarial Verification agents that provide **peer review** of primary agent outputs to reduce confirmation bias, identify completeness gaps, and improve quality through independent critique. This guide explains how to ensure reviewers are invoked in your workflows.

**Current Status**: Reviewer agents exist in source code (`5d-wave/agents/reviewers/`) but are **NOT currently included in the build/installation** process. They need to be either:
1. Added to the build process, OR
2. Manually invoked through the Task tool

---

## Table of Contents

1. [Reviewer System Overview](#reviewer-system-overview)
2. [Current Installation Status](#current-installation-status)
3. [Manual Invocation Methods](#manual-invocation-methods)
4. [Automated Invocation (Future)](#automated-invocation-future)
5. [Workflow Integration Patterns](#workflow-integration-patterns)
6. [Configuration and Setup](#configuration-and-setup)

---

## Reviewer System Overview

### What Are Reviewers?

Reviewers are **peer agents with equal expertise** to primary agents that provide independent critique to:
- **Reduce bias**: Confirmation bias, technology bias, happy path bias
- **Improve completeness**: Identify missing scenarios, stakeholders, requirements
- **Enhance clarity**: Find ambiguities, vague requirements, unmeasurable criteria
- **Validate quality**: Ensure testability, feasibility, adherence to standards

### 12 Reviewer Agents

| # | Primary Agent | Reviewer Agent | Persona | Focus |
|---|---------------|----------------|---------|-------|
| 1 | business-analyst | business-analyst-reviewer | Scout | Requirements bias, completeness, testability |
| 2 | solution-architect | solution-architect-reviewer | Atlas | Architectural bias, ADR quality, feasibility |
| 3 | acceptance-designer | acceptance-designer-reviewer | Sentinel | Happy path bias, GWT quality, coverage |
| 4 | software-crafter | software-crafter-reviewer | Mentor | Implementation bias, test coupling, complexity |
| 5 | knowledge-researcher | knowledge-researcher-reviewer | Scholar | Source bias, evidence quality, replicability |
| 6 | data-engineer | data-engineer-reviewer | Validator | Performance claims, query optimization, security |
| 7 | architecture-diagram-manager | architecture-diagram-manager-reviewer | Clarity | Visual clarity, consistency, accessibility |
| 8 | visual-2d-designer | visual-2d-designer-reviewer | Critic | 12 principles compliance, timing, readability |
| 9 | feature-completion-coordinator | feature-completion-coordinator-reviewer | Auditor | Handoff completeness, phase validation, traceability |
| 10 | root-cause-analyzer | root-cause-analyzer-reviewer | Logician | Causality logic, evidence quality, alternatives |
| 11 | walking-skeleton-helper | walking-skeleton-helper-reviewer | Minimalist | Minimal scope, E2E completeness, deployment viability |
| 12 | agent-forger | agent-forger-reviewer | Inspector | Template compliance, framework completeness, design patterns |

### 5-Phase Review Workflow

```
Phase 1: Production → Primary agent produces artifact
Phase 2: Review    → Reviewer critiques artifact
Phase 3: Revision  → Primary agent addresses feedback
Phase 4: Approval  → Reviewer validates revisions
Phase 5: Handoff   → Approved artifact handed to next wave
```

**Iteration Limit**: Maximum 2 iterations. If not approved after 2 iterations, escalate to human facilitator.

---

## Current Installation Status

### ❌ Reviewers NOT Installed

**Issue**: Reviewer agents in `5d-wave/agents/reviewers/` are **NOT included** in the build process.

**Evidence**:
```bash
# Source has reviewers
$ ls 5d-wave/agents/reviewers/ | wc -l
12

# Installation does NOT have reviewers
$ ls ~/.claude/agents/dw/ | grep reviewer | wc -l
0
```

**Root Cause**: Build script (`tools/build_ide_bundle.py`) only processes agents from `5d-wave/agents/*.md`, NOT subdirectories like `reviewers/`.

```python
# Line 114 in build_ide_bundle.py
agent_files = list(agents_dir.glob("*.md"))  # ← Only gets *.md in agents/, not reviewers/
```

### Two Options to Fix

#### Option 1: Include Reviewers in Build (Recommended)

**Modify build script** to include reviewers:

```python
# In build_ide_bundle.py, line 114:
agent_files = list(agents_dir.glob("*.md"))
reviewer_files = list(agents_dir.glob("reviewers/*.md"))
all_agent_files = agent_files + reviewer_files

for agent_file in all_agent_files:
    # ... process
```

**Then rebuild and reinstall**:
```bash
./scripts/update-ai-craft.sh --backup --force
```

#### Option 2: Manual Invocation (Current Workaround)

Use Task tool to invoke reviewers from source files until build is fixed.

---

## Manual Invocation Methods

### Method 1: Task Tool Invocation

Since reviewers are not installed, **use the Task tool** to invoke them directly from source files.

#### Example: Business Analyst Review

```markdown
**User**: Review my requirements document for bias and completeness

**Claude**: I'll use the Task tool to invoke the business-analyst-reviewer agent.

<Task>
  subagent_type: general-purpose
  description: Invoke business-analyst-reviewer
  prompt: |
    You are the business-analyst-reviewer agent (Scout persona).

    Read the complete agent specification from:
    5d-wave/agents/reviewers/business-analyst-reviewer.md

    Then review the artifact at:
    docs/requirements/requirements.md

    Conduct comprehensive peer review following the specification:
    1. Analyze for confirmation bias (technology bias, happy path bias)
    2. Validate completeness (stakeholders, scenarios, requirements)
    3. Assess clarity (ambiguities, vague requirements, measurability)
    4. Verify testability (acceptance criteria testable)

    Provide structured feedback in YAML format:
    - strengths
    - issues_identified (with severity: critical/high/medium/low)
    - recommendations
    - approval_status (approved/rejected_pending_revisions/conditionally_approved)
</Task>
```

#### Example: Acceptance Test Review

```markdown
**User**: Review my acceptance tests for happy path bias

**Claude**: I'll invoke the acceptance-designer-reviewer.

<Task>
  subagent_type: general-purpose
  description: Review acceptance tests
  prompt: |
    You are the acceptance-designer-reviewer agent (Sentinel persona).

    Read the specification from:
    5d-wave/agents/reviewers/acceptance-designer-reviewer.md

    Review the acceptance tests at:
    tests/acceptance/features/checkout.feature

    Focus on:
    1. Happy path bias detection (error scenarios coverage)
    2. GWT format compliance (Given-When-Then structure)
    3. Business language purity (no technical terms)
    4. Coverage completeness (all user stories tested)

    Provide YAML feedback with:
    - bias_detected
    - gwt_quality
    - coverage_gaps
    - tdd_readiness
    - approval_status
</Task>
```

### Method 2: Direct Agent Activation

**Read reviewer file directly** and adopt persona:

```markdown
**User**: Activate as acceptance-designer-reviewer and review my tests

**Claude**:
<Read file="5d-wave/agents/reviewers/acceptance-designer-reviewer.md" />

[Adopts Sentinel persona]

Hello! I'm Sentinel, the Acceptance Test Quality Reviewer (acceptance-designer-reviewer).

I provide independent peer review of acceptance tests to detect:
- Happy path bias (insufficient error scenario coverage)
- GWT format violations (business language purity)
- Coverage gaps (missing user stories)
- TDD readiness issues

Please provide the acceptance test artifact to review.
```

### Method 3: Workflow Command Pattern

**Add reviewer invocation to workflow commands** (e.g., `/dw:distill`):

```markdown
# In task file: 5d-wave/tasks/dw/distill.md

## Workflow Steps

1. Create acceptance tests (acceptance-designer)
2. **Layer 4 Review** (acceptance-designer-reviewer) ← ADD THIS STEP
   - Invoke reviewer via Task tool
   - Address critical/high issues
   - Obtain approval before handoff
3. Handoff to DEVELOP wave
```

---

## Automated Invocation (Future)

### Trigger Points

Reviewers should be **automatically invoked** at these points:

#### 1. After Layer 1 Pass

```yaml
layer_1_validation:
  status: PASS
trigger:
  action: invoke_layer_4_review
  reviewer: "{primary-agent}-reviewer"
  auto_iterate: true
  max_iterations: 2
```

#### 2. Critical Wave Handoffs

```yaml
handoff_triggers:
  DISCUSS → DESIGN:
    reviewer: business-analyst-reviewer
    required: true

  DESIGN → DISTILL:
    reviewer: solution-architect-reviewer
    required: true

  DISTILL → DEVELOP:
    reviewer: acceptance-designer-reviewer
    required: true

  DEVELOP → DEMO:
    reviewer: software-crafter-reviewer
    required: true
```

#### 3. On-Demand User Request

```bash
# CLI command (future implementation)
ai-craft review \
  --artifact docs/requirements/requirements.md \
  --reviewer business-analyst-reviewer \
  --interactive
```

#### 4. CI/CD Pipeline Integration

```yaml
# .github/workflows/layer4-review.yml
name: Layer 4 Peer Review

on:
  pull_request:
    paths:
      - 'docs/requirements/**'
      - 'docs/architecture/**'

jobs:
  peer-review:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Layer 4 Review
        run: |
          ai-craft review \
            --artifact docs/requirements/requirements.md \
            --reviewer business-analyst-reviewer \
            --fail-on-critical

      - name: Upload Review Feedback
        uses: actions/upload-artifact@v3
        with:
          name: layer4-review
          path: reviews/*.yaml
```

---

## Workflow Integration Patterns

### Pattern 1: Explicit Review Step

**Add explicit review step** to wave workflows:

```markdown
## DISCUSS Wave Workflow

1. Gather requirements (business-analyst)
2. **REVIEW** requirements (business-analyst-reviewer) ← EXPLICIT STEP
   - Auto-trigger or manual request
   - Iterate until approved (max 2 iterations)
   - Escalate if not approved after 2 iterations
3. Handoff to DESIGN wave (solution-architect)
```

### Pattern 2: Quality Gate Before Handoff

**Block handoff** until reviewer approval:

```yaml
handoff_quality_gate:
  condition: reviewer_approval_obtained == true
  on_failure:
    action: block_handoff
    message: "Artifact requires peer review approval before handoff"
    next_step: invoke_reviewer
```

### Pattern 3: Iterative Improvement Cycle

**Automate revision loop**:

```yaml
review_cycle:
  phase_1: primary_agent_produces_artifact
  phase_2: reviewer_critiques_artifact
  phase_3: primary_agent_revises_artifact
  phase_4: reviewer_validates_revision

  iteration_limit: 2

  outcomes:
    approved: handoff_to_next_wave
    rejected_after_2_iterations: escalate_to_human
    conditionally_approved: handoff_with_caveats
```

### Pattern 4: Parallel Review for Critical Artifacts

**Multi-reviewer consensus**:

```yaml
critical_artifact_review:
  artifact: "docs/architecture/security-architecture.md"
  reviewers:
    - solution-architect-reviewer
    - root-cause-analyzer-reviewer

  approval_threshold: 2/2  # Both must approve

  on_disagreement:
    action: escalate_to_human_facilitator
```

---

## Configuration and Setup

### Step 1: Fix Build to Include Reviewers

**Modify** `tools/build_ide_bundle.py`:

```python
def process_agents(self) -> None:
    """Process all agent files including reviewers."""
    logging.info("Processing agents...")
    agents_dir = self.source_dir / "agents"

    if not agents_dir.exists():
        logging.warning(f"Agents directory not found: {agents_dir}")
        return

    # Process main agents
    agent_files = list(agents_dir.glob("*.md"))
    logging.info(f"Found {len(agent_files)} main agent files")

    # Process reviewer agents (NEW)
    reviewer_files = list((agents_dir / "reviewers").glob("*.md"))
    logging.info(f"Found {len(reviewer_files)} reviewer agent files")

    # Combine and process all
    all_agent_files = agent_files + reviewer_files

    for agent_file in all_agent_files:
        try:
            logging.info(f"Processing agent: {agent_file.stem}")
            self.agent_processor.process_agent(agent_file)
            self.stats['agents_processed'] += 1
        except Exception as e:
            logging.error(f"Error processing agent {agent_file.name}: {e}")
            self.stats['errors'] += 1
```

### Step 2: Rebuild and Install

```bash
# Rebuild with reviewers included
./scripts/update-ai-craft.sh --backup --force

# Verify installation
ls ~/.claude/agents/dw/ | grep reviewer
# Should show 12 reviewer agents
```

### Step 3: Configure Layer 4 Settings

**Create** `.ai-craft/layer4.yaml`:

```yaml
layer_4_config:
  enabled: true

  automation:
    auto_trigger_after_layer_1: true
    auto_iterate: true
    max_iterations: 2

  quality_gates:
    block_handoff_without_approval: true
    escalate_after_max_iterations: true

  reviewers:
    business-analyst-reviewer:
      enabled: true
      auto_invoke_on: ["DISCUSS wave completion"]

    solution-architect-reviewer:
      enabled: true
      auto_invoke_on: ["DESIGN wave completion"]

    acceptance-designer-reviewer:
      enabled: true
      auto_invoke_on: ["DISTILL wave completion"]

    software-crafter-reviewer:
      enabled: true
      auto_invoke_on: ["DEVELOP wave completion"]

  metrics:
    collect_review_metrics: true
    export_to: ["prometheus", "datadog"]

  escalation:
    human_facilitator_email: "team-lead@example.com"
    escalation_timeout: "5 minutes"
```

### Step 4: Update Wave Commands

**Modify** wave commands to include review steps:

```markdown
# Example: /dw:distill command

## Implementation Steps

1. Load business requirements from DISCUSS wave
2. Create acceptance tests (acceptance-designer)
3. **Layer 4 Review** (acceptance-designer-reviewer)
   ```
   IF layer4.enabled:
     invoke acceptance-designer-reviewer
     iterate until approved (max 2)
     escalate if not approved
   ```
4. Handoff to DEVELOP wave (software-crafter)
```

---

## Testing Reviewer Invocation

### Test 1: Manual Invocation

```bash
# Test manual Task invocation
claude-code

> I need to review my requirements document. Use the Task tool to invoke
> business-analyst-reviewer from 5d-wave/agents/reviewers/business-analyst-reviewer.md
> to review docs/requirements/requirements.md
```

### Test 2: Direct Activation

```bash
> Read 5d-wave/agents/reviewers/acceptance-designer-reviewer.md and adopt
> the Sentinel persona. Then review tests/acceptance/features/checkout.feature
```

### Test 3: Workflow Integration

```bash
> Run /dw:distill for checkout feature. Ensure Layer 4 review is invoked
> before handoff to DEVELOP wave.
```

---

## Validation Checklist

- [ ] **Build includes reviewers**: Verify 12 reviewer agents installed
- [ ] **Manual invocation works**: Test Task tool invocation
- [ ] **Direct activation works**: Test persona adoption
- [ ] **Workflow integration**: Reviewers invoked in wave commands
- [ ] **Configuration valid**: `.ai-craft/layer4.yaml` loaded
- [ ] **Quality gates active**: Handoff blocked without approval
- [ ] **Escalation works**: Human facilitator notified after max iterations
- [ ] **Metrics collected**: Review effectiveness tracked

---

## Troubleshooting

### Issue: Reviewer Not Found

**Symptom**: "Reviewer agent not found: business-analyst-reviewer"

**Solution**:
1. Check if reviewers installed: `ls ~/.claude/agents/dw/ | grep reviewer`
2. If empty, rebuild with fixed build script
3. Use manual Task invocation as workaround

### Issue: Review Not Auto-Triggered

**Symptom**: Workflow proceeds to handoff without review

**Solution**:
1. Check `.ai-craft/layer4.yaml` has `auto_trigger_after_layer_1: true`
2. Verify Layer 1 passed (review only triggers after Layer 1 PASS)
3. Check wave command includes explicit review step

### Issue: Infinite Revision Loop

**Symptom**: Agent and reviewer keep iterating beyond 2 cycles

**Solution**:
1. Verify `max_iterations: 2` in configuration
2. Check escalation logic is implemented
3. Manually escalate to human facilitator

---

## Summary: How to Ensure Reviewers Are Invoked

### Current State (Workaround)

**Use Task tool** to manually invoke reviewers from source files:

```markdown
<Task subagent_type="general-purpose">
  Read 5d-wave/agents/reviewers/{reviewer-name}.md
  Review artifact at {path}
  Provide YAML feedback
</Task>
```

### Future State (Automated)

1. **Fix build**: Include `reviewers/` in build script
2. **Rebuild**: Run `./scripts/update-ai-craft.sh`
3. **Configure**: Create `.ai-craft/layer4.yaml`
4. **Auto-trigger**: Reviewers invoked automatically after Layer 1 pass
5. **Quality gate**: Handoff blocked without reviewer approval

---

## References

- **Layer 4 Implementation**: `docs/guides/LAYER_4_IMPLEMENTATION_SUMMARY.md`
- **Integration Guide**: `docs/guides/LAYER_4_INTEGRATION_GUIDE.md`
- **Workflow Documentation**: `docs/reports/adversarial/ADVERSARIAL_VERIFICATION_WORKFLOW.md`
- **Example Review Cycle**: `examples/adversarial-verification-example.md`
- **Reviewer Specifications**: `5d-wave/agents/reviewers/*.md`

---

**Last Updated**: 2025-10-06
**Status**: Production Ready (pending build fix)
**Next Action**: Fix build script to include reviewers in installation
