---
agent-activation:
  required: true
  agent-id: software-crafter
  agent-name: "Crafty"
  agent-command: "*refactor"
  auto-activate: true
---

# DW-REFACTOR: Systematic Code Analysis and Refactoring

**Wave**: CROSS_WAVE (continuous improvement support)
**Agent**: Crafty (software-crafter)
**Command**: `*refactor`

## Overview

Execute systematic refactoring of existing codebases through progressive code quality improvement, Mikado Method planning for complex refactorings, and six-level refactoring hierarchy implementation.

Progressive refactoring hierarchy: Readability (L1-2) → Structure (L3-4) → Design (L5-6) with continuous validation and automated quality gates.

## Context Files Required

- src/\* - Codebase to analyze and refactor

## Previous Artifacts (Wave Handoff)

- Varies based on refactoring context

## Agent Invocation

@software-crafter

Execute \*refactor for {target-class-or-module}.

**Context Files:**

- src/\*

**Configuration:**

- level: 3 # Refactoring levels 1-6 (1=readability, 6=SOLID++)
- scope: module # file/module/project
- method: extract # extract/inline/rename/move
- mikado_planning: false # Use Mikado Method for complex refactorings

## Success Criteria

Refer to Crafty's quality gates in nWave/agents/software-crafter.md (Refactoring section).

**Key Validations:**

- [ ] Code quality metrics improved
- [ ] All tests passing after refactoring
- [ ] Refactoring levels applied systematically
- [ ] Technical debt reduced measurably
- [ ] Business naming and domain language consistent

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Refactored codebase with quality improvements

# Expected outputs (reference only):

# - src/\* (refactored implementation)

# - docs/refactoring/refactoring-log.md

# - docs/refactoring/quality-metrics.md
