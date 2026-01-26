# DW-BASELINE: Establish Measurement Baseline

---
## ORCHESTRATOR INVOCATION PROTOCOL (MANDATORY)

**When YOU (orchestrator) delegate this command to an agent via Task tool:**

### CORRECT Pattern (minimal prompt):
```python
Task(
    subagent_type="researcher",
    prompt="Create baseline: test-optimization (type: performance_optimization)"
)
```

### Why This Works:
- ✅ Researcher agent has internal baseline schema knowledge
- ✅ Project ID specifies where to save: docs/feature/{project-id}/baseline.yaml
- ✅ Baseline type specifies which sections are required
- ✅ No conversation context needed

### WRONG Patterns (avoid):
```python
# ❌ Embedding baseline schema (researcher already knows this)
Task(prompt="Create baseline for test-optimization. Use this YAML structure: [long schema]")

# ❌ Listing measurement requirements (researcher knows what to measure)
Task(prompt="Create baseline. Measure timing, breakdown by category, rank by impact...")

# ❌ Validation rules (researcher has internal validation)
Task(prompt="Create baseline. Ensure baseline_metric.value matches target.current...")

# ❌ Any context from current conversation
Task(prompt="Create baseline. As we discussed, the test suite has tier 2 and tier 3...")
```

### Key Principle:
**Command invocation = Project ID + Baseline type ONLY**

The researcher agent knows how to create baselines. Your prompt should not duplicate schema.

---

## AGENT PROMPT REINFORCEMENT (Command-Specific Guidance)

Reinforce command-specific principles extracted from THIS file (baseline.md):

### Recommended Prompt Template:
```python
Task(
    subagent_type="researcher",
    prompt="""Create baseline: test-optimization (type: performance_optimization)

CRITICAL (from baseline.md):
- Measurements MUST be actual numbers (NOT placeholders like "TBD" or "~500")
- Quick wins identified BEFORE complex solutions
- Breakdown analysis: rank by TIME IMPACT (not by type/category)
- baseline_metric.value must equal target.current

AVOID:
- ❌ Using placeholders or estimates without measurement
- ❌ Categorizing without timing (need time impact, not just counts)
- ❌ Skipping quick win analysis (may not need complex solution)
- ❌ Assuming most-mentioned = most important (measure, don't assume)"""
)
```

### Why Add This Guidance:
- **Source**: Extracted from baseline.md (not conversation context)
- **Deterministic**: Same principles every time you invoke baseline
- **Reinforcing**: Prevents wrong-problem pattern (Incident ROADMAP-2025-12-03-001)
- **Token-efficient**: ~100 tokens vs wrong roadmap creation

### What NOT to Add:
```python
# ❌ WRONG - This uses orchestrator's conversation context
Task(prompt="""Create baseline: test-optimization

As we discussed, the test suite has tier 2 and tier 3 tests.
The SISTER constraint is mentioned but only affects 20%.""")
```

---

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

The compact baseline template is embedded below for direct use without external file dependencies.

<!-- BUILD:INJECT:START:nWave/templates/baseline-compact.yaml -->
<!-- Baseline template will be injected here at build time -->
<!-- BUILD:INJECT:END -->
