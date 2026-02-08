# DW-REFACTOR: Systematic Code Analysis and Refactoring

**Wave**: CROSS_WAVE (continuous improvement support)
**Agent**: Crafty (nw-software-crafter)
**Command**: `*refactor`

## Overview

Execute systematic refactoring of existing codebases through progressive code quality improvement, Mikado Method planning for complex refactorings, and six-level refactoring hierarchy implementation.

Progressive refactoring hierarchy: Readability (L1-2) → Structure (L3-4) → Design (L5-6) with continuous validation and automated quality gates.

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

1. **Read codebase and refactoring specifications** and embed complete specifications inline
2. **Create a complete agent prompt** that includes:
   - Full codebase context (file structure, dependencies, existing quality metrics)
   - Complete refactoring hierarchy (6 levels with techniques and timing)
   - Mikado Method procedures (if refactoring is complex, > 1 day effort)
   - Quality gate checks and test execution procedures (inline, all bash commands)
   - Code quality metrics measurement procedures (cyclomatic complexity, maintainability index, duplication, coverage)
   - Multi-instance coordination procedures (how agents read modified code from prior refactoring instances)
   - All bash commands for building, testing, and measuring quality
   - Expected output formats and file structure
3. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
4. **Embed all refactoring procedures** - agent executes directly, no command delegation

### Agent Prompt Must Contain

- Full codebase context and file structure (inline, not path reference)
- Complete refactoring hierarchy with all 6 levels:
  - Level 1-2 (Readability/Complexity): Dead code, comments, naming, method extraction, duplication elimination
  - Level 3-4 (Organization/Abstraction): Class responsibilities, parameter objects, data clumps, primitive obsession
  - Level 5-6 (Design Patterns/SOLID): Strategy pattern, State pattern, SOLID principles, architectural patterns
- Test refactoring procedures: Apply L1-6 hierarchy to test code (naming clarity, complexity reduction, organization, abstractions, patterns, SOLID); detect test code smells (Obscure Test, Eager Test, Test Duplication, Mystery Guest); use same atomic transformations on test code
- Mikado Method procedures (if applicable): Goal definition, exploration cycle, tree visualization, discovery-tracking commits, execution sequencing
- Quality gate checks to perform before/after each level: All tests passing (100% required), code quality metrics collected, no regressions
- Test execution procedures: Build command, test command, expected output validation
- Code quality metrics procedures: Cyclomatic complexity measurement, duplication detection, coverage validation, maintainability scoring
- Multi-instance coordination: How to read files modified by previous refactoring instances, handle sequential refactorings, update quality baselines
- Bash commands for building, testing, measuring (complete with options and error handling)
- Expected deliverables: refactored src/*, refactoring-log.md, quality-metrics-report.md
- Quality gate criteria for refactoring completion

### What NOT to Include

- ❌ "Agent should invoke /nw:execute to run refactoring" (agent executes directly)
- ❌ "Use /nw:mikado to plan complex refactoring" (agent receives Mikado procedures inline)
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without complete specification embedded (agent needs level specs, not tool references)
- ❌ External code analysis tool references without complete command syntax embedded

### Example: What TO Do

✅ "Apply these 6 levels of refactoring in mandatory sequence: [COMPLETE LEVEL SPECIFICATIONS WITH TECHNIQUES]"
✅ "For complex refactoring, use Mikado Method following this procedure: [COMPLETE DISCOVERY AND EXECUTION STEPS]"
✅ "Measure quality before and after each level using: [COMPLETE MEASUREMENT PROCEDURES WITH BASH COMMANDS]"
✅ "Coordinate with prior refactoring instances by reading [COORDINATION PROCEDURE]"
✅ "Validate all tests passing (100% required) using: [COMPLETE TEST EXECUTION PROCEDURE]"
✅ "Provide these refactoring outputs: src/* (production code), tests/* (test code), refactoring-log.md, quality-metrics-report.md"

## Refactoring Across Agent Instances

The /nw:refactor command may be invoked as a new agent instance (via Task tool) to perform systematic refactoring. Each refactoring instance is independent: it loads the codebase, reads the refactoring specification, performs improvements, runs tests, documents changes, and terminates. If refactoring is complex and spans multiple instances (/nw:refactor L1, L2, L3), each instance reads prior modifications from the codebase and builds on them. Code files themselves serve as state: changes made by Instance 1 (L1 refactoring) are visible to Instance 2 (L2 refactoring) in the modified source.

## Context Files Required

- src/* - Production codebase to analyze and refactor
- tests/* - Test codebase to analyze and refactor

## Previous Artifacts (Wave Handoff)

- Varies based on refactoring context

## Agent Invocation

@nw-software-crafter

Execute \*refactor for {target-class-or-module}.

**Context Files:**

- src/\*

**Configuration:**

- level: 3 # Refactoring levels 1-6 (1=readability, 6=SOLID++)
- scope: module # file/module/project
- method: extract # extract/inline/rename/move
- mikado_planning: false # Use Mikado Method for complex refactorings

## Success Criteria

Refer to Crafty's quality gates in nWave/agents/nw-software-crafter.md (Refactoring section).

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

# - src/* (refactored production code)
# - tests/* (refactored test code)

# - docs/refactoring/refactoring-log.md

# - docs/refactoring/quality-metrics.md
