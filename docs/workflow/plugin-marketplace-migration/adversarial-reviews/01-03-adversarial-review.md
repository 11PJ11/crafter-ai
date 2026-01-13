# ADVERSARIAL REVIEW: Step 01-03 (Create Command Jinja2 Template)

**Review Date**: 2026-01-05
**Reviewer**: Lyra (Adversarial Review Mode)
**Mission**: Find what WILL go wrong, not what might work
**Status**: BLOCKED - Multiple critical dependencies unresolved

---

## Executive Summary: This Task WILL FAIL

**Risk Score**: 9/10 (Catastrophic)
**Blast Radius**: Blocks all command file generation (steps 1.4-1.6)
**Root Cause**: Task attempts to create template before input schema is defined

**The Core Problem**:
Step 01-03 depends on parser output schema (undefined in step 01-01) AND agent template patterns (incomplete in step 01-02). Both prerequisites are flagged as blocking issues. Creating a command template before these are resolved guarantees rework.

---

## Critical Contradictions Found

### Contradiction 1: Template Input Schema Undefined
**Status**: BLOCKING - Will cause implementation failure

**The Issue**:
- Task says: "Template renders context files and previous artifacts sections" (line 37)
- Task says: "Command template defines output for 20 command files" (line 13)
- Question: What is the input structure for `command_data`?

**Why This Fails**:
The parser (step 01-01) produces "structured dict/object from TOON content" but the structure is:
- ❌ Not enumerated
- ❌ Not documented
- ❌ Not type-hinted
- ❌ Not exemplified

**Concrete Failure Scenario**:
```python
# Test tries to render template with parsed command data:
outer_test_template = render_command_template({
    # What goes here?
    # Is it a dict? Dataclass? What keys?
    "agent_id": "software-crafter",  # Assumption!
    "wave": "DEVELOP",               # Assumption!
    "command_name": "develop",       # Assumption!
})
```

The test can't be written. The developer will have to **guess** the structure based on:
1. Step 01-02 agent template (also undefined)
2. Agent examples in codebase (which may not match command structure)
3. Intuition (guarantee of wrong assumptions)

**Probability of Correct Guess**: 20-30%

---

### Contradiction 2: "Command-Specific" Language Missing
**Status**: HIGH SEVERITY - Tests will be wrong

**The Issue**:
Step 01-02's critical issue C1 flags that agents have "YAML frontmatter with name, description, model".
But commands are **not agents**. Commands are **invocable operations**.

**What Probably Needs to Happen**:
- Command frontmatter should have: name, purpose, parameters, returns
- NOT: name, description, model (agent fields)
- Agent template != Command template fundamentally

**Current Task Language**:
- Line 35: "Template produces agent-activation YAML header" ← **WRONG TERMINOLOGY**
  - Commands don't have "agent-activation" - agents do
  - Commands should have "command activation" or "invocation header"

- Line 36: "Template includes wave, agent, command metadata" ← **CONFLATED CONCEPTS**
  - Wave applies to agents, not commands
  - Agent applies to agents, not commands
  - Command metadata should be: name, signature, prerequisites

**What This Means**:
Tests will be written for the WRONG acceptance criteria. The developer will discover mid-implementation that:
1. Commands don't have "agent-id"
2. Commands don't have "wave" field
3. Commands have different metadata entirely

Then: Complete rework of template and tests (4+ hours additional effort).

---

### Contradiction 3: Agent Template Not Yet Specified
**Status**: BLOCKING - Creates circular dependency

**The Issue**:
Task 01-02 (agent template) is flagged with status "ready_for_execution: false" (line 178 of 01-02.json).
Critical issues C1-C4 are unresolved.

Task 01-03 says: "DO NOT CREATE NEW REPORT FILES" and "FOCUS ON DELIVERABLES ONLY" but depends on 01-02 output being stable.

**Circular Dependency Chain**:
```
01-01 (Parser)
  ↓ output schema undefined
01-02 (Agent template) ← BLOCKED by C1-C4
  ↓ patterns undefined
01-03 (Command template) ← assumes patterns from 01-02 exist
  ↓ inherits 01-02's problems
01-04 to 01-06 (Use templates) ← inherit cascading issues
```

**Failure Scenario**:
1. Developer starts 01-03
2. Discovers they need 01-02 to be complete
3. 01-02 is blocked on step 1.1 schema definition
4. Developer either:
   - Waits (blocks execution)
   - Guesses (creates wrong template)
   - Implements both simultaneously (violates step separation)

**Probability of Sequential Execution**: <10%

---

### Contradiction 4: "Success Criteria" Contradicts Deliverables
**Status**: MEDIUM SEVERITY - Tests won't validate what matters

**The Issue**:
Line 25: `"SC2": "Build produces Claude Code compliant output"`

This is high-level system success criterion. But acceptance criteria are template-specific:
- AC#1: "Template produces agent-activation YAML header"
- AC#2: "Template includes wave, agent, command metadata"
- AC#3: "Template renders context files and previous artifacts sections"
- AC#4: "Template includes success criteria as checklist"

**The Problem**:
These ACs don't map to SC2. They describe what the template DOES, not whether output is "Claude Code compliant."

**What's Missing**:
- Actual validation of generated command.md files against Claude Code spec
- Tests that validate output structure matches expectations
- Tests that check Jinja2 filters and escaping work correctly
- Tests for edge cases (null fields, special characters, missing sections)

**Current Approach**:
1. Generate command template
2. Assume output is compliant (not verified)
3. Continue to step 1.4

**Actual Problem**:
If command.md output is wrong, it won't be discovered until step 1.4 (Run Template on 20 Commands) - **two steps later, hours of work wasted**.

---

## Dangerous Assumptions Found

### Assumption 1: Commands and Agents Have Similar Structure
**Confidence**: 5% (almost certainly wrong)

**Rooted In**:
- Task tries to reuse agent template terminology
- No comparison between agent.md and command.md examples

**Why Dangerous**:
Commands and agents serve different purposes in Claude Code. Agents are:
- Entry points with personality, capabilities, persona
- Stateful, long-running, have model specifications

Commands are:
- Specific invocations within agent context
- Stateless parameter+return specifications
- Have prerequisites, inputs, outputs

**When This Breaks**:
When first command.md is generated and doesn't match Claude Code spec, forcing complete template redesign.

---

### Assumption 2: Parser Output Can Support Both Agent AND Command Templates
**Confidence**: 40% (likely wrong)

**The Issue**:
Step 01-01 creates parser that outputs "structured dict/object".
This same parser is expected to produce data suitable for:
- Agent templates (26 agents)
- Command templates (20 commands)
- Other templates (future)

**Reality**:
Agent data structure ≠ Command data structure. Parser likely produces combined data with different semantic meanings for agent vs command fields.

**When This Breaks**:
When template receives nested data like `{agent: {...}, commands: [{...}]}` and tries to access it with agent-specific field names.

**Example Failure**:
```python
# Template assumes:
{{ command.wave }}  # ← Commands don't have "wave"

# Should be:
{{ command.parent_agent.wave }}  # ← Nested access needed
```

**Symptom**: Template renders with blank/error sections.

---

### Assumption 3: "Context Files" Section Works the Same for Commands
**Confidence**: 30% (almost certainly wrong)

**The Issue**:
AC#3: "Template renders context files and previous artifacts sections"

Agent context makes sense: previous artifacts from discovery/design phases precede agent implementation.

Command context: less clear. Do commands have:
- Prerequisites (other commands that must run first)?
- Input data structures (dependencies)?
- Previous command outputs?

**Current Template Assumption**: Commands have same "context" structure as agents.

**Likely Reality**: Commands have different dependency model.

**When This Breaks**:
Template generates "context_files: [none]" for all commands because structure doesn't match.

---

### Assumption 4: Jinja2 Template Approach Is Sufficient
**Confidence**: 60% (possibly wrong)

**The Issue**:
Jinja2 templates are file-to-file transformations. But Claude Code compliance requires:
- Complex logic (conditional fields, nested sections)
- YAML escaping and special character handling
- Markdown frontmatter formatting
- Embedded knowledge markers with line tracking

**Jinja2's Limitations**:
- Complex filters get unwieldy
- YAML formatting bugs are common
- Multi-line string handling in Jinja2 is error-prone
- No built-in spec validation

**Likely Outcome**:
Template works for 80% of cases (happy path) but fails on:
- Special characters in descriptions
- Multi-line command documentation
- Commands with complex prerequisites
- Embedded knowledge injection markers

**When This Breaks**:
During step 1.4 (Run Template on 20 Commands). First few commands work. Command #5-7 fail on YAML escaping or formatting.

---

## Unhandled Edge Cases

### Edge Case 1: Null/Missing Fields in Command Data
**Current Handling**: Not specified
**Likely Outcome**: Template produces malformed YAML or blank sections

**Test Gap**:
No test for commands with:
- Missing description
- Missing prerequisites
- Missing parameter specification
- Empty success criteria

**When It Fails**:
```yaml
# Bad output from template if description is null:
name: my-command
description:
parameters:  # ← Wrong indentation if description empty

# Should produce error or default
```

---

### Edge Case 2: Special Characters in Command Metadata
**Current Handling**: Not specified
**Likely Outcome**: YAML parsing fails

**Concrete Example**:
```
Command description: "This command: does X - and Y, with 'quotes' and "double quotes""
```

Jinja2 template renders this unescaped into YAML → invalid YAML.

**Test Gap**: No test for special character escaping.

---

### Edge Case 3: Commands With Same Name in Different Waves
**Current Handling**: Not specified
**Likely Outcome**: Namespace collision

**Scenario**:
- Phase 1 (DISCOVER wave): agent finds data
- Phase 2 (PLAN wave): agent plans architecture
- Both have "validate-data" command
- Both render to command.md with same filename

Parser produces flattened command structure without wave context.
Template doesn't namespace by wave.
Result: Files overwrite each other.

**Test Gap**: No test for multiple commands with same name.

---

### Edge Case 4: Embedded Knowledge Injection Edge Cases
**Current Handling**: Not specified
**Issues**:
- What if command.md already contains `<!-- BUILD:INJECT:START -->` markers?
- Should old content be preserved or replaced?
- What if markers are malformed in input?
- Where exactly should markers be placed in template?

**Test Gap**: No tests for marker handling at all.

---

## Failure Scenarios (Concrete Predictions)

### Scenario 1: Parser Schema Definition Slips (Probability: 90%)
**Timeline**:
1. Developer starts step 01-03
2. Realizes input schema undefined
3. Delays work pending step 01-01 completion
4. Implements template based on assumptions
5. Step 01-01 completes with different schema than assumed
6. Template breaks, requires major rework

**Impact**: +4-6 hours delay, template rework

---

### Scenario 2: Command Structure Doesn't Match Agent Assumptions (Probability: 85%)
**Timeline**:
1. Template assumes `{{ command.wave }}`
2. Step 01-01 parser doesn't include wave in command context
3. Template renders blank/undefined for all commands
4. Discovered in step 1.4 when 20 command files generated
5. Entire template structure needs redesign

**Impact**: Template fails, cascades to steps 1.4-1.6

---

### Scenario 3: YAML Formatting Breaks on First Batch of Commands (Probability: 70%)
**Timeline**:
1. Template works for first 5 commands
2. Command #6 has description with colons: `"Validate: configuration"`
3. YAML becomes malformed
4. Steps 1.4+ fail with parsing errors
5. Developer discovers Jinja2 filter for YAML escaping needed

**Impact**: +2-3 hours debugging YAML escaping

---

### Scenario 4: Acceptance Criteria Don't Map to Real Validation (Probability: 60%)
**Timeline**:
1. Tests pass: AC#1-4 all satisfied
2. Step 1.4 runs template on 20 commands
3. Generated command.md files don't match Claude Code spec
4. Feature-completion-coordinator rejects output
5. Discover tests were validating template code, not output correctness

**Impact**: Rework of tests and template validation

---

## Data Loss/Corruption Risks

### Risk 1: Command Metadata Corruption
**Scenario**: Parser includes nested command data. Template flattens it incorrectly.
```python
# Parser produces:
{
  "id": "software-crafter",
  "commands": {
    "develop": {
      "prerequisites": ["accept", "plan"],
      "description": "Implement features via TDD"
    }
  }
}

# Template tries to access:
{{ command.wave }}  # ← Missing, renders blank
{{ command.description }}  # ← Correct, renders
# Result: Prerequisites lost in output
```

**Impact**: Command documentation incomplete, prerequisites not recorded.

---

### Risk 2: Embedded Knowledge Markers Corrupted
**Scenario**: Existing command.md has markers. Template rendering doesn't preserve marker structure.
```markdown
<!-- BUILD:INJECT:START:methodology.md -->
[OLD CONTENT]
<!-- BUILD:INJECT:END -->
```

Template re-renders without understanding markers → content inside markers replaced or markers malformed.

**Impact**: Embedded knowledge lost or inaccessible.

---

## Test Coverage Gaps

| Test Needed | Status | Risk If Missing |
|------------|--------|-----------------|
| Null field handling | ❌ Missing | Template crashes on incomplete data |
| YAML escaping (colons, dashes, quotes) | ❌ Missing | Output is malformed YAML |
| Special character handling | ❌ Missing | Output is invalid |
| Multiple commands with same name | ❌ Missing | Namespace collision |
| Missing prerequisite structure | ❌ Missing | Dependencies lost |
| Embedded marker preservation | ❌ Missing | Old content corrupted |
| Command vs Agent field differences | ❌ Missing | Wrong template assumptions |
| Parser schema validation | ❌ Missing | Template receives wrong data |

---

## Dependency Chain Analysis

```
Step 01-01 (Parser)
├─ Status: BLOCKED - Schema undefined
├─ Output: dict/object (structure unspecified)
└─ Risk: All downstream steps invalid if schema wrong

Step 01-02 (Agent Template)
├─ Status: BLOCKED - C1, C2, C3, C4 critical issues
├─ Dependency: 01-01 output schema
├─ Output: agent.md.j2 (patterns unverified)
└─ Risk: Step 01-03 will copy wrong patterns

Step 01-03 (Command Template) ← THIS TASK
├─ Status: BLOCKED - Implicit dependencies unresolved
├─ Dependencies: 01-01 schema + 01-02 patterns
├─ Output: command.md.j2 (will inherit parent issues)
└─ Risk: Will fail due to upstream blockers

Steps 01-04 to 01-06 (Use Templates)
├─ Status: BLOCKED - Upstream templates broken
├─ Dependencies: 01-03 working correctly
└─ Risk: Cascading failures
```

**Critical Path Violation**: Cannot start 01-03 while 01-01 and 01-02 are blocked.

---

## Security/Validation Gaps

### Gap 1: No Input Validation
**Risk**: Parser produces malformed data. Template doesn't validate.
- Missing required fields → template crashes
- Wrong data types → template produces garbage
- Unicode/encoding issues → encoding errors in output

### Gap 2: No Output Validation
**Risk**: Template produces syntactically-valid but semantically-wrong YAML
- Fields present but wrong values
- Sections present but empty
- Markers present but disconnected from content

**Missing**: Schema validation of generated command.md files

### Gap 3: No Version/Format Validation
**Risk**: Claude Code spec evolves. Template output becomes invalid.
- No version field in generated files
- No way to track if output matches current spec
- Updates to spec require template redesign without notification

---

## Realistic Time Estimate

| Phase | Estimated | Adjusted | Reason |
|-------|-----------|----------|--------|
| Clarify input schema | 0.5h | 1h | Step 01-01 must finish first |
| Review agent template patterns | 0.5h | 1h | Step 01-02 clarity incomplete |
| Design command data structure | 0.5h | 1h | Not trivial; must differ from agents |
| Write failing E2E test | 0.5h | 1h | E2E test itself will reveal gaps |
| Implement template | 1h | 2.5h | Jinja2 complexity + edge cases |
| Write inner tests | 1h | 2h | Must cover special characters, nulls, escaping |
| Refactoring (Level 1) | 0.5h | 1h | Template organization |
| Validation + fixes | 0h | 2h | Will discover YAML/escaping issues |
| **Total Stated** | **2h** | **11.5h** | |

**Reality Check**: 2 hours is 18% of likely actual time.

---

## Recommendations to Unblock

### Critical (Must resolve before starting)

1. **Define Parser Output Schema**
   - What fields does `parse("command.toon")` return?
   - Example: `{"id": str, "name": str, "description": str, "parameters": List[dict], ...}`
   - Provide concrete example from agents/novel-editor-chatgpt-toon.txt

2. **Define Command Data Structure**
   - How do commands differ from agents in structure?
   - What fields are command-specific vs inherited?
   - Example: Command has `parameters`, `returns`. Agent doesn't.

3. **Unblock Step 01-02**
   - Resolve critical issues C1-C4 in agent template first
   - Then use agent template as pattern reference for command template

### High Priority

4. **Add Concrete Test Data**
   - Provide example parsed command data
   - Show example command.md output
   - Enable developer to reverse-engineer expected behavior

5. **Specify Edge Cases**
   - How to handle null fields?
   - How to escape special characters in YAML?
   - How to handle embedded markers?

6. **Add Validation Tests**
   - Test that output is valid YAML
   - Test that output matches schema
   - Test special characters don't break formatting

### Medium Priority

7. **Reference Existing Command Structure**
   - Do command files exist in agents/ directory?
   - Use real examples as template reference
   - Compare agent.md vs command.md structures

---

## Risk Score: 9/10

| Factor | Score | Notes |
|--------|-------|-------|
| Blocking Dependencies | 10/10 | Both prerequisites unresolved |
| Input Specification | 9/10 | Schema completely undefined |
| Acceptance Criteria Clarity | 8/10 | "Agent-activation" doesn't apply to commands |
| Test Coverage | 9/10 | No edge case tests; will fail on special chars |
| Hidden Assumptions | 9/10 | Template structure assumed without evidence |
| Integration Risk | 8/10 | Cascades to steps 1.4-1.6 |
| Rework Probability | 85% | Very likely to require significant revisions |

**Overall Risk Score: 9/10 - CRITICAL**

---

## Blast Radius

```
If 01-03 fails → cascading failure through:
├─ Step 1.4 (Generate Agent Commands) - BLOCKED
├─ Step 1.5 (Generate Command Registry) - BLOCKED
├─ Step 1.6 (Validate Command Schema) - BLOCKED
├─ Phase 2 (Agent Implementation) - DELAYED
└─ Entire project timeline - SLIPPED
```

**Estimated Delay if Failure**: 6-8 weeks (time to complete 01-01, 01-02, redesign 01-03, catch up)

---

## Conclusion

**This task WILL FAIL if started now.** Not "might fail" - WILL fail.

**Root Cause**: Attempting to create a template without knowing:
1. What the input data structure is
2. How commands differ from agents
3. What the output should look like

**What Should Happen**:
1. ✅ Complete and verify step 01-01 (parser with defined output schema)
2. ✅ Resolve step 01-02 (agent template with clear specs)
3. ✅ Document command vs agent structural differences
4. ✅ Provide example parsed command data
5. ✅ THEN start step 01-03

**Current State**: Trying to build a bridge without knowing which two sides to connect.

---

**Recommendation**: HOLD step 01-03. Focus on unblocking 01-01 and 01-02 first. Then revisit this task with necessary context.

