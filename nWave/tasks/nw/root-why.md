# DW-ROOT-WHY: Toyota 5 Whys Multi-Causal Analysis

**Wave**: CROSS_WAVE
**Agent**: Sage (troubleshooter)
**Command**: `*investigate-root-cause`

## Overview

Execute systematic root cause analysis using Toyota's enhanced 5 Whys technique with multi-causal investigation and evidence-based validation for complex system failures and architectural decisions.

Philosophy: "By repeating why five times, the nature of the problem as well as its solution becomes clear." - Taiichi Ohno. Enhanced for multi-causal software system analysis.

## Context Files Required

- Varies based on problem domain

## Previous Artifacts (Wave Handoff)

- Problem statement and observable symptoms

## Agent Invocation

@troubleshooter

Execute \*investigate-root-cause for {problem-statement}.

**Context Files:**

- (problem-domain-specific files)

**Configuration:**

- investigation_depth: 5 # WHY levels (typically 5)
- multi_causal: true # Investigate multiple causes at each level
- evidence_required: true # Require evidence for each causal claim

## Success Criteria

Refer to Sage's quality gates in nWave/agents/troubleshooter.md.

**Key Validations:**

- [ ] All 5 WHY levels investigated with evidence
- [ ] Multi-causal branches explored at each level
- [ ] Root causes identified and validated
- [ ] Solutions address ALL identified root causes
- [ ] Backward chain validation performed

## Usage: DEVELOP Wave Retrospective (Phase 3.5)

When invoked as part of `/nw:develop` Phase 3.5, the analysis follows a structured 4-category framework:

1. **What worked well** (and WHY — preserve these practices)
2. **What worked better than before** (and WHY — reinforce improvements)
3. **What worked badly** (5 Whys root cause → actionable fix)
4. **What worked worse than before** (5 Whys root cause → prevent regression)

**Inputs**: Evolution document, execution-status.yaml, mutation results, git log.
**Output**: Retrospective section appended to evolution document.
**Skip**: If clean execution (no skips, no failures, no tooling issues), generate brief summary only.

Items flagged as requiring nWave framework changes should be tagged as **meta-improvements** for the framework maintainer.

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Root cause analysis report with solutions

# Expected outputs (reference only):

# - docs/analysis/root-cause-analysis-{problem}.md
