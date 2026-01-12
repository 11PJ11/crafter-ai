---
description: 'Create comprehensive planning document [agent] [goal-description]'
argument-hint: '[agent] [goal-description] - Example: @solution-architect "Migrate to microservices"'
agent-activation:
  required: false
  agent-parameter: true
  agent-command: "*feature-roadmap"
---

# DW-ROADMAP: Comprehensive Goal Planning Document

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT create the roadmap yourself. Your role is to dispatch to the appropriate expert agent.

### STEP 1: Extract Agent Parameter

Parse the first argument to extract the agent name:
- User provides: `/dw:roadmap @solution-architect "Migrate to microservices"`
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

### STEP 3.5: Baseline File Validation Gate (BLOCKING)

**This gate BLOCKS roadmap creation until baseline measurement file exists.**

#### 3.5.1: Derive Project ID

Convert goal description to kebab-case project ID:
- "Optimize test execution time" -> "optimize-test-execution-time"
- "Migrate to microservices" -> "migrate-to-microservices"

Rules:
- Lowercase all characters
- Replace spaces with hyphens
- Remove special characters except hyphens
- Collapse multiple hyphens to single hyphen

#### 3.5.2: Check Baseline File Existence

Expected path: `docs/feature/{project-id}/baseline.yaml`

Use the Read tool to check if file exists:
- If file exists AND is valid YAML: Proceed to 3.5.3
- If file exists but invalid YAML: Return syntax error
- If file NOT found: Return blocking error (3.5.4)

#### 3.5.3: Validate Baseline Structure

Check required fields based on baseline type:

For `performance_optimization`:
- [ ] `baseline.measurements.baseline_metric.value` is a number
- [ ] `baseline.measurements.breakdown` has >= 2 categories
- [ ] `baseline.measurements.bottleneck_ranking` is present
- [ ] `baseline.target.evidence_achievable` is non-empty
- [ ] No placeholder values detected

For `process_improvement`:
- [ ] At least one evidence section present (incident_references OR failure_modes OR stakeholder_input)
- [ ] `simplest_alternatives_considered` has >= 1 alternative

For `feature_development`:
- [ ] `current_state.description` is non-empty
- [ ] `simplest_alternatives_considered` has >= 1 alternative

If validation fails, return specific error:
```
BASELINE VALIDATION FAILED

File: docs/feature/{project-id}/baseline.yaml
Issue: {specific validation failure}

Please fix the baseline file and retry.
```

#### 3.5.4: Blocking Error (File Not Found)

If baseline file does not exist, return this error and STOP:

```
================================================================================
ROADMAP BLOCKED: Baseline measurement file not found
================================================================================

Expected location: docs/feature/{project-id}/baseline.yaml

WHAT TO DO:

Option 1: Create baseline using command (RECOMMENDED)
  /dw:baseline "{goal-description}"

Option 2: Create baseline.yaml manually
  See baseline specification at: 5d-wave/templates/baseline-template.yaml

WHY IS THIS REQUIRED?

  Roadmaps created without measurement data often address the wrong problem.
  This gate ensures:
  - The problem is quantified BEFORE solution design
  - The LARGEST bottleneck is identified
  - Quick wins are considered BEFORE complex solutions

  Reference: Incident ROADMAP-2025-12-03-001

FOR PROCESS IMPROVEMENTS (non-performance):
  Create baseline with type: "process_improvement"
  Include incident references or failure mode evidence
  Timing metrics are NOT required for process improvements

================================================================================
```

#### 3.5.5: Pass Baseline Data to Agent

If baseline validation passes, extract key data for agent:

```
Baseline Summary (from docs/feature/{project-id}/baseline.yaml):
- Type: {baseline.type}
- Problem: {baseline.problem_statement.summary}
- Largest Bottleneck: {baseline.measurements.bottleneck_ranking[0].component} ({baseline.measurements.bottleneck_ranking[0].impact})
- Quick Win Identified: {baseline.quick_wins[0].action} (Effort: {effort}, Impact: {expected_impact})
- Target: {baseline.target.current} -> {baseline.target.proposed} ({baseline.target.improvement_factor} improvement)

The roadmap MUST address the largest bottleneck first.
Quick wins should be Phase 1 before complex solutions.
```

Include this summary in the Task tool prompt after "Task type: roadmap".

### Parameter Parsing Rules

Apply these rules to ALL extracted parameters:
1. Strip leading and trailing whitespace
2. Remove surrounding quotes (single or double) if present
3. Validate parameter is non-empty after stripping
4. Reject if extra parameters provided beyond expected count

Example for roadmap.md:
- Input: `/dw:roadmap  @solution-architect  "Migrate to microservices"`
- After parsing:
  - agent_name = "solution-architect" (whitespace trimmed)
  - goal_description = "Migrate to microservices" (quotes removed)
- Input: `/dw:roadmap @solution-architect "Migrate to microservices" extra`
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
- Offer to help gather metrics with /dw:research or profiling

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

Note: This list is maintained in sync with the agent registry at `~/.claude/agents/dw/`. If you encounter "agent not found" errors, verify the agent is registered in that location.

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
  "Goal description is required. Usage: /dw:roadmap @agent 'goal description'"

---

## Overview

Invokes an expert agent to create a comprehensive, structured roadmap document that defines all phases and steps required to achieve a specific goal. The agent parameter allows selection of the most appropriate expert for the domain.

Produces a token-efficient master plan designed to be split into self-contained, atomic task files that prevent context degradation during implementation.

## Usage Examples

```bash
# Software architecture roadmap
/dw:roadmap @solution-architect "Migrate monolith to microservices"

# Data engineering roadmap
/dw:roadmap @data-engineer "Build real-time analytics pipeline"

# Complex refactoring with Mikado
/dw:roadmap @software-crafter "Replace legacy authentication system"

# Product feature roadmap
/dw:roadmap @product-owner "Implement multi-tenant support"
```

## Complete Workflow Integration

These commands work together to form a complete workflow:

```bash
# Step 1: Create comprehensive plan
/dw:roadmap @solution-architect "Migrate authentication system"

# Step 2: Decompose into atomic tasks
/dw:split @solution-architect "auth-migration"

# Step 3: Execute first research task
/dw:execute @researcher "docs/feature/auth-migration/steps/01-01.json"

# Step 4: Review before implementation
/dw:review @software-crafter task "docs/feature/auth-migration/steps/02-01.json"

# Step 5: Execute implementation
/dw:execute @software-crafter "docs/feature/auth-migration/steps/02-01.json"

# Step 6: Finalize when all tasks complete
/dw:finalize @devop "auth-migration"
```

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
- [ ] Acceptance criteria are specific and measurable
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
  created: "2024-01-01T00:00:00Z"
  estimated_duration: "2 weeks"  # human estimate

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
        acceptance_criteria:
          - "Provider comparison documented"
          - "Cost analysis complete"
```

## Next Steps

**Handoff To**: DW-SPLIT command for atomic task generation
**Deliverables**:
- Comprehensive roadmap.yaml file
- All steps designed to be executable independently
- Clear dependency graph for parallel execution

## Notes

### Design Philosophy

The roadmap is designed to be the **single source of truth** that gets transformed into atomic, self-contained tasks. The expert agent creating the roadmap should:

1. **Include all context** needed for each step
2. **Avoid forward references** to information in later steps
3. **Make dependencies explicit** rather than implicit
4. **Design for parallel execution** where possible

### Integration with Mikado Method

For complex refactoring projects, the roadmap can integrate with Mikado Method:
- Set `methodology: "mikado"` in project metadata
- Reference the Mikado graph for dependency structure
- Map leaf nodes to specific implementation steps
- Ensure discovery tracking for exploration phases

### Context Degradation Prevention

By creating a comprehensive roadmap first, we capture the full context while the expert agent has complete visibility. The subsequent split into atomic tasks ensures each sub-agent can work effectively without context accumulation that degrades performance over time.
