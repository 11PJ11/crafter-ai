---
agent-activation:
  required: true
  agent-id: software-crafter
  agent-name: "Crafty"
  agent-command: "*mikado"
  auto-activate: true
---

# DW-MIKADO: Complex Refactoring Roadmaps with Visual Tracking

**Wave**: CROSS_WAVE (complex refactoring support)
**Agent**: Crafty (software-crafter)
**Command**: `*mikado`

## Overview

Execute complex refactoring operations using enhanced Mikado Method with discovery-tracking commits, exhaustive exploration, and visual architecture coordination for architectural changes spanning multiple classes.

Revolutionary implementation captures every exploration attempt through commits, ensures all dependencies identified, and provides complete audit trail of refactoring decisions.

## Context Files Required

- src/* - Codebase to refactor
- docs/architecture/architecture-design.md - Target architecture (if available)

## Previous Artifacts (Wave Handoff)

- Varies based on refactoring context

## Agent Invocation

@software-crafter

Execute *mikado for {refactoring-goal}.

**Context Files:**
- src/*
- docs/architecture/architecture-design.md

**Configuration:**
- refactoring_goal: "Replace legacy UserManager with hexagonal architecture"
- complexity: complex  # simple/moderate/complex
- parallel_change: true
- visual_tracking: true

## Success Criteria

Refer to Crafty's quality gates in 5d-wave/agents/software-crafter.md (Mikado section).

**Key Validations:**
- [ ] Mikado graph complete with all dependencies
- [ ] Discovery commits capture all exploration attempts
- [ ] Leaf nodes implemented successfully
- [ ] Goal node achieved
- [ ] All tests passing throughout refactoring

## Next Wave

**Handoff To**: {invoking-agent-returns-to-workflow}
**Deliverables**: Refactored codebase with Mikado documentation

# Expected outputs (reference only):
# - docs/refactoring/mikado-graph.md
# - src/* (refactored implementation)
