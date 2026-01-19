# DW-REFACTOR: Systematic Code Analysis and Refactoring

**Wave**: CROSS_WAVE (continuous improvement support)
**Agent**: Crafty (software-crafter)
**Command**: `*refactor`

## Overview

Execute systematic refactoring of existing codebases through progressive code quality improvement, Mikado Method planning for complex refactorings, and six-level refactoring hierarchy implementation.

Progressive refactoring hierarchy: Readability (L1-2) → Structure (L3-4) → Design (L5-6) with continuous validation and automated quality gates.

## Refactoring Across Agent Instances

The /nw:refactor command may be invoked as a new agent instance (via Task tool) to perform systematic refactoring. Each refactoring instance is independent: it loads the codebase, reads the refactoring specification, performs improvements, runs tests, documents changes, and terminates. If refactoring is complex and spans multiple instances (/nw:refactor L1, L2, L3), each instance reads prior modifications from the codebase and builds on them. Code files themselves serve as state: changes made by Instance 1 (L1 refactoring) are visible to Instance 2 (L2 refactoring) in the modified source.

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
