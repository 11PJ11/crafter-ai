---
agent-activation:
  required: true
  agent-id: root-cause-analyzer
  agent-name: "Sage"
  agent-command: "*investigate-root-cause"
  auto-activate: true
---

# DW-ROOT-WHY: Toyota 5 Whys Multi-Causal Analysis

**Wave**: CROSS_WAVE
**Agent**: Sage (root-cause-analyzer)
**Command**: `*investigate-root-cause`

## Overview

Execute systematic root cause analysis using Toyota's enhanced 5 Whys technique with multi-causal investigation and evidence-based validation for complex system failures and architectural decisions.

Philosophy: "By repeating why five times, the nature of the problem as well as its solution becomes clear." - Taiichi Ohno. Enhanced for multi-causal software system analysis.

## Context Files Required

- Varies based on problem domain

## Previous Artifacts (Wave Handoff)

- Problem statement and observable symptoms

## Agent Invocation

@root-cause-analyzer

Execute *investigate-root-cause for {problem-statement}.

**Context Files:**
- (problem-domain-specific files)

**Configuration:**
- investigation_depth: 5  # WHY levels (typically 5)
- multi_causal: true  # Investigate multiple causes at each level
- evidence_required: true  # Require evidence for each causal claim

## Success Criteria

Refer to Sage's quality gates in 5d-wave/agents/root-cause-analyzer.md.

**Key Validations:**
- [ ] All 5 WHY levels investigated with evidence
- [ ] Multi-causal branches explored at each level
- [ ] Root causes identified and validated
- [ ] Solutions address ALL identified root causes
- [ ] Backward chain validation performed

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Root cause analysis report with solutions

# Expected outputs (reference only):
# - docs/analysis/root-cause-analysis-{problem}.md
