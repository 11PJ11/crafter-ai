---
agent-activation:
  required: true
  agent-id: feature-completion-coordinator
  agent-name: "Dakota"
  agent-command: "*git-workflow"
  auto-activate: true
---

# DW-GIT: Git Workflow Operations

**Wave**: CROSS_WAVE
**Agent**: Dakota (feature-completion-coordinator)
**Command**: `*git-workflow`

## Overview

Intelligent Git workflow assistant that streamlines version control operations with automated commit message generation, branch management, and deployment coordination for nWave workflows.

Supports commit, branch, merge, status operations with intelligent automation and nWave methodology integration.

## Context Files Required

- .git/\* - Git repository metadata

## Previous Artifacts (Wave Handoff)

- Varies based on git operation context

## Agent Invocation

@feature-completion-coordinator

Execute \*git-workflow with {operation}.

**Context Files:**

- .git/\*

**Configuration:**

- operation: commit # commit/branch/merge/status/push
- auto_message: true # Generate commit message automatically
- quality_gates: true # Run quality checks before commit

## Success Criteria

Refer to Dakota's quality gates in nWave/agents/feature-completion-coordinator.md (Git section).

**Key Validations:**

- [ ] Git operation completed successfully
- [ ] Commit message follows conventions
- [ ] Quality gates passed (if commit operation)
- [ ] All tests passing (if commit operation)

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Git operation completed

# Expected outputs (reference only):

# - Git commits, branches, or merges as requested
