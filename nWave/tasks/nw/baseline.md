---
description: 'Establish measurement baseline before roadmap creation [goal-description]'
argument-hint: '[goal-description] - Example: "optimize test execution time"'
agent-activation:
  required: false
  agent-parameter: false
  agent-command: "*research"
---

# DW-BASELINE: Establish Measurement Baseline

## CRITICAL: Agent Invocation Protocol

**YOU ARE THE COORDINATOR** - Do NOT gather baseline data yourself. Your role is to dispatch to the researcher agent for evidence-based data gathering.

### STEP 1: Extract Goal Description

Parse the argument to extract the goal:
- User provides: `/nw:baseline "optimize test execution time"`
- Extract goal: `optimize test execution time`

### STEP 2: Derive Project ID

Convert goal description to kebab-case project ID:
- Input: `"Optimize Test Execution Time"`
- Output: `optimize-test-execution-time`

Rules:
- Lowercase all characters
- Replace spaces with hyphens
- Remove special characters except hyphens
- Collapse multiple hyphens to single hyphen

### STEP 3: Check for Existing Baseline

Check if baseline file already exists:
- Path: `docs/feature/{project-id}/baseline.yaml`

If exists:
```
WARNING: Baseline file already exists at docs/feature/{project-id}/baseline.yaml

Options:
1. View existing baseline and continue to /nw:roadmap
2. Replace baseline with new measurements (overwrites existing)
3. Cancel and review existing baseline first

Which option? [1/2/3]
```

### STEP 4: Determine Baseline Type

Ask user which type of work this baseline supports:

```
What type of baseline is needed?

1. PERFORMANCE_OPTIMIZATION
   - Improving speed, reducing resource usage, optimizing throughput
   - Requires: timing measurements, breakdown analysis, target metrics

2. PROCESS_IMPROVEMENT
   - Fixing workflow issues, preventing incidents, improving reliability
   - Requires: incident references, failure modes, qualitative evidence

3. FEATURE_DEVELOPMENT
   - Building new capabilities, greenfield or brownfield development
   - Requires: current state analysis, requirements source

Select type [1/2/3]:
```

### STEP 5: Pre-Invocation Validation Checklist

Before invoking Task tool, verify ALL items:
- [ ] Goal description extracted and non-empty
- [ ] Project ID derived (kebab-case)
- [ ] Baseline type selected (1, 2, or 3)
- [ ] Target directory can be created: `docs/feature/{project-id}/`
- [ ] No secrets or credentials in goal description

**ONLY proceed to Task tool invocation if ALL items above are checked.**

### STEP 6: Invoke Researcher Agent Using Task Tool

**MANDATORY**: Use the Task tool to invoke the researcher agent. Do NOT attempt to gather baseline data yourself.

Select the appropriate Task prompt based on baseline type:

---

#### FOR TYPE 1: PERFORMANCE_OPTIMIZATION

```
Task: "You are the researcher agent (Nova).

Your specific role for this command: Establish quantitative baseline measurements for performance optimization

Task type: baseline_measurement

Goal: {goal-description}
Project ID: {project-id}
Baseline Type: performance_optimization

Your responsibilities:

1. MEASURE THE CURRENT STATE
   - Identify what metric defines success (time, memory, throughput, etc.)
   - Gather actual measurements - NO placeholders or estimates
   - Document measurement method and timestamp
   - Ensure measurements are reproducible

2. CREATE BREAKDOWN ANALYSIS
   - Identify all components contributing to the metric
   - Measure each component individually
   - Calculate percentage contribution of each
   - Sort by impact (largest first)

3. RANK BOTTLENECKS
   - List components by impact (highest first)
   - For each bottleneck, assess if quick win is possible
   - If quick win exists, describe it and estimate effort
   - Effort levels: LOW (config only), MEDIUM (small code change), HIGH (significant work)

4. IDENTIFY QUICK WINS
   - Find changes with HIGH impact/effort ratio
   - Document at least 1 quick win if largest bottleneck has one
   - Be specific about what the change involves
   - Estimate expected impact with evidence

5. SET REALISTIC TARGET
   - Current value MUST match baseline metric
   - Proposed value MUST be achievable based on breakdown analysis
   - Show calculation: if we fix X, we expect Y improvement because Z
   - Do NOT set arbitrary targets

6. VALIDATE AND OUTPUT
   - Verify all numeric fields contain actual numbers
   - Ensure baseline_metric.value == target.current
   - Save to: docs/feature/{project-id}/baseline.yaml
   - Use the BASELINE FILE SCHEMA (embedded below) for structure

Output Location: docs/feature/{project-id}/baseline.yaml

CRITICAL: All numeric values MUST be actual measurements.
- value: 532 (CORRECT - actual number)
- value: 'TBD' (WRONG - placeholder)
- value: '~500' (WRONG - estimate without measurement)

If you cannot measure something, document WHY and what would be needed to measure it.
Do NOT proceed with estimates disguised as measurements."
```

---

#### FOR TYPE 2: PROCESS_IMPROVEMENT

```
Task: "You are the researcher agent (Nova).

Your specific role for this command: Establish qualitative baseline for process improvement

Task type: baseline_measurement

Goal: {goal-description}
Project ID: {project-id}
Baseline Type: process_improvement

Your responsibilities:

1. GATHER INCIDENT EVIDENCE
   - Search for related incidents, post-mortems, or failure records
   - Document at least 1 concrete incident with:
     - ID, date, summary, root cause, link to documentation
   - If no formal incidents exist, document informal failure patterns

2. IDENTIFY FAILURE MODES
   - What patterns of failure occur?
   - How frequently does each pattern occur?
   - What is the impact when it happens?
   - What evidence supports this failure mode?

3. COLLECT STAKEHOLDER INPUT (if available)
   - Who is affected by this problem?
   - What are their specific concerns?
   - What solutions have they proposed?

4. DOCUMENT ALTERNATIVES CONSIDERED
   - REQUIRED: At least 2 simpler alternatives
   - For each alternative:
     - Describe what it would involve
     - Explain specifically WHY it's insufficient
     - Provide verdict: INSUFFICIENT, PARTIAL, or ADEQUATE
   - If no simple alternative is insufficient, maybe complex solution isn't needed?

5. VALIDATE AND OUTPUT
   - Ensure at least one of: incident_references OR failure_modes
   - Ensure at least 2 alternatives documented
   - Each alternative must have specific why_insufficient reason
   - Save to: docs/feature/{project-id}/baseline.yaml
   - Use the BASELINE FILE SCHEMA (embedded below) for structure

Output Location: docs/feature/{project-id}/baseline.yaml

CRITICAL: Process improvements need EVIDENCE, not assumptions.
- 'This seems like a problem' (WRONG - no evidence)
- 'Incident X on date Y showed...' (CORRECT - concrete evidence)

If you cannot find concrete evidence, document what would need to happen
to establish that this is actually a problem worth solving."
```

---

#### FOR TYPE 3: FEATURE_DEVELOPMENT

```
Task: "You are the researcher agent (Nova).

Your specific role for this command: Establish baseline for feature development

Task type: baseline_measurement

Goal: {goal-description}
Project ID: {project-id}
Baseline Type: feature_development

Your responsibilities:

1. ANALYZE CURRENT STATE
   - Is this greenfield (nothing exists) or brownfield (existing code)?
   - If brownfield:
     - What capabilities exist today?
     - What are the limitations?
     - Why is the current approach insufficient?
   - If greenfield:
     - What related functionality exists?
     - What constraints does existing code impose?

2. DOCUMENT REQUIREMENTS SOURCE
   - Where did these requirements come from?
   - How were they validated?
   - Is there user feedback, business case, or technical need?
   - List specific requirements if known

3. CONSIDER SIMPLEST ALTERNATIVES (RECOMMENDED)
   - Even for features, consider if simpler approaches exist
   - Could existing tools/libraries solve this?
   - Is there a minimal version that delivers 80% of value?
   - Document why alternatives are insufficient (if they are)

4. VALIDATE AND OUTPUT
   - Ensure current_state.description is filled
   - Ensure requirements_source.origin is filled
   - Save to: docs/feature/{project-id}/baseline.yaml
   - Use the BASELINE FILE SCHEMA (embedded below) for structure

Output Location: docs/feature/{project-id}/baseline.yaml

CRITICAL: Features need clear origin and validation.
- 'We should build X' (WRONG - no origin or validation)
- 'User feedback from Y requested X, validated with stakeholder Z' (CORRECT)"
```

---

### Parameter Substitution

Replace in Task prompts:
- `{goal-description}` with the extracted goal text
- `{project-id}` with the derived kebab-case ID

### Error Handling

**Missing Goal Description**:
```
ERROR: Goal description is required.
Usage: /nw:baseline "description of what you want to optimize/improve/build"

Examples:
  /nw:baseline "optimize test execution time"
  /nw:baseline "fix roadmap prioritization process"
  /nw:baseline "add baseline enforcement to workflow"
```

**Directory Creation Failure**:
```
ERROR: Cannot create workflow directory.
Path: docs/feature/{project-id}/

Please ensure docs/feature/ exists and is writable.
```

---

## Overview

Invokes the researcher agent to establish a quantitative or qualitative baseline BEFORE roadmap creation. This command creates the baseline.yaml file required by /nw:roadmap.

The baseline file ensures measurement-first approach and prevents the "wrong problem" anti-pattern identified in incident ROADMAP-2025-12-03-001.

## Usage Examples

```bash
# Performance optimization baseline
/nw:baseline "optimize test execution time"

# Process improvement baseline
/nw:baseline "prevent roadmap prioritization errors"

# Feature development baseline
/nw:baseline "add multi-tenant support"
```

## Complete Workflow Integration

```bash
# Step 1: Establish baseline (THIS COMMAND)
/nw:baseline "optimize test execution time"

# Step 2: Create roadmap (now allowed - baseline exists)
/nw:roadmap @solution-architect "optimize test execution time"

# Step 3: Split into tasks
/nw:split @solution-architect "test-optimization"

# Step 4: Execute tasks
/nw:execute @researcher "docs/feature/test-optimization/steps/01-01.json"
```

## Context Files Required

- None (baseline schema is embedded below)

---

## Coordinator Success Criteria

Verify the coordinator performed these tasks:
- [ ] Goal description extracted from parameters
- [ ] Project ID derived (kebab-case)
- [ ] Existing baseline check performed
- [ ] Baseline type selected by user
- [ ] Pre-invocation validation checklist passed
- [ ] Task tool invocation prepared with correct type-specific prompt
- [ ] Task tool returned success status
- [ ] User informed of baseline file location

## Agent Execution Success Criteria

The researcher agent must accomplish (Reference Only):

**For PERFORMANCE_OPTIMIZATION:**
- [ ] baseline_metric.value is an actual number (not placeholder)
- [ ] breakdown has at least 2 categories with percentages
- [ ] bottleneck_ranking identifies #1 bottleneck
- [ ] target.current matches baseline_metric.value
- [ ] quick_wins has at least 1 entry if applicable
- [ ] File saved to docs/feature/{project-id}/baseline.yaml

**For PROCESS_IMPROVEMENT:**
- [ ] At least one of: incident_references OR failure_modes populated
- [ ] simplest_alternatives_considered has at least 2 entries
- [ ] Each alternative has specific why_insufficient reason
- [ ] File saved to docs/feature/{project-id}/baseline.yaml

**For FEATURE_DEVELOPMENT:**
- [ ] current_state.description is populated
- [ ] requirements_source.origin is populated
- [ ] File saved to docs/feature/{project-id}/baseline.yaml

---

## Next Steps

**Handoff To**: /nw:roadmap command
**Deliverables**:
- Validated baseline file at docs/feature/{project-id}/baseline.yaml
- All required sections populated based on baseline type
- Numeric values are actual measurements (not placeholders)

**Next Command**:
```bash
/nw:roadmap @{appropriate-agent} "{goal-description}"
```

The roadmap command will now proceed since baseline file exists.

---

## Notes

### Design Philosophy

The baseline command implements the PRIMARY enforcement layer for measurement-first roadmap creation. By requiring a physical file artifact:

1. **Cannot be skipped** - File must exist for roadmap to proceed
2. **Creates audit trail** - Measurements are documented and timestamped
3. **Forces thinking** - User must choose baseline type and provide data
4. **Enables validation** - Roadmap command can check file contents

### Relationship to Incident Prevention

This command directly addresses Root Cause 1 from ROADMAP-2025-12-03-001:
> "Agents proceeded to solution design without quantitative problem analysis."

By making baseline.yaml a prerequisite for roadmap.yaml, we ensure:
- Measurement happens BEFORE planning, not after
- Agents cannot rationalize skipping measurement
- Quick wins are identified BEFORE architecture design
- Wrong problems are caught BEFORE extensive roadmap creation

### Embedded Baseline Schema

The baseline file schema is embedded below for direct use without external file dependencies.

```yaml
# =============================================================================
# BASELINE FILE SCHEMA
# =============================================================================
# Purpose: Establish quantitative baseline BEFORE roadmap creation
# Usage: Save to docs/feature/{project-id}/baseline.yaml
# Command: /nw:baseline "{goal-description}"
# =============================================================================
#
# This file is REQUIRED before running /nw:roadmap.
# It ensures measurement-first approach prevents wrong-problem prioritization.
#
# VALIDATION RULES:
# - All numeric fields MUST contain actual numbers, NOT placeholders
# - Type field determines which sections are required
# - Fields marked (REQUIRED) must be filled in
# - Fields marked (OPTIONAL) can be removed if not applicable
#
# =============================================================================

baseline:
  # ---------------------------------------------------------------------------
  # METADATA (REQUIRED for all types)
  # ---------------------------------------------------------------------------
  project_id: "your-project-id"  # (REQUIRED) kebab-case, matches feature folder
  created: "2025-01-01T00:00:00Z"  # (REQUIRED) ISO-8601 timestamp
  type: "performance_optimization"  # (REQUIRED) One of: performance_optimization | process_improvement | feature_development
  author: "researcher"  # (REQUIRED) human | researcher

  # ---------------------------------------------------------------------------
  # PROBLEM STATEMENT (REQUIRED for all types)
  # ---------------------------------------------------------------------------
  problem_statement:
    summary: "One sentence describing the problem"  # (REQUIRED)
    evidence: "How we know this is a problem (metrics, incidents, user feedback)"  # (REQUIRED)
    scope:  # (REQUIRED)
      in_scope:
        - "What IS included in this effort"
      out_of_scope:
        - "What is explicitly NOT included"

  # ===========================================================================
  # TYPE 1: PERFORMANCE OPTIMIZATION
  # ===========================================================================
  # Use when: Improving speed, reducing resource usage, optimizing throughput
  # REQUIRED sections: measurements, target, quick_wins
  # ---------------------------------------------------------------------------

  measurements:  # (REQUIRED for performance_optimization)
    baseline_metric:
      name: "total_execution_time"  # What are we measuring?
      value: 532  # (REQUIRED) MUST be a NUMBER - actual measured value
      unit: "seconds"  # Unit of measurement
      measured_at: "2025-01-01T10:00:00Z"  # When was this measured?
      measurement_method: "CI pipeline timer for full test suite"  # How was this measured?

    # Breakdown shows WHERE the time/resources are spent
    # REQUIRED: At least 2 categories to show distribution
    breakdown:
      - category: "tier2_integration_tests"
        value: 532  # (REQUIRED) MUST be a NUMBER
        unit: "seconds"
        percentage: 70  # (REQUIRED) Percentage of total
        notes: "8m 52s - largest contributor"
      - category: "tier3_e2e_tests"
        value: 228  # (REQUIRED) MUST be a NUMBER
        unit: "seconds"
        percentage: 30
        notes: "3m 48s - secondary contributor"

    # Bottleneck ranking identifies priorities by IMPACT
    # REQUIRED: Ranked list with #1 bottleneck clearly identified
    bottleneck_ranking:
      - rank: 1
        component: "tier2_integration_tests"
        impact: "70% of total execution time"
        quick_win_possible: true
        quick_win_description: "80% of these tests can parallelize with config change only"
        quick_win_effort: "LOW"  # LOW | MEDIUM | HIGH
      - rank: 2
        component: "tier3_e2e_tests"
        impact: "30% of total execution time"
        quick_win_possible: false
        quick_win_description: "Requires credential isolation infrastructure"
        quick_win_effort: "HIGH"

  # Target defines success criteria with evidence
  target:  # (REQUIRED for performance_optimization)
    metric: "total_execution_time"
    current: 532  # (REQUIRED) MUST match baseline_metric.value
    proposed: 180  # (REQUIRED) Target value - MUST be achievable
    unit: "seconds"
    improvement_factor: "3x"  # How much better?
    evidence_achievable: |
      Based on breakdown analysis:
      - Tier 2 parallelization (80% of 70%): ~5 minute savings
      - Estimated remaining: ~3 minutes
      - Target of 180s (3 min) is achievable with parallelization

  # Quick wins identify low-effort high-impact opportunities
  # REQUIRED: At least 1 quick win if largest bottleneck has one
  quick_wins:  # (REQUIRED for performance_optimization)
    - action: "Enable xUnit parallelization for non-SISTER tests"
      effort: "LOW"  # LOW | MEDIUM | HIGH
      expected_impact: "~5 minutes saved (80% of tier 2 tests)"
      impact_effort_ratio: "HIGH"  # HIGH | MEDIUM | LOW
      implementation_notes: "Configuration change only - no code required"
    - action: "Optimize test database initialization"
      effort: "MEDIUM"
      expected_impact: "~30 seconds saved"
      impact_effort_ratio: "MEDIUM"
      implementation_notes: "Requires shared test fixture setup"

  # ===========================================================================
  # TYPE 2: PROCESS IMPROVEMENT
  # ===========================================================================
  # Use when: Fixing workflow issues, preventing incidents, improving reliability
  # REQUIRED sections: qualitative_evidence, simplest_alternatives_considered
  # ---------------------------------------------------------------------------

  qualitative_evidence:  # (REQUIRED for process_improvement)
    # Incident references provide concrete evidence
    # REQUIRED: At least one of incident_references OR failure_modes
    incident_references:
      - id: "ROADMAP-2025-12-03-001"
        date: "2025-12-03"
        summary: "Roadmap optimized wrong bottleneck"
        root_cause: "No measurement data before roadmap creation"
        link: "docs/agent-improvements/2025-12-03_roadmap-prioritization-lessons.md"
      - id: "INCIDENT-EXAMPLE-002"
        date: "2025-01-15"
        summary: "Second example incident"
        root_cause: "Root cause description"
        link: "path/to/incident/doc.md"

    # Failure modes describe patterns of problems
    failure_modes:
      - name: "Architecture Before Measurement"
        frequency: "Common - observed in 3 of 5 recent roadmaps"
        impact: "Wasted effort on wrong solutions"
        evidence: "Incident ROADMAP-2025-12-03-001 is primary example"
      - name: "Constraint-Anchored Architecture"
        frequency: "Occasional"
        impact: "Over-engineering for minority constraints"
        evidence: "SISTER constraint dominated 20% problem"

    # Stakeholder input captures concerns from team
    stakeholder_input:  # (OPTIONAL)
      - source: "Tech Lead"
        concern: "Agents skip measurement when under time pressure"
        proposed_solution: "Make measurement a blocking prerequisite"
      - source: "Product Owner"
        concern: "Roadmaps often miss quick wins"
        proposed_solution: "Require quick-win analysis before architecture"

  # ===========================================================================
  # TYPE 3: FEATURE DEVELOPMENT
  # ===========================================================================
  # Use when: Building new capabilities, adding features, greenfield development
  # REQUIRED sections: current_state, requirements_source
  # ---------------------------------------------------------------------------

  current_state:  # (REQUIRED for feature_development)
    description: "No baseline command exists - greenfield development"
    # For brownfield (existing code):
    # description: "Current implementation uses manual approach"
    capabilities:  # What exists today?
      - "/nw:roadmap command exists"
      - "Manual measurement possible via CI/profiling"
    limitations:  # What's missing?
      - "No enforcement of measurement-first approach"
      - "No standardized baseline file format"
      - "No command to guide baseline creation"

  requirements_source:  # (REQUIRED for feature_development)
    origin: "Incident analysis ROADMAP-2025-12-03-001"
    validation: "Reviewed with team, confirmed as priority"
    requirements:  # (OPTIONAL) List specific requirements
      - "Must block /nw:roadmap without baseline file"
      - "Must support three baseline types"
      - "Must integrate with researcher agent for data gathering"

  # ===========================================================================
  # COMMON: SIMPLEST ALTERNATIVES CONSIDERED
  # ===========================================================================
  # REQUIRED for: process_improvement
  # RECOMMENDED for: feature_development, performance_optimization
  # ---------------------------------------------------------------------------

  simplest_alternatives_considered:
    - alternative: "Add checklist item to /nw:roadmap command"
      description: "Single line reminder to measure first"
      why_insufficient: |
        Checklists are advisory, not blocking. The incident showed agents
        already had similar guidance but placed measurement AFTER solution design.
        A checklist would be ignored the same way.
      verdict: "INSUFFICIENT"  # INSUFFICIENT | PARTIAL | ADEQUATE
    - alternative: "Add reminder note to solution-architect principles"
      description: "Core principle saying 'remember to measure'"
      why_insufficient: |
        Core principles are guidance, not enforcement. The incident showed
        agents followed other principles but not measurement-first.
        Non-blocking guidance was insufficient.
      verdict: "INSUFFICIENT"
    - alternative: "Add Priority Validation to review only"
      description: "Reviewer checks if measurement data exists"
      why_insufficient: |
        Reviews happen AFTER roadmap creation. The entire 34-step roadmap
        was created before review. Prevention is cheaper than detection.
        Good secondary layer but needs earlier gate.
      verdict: "PARTIAL"

  # ===========================================================================
  # VALIDATION STATUS
  # ===========================================================================
  # Track review and approval of this baseline
  # ---------------------------------------------------------------------------

  validation:
    status: "complete"  # complete | draft | needs_review
    validated_by: "researcher"  # human | agent | reviewer
    validation_date: "2025-01-01"
    notes: "Baseline established from CI metrics and incident analysis"  # (OPTIONAL)

# =============================================================================
# EXAMPLE: MINIMAL PERFORMANCE OPTIMIZATION BASELINE
# =============================================================================
# This shows the minimum required fields for a performance optimization:
#
# baseline:
#   project_id: "test-optimization"
#   created: "2025-01-01T00:00:00Z"
#   type: "performance_optimization"
#   author: "researcher"
#
#   problem_statement:
#     summary: "Tests take too long in CI"
#     evidence: "CI pipeline averages 12 minutes, blocking PRs"
#     scope:
#       in_scope: ["Unit tests", "Integration tests"]
#       out_of_scope: ["E2E tests"]
#
#   measurements:
#     baseline_metric:
#       name: "total_test_time"
#       value: 720
#       unit: "seconds"
#       measured_at: "2025-01-01T10:00:00Z"
#       measurement_method: "CI timer"
#     breakdown:
#       - category: "unit_tests"
#         value: 120
#         unit: "seconds"
#         percentage: 17
#       - category: "integration_tests"
#         value: 600
#         unit: "seconds"
#         percentage: 83
#     bottleneck_ranking:
#       - rank: 1
#         component: "integration_tests"
#         impact: "83% of total"
#         quick_win_possible: true
#         quick_win_description: "Parallelization"
#         quick_win_effort: "LOW"
#
#   target:
#     metric: "total_test_time"
#     current: 720
#     proposed: 240
#     unit: "seconds"
#     improvement_factor: "3x"
#     evidence_achievable: "Parallelization can reduce integration by 75%"
#
#   quick_wins:
#     - action: "Enable parallel test execution"
#       effort: "LOW"
#       expected_impact: "~6 minute savings"
#       impact_effort_ratio: "HIGH"
#
#   validation:
#     status: "complete"
#     validated_by: "researcher"
#     validation_date: "2025-01-01"
#
# =============================================================================
# EXAMPLE: MINIMAL PROCESS IMPROVEMENT BASELINE
# =============================================================================
#
# baseline:
#   project_id: "roadmap-prioritization-fix"
#   created: "2025-12-03T00:00:00Z"
#   type: "process_improvement"
#   author: "human"
#
#   problem_statement:
#     summary: "Roadmaps address wrong problems"
#     evidence: "Incident ROADMAP-2025-12-03-001"
#     scope:
#       in_scope: ["Roadmap creation process"]
#       out_of_scope: ["Implementation process"]
#
#   qualitative_evidence:
#     incident_references:
#       - id: "ROADMAP-2025-12-03-001"
#         date: "2025-12-03"
#         summary: "Optimized wrong bottleneck"
#         root_cause: "No measurement before planning"
#         link: "docs/agent-improvements/..."
#     failure_modes:
#       - name: "Architecture Before Measurement"
#         frequency: "Common"
#         impact: "Wasted effort"
#         evidence: "Incident analysis"
#
#   simplest_alternatives_considered:
#     - alternative: "Add checklist"
#       description: "Reminder to measure"
#       why_insufficient: "Checklists can be ignored"
#       verdict: "INSUFFICIENT"
#     - alternative: "Add to principles"
#       description: "Core principle update"
#       why_insufficient: "Principles are guidance, not blocking"
#       verdict: "INSUFFICIENT"
#
#   validation:
#     status: "complete"
#     validated_by: "human"
#     validation_date: "2025-12-03"
#
# =============================================================================
# EXAMPLE: MINIMAL FEATURE DEVELOPMENT BASELINE
# =============================================================================
#
# baseline:
#   project_id: "add-baseline-command"
#   created: "2025-12-03T00:00:00Z"
#   type: "feature_development"
#   author: "human"
#
#   problem_statement:
#     summary: "No command exists to enforce measurement-first approach"
#     evidence: "Incident ROADMAP-2025-12-03-001 showed measurement was skipped"
#     scope:
#       in_scope: ["New /nw:baseline command", "Baseline file format"]
#       out_of_scope: ["Changes to /nw:roadmap enforcement"]
#
#   current_state:
#     description: "Greenfield - no baseline command exists"
#     capabilities:
#       - "/nw:roadmap command exists"
#       - "Researcher agent available for measurements"
#     limitations:
#       - "No blocking mechanism before roadmap"
#       - "No standard baseline format"
#
#   requirements_source:
#     origin: "Incident analysis and team discussion"
#     validation: "Confirmed with tech lead"
#     requirements:
#       - "Must create baseline.yaml file"
#       - "Must support three baseline types"
#       - "Must invoke researcher agent"
#
#   validation:
#     status: "complete"
#     validated_by: "human"
#     validation_date: "2025-12-03"
#
# =============================================================================
```
