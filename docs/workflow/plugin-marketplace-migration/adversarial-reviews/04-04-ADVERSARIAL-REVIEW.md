# Adversarial Review: Step 04-04 (DEVELOP Wave Command Migration)

**Review Date**: 2026-01-05
**Reviewer**: Lyra (Adversarial Mode)
**Risk Score**: 6.5/10
**Blast Radius**: HIGH - Affects core 8 commands used in all DEVELOP phases
**Status**: APPROVED WITH CRITICAL GAPS

---

## Executive Summary: DANGEROUS ASSUMPTIONS DETECTED

The task assumes knowledge that doesn't exist in the specification. Three classes of failures are possible:

1. **Format Mismatch**: Converters may produce invalid TOON without seeing TOON v3.0 spec
2. **Agent Binding Failures**: Tests validate bindings that may violate actual binding rules
3. **Incomplete Refactoring**: Inconsistent command structures left unaddressed due to vague "consistency" definition

---

## CONTRADICTIONS FOUND

### Contradiction 1: Refactoring Scope Mismatch
**Type**: Specification Inconsistency
**Severity**: CRITICAL
**Impact**: Task outcome ambiguous

**The Problem**:
```
Step 04-04 specifies:
  refactoring:
    targets:
      - level: 1
        focus: "Consistent command structure"

But previous steps (04-01, 04-02, 04-03) have:
  refactoring:
    targets: []  # Empty!
```

**Why This Matters**:
- If refactoring is important, why does 04-01 skip it?
- If refactoring isn't needed, why does 04-04 require it?
- Is "consistent command structure" a NEW requirement or existing pattern?

**Hidden Assumption**:
The task assumes that DEVELOP commands need refactoring that BASELINE and ROADMAP commands don't. This is unjustified by the specification.

**Risk**:
- Executor may skip refactoring (following 04-01 pattern), failing acceptance criteria
- OR executor over-refactors based on vague "consistency" definition

**Mitigation Required**:
Either:
- Remove refactoring section to match 04-01/02/03 pattern, OR
- Explicitly define: "What makes DEVELOP commands structurally inconsistent? What consistency rule applies?"

---

### Contradiction 2: Agent Binding Specification Absent
**Type**: Missing Definition
**Severity**: CRITICAL
**Impact**: Tests may validate wrong bindings

**The Problem**:
```
Inner test:
  "test_review_command_binds_reviewer"

Acceptance criteria:
  "Agent bindings correct for each command"

But NO SPECIFICATION OF:
  - Which command binds to which agent
  - Whether 'review' → software-crafter or software-crafter-reviewer
  - Whether different commands bind to same or different agents
```

**Why This Matters**:
Commands like `review` might need to bind to:
- `software-crafter` (peer review), OR
- `software-crafter-reviewer` (specialized reviewer)

The test assumes one binding; actual binding rules may differ.

**Hidden Assumption**:
Task assumes executor knows the agent binding rules from external context (probably the TOON v3.0 specification or agent registry).

**Risk Scenarios**:
1. Executor creates `review.toon` binding to `software-crafter`
2. Test validates: "Does review command bind to reviewer?" → Assumes `software-crafter-reviewer` exists and is correct
3. Test PASSES locally (mock validates any binding)
4. Runtime FAILS: Agent registry doesn't have `software-crafter-reviewer` or binding is wrong

**Mitigation Required**:
Document explicit agent binding table:
```
Command         → Agent Binding
baseline        → software-crafter
roadmap         → software-crafter
split           → software-crafter
execute         → software-crafter
review          → software-crafter-reviewer (or software-crafter?)
develop         → software-crafter
refactor        → software-crafter
mikado          → software-crafter
```

---

### Contradiction 3: Implicit Format Assumption
**Type**: Knowledge Prerequisite
**Severity**: CRITICAL
**Impact**: Converter may produce invalid TOON

**The Problem**:
```
Task requires: "All 8 commands compile with agent-activation headers"

But NOWHERE specifies:
  - What is TOON v3.0 format?
  - What does "agent-activation headers" syntax look like?
  - Are headers prefixed with special characters? (e.g., #!, //, @)
  - Required vs optional fields?
  - Data type expectations?
```

**Hidden Assumption**:
Task assumes executor has access to:
1. TOON v3.0 specification document, OR
2. Reference implementation of converted .toon files, OR
3. Compiler error messages that clarify syntax

**Risk Scenarios**:
1. Executor converts using best guess: `wave: DEVELOP`
2. Compiler rejects: `wave_name: DEVELOP` expected
3. OR compiler accepts but runtime binding fails due to format mismatch
4. OR compilation succeeds but agent system can't parse metadata

**Example of Format Ambiguity**:
```
Valid TOON v3.0? Unknown:
wave: DEVELOP
activation_header: software-crafter

OR:

--WAVE: DEVELOP
--AGENT: software-crafter

OR:

@wave DEVELOP
@agent software-crafter
```

All might compile, but only one works correctly.

---

## DANGEROUS ASSUMPTIONS

### Assumption 1: TOON Compiler Exists and Is Accessible
**Status**: UNVERIFIED
**Risk Level**: HIGH

**The Assumption**:
Task step 2 says "Compile each TOON file" without specifying compiler name, location, or how to invoke it.

**Dangerous Because**:
- If compiler isn't available, entire step fails immediately
- If compiler path is wrong, failure point isn't obvious
- No fallback or verification step

**Test Coverage Gap**:
No test validates compiler availability BEFORE conversion work starts.

**Mitigation**:
Add pre-work validation:
```
Pre-work validation test:
  GIVEN TOON compiler environment
  WHEN check if compiler is available
  THEN compiler found at [path] with version >= [X.Y]
```

---

### Assumption 2: All 8 Source .md Files Are Syntactically Valid
**Status**: UNVERIFIED
**Risk Level**: MEDIUM

**The Assumption**:
Task assumes all 8 source .md files at `5d-wave/tasks/dw/*.md` are valid input for conversion.

**Dangerous Because**:
- No test validates source files before conversion starts
- Malformed source .md could cause conversion tool to:
  - Silently produce incomplete .toon (bugs left undetected)
  - Crash mid-conversion, leaving partial files
  - Produce TOON with metadata corruption

**Example Failure Scenario**:
```
Source: baseline.md
  [Missing closing code fence]

  # Baseline Task
  ```yaml
  wave: BASELINE
  [No closing ```]

Conversion tool:
  - Reads until EOF
  - Metadata truncated
  - Result: Invalid TOON
```

**Test Coverage Gap**:
No test validates source file syntax before conversion.

**Mitigation**:
Add validation:
```
Pre-work validation:
  FOR each source .md file:
    WHEN parse file
    THEN valid YAML/markdown structure confirmed
```

---

### Assumption 3: Token Savings Target Is Achievable
**Status**: QUESTIONABLE
**Risk Level**: MEDIUM

**The Assumption**:
Success criteria references "~60% token savings in source files" (SC7).

**Dangerous Because**:
1. No baseline measurement provided
   - Current token count of 8 .md files: UNKNOWN
   - Expected token count after conversion: UNKNOWN
   - How 60% was calculated: UNKNOWN

2. Task doesn't include token counting in workflow
   - No measurement step in execution guidance
   - No acceptance criteria that validates token savings
   - No definition of what counts as "token" (OpenAI tokenizer? Huggingface? Custom?)

3. TOON format may not achieve 60% savings
   - If TOON v3.0 uses verbose syntax, savings could be 10-20%
   - If markdown redundancy is minimal, savings are artificial
   - Compression-style claims are common without measurement

**Hidden Question**:
Is 60% a real measurement target or an aspirational guess?

**Risk**:
- Step completes: All 8 commands converted and compiling
- Token analysis shows 30% savings instead of 60%
- Success criteria technically passed (no specific token test in QG list)
- BUT project goal (60% token savings) not achieved
- Stakeholders confused about whether step succeeded

**Test Coverage Gap**:
Quality gates list doesn't include token savings validation.

**Mitigation**:
Either:
1. Remove token savings claim (focus on functionality), OR
2. Add acceptance criterion: "Token analysis: Measure savings vs. baseline; document achieved savings percentage"

---

### Assumption 4: Agent Binding Rules Are Stable
**Status**: UNVERIFIED
**Risk Level**: MEDIUM

**The Assumption**:
Task assumes the agent binding rules (which command uses which agent) won't change during conversion.

**Dangerous Because**:
1. No centralized agent registry reference provided
2. Tests validate local binding correctness but not integration correctness
3. If agent system changes (e.g., `software-crafter-reviewer` is removed), tests still pass but runtime fails

**Example Failure Scenario**:
```
Step 04-04 executes:
  - All 8 commands converted and tested locally ✓
  - Tests pass: "review command binds to software-crafter-reviewer" ✓
  - All tests pass ✓

Later, agent registry is reorganized:
  - software-crafter-reviewer agent is removed
  - review command binding now: software-crafter
  - But converted commands still reference old binding

Runtime failure: Agent system can't find software-crafter-reviewer
```

**Test Coverage Gap**:
Tests validate binding syntax but not binding validity against actual agent registry.

**Mitigation**:
Add integration validation:
```
Integration test:
  FOR each command binding in generated .toon:
    WHEN query agent registry
    THEN agent exists and is active
```

---

### Assumption 5: Refactoring Level 1 Definition Is Understood
**Status**: AMBIGUOUS
**Risk Level**: LOW-MEDIUM

**The Assumption**:
Task requires "refactoring applied (level 1)" but Level 1 is defined vaguely as "Foundation Refactoring (Readability)".

**Dangerous Because**:
1. Executor interprets "consistency" and "readability" differently
2. What looks consistent to one person looks inconsistent to another
3. No checkpoints to validate consistency decisions

**Example Ambiguity**:
```
Command 1 agent-activation header:
  # AGENT: software-crafter (Comment style)

Command 2 agent-activation header:
  @agent software-crafter (Decorator style)

Command 3 agent-activation header:
  agent: software-crafter (YAML style)

Which is "consistent"? All compile, but structure differs.
Refactoring guidance: "Consistent command structure" doesn't specify choice.
```

**Risk**:
- Executor applies Level 1 refactoring
- Peer review says "This isn't consistent with pattern X"
- Back-and-forth on what "consistent" means
- Rework required

**Mitigation**:
Explicitly define consistency rule:
```
Refactoring level 1 - Consistency rule:
  All agent-activation headers MUST use format: @agent [agent-name]
  All wave declarations MUST use format: wave: [WAVE_NAME]
  All metadata fields MUST follow YAML:key: value style
```

---

## UNHANDLED EDGE CASES

### Edge Case 1: Command File Collision
**Type**: State Management
**Severity**: HIGH

**Scenario**:
```
Pre-execution state:
  5d-wave/tasks/dw/develop.toon exists (from previous phase)

Step 04-04 execution:
  Convert develop.md → develop.toon
  Write develop.toon to disk

Collision: develop.toon already exists!

Behavior undefined:
  - Overwrite existing? (Data loss risk)
  - Skip? (Incomplete conversion)
  - Error? (Task failure)
```

**Test Coverage Gap**:
No test validates pre-existing file handling.

**Mitigation**:
Add pre-work validation:
```
Pre-work check:
  IF any .toon file exists in target directory:
    THEN abort and report: "Files already exist. Remove old .toon files first."
```

OR

Add idempotency:
```
Conversion:
  1. Convert all 8 .md → temporary .toon files
  2. Validate all 8 compile successfully
  3. THEN atomically replace old .toon files with new ones
```

---

### Edge Case 2: Partial Conversion Failure
**Type**: Error Recovery
**Severity**: HIGH

**Scenario**:
```
Execution progress:
  ✓ Convert baseline.md → baseline.toon (success)
  ✓ Convert roadmap.md → roadmap.toon (success)
  ✗ Convert split.md → ERROR (malformed YAML?)

State at failure:
  - 2 new .toon files created
  - split.md not converted
  - 5 remaining .md files not started
  - Tests may pass on successfully converted files
  - Tests fail on split.toon (missing)

Executor decision unclear:
  - Rollback all 2 successful conversions?
  - Keep them and continue from failure point?
  - Start over?
```

**Test Coverage Gap**:
No test covers failure recovery or rollback logic.

**Mitigation**:
Add error handling specification:
```
Conversion error handling:
  IF any conversion fails:
    THEN rollback all converted files
    AND report which conversion failed and why
    AND STOP (do not proceed to next conversion)
```

---

### Edge Case 3: Compiler Validation Contradiction
**Type**: Test Validation
**Severity**: MEDIUM

**Scenario**:
```
Test: "All 8 commands compile successfully"

Possible interpretations:
  1. Compiler exits with status 0 (success exit code)
  2. Compiler produces no error output (stderr empty)
  3. Compiler produces valid output file (output size > 0)
  4. Compiler produces output matching schema validation
  5. ALL OF THE ABOVE

If test uses interpretation 1 (exit code):
  - Compiler could exit 0 but produce warnings
  - Generated files could be incomplete
  - Test PASSES but files are invalid

If test uses interpretation 4 (schema validation):
  - Excellent coverage
  - But validation schema isn't specified
```

**Test Coverage Gap**:
Acceptance criteria says "All 8 commands compile successfully" without defining "successful compilation".

**Mitigation**:
Add explicit compilation validation criteria:
```
Compilation success criteria:
  1. Compiler exit code = 0
  2. No error messages in stderr
  3. Output file size > [minimum bytes] (indicates content)
  4. Output file validates against TOON v3.0 schema
  5. All required metadata fields present (wave, agent-binding, etc.)
```

---

### Edge Case 4: Wave Metadata Inconsistency
**Type**: Data Validation
**Severity**: MEDIUM

**Scenario**:
```
Acceptance criteria: "Wave metadata correct (DEVELOP)"

Possible issues:
  1. Some commands have wave: DEVELOP (correct)
     Others have wave: develop (lowercase - wrong?)
  2. Some commands have wave_name: DEVELOP (alternate field name)
  3. Some commands missing wave field entirely

Tests might validate:
  - Case sensitivity: Does wave: develop fail?
  - Field naming: Does wave_name: DEVELOP validate?
  - Required vs optional: Can commands omit wave field?

Specification missing:
  - Which format is authoritative?
  - How strict is validation?
```

**Test Coverage Gap**:
No example of valid vs invalid wave metadata shown.

**Mitigation**:
Embed validation examples in task:
```
Valid wave metadata (examples):
  wave: DEVELOP          ✓ Correct
  wave: develop          ✗ Case mismatch (fail)
  wave_name: DEVELOP     ✗ Wrong field name (fail)
  (no wave field)        ✗ Missing required field (fail)
```

---

### Edge Case 5: Agent Binding Inconsistency
**Type**: Data Validation
**Severity**: HIGH

**Scenario**:
```
Acceptance criteria: "Agent bindings correct for each command"

8 commands need bindings. Possible inconsistencies:

1. Different syntax for same concept:
   agent: software-crafter
   agent_binding: software-crafter
   activation: software-crafter
   (Which is correct?)

2. Different binding targets:
   review → software-crafter
   develop → software-crafter-develop (specific?)
   refactor → software-crafter (reuse?)
   (Inconsistent pattern)

3. Missing bindings:
   Some commands don't have agent binding field
   Others do
   (Incomplete specification)

Test might pass if:
  - It only checks syntax (all are non-empty)
  - It doesn't validate against agent registry
  - It doesn't check consistency across commands
```

**Test Coverage Gap**:
No example of correct agent binding shown for each command.

**Mitigation**:
Document expected bindings for all 8 commands:
```
Command       Expected Binding         Field Name
baseline      software-crafter         agent
roadmap       software-crafter         agent
split         software-crafter         agent
execute       software-crafter         agent
review        software-crafter-reviewer agent
develop       software-crafter         agent
refactor      software-crafter         agent
mikado        software-crafter         agent
```

---

## FAILURE SCENARIOS

### Failure Scenario 1: TOON Format Incompatibility
**Trigger**: Format assumption wrong
**Severity**: CRITICAL
**Detection**: Post-commit

**Timeline**:
```
T+0h: Conversion starts
T+2h: All 8 commands converted and tested locally ✓
T+4h: Step complete, user approval requested ✓
T+4.5h: User approves, commit pushed ✓

[Later, integration testing with agent system]

T+6h: Agent system attempts to parse .toon files
      Fails: "Invalid metadata format"

Discovered: Converted files use wrong field names
            field: wave (incorrect)
            Expected: wave_designation (correct)

Impact: 8 command files must be re-converted
        All tests invalidated (format assumed wrongly)
        2 additional hours of rework
```

**Prevention**:
- Specify TOON v3.0 format schema before conversion starts
- Add schema validation test

---

### Failure Scenario 2: Agent Binding Cascade Failure
**Trigger**: Agent binding assumptions wrong
**Severity**: CRITICAL
**Detection**: Runtime during agent activation

**Timeline**:
```
T+0h: Conversion and testing completed ✓
      All tests pass: "review command binds to software-crafter-reviewer" ✓

T+5h: Deployed to agent system
      Agent system loads review.toon
      Attempts to activate software-crafter-reviewer agent

Failure: Agent not found in registry
         (Was renamed/removed in interim)

Impact: review command unavailable
        Entire DEVELOP wave blocked
        User cannot execute reviews

Root cause: Test validated binding syntax, not binding existence
```

**Prevention**:
- Add integration test that validates bindings against actual agent registry
- Don't assume agent availability

---

### Failure Scenario 3: Refactoring Incomplete or Over-Applied
**Trigger**: Vague refactoring definition
**Severity**: MEDIUM
**Detection**: Peer review

**Timeline**:
```
T+0h: Step completes, all tests pass ✓
      All 8 commands converted ✓
      All 8 commands compile ✓
      Refactoring "applied" ✓

T+4h: Code review begins
      Reviewer: "These command structures are inconsistent"

Examples:
      baseline.toon:
        # AGENT: software-crafter
        wave: BASELINE

      develop.toon:
        agent: software-crafter
        wave: DEVELOP

Reviewer: "Different header styles, different field ordering,
          different comment usage. Not consistent."

Executor: "I applied refactoring level 1"
Reviewer: "But you didn't address structural inconsistency"

Result: Rework required, step deemed incomplete
```

**Prevention**:
- Explicitly define what "consistent command structure" means
- Add definition to acceptance criteria

---

## RISK ASSESSMENT

**Risk Score: 6.5/10 (HIGH)**

### Risk Composition:
- **Critical Path Specification Gaps**: 3 (Format, Bindings, Refactoring definition)
- **Unverified Assumptions**: 5 (Compiler, File syntax, Token savings, Bindings stable, Refactoring level)
- **Unhandled Edge Cases**: 5 (File collision, Partial failure, Compilation validation, Wave metadata, Bindings)
- **Failure Scenarios**: 3 (Format mismatch, Binding cascade, Refactoring incomplete)

### Blast Radius: VERY HIGH
- **Scope**: 8 core DEVELOP commands
- **Downstream Impact**: All DEVELOP phases depend on these commands
- **Propagation**: Format/binding errors cascade to agent system
- **Recovery Cost**: Full re-conversion if format wrong (2-4 hours)

---

## CRITICAL GAPS REQUIRING RESOLUTION

### Gap 1: TOON v3.0 Format Specification MISSING
**Resolution Required**: YES
**Priority**: P0 (Blocks execution)

**What's Missing**:
- Format specification document or link
- Syntax examples (valid and invalid)
- Required vs optional fields
- Field name conventions
- Data type expectations

**Mitigation**:
Embed specification or reference in task before execution.

---

### Gap 2: Agent Binding Rules MISSING
**Resolution Required**: YES
**Priority**: P0 (Blocks execution)

**What's Missing**:
- Explicit mapping of which command → which agent
- Binding field name specification
- How bindings are validated
- How bindings integrate with agent system

**Mitigation**:
Document agent binding table with examples.

---

### Gap 3: Refactoring Definition MISSING
**Resolution Required**: YES
**Priority**: P1 (Blocks validation)

**What's Missing**:
- Definition of "consistent command structure"
- Which structural elements must be consistent
- Formatting rules (header style, field ordering)
- Refactoring examples

**Mitigation**:
Either remove refactoring requirement or define explicitly.

---

### Gap 4: Compiler Specification MISSING
**Resolution Required**: YES
**Priority**: P1 (Blocks execution)

**What's Missing**:
- Compiler name and version
- Invocation syntax
- Expected output location
- Success/failure criteria

**Mitigation**:
Specify compiler details in task.

---

### Gap 5: Test Framework MISSING
**Resolution Required**: YES
**Priority**: P1 (Blocks execution)

**What's Missing**:
- Test framework name (NUnit, xUnit, pytest, etc.)
- How to run tests
- What validates "success" in testing

**Mitigation**:
Specify test framework in task.

---

## RECOMMENDED ADDITIONS TO TASK

### 1. Pre-Work Validation
```json
"pre_work_validation": {
  "checks": [
    {
      "name": "TOON Format Specification Available",
      "required": true,
      "validation": "Document or reference provided"
    },
    {
      "name": "Agent Binding Mapping Document Available",
      "required": true,
      "validation": "8 commands with explicit agent targets"
    },
    {
      "name": "TOON Compiler Available",
      "required": true,
      "validation": "Compiler found and callable"
    },
    {
      "name": "Test Framework Configured",
      "required": true,
      "validation": "Framework installed and runnable"
    },
    {
      "name": "No Existing Target .toon Files",
      "required": true,
      "validation": "5d-wave/tasks/dw/*.toon must not exist"
    },
    {
      "name": "Source .md Files Valid",
      "required": true,
      "validation": "Each .md file parses without errors"
    }
  ]
}
```

### 2. Agent Binding Table
```json
"agent_binding_specification": {
  "format_example": "agent: software-crafter",
  "bindings": [
    { "command": "baseline", "agent": "software-crafter" },
    { "command": "roadmap", "agent": "software-crafter" },
    { "command": "split", "agent": "software-crafter" },
    { "command": "execute", "agent": "software-crafter" },
    { "command": "review", "agent": "software-crafter-reviewer" },
    { "command": "develop", "agent": "software-crafter" },
    { "command": "refactor", "agent": "software-crafter" },
    { "command": "mikado", "agent": "software-crafter" }
  ]
}
```

### 3. Compilation Validation Criteria
```json
"compilation_validation": {
  "criteria": [
    "Compiler exit code = 0",
    "No errors in stderr",
    "Output file size > 1000 bytes (minimum)",
    "Output validates against TOON v3.0 schema",
    "All required metadata fields present (wave, agent)"
  ]
}
```

### 4. Refactoring Definition
```json
"refactoring_level_1_rules": {
  "focus": "Consistent command structure",
  "rules": [
    "All agent-activation headers use @agent [name] format",
    "All wave declarations use wave: [WAVE] format",
    "All metadata uses YAML key: value style",
    "Field order consistent across all 8 files"
  ]
}
```

---

## VERDICT

**Status**: APPROVED WITH CRITICAL GAPS
**Confidence**: 0.65 (was 0.85, downgraded due to specification gaps)
**Execution Risk**: HIGH
**Recommendation**: DO NOT EXECUTE until gaps resolved

### Before Execution:
- [ ] Provide or reference TOON v3.0 format specification
- [ ] Document agent binding mapping for all 8 commands
- [ ] Define refactoring level 1 rules explicitly
- [ ] Specify compiler name and invocation syntax
- [ ] Specify test framework to use
- [ ] Add pre-work validation checks to task

### After Resolution:
- Re-assess risk (should drop to 3-4/10)
- Proceed with execution
- Run pre-work validation immediately
- Monitor compilation and binding validation closely

---

## SUMMARY OF ADVERSARIAL FINDINGS

**Contradictions Found**: 3 (Format, Binding, Refactoring scope)
**Dangerous Assumptions**: 5 (Compiler, File syntax, Token savings, Bindings stability, Refactoring level)
**Unhandled Edge Cases**: 5 (File collision, Partial failure, Compiler validation, Wave metadata, Bindings)
**Failure Scenarios**: 3 (Format incompatibility, Agent binding cascade, Refactoring incomplete)
**Critical Gaps**: 5 (Format spec, Binding rules, Refactoring def, Compiler spec, Test framework)

**Overall Assessment**: Task is achievable but hazardous without specification clarification. Specification gaps represent single points of failure that cascade to entire DEVELOP phase.
