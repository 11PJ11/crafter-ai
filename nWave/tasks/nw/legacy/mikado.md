# DW-MIKADO: Complex Refactoring Roadmaps with Visual Tracking

**Wave**: CROSS_WAVE (complex refactoring support)
**Agent**: Crafty (nw-software-crafter)
**Command**: `*mikado`

## Overview

Execute complex refactoring operations using enhanced Mikado Method with discovery-tracking commits, exhaustive exploration, and visual architecture coordination for architectural changes spanning multiple classes.

Revolutionary implementation captures every exploration attempt through commits, ensures all dependencies identified, and provides complete audit trail of refactoring decisions.

## Orchestrator Briefing

**CRITICAL ARCHITECTURAL CONSTRAINT**: Sub-agents launched via Task tool have NO ACCESS to the Skill tool. They can ONLY use: Read, Write, Edit, Bash, Glob, Grep.

### What Orchestrator Must Do

1. **Read codebase and refactoring goal** and embed complete specifications inline
2. **Create a complete agent prompt** that includes:
   - Full codebase context (file structure, dependencies, existing architecture)
   - Complete Mikado Method procedures (goal definition, exploration cycle, tree visualization, discovery-tracking commits)
   - Exhaustive exploration algorithm with termination criteria (all leaves tested, no new dependencies, tree stable, true leaves confirmed, complete dependency landscape mapped)
   - Concrete node specification standards (method signatures, file locations, refactoring techniques, atomic transformations)
   - Quality gate checks and test execution procedures (inline, all bash commands)
   - Code quality metrics procedures (inline measurement with tools available)
   - Multi-instance coordination procedures (how agents read modified code and updated Mikado graph from prior instances)
   - Tree file management procedures (markdown with checkbox format, indentation-based nesting, progress tracking)
   - All bash commands for building, testing, measuring quality
   - Expected output formats (Mikado graph, refactored src/*, discovery-tracking commits)
3. **Do NOT reference any /nw:* commands** in the agent prompt (agent cannot invoke them)
4. **Embed all Mikado procedures** - agent executes directly with no command delegation

### Agent Prompt Must Contain

- Full codebase context and file structure (inline, not path reference)
- Complete refactoring goal with business value articulation (specific objective, not vague technical goal)
- Complete Mikado Method procedures inline:
  - Goal definition framework (convert technical goals to stakeholder-understandable business value)
  - Discovery-tracking protocol (commit immediately after each discovery with specific format: "Discovery: [SpecificClass.Method(parameters)] requires [ExactPrerequisite] in [FilePath:LineNumber]")
  - Exhaustive exploration algorithm (EXPERIMENT → LEARN → GRAPH → COMMIT GRAPH → REVERT cycle)
  - Termination criteria (all leaves tested, no new dependencies emerge, stable tree structure, true leaves confirmed, complete landscape mapped)
  - Concrete node specification standards ([RefactoringTechnique | AtomicTransformation | CodeSmellTarget])
- Mikado tree file management:
  - Directory structure (docs/mikado/ with filename format <goal-name>.mikado.md)
  - Checkbox format (- [ ] for pending, - [x] for completed)
  - Indentation standards (4 spaces per nesting level for dependency depth)
  - Two-mode operation (exploration mode with discovery commits, execution mode with bottom-up implementation)
  - Dependency indentation rules (deeper indentation = higher dependency, parallel execution for same-level items)
  - Bottom-up execution order (deepest leaves first, one at a time)
  - Tree validation rules (structural integrity, execution readiness)
- Quality gate checks before/after each Mikado phase:
  - All tests passing (100% required)
  - Code quality metrics collected before/after exploration
  - Mikado graph stability verified (no new prerequisites emerging)
- Test execution procedures: Build command, test command, expected output validation (inline bash commands)
- Code quality metrics procedures: Cyclomatic complexity, duplication detection, coverage validation (inline with available tools)
- Multi-instance coordination: How to read modified code from prior instances, update Mikado graph state, continue exploration from last checkpoint
- Bash commands for building, testing, measuring (complete with options and error handling)
- Expected deliverables: docs/mikado/<goal-name>.mikado.md, src/* (refactored), discovery-tracking commits in git log
- Quality gate criteria for Mikado completion (all true leaves executed, tree converged to goal node)

### What NOT to Include

- ❌ "Agent should invoke /nw:execute to run Mikado phases" (agent executes directly)
- ❌ "Use /nw:refactor to implement leaf nodes" (agent receives refactoring procedures inline)
- ❌ Any reference to skills or other commands the agent should call
- ❌ References to next wave invocation (orchestrator handles wave transitions)
- ❌ Path references without complete specification embedded (agent needs procedures, not tool references)
- ❌ External analysis tools without complete bash command syntax embedded

### Example: What TO Do

✅ "Define Mikado goal using this business-value framework: [COMPLETE GOAL DEFINITION PROCEDURE WITH EXAMPLES]"
✅ "Execute exhaustive exploration following this procedure: [COMPLETE EXPERIMENT → LEARN → GRAPH → COMMIT → REVERT CYCLE WITH TERMINATION CRITERIA]"
✅ "Manage Mikado tree using this markdown format: [COMPLETE TREE STRUCTURE WITH INDENTATION RULES AND EXAMPLES]"
✅ "Implement leaf nodes bottom-up using these procedures: [COMPLETE EXECUTION STRATEGY WITH DEPENDENCY VALIDATION]"
✅ "Coordinate with prior instances by reading: [COMPLETE MULTI-INSTANCE COORDINATION PROCEDURE]"
✅ "Provide these Mikado outputs: docs/mikado/<goal>.mikado.md, discovery-tracking commits in git log, refactored src/*"

## Mikado Execution Across Multiple Instances

Complex Mikado refactorings may span multiple agent instances. The Mikado graph is persisted in docs/refactoring/mikado-graph.md. Each instance (working on different leaf nodes or consolidation steps) reads the graph, sees what prior instances accomplished (marked nodes and dependencies), updates the graph with new progress, and commits this progress. The graph is the cross-instance coordination mechanism. Discovery commits create an audit trail showing which paths each instance explored.

## Context Files Required

- src/\* - Codebase to refactor
- docs/architecture/architecture-design.md - Target architecture (if available)

## Previous Artifacts (Wave Handoff)

- Varies based on refactoring context

## Agent Invocation

@nw-software-crafter

Execute \*mikado for {refactoring-goal}.

**Context Files:**

- src/\*
- docs/architecture/architecture-design.md

**Configuration:**

- refactoring_goal: "Replace legacy UserManager with hexagonal architecture"
- complexity: complex # simple/moderate/complex
- parallel_change: true
- visual_tracking: true

## Success Criteria

Refer to Crafty's quality gates in nWave/agents/nw-software-crafter.md (Mikado section).

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

# - src/\* (refactored implementation)
