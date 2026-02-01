# DW-ROADMAP: Comprehensive Goal Planning Document

---
## ORCHESTRATOR INVOCATION PROTOCOL (MANDATORY)

**When YOU (orchestrator) delegate this command to an agent via Task tool:**

### CORRECT Pattern (minimal prompt):
```python
Task(
    subagent_type="solution-architect",
    prompt="Create roadmap: test-optimization (baseline: docs/feature/test-optimization/baseline.yaml)"
)
```

### Why This Works:
- ✅ Solution architect has internal roadmap template knowledge
- ✅ Baseline file contains all measurement context
- ✅ Project ID specifies where to save: docs/feature/{project-id}/roadmap.yaml
- ✅ No conversation context needed

### WRONG Patterns (avoid):
```python
# ❌ Embedding roadmap structure (architect already knows this)
Task(prompt="Create roadmap. Use this YAML structure: project/phases/steps...")

# ❌ Listing baseline details (baseline file has these)
Task(prompt="Create roadmap. Baseline shows tier 2 is 70%, tier 3 is 30%...")

# ❌ Phase guidance (architect knows how to organize phases)
Task(prompt="Create roadmap. Start with research phase, then implementation...")

# ❌ Any context from current conversation
Task(prompt="Create roadmap. As we discussed earlier, SISTER constraint is minority...")
```

### Key Principle:
**Command invocation = Project ID + Baseline file path ONLY**

The baseline file contains all measurement context. Your prompt should not duplicate it.

---

## AGENT PROMPT REINFORCEMENT (Command-Specific Guidance)

Reinforce command-specific principles extracted from THIS file (roadmap.md):

### Recommended Prompt Template:
```python
Task(
    subagent_type="solution-architect",
    prompt="""Create roadmap: test-optimization (baseline: docs/feature/test-optimization/baseline.yaml)

CRITICAL (from roadmap.md):
- Baseline file REQUIRED (blocking gate for measurement-first approach)
- Address LARGEST bottleneck first (from baseline ranking)
- Quick wins = Phase 1 (before complex architecture solutions)
- Research outputs MUST be quantitative (timing, not just categorization)

AVOID:
- ❌ Creating roadmap without baseline (enables wrong-problem pattern)
- ❌ Designing architecture before completing research
- ❌ Qualitative-only research (categorize by type without timing)
- ❌ Constraint-anchored design (optimizing for minority constraint)"""
)
```

### Why Add This Guidance:
- **Source**: Extracted from roadmap.md (not conversation context)
- **Deterministic**: Same principles every time you invoke roadmap
- **Reinforcing**: Prevents Incident ROADMAP-2025-12-03-001 pattern
- **Token-efficient**: ~100 tokens vs 34-step wrong roadmap

### What NOT to Add:
```python
# ❌ WRONG - This uses orchestrator's conversation context
Task(prompt="""Create roadmap: test-optimization

The baseline shows tier 2 is 70% and tier 3 is 30%.
SISTER constraint is minority but was emphasized in discussion.""")
```

---

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT create the roadmap yourself. Your role is to dispatch to the appropriate expert agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/nw:roadmap @solution-architect "Migrate to microservices"`
- Extract agent name: `solution-architect` (remove @ prefix)
- Validate agent name is one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

### STEP 2: Verify Agent Availability

Before proceeding to Task tool invocation:
- Verify the extracted agent name matches an available agent in the system
- Check agent is not at maximum concurrency
- Confirm agent type is compatible with this command

Valid agents: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

If agent unavailable:
- Return error: "Agent '{agent-name}' is not currently available. Available agents: {list}"
- Suggest alternative agents if applicable

### STEP 3: Extract Goal Description

Extract the second argument (goal description):
- Example: `"Migrate monolith to microservices"`
- This is the high-level objective the roadmap will plan for

### STEP 3.5: Baseline Validation (Schema v2.0)

<!-- Baseline file validation gate removed in Schema v2.0 -->
<!-- Baseline files eliminated as write-only artifacts (300k token savings) -->
<!-- All measurement data now embedded directly in roadmap via measurement_gate section -->

**Schema v2.0**: Baseline files are no longer required as separate artifacts. The orchestrator (develop.md) embeds measurement data directly in the roadmap creation prompt. If measurement context is available, it is passed inline to the architect agent.

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for roadmap.md:
- Input: `/nw:roadmap  @solution-architect  "Migrate to microservices"`
- After parsing:
  - agent_name = "solution-architect" (whitespace trimmed)
  - goal_description = "Migrate to microservices" (quotes removed)
- Input: `/nw:roadmap @solution-architect "Migrate to microservices" extra`
- Error: "Too many parameters. Expected 2, got 3"

### STEP 4: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Agent name extracted and validated (not empty)
- [ ] Agent name in valid agent list
- [ ] Agent availability confirmed
- [ ] Goal description extracted and non-empty
- [ ] Goal description within reasonable bounds (< 500 chars)
- [ ] Parameters contain no secrets or credentials
- [ ] No user input still has surrounding quotes

**ONLY proceed to Task tool invocation if ALL items above are checked.**

If any check fails, return specific error and stop.

### STEP 5: Invoke Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the specified expert agent. Do NOT attempt to create the roadmap yourself.

Invoke the Task tool with this exact pattern:

```
Task: "You are the {agent-name} agent.

Your specific role for this command: Create comprehensive planning documents that enable atomic task execution

Task type: roadmap

## Pre-Planning Measurement Gate (MANDATORY - BLOCKING)

**This gate BLOCKS roadmap creation until baseline data is provided.**

Before creating this roadmap, the user MUST provide:

### Baseline Metrics (REQUIRED)
- [ ] Current total execution time: ___ seconds
- [ ] Execution time breakdown by component:
  | Component | Time | % of Total |
  |-----------|------|------------|
  | ... | ... | ... |
- [ ] Largest bottleneck identified: ___
- [ ] Second largest bottleneck: ___

### Target Validation (REQUIRED)
- [ ] Proposed target: ___ seconds
- [ ] Theoretical speedup with approach: ___x
- [ ] Evidence showing target is achievable: ___

### Quick Win Analysis (REQUIRED)
- [ ] Simplest possible change identified: ___
- [ ] Expected impact of simple change: ___
- [ ] Why simple change is insufficient (if proposing complex solution): ___

### Gate Status
- [ ] **PASSED**: All measurements complete, proceed with roadmap
- [ ] **BLOCKED**: Missing measurements, CANNOT proceed

**If BLOCKED:**
- DO NOT create a roadmap
- Request measurement data from user
- Offer to help gather metrics with /nw:research or profiling

**For process improvements (non-performance):**
- Document that this is a process improvement, not performance optimization
- Provide qualitative evidence of the problem being solved
- Still require "simplest alternatives considered" analysis

Create a comprehensive roadmap for achieving this goal: {goal-description}

Your responsibilities:
1. Analyze the goal and determine all phases and steps required
2. Design each step to be self-contained and atomic
3. Identify dependencies and parallel execution opportunities
4. Provide realistic time estimates for each step
5. Include complete context in each step for sub-agent execution
6. Generate structured YAML roadmap document

Output Location: docs/feature/{project-id}/roadmap.yaml

Roadmap Structure (YAML):
- project: Metadata including id, name, goal, methodology, estimated_duration
- phases: Numbered phases with purpose and steps
- steps: Self-contained tasks with description, motivation, estimated_hours, dependencies, acceptance_criteria

Key Principles:
- Each step must be executable without prior context
- Include all necessary information within each step
- Avoid forward references to information in later steps
- Make dependencies explicit rather than implicit
- Design for parallel execution where possible
- Use YAML format for token efficiency

Research Phase Requirements (MANDATORY for performance roadmaps):

The research phase MUST produce QUANTITATIVE outputs, not just categorization.

### Required Research Outputs

**1. Timing Analysis (REQUIRED)**
```yaml
timing_breakdown:
  format: |
    | Category | Count | Total Time | % of Total | Quick Win? |
    |----------|-------|------------|------------|------------|
    | {cat1}   | N     | Xm Ys      | XX%        | YES/NO     |
  requirement: "MUST measure time, not just count or categorize"
```

**2. Impact Ranking (REQUIRED)**
```yaml
impact_ranking:
  format: |
    1. {category}: {time} ({percentage}%) - {parallelizable?}
    2. {category}: {time} ({percentage}%) - {parallelizable?}
  requirement: "MUST rank by TIME IMPACT, not by type"
```

**3. Quick Win Identification (REQUIRED)**
```yaml
quick_wins:
  format: |
    | Change | Effort | Expected Impact | Impact/Effort |
    |--------|--------|-----------------|---------------|
    | {change} | LOW/MED/HIGH | {time saved} | {ratio} |
  requirement: "MUST identify before architecture design"
```

### Research Anti-Patterns to Avoid

- DO NOT categorize only by type (SISTER/non-SISTER) - include timing
- DO NOT assume most-mentioned constraint is most important
- DO NOT skip timing analysis for "obvious" problems
- DO NOT design architecture before completing research

### Research Validation Gate

Before proceeding to architecture design, verify:
- [ ] Timing breakdown includes ALL categories
- [ ] Categories ranked by time impact (not alphabetically or by type)
- [ ] Quick wins identified with impact/effort ratio
- [ ] Largest bottleneck explicitly identified

If research is qualitative-only (no timing), STOP and gather metrics.

For complex refactoring projects, set methodology: 'mikado' and include mikado_integration section referencing the Mikado graph.

Save the roadmap to docs/feature/{project-id}/roadmap.yaml where project-id is kebab-case derived from the goal."
```

**Parameter Substitution**:
- Replace `{agent-name}` with the extracted agent name (e.g., "solution-architect")
- Replace `{goal-description}` with the goal text

### Agent Registry

Valid agents are: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop

Note: This list is maintained in sync with the agent registry at `~/.claude/agents/nw/`. If you encounter "agent not found" errors, verify the agent is registered in that location.

Each agent has specific capabilities:
- **researcher**: Information gathering, analysis, documentation
- **software-crafter**: Implementation, testing, refactoring, code quality
- **solution-architect**: System design, architecture decisions, planning
- **product-owner**: Requirements, business analysis, stakeholder alignment
- **acceptance-designer**: Test definition, acceptance criteria, BDD
- **devop**: Deployment, operations, infrastructure, lifecycle management

### Example Invocations

**For solution-architect planning microservices migration**:
```
Task: "You are the solution-architect agent.

Your specific role for this command: Create comprehensive planning documents that enable atomic task execution

Task type: roadmap

Create a comprehensive roadmap for achieving this goal: Migrate monolith to microservices

[... rest of instructions ...]"
```

**For software-crafter planning authentication refactor**:
```
Task: "You are the software-crafter agent.

Your specific role for this command: Create comprehensive planning documents that enable atomic task execution

Task type: roadmap

Create a comprehensive roadmap for achieving this goal: Replace legacy authentication system

[... rest of instructions ...]"
```

### Error Handling

**Invalid Agent Name**:
- If agent name is not in the valid list, respond with error:
  "Invalid agent name: {name}. Must be one of: researcher, software-crafter, solution-architect, product-owner, acceptance-designer, devop"

**Missing Goal Description**:
- If goal description is not provided, respond with error:
  "Goal description is required. Usage: /nw:roadmap @agent 'goal description'"

---

## Overview

Invokes an expert agent to create a comprehensive, structured roadmap document that defines all phases and steps required to achieve a specific goal. The agent parameter allows selection of the most appropriate expert for the domain.

Produces a token-efficient master plan designed to be split into self-contained, atomic task files that prevent context degradation during implementation.

## Usage Examples

```bash
# Software architecture roadmap
/nw:roadmap @solution-architect "Migrate monolith to microservices"

# Data engineering roadmap
/nw:roadmap @data-engineer "Build real-time analytics pipeline"

# Complex refactoring with Mikado
/nw:roadmap @software-crafter "Replace legacy authentication system"

# Product feature roadmap
/nw:roadmap @product-owner "Implement multi-tenant support"
```

## Complete Workflow Integration (Schema v2.0)

These commands work together to form a complete workflow:

```bash
# Step 1: Create comprehensive plan
/nw:roadmap @solution-architect "Migrate authentication system"

# Step 2: Execute first research task (NEW SIGNATURE - Schema v2.0)
/nw:execute @researcher "auth-migration" "01-01"

# Step 3: Execute implementation tasks (review is now inline during execution)
/nw:execute @software-crafter "auth-migration" "02-01"
/nw:execute @software-crafter "auth-migration" "02-02"

# Step 4: Finalize when all tasks complete
/nw:finalize @devop "auth-migration"
```

**Eliminated Steps** (Schema v2.0):
- ❌ `/nw:split` - No longer needed, context extracted directly from roadmap
- ❌ `/nw:review` for individual steps - Review now inline during execution (REVIEW phase)

For details on each command, see respective sections.

## Context Files Required

- Goal description or requirements
- Relevant existing documentation
- docs/refactoring/mikado-graph.md - If using Mikado Method

---

## Coordinator Success Criteria

Verify the coordinator performed these tasks:
- [ ] Agent name extracted from parameters correctly
- [ ] Agent name validated against known agents
- [ ] Goal description extracted and validated
- [ ] Pre-invocation validation checklist passed
- [ ] Task tool invocation prepared with correct parameters
- [ ] Task tool returned success status
- [ ] User received confirmation of agent invocation

## Agent Execution Success Criteria

The invoked agent must accomplish (Reference Only):
- [ ] Valid YAML syntax
- [ ] Unique project ID in kebab-case
- [ ] All phases numbered sequentially
- [ ] Each step contains enough information to be self-contained
- [ ] Acceptance criteria are specific, measurable, and BEHAVIORAL (no private methods, no internal structure)
- [ ] Step decomposition ratio <= 2.5 (steps / production files)
- [ ] No 3+ identical-pattern steps (must be batched)
- [ ] No validation-only steps (validation belongs in REVIEW phase)
- [ ] Dependencies properly mapped between steps
- [ ] Time estimates provided for planning
- [ ] File saved as `docs/feature/{project-id}/roadmap.yaml`
- [ ] Mikado integration included if applicable

---

## Agent Invocation (Reference Documentation)

The following section documents what the invoked agent will do. **You (the coordinator) do not execute this - the planning expert does.**

### Primary Task Instructions

**Task**: Analyze goal and generate comprehensive action plan

**Key Principles**:
- Each step must be **self-contained and atomic**
- Steps should be **executable without prior context**
- Include all necessary information within each step
- Design for parallel execution where possible
- Prevent context degradation through completeness

**Output Location**: `docs/feature/{project-id}/roadmap.yaml`

**Roadmap Structure (YAML format for token efficiency):**

```yaml
project:
  id: "project-unique-id"  # kebab-case, no spaces
  name: "Human Readable Project Name"
  goal: "Clear description of end goal"
  methodology: "standard"  # or "mikado" for complex refactoring
  schema_version: "2.0"  # REQUIRED: Schema version for 7-phase TDD
  created: "2024-01-01T00:00:00Z"
  estimated_duration: "2 weeks"  # human estimate

# TDD Phases Configuration (Schema v2.0)
tdd_phases:
  - PREPARE
  - RED_ACCEPTANCE
  - RED_UNIT
  - GREEN
  - REVIEW
  - REFACTOR_CONTINUOUS
  - COMMIT

# Execution Configuration (Schema v2.0)
execution_config:
  context_extraction_method: "from_roadmap"  # No step files needed
  status_tracking_file: "execution-status.yaml"
  token_budget_per_step: 5000  # Extracted context limit

phases:
  - number: 1
    name: "Planning"
    purpose: "Define scope and requirements"
    steps:
      - number: 1
        name: "Requirements Analysis"
        description: "Analyze and document functional requirements"
        motivation: "Clear requirements prevent scope creep"
        estimated_hours: 4
        dependencies: []  # step references like "1.2", "2.1"
        step_type: "research"  # research|infrastructure|atdd
        suggested_agent: "researcher"  # Optional: agent best suited
        acceptance_criteria:
          - "All user stories documented"
          - "Acceptance criteria defined"
          - "Non-functional requirements identified"

      - number: 2
        name: "Technical Design"
        description: "Create technical architecture"
        motivation: "Architecture guides implementation"
        estimated_hours: 6
        dependencies: ["1.1"]
        step_type: "research"
        suggested_agent: "solution-architect"
        acceptance_criteria:
          - "Component diagram created"
          - "Data flow documented"
          - "Technology stack selected"

  - number: 2
    name: "Implementation"
    purpose: "Build the solution"
    steps:
      - number: 1
        name: "Core Module Development"
        description: "Implement core business logic"
        motivation: "Core functionality enables all features"
        estimated_hours: 16
        dependencies: ["1.2"]
        step_type: "atdd"  # ATDD step with acceptance test
        suggested_agent: "software-crafter"
        suggested_scenario:  # Optional: mapped acceptance test
          test_file: "tests/acceptance/core_module.feature"
          scenario_name: "Create core module with basic functionality"
          scenario_index: 0
          test_format: "feature"  # Optional: auto-detected from extension
        acceptance_criteria:
          - "Core module passes all unit tests"
          - "API contracts fulfilled"
          - "Performance benchmarks met"

mikado_integration:  # Only if methodology: "mikado"
  graph_location: "docs/refactoring/mikado-graph.md"
  goal_node: "Replace legacy system"
  leaf_nodes:
    - "Extract interface"
    - "Create adapter"
    - "Implement new service"
  discovery_tracking: true
```

### Roadmap Creation Guidelines:

1. **Project Identification**:
   - Use kebab-case for project ID (e.g., "user-auth-refactor")
   - Keep IDs unique and descriptive
   - No spaces or special characters in ID

2. **Phase Organization**:
   - Typical phases: Planning, Design, Implementation, Testing, Deployment
   - Number phases sequentially (1, 2, 3...)
   - Each phase should have clear purpose

3. **Step Definition**:
   - Steps numbered within phase (1.1, 1.2, 2.1...)
   - Include concrete acceptance criteria
   - List explicit dependencies between steps
   - Provide realistic time estimates

4. **Mikado Method Integration**:
   - Set methodology: "mikado" for complex refactoring
   - Reference existing Mikado graph
   - Map leaf nodes to implementation steps
   - Include discovery tracking flag

5. **Token Optimization**:
   - Use YAML format (more compact than JSON)
   - Abbreviate where clear (hrs, deps, desc)
   - Avoid redundant descriptions
   - Keep acceptance criteria concise

6. **Step Decomposition Principles** (ANTI-OVER-DECOMPOSITION):
   - **Rule**: Decompose by IMPLEMENTATION UNIT, not by test scenario
   - Each step MUST produce NEW production code (not just test validation)
   - If a step only validates existing behavior, MERGE it with the producing step
   - Target ratio: **<= 2.5 steps per production file**
   - Detection: If `steps_count / production_files > 2.5`, likely over-decomposed
   - Acceptance test scenarios ≠ implementation steps
   - **Merge candidates**:
     - Steps that only add tests for already-implemented behavior
     - Steps that validate non-functional properties (metadata, stateless, no-daemon)
     - Steps that test error handling already implemented in a prior step
   - **Example (BAD)**: 13 steps for 4 production files (ratio 3.25, 38% no-op steps)
   - **Example (GOOD)**: 7 steps for 4 production files (ratio 1.75, 0% no-op steps)

### Example Minimal Roadmap:

```yaml
project:
  id: "auth-upgrade"
  name: "Authentication System Upgrade"
  goal: "Migrate from basic auth to OAuth2"
  methodology: "standard"
  created: "2024-01-01T00:00:00Z"

phases:
  - number: 1
    name: "Planning"
    purpose: "Define OAuth2 requirements"
    steps:
      - number: 1
        name: "OAuth2 Provider Selection"
        description: "Evaluate and select OAuth2 provider"
        motivation: "Provider choice affects entire implementation"
        estimated_hours: 3
        step_type: "research"  # Non-ATDD step
        suggested_agent: "researcher"
        acceptance_criteria:
          - "Provider comparison documented"
          - "Cost analysis complete"

  - number: 2
    name: "Implementation"
    purpose: "Implement OAuth2 authentication"
    steps:
      - number: 1
        name: "OAuth2 Login Flow"
        description: "Implement user login via OAuth2"
        motivation: "Core authentication feature"
        estimated_hours: 8
        step_type: "atdd"  # ATDD step
        suggested_agent: "software-crafter"
        # Schema v2.0: Per-step execution fields
        test_file: "tests/acceptance/auth.feature"
        scenario_line: 12  # Line number where scenario starts
        scenario_name: "User logs in via OAuth2"
        quality_gates:
          acceptance_test_must_fail_first: true
          unit_tests_must_fail_first: true
          no_mocks_inside_hexagon: true
          refactor_level: 3
        acceptance_criteria:
          - "User can authenticate via OAuth2 provider"
          - "JWT token generated after successful login"
```

### Step Types (COSA - What to Do)

The roadmap defines WHAT needs to be done. The `/nw:split` command determines HOW.

**Valid step_type values:**

| Type | Description | TDD Phases | Example |
|------|-------------|------------|---------|
| `atdd` | Acceptance Test Driven Development | All phases (from canonical schema) | Feature implementation |
| `research` | Investigation, analysis, documentation | Partial phases (skip RED/GREEN) | Requirements analysis |
| `infrastructure` | Setup, configuration, tooling | Partial phases (skip RED/GREEN) | CI/CD pipeline setup |

**Field Descriptions:**

- **step_type**: Required. Indicates how `/nw:split` should generate the step file
- **suggested_agent**: Optional. Recommended agent for execution (validated by split)
- **suggested_scenario**: Optional. Mapped acceptance test for ATDD steps
  - `test_file`: Path to acceptance test file (any format: .feature, .cs, .py, .js, .java, etc.)
  - `scenario_name`: Business scenario/test method description
  - `scenario_index`: 0-based index in test file (or test method name for xUnit-style)
  - `test_format`: Optional. Test format hint (feature, pytest, jest, nunit, xunit, junit5)

**Supported Test Formats:**

| Format | Extension | Framework | Scenario Identifier |
|--------|-----------|-----------|---------------------|
| feature | .feature | Cucumber/SpecFlow/Behave | Scenario name |
| pytest | .py | pytest-bdd, pytest | Test function name |
| jest | .js/.ts | Jest | test() description |
| nunit | .cs | NUnit | [Test] method name |
| xunit | .cs | xUnit | [Fact] method name |
| junit5 | .java | JUnit 5 | @Test method name |

**Roadmap Responsibility (COSA):**
- Define WHAT needs to be accomplished
- Suggest appropriate agent and scenario mapping
- Keep steps high-level and business-focused

**Split Responsibility (COME):**
- Validate suggested mappings against actual files
- Generate detailed instructions
- Create self_contained_context
- Assign final execution_agent

## Next Steps

**Handoff To**: DW-SPLIT command for atomic task generation
**Deliverables**:
- Comprehensive roadmap.yaml file
- All steps designed to be executable independently
- Clear dependency graph for parallel execution

## Embedded Roadmap Schema

The compact roadmap template is embedded below for direct use without external file dependencies.

<!-- BUILD:INJECT:START:nWave/templates/roadmap-compact.yaml -->
<!-- Roadmap template will be injected here at build time -->
<!-- BUILD:INJECT:END -->

## Notes

### Design Philosophy (Schema v2.0)

The roadmap is designed to be the **single source of truth** for step execution. In Schema v2.0, there are NO intermediate step files - the orchestrator extracts context directly from the roadmap. The expert agent creating the roadmap should:

1. **Include all context** needed for each step (agents receive this via context extraction)
2. **Avoid forward references** to information in later steps
3. **Make dependencies explicit** rather than implicit
4. **Design for parallel execution** where possible
5. **Include per-step execution fields** (test_file, scenario_line, quality_gates)

### Context Extraction Pattern (Schema v2.0)

**How Orchestrator Passes Context to Sub-Agents:**

```python
# Step 1: Read roadmap
roadmap = read_yaml(f"docs/feature/{project_id}/roadmap.yaml")

# Step 2: Extract context for specific step
phase_idx = int(step_id.split('-')[0]) - 1
step_idx = int(step_id.split('-')[1]) - 1
step_context = roadmap['phases'][phase_idx]['steps'][step_idx]

# Step 3: Build prompt with extracted context
Task(
    subagent_type="software-crafter",
    prompt=f"""Execute step {step_id}: {step_context['name']}

    DESCRIPTION:
    {step_context['description']}

    MOTIVATION:
    {step_context['motivation']}

    ACCEPTANCE CRITERIA:
    {chr(10).join(f'- {ac}' for ac in step_context['acceptance_criteria'])}

    TEST FILE: {step_context.get('test_file', 'N/A')}
    SCENARIO LINE: {step_context.get('scenario_line', 'N/A')}

    QUALITY GATES:
    - Acceptance test must fail first: {step_context['quality_gates']['acceptance_test_must_fail_first']}
    - No mocks inside hexagon: {step_context['quality_gates']['no_mocks_inside_hexagon']}
    - Refactor level: {step_context['quality_gates']['refactor_level']}

    Execute using 7-phase TDD cycle (PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN, REVIEW, REFACTOR_CONTINUOUS, COMMIT).
    """
)
```

**Token Budget**: ~5k tokens per step (extracted on-demand, not stored)
**Result**: 94% token reduction vs step files (5.2M → 310k for 35-step project)

### Integration with Mikado Method

For complex refactoring projects, the roadmap can integrate with Mikado Method:
- Set `methodology: "mikado"` in project metadata
- Reference the Mikado graph for dependency structure
- Map leaf nodes to specific implementation steps
- Ensure discovery tracking for exploration phases

### Context Degradation Prevention

By creating a comprehensive roadmap first, we capture the full context while the expert agent has complete visibility. The subsequent split into atomic tasks ensures each sub-agent can work effectively without context accumulation that degrades performance over time.
