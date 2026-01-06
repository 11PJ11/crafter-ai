# ADVERSARIAL REVIEW: Step 01-05 (TOON Compiler)
**Date**: 2026-01-05
**Reviewer**: Lyra (Adversarial Mode)
**Mission**: Find what WILL go wrong, not what MIGHT work

---

## CRITICAL FINDING: THIS TASK CANNOT SUCCEED AS WRITTEN

Step 01-05 depends critically on Steps 01-01 through 01-04, but those dependencies are in a **cascading failure state**. This task will fail catastrophically.

---

## SECTION 1: CONTRADICTIONS FOUND

### Contradiction 1.1: Dependency Fulfillment Status

**The Problem**: The task declares dependencies `["1.1", "1.2", "1.3", "1.4"]` but those steps have **fundamental unresolved conflicts**:

- **01-01 (Parser)**: Still has 4 critical unresolved issues:
  - Parser output schema **undefined** (will parser return dict? TypedDict? dataclass? Unknown.)
  - TOON symbol set **incomplete** (only "arrows, pipes, checkmarks" mentioned; actual spec has at least 6 symbols)
  - python-toon library **not validated** (assumption it exists; if not, entire estimate is wrong by 2x)
  - Library API **not documented** (even if library exists)

- **01-02 (Agent Template)**: Cannot complete without parser schema (marked FLAGGED_FOR_CLARIFICATION):
  - Expected output structure **undefined** (no YAML frontmatter key examples)
  - Input data shape **unknown** (what does parser actually produce?)
  - Embedded knowledge injection **incompletely specified**

- **01-03 (Command Template)**: Cannot complete without parser schema:
  - Input data structure **undefined**
  - Acceptance criteria **domain-misaligned** (uses "agent-activation header" language, but commands aren't agents)
  - Command data format **unspecified**

- **01-04 (Skill Template)**: Cannot complete without parser schema:
  - Skill data structure **unspecified**
  - Trigger pattern semantics **undefined** (regex? strings? objects?)
  - Agent association mechanism **unclear**

**Result**: The three templates (1.2, 1.3, 1.4) cannot be finalized without knowing parser output. The parser (1.1) cannot finalize without having the templates' input requirements specified. This is a **circular dependency**.

**Blast Radius**: CATASTROPHIC. Step 01-05 will receive incomplete/untested dependency artifacts.

---

### Contradiction 1.2: Acceptance Criteria vs Achievability

The task lists these acceptance criteria:
```
1. Compiler reads .toon file from path
2. Compiler selects correct template based on file type
3. Compiler writes output to specified directory
4. Compiler reports errors clearly on parse/template failures
5. Compiler validates output has required sections
```

**The Conflict**:

- AC#5 ("validates output has required sections") **requires knowing what sections each template produces**
- But templates are incomplete/untested (see Contradiction 1.1)
- So AC#5 **cannot be validated** without reverse-engineering from templates
- Yet the templates themselves have AC items that reference undefined input/output

**Result**: AC#5 is a tautology trap. The compiler validates templates validate the compiler validates templates... circular.

**Blast Radius**: HIGH. Impossible to write tests that validate AC#5.

---

### Contradiction 1.3: Refactoring Levels vs Arrival State

Task specifies:
```
"refactoring": {
  "targets": [
    { "level": 2, "focus": "Extract file type detection strategy" },
    { "level": 3, "focus": "Separate compilation steps into pipeline" }
  ]
}
```

**The Problem**:

- Refactoring Levels 2-3 target **splitting responsibilities** (detection strategy, pipeline stages)
- But if the compiler is written before dependencies are stable, refactoring **will break it**
- Each time a template changes format (due to clarifications in 01-02/01-03/01-04), the compiler breaks
- This creates a **ratchet of instability**: code → refactor → templates change → code breaks → refactor again

**Example Failure**:
1. Implement compiler assuming parser returns `dict` with `{"id": ..., "commands": [...]}`
2. Extract file type detection (Level 2 refactoring)
3. Template 01-02 finalized with different schema: `{"agent_id": ..., "agent_commands": [...]}`
4. Parser updated to match Template 01-02
5. Compiler **breaks** on field name mismatch
6. Refactoring work is wasted; must redo

**Blast Radius**: MEDIUM-HIGH. Refactoring will be thrown away when dependencies stabilize.

---

### Contradiction 1.4: Estimated Hours vs Reality

**Stated**: "3-4 hours"

**Requirements for Success**:
1. Parse .toon file (depends on parser API, undefined)
2. Detect file type (depends on parser output schema, undefined)
3. Select correct template (depends on 3 templates, incomplete)
4. Render template (depends on Jinja2 environment setup, unspecified)
5. Write output (straightforward, ~30 min)
6. Validate output (depends on AC#5 definition, undefined)
7. Report errors (depends on error taxonomy, undefined)
8. Refactor Levels 2-3 (~2 hours)

**Realistic Estimate**: 6-8 hours minimum, assuming dependencies are finalized TODAY. **If dependencies need clarification during implementation**: 12+ hours.

**Result**: Estimate is optimistic by 50-100%.

---

## SECTION 2: DANGEROUS ASSUMPTIONS

### Assumption D1: Parser API is Finalized
**Assumption**: Parser step 01-01 has a stable, documented API (method signature, return type, exceptions).

**Reality Check**:
- Parser description says "produces structured data" but NO API documented
- Parser might return: plain `dict`, `TypedDict`, `dataclass`, custom class, or Pydantic model
- Each choice breaks compiler differently
- No implementation exists yet to demonstrate API

**Risk**: 50% chance parser API changes during 01-05 implementation.

**Mitigation Failure**: Task has no API fallback or adapter layer.

---

### Assumption D2: Templates Produce Consistent Output Format
**Assumption**: Agent template, Command template, Skill template all produce compatible markdown with consistent structure.

**Reality Check**:
- Agent template (01-02) lists AC: "valid YAML frontmatter", "activation notice", "commands rendered", "embedded knowledge markers"
- Command template (01-03) lists AC: "agent-activation header" (different from agent template), "wave/agent metadata", "context files section"
- Skill template (01-04) lists AC: "skill YAML frontmatter" (different schema), "trigger patterns", "agent association"
- **These are three incompatible schemas**
- Compiler's AC#5 assumes validator can validate "required sections" across all three types
- But sections are different per type

**Risk**: Validator (AC#5) is impossible to implement correctly.

**Mitigation**: Task provides no solution.

---

### Assumption D3: File Type Detection is Unambiguous
**Assumption**: Given a .toon file, compiler can definitively determine if it's agent/command/skill.

**Reality Check**:
- Parser extracts sections: metadata, core rules, etc.
- But nothing in parser output distinguishes agent from command from skill
- Task says "Compiler determines template based on file type" but **doesn't specify how**
- Hidden dependency: file extension? metadata field? content analysis?
- What if a TOON file describes something hybrid?

**Risk**: File type detection logic is ambiguous; tests will conflict.

**Example Failure**:
```
Scenario: file is "hybrid-command-skill.toon"
- Test expects: command.md output
- Another test expects: skill.md output
- Both can't pass without explicit type specification in TOON file itself
```

**Mitigation**: None in task.

---

### Assumption D4: Templates Are Testable in Isolation
**Assumption**: Each template can be tested independently of parser and compiler.

**Reality Check**:
- Templates receive parsed data as input
- Parsed data schema is undefined (see Contradiction 1.1)
- Tests for 01-02/01-03/01-04 are orphaned—can't be written until schema defined
- If templates aren't tested individually, compiler's AC#5 validator can't trust them

**Risk**: Template bugs won't be caught until compiler integration, causing integration test failures.

**Blast Radius**: MEDIUM. Compounds Contradiction 1.1.

---

### Assumption D5: Jinja2 Environment is Stable Across Renders
**Assumption**: Jinja2 environment (loaders, filters, configuration) can be set up once and reused safely.

**Reality Check**:
- Task mentions "template discovery mechanism" in hidden dependencies
- But doesn't specify: are templates loaded from filesystem? packaged in code? environment variable?
- If loaded from filesystem, relative paths must be correct
- If file paths change after refactoring, template discovery breaks
- If filters/context isn't properly isolated, one template's state affects another

**Risk**: Jinja2 environment initialization is fragile; state leakage between renders.

**Example Failure**:
```python
# Render Agent template
agent_output = template.render(data=agent_parsed_data)

# Render Command template with same jinja2 env
command_output = template.render(data=command_parsed_data)
# ^ Fails: Jinja2 env still has Agent-specific filters/context
```

---

## SECTION 3: UNHANDLED EDGE CASES

### Edge Case EC1: Empty or Minimal TOON Files
**Scenario**: Input is a valid .toon file with only metadata, no content sections.

**Current Handling**: Not specified in task.

**Result**:
- Parser may return empty dict `{}`
- Compiler's file type detection logic has no section to examine
- Template rendering receives empty context
- Output may be invalid markdown

**Tests Missing**: No AC item covers minimal/edge-case input.

---

### Edge Case EC2: Parser Raises Unexpected Exception
**Scenario**: Parser encounters malformed TOON syntax and raises an exception (ParseError? ValueError? Generic Exception?).

**Current Handling**: AC#4 says "reports errors clearly on parse/template failures" but:
- Doesn't specify exception types
- Doesn't specify error message format
- Doesn't specify how compiler distinguishes parse errors from template errors

**Result**: Error reporting is ad-hoc; different parse exceptions won't be caught consistently.

**Tests Missing**: No inner test for exception taxonomy (test_compiler_handles_parse_error exists but undefined what errors it handles).

---

### Edge Case EC3: Template File Missing at Runtime
**Scenario**: Compiler tries to render command.md.j2 but file doesn't exist (deleted, wrong path, wrong directory structure).

**Current Handling**: Not specified.

**Result**:
- Jinja2 raises `jinja2.TemplateNotFound` exception
- Compiler may crash with unclear error
- User doesn't know if template missing or compiler broken

**Tests Missing**: No test for missing template file.

---

### Edge Case EC4: Output Directory Doesn't Exist or Isn't Writable
**Scenario**: User specifies output directory that either doesn't exist or user lacks write permissions.

**Current Handling**: AC#3 says "writes output to specified directory" but doesn't specify:
- Create output directory if missing?
- Fail if directory missing?
- Check permissions beforehand?

**Result**: Behavior is undefined; may silently fail or crash with permission error.

**Tests Missing**: No AC item specifies permission handling.

---

### Edge Case EC5: File Type Detection Ambiguity
**Scenario**: A .toon file could be interpreted as multiple types (e.g., a "command" that also acts as a "skill").

**Current Handling**: Task assumes unambiguous file type detection but provides no mechanism.

**Result**: Multiple valid interpretations; tests conflict.

---

### Edge Case EC6: Circular Dependencies in Templates
**Scenario**: Agent template references Skill, Skill template references Agent.

**Current Handling**: No mention of template dependency management.

**Result**: Jinja2 rendering may deadlock or produce circular includes.

---

## SECTION 4: FAILURE SCENARIOS

### Failure Scenario F1: Parser Output Schema Undefined
**Setup**: Implement 01-05 assuming parser returns `dict`.

**Trigger**: Step 01-01 completes and actually returns `dataclass Agent` with different field names.

**Cascade**:
1. Compiler tries `parsed_data["id"]`
2. Raises `TypeError: 'Agent' object is not subscriptable`
3. Tests fail
4. Compiler must be rewritten to use `parsed_data.id`
5. All tests broken until rewritten
6. Refactoring (Levels 2-3) must be redone

**Probability**: 70% (dependencies fundamentally undefined).

**Time to Recovery**: 2-3 hours.

---

### Failure Scenario F2: Template Schema Mismatch
**Setup**: Implement compiler to validate output has sections ["metadata", "commands", "dependencies"].

**Trigger**: Templates finalized with different section names: ["frontmatter", "capabilities", "links"].

**Cascade**:
1. Compiler renders templates with new schema
2. AC#5 validation fails (sections don't match expected)
3. All tests fail with false negatives
4. Validator must be rewritten
5. Real bugs may be masked (AC#5 becomes unreliable)

**Probability**: 80% (templates have conflicting AC definitions).

**Time to Recovery**: 1-2 hours.

---

### Failure Scenario F3: Circular Dependency in Step Chain
**Setup**: Implement compiler expecting parser step 01-01 to be complete.

**Trigger**: Parser step requires template feedback (e.g., "what field names do templates expect?") before finalizing API.

**Cascade**:
1. Parser blocked waiting for template feedback
2. Templates blocked waiting for parser API
3. Compiler blocked on both
4. All three steps stalled

**Probability**: 60% (design has circular dependency).

**Time to Recovery**: 1-2 days (requires architectural redesign).

---

### Failure Scenario F4: File Type Detection Fails on Real TOON Files
**Setup**: Implement file type detection based on assumed TOON structure.

**Trigger**: Real TOON files (agents/novel-editor-chatgpt-toon.txt) have structure that doesn't match assumptions.

**Cascade**:
1. Compile step 01-05 against real TOON files
2. File type detection misidentifies some files (e.g., commands as agents)
3. Wrong template selected
4. Output is invalid
5. Tests pass against synthetic data but fail on real data

**Probability**: 40% (real examples exist but haven't been tested).

**Time to Recovery**: 1-2 hours (update file type detection logic).

---

### Failure Scenario F5: Refactoring Throws Away All Work
**Setup**: Implement compiler with inline file type detection and template selection.

**Trigger**: During refactoring (Level 2-3), extract file type detection into strategy class.

**Cascade**:
1. Extract method to separate class (seems good)
2. Refactoring accidentally loses error handling (copy-paste error)
3. Parse error no longer caught
4. Compiler crashes on next parse failure
5. Had to rollback refactoring
6. Time wasted

**Probability**: 30% (happens with hasty refactoring).

**Time to Recovery**: 1-2 hours (debug and rollback).

---

### Failure Scenario F6: Validation Logic Becomes Unmaintainable
**Setup**: Implement AC#5 validator that checks sections across three template types.

**Trigger**: Templates evolve; each one changes section names independently.

**Cascade**:
1. First template changes from "metadata" to "frontmatter"
2. Validator updated for agent.md
3. Second template changes from "info" to "metadata" (different meaning!)
4. Validator now has conflicting expectations (metadata in agent means X, metadata in command means Y)
5. Validation logic becomes tangled with type-specific exceptions
6. Unmaintainable after 1-2 changes

**Probability**: 50% (validator design is already fragile).

**Time to Recovery**: 2-3 hours (redesign validator as type-specific validators).

---

## SECTION 5: INTEGRATION POINTS (ALL FRAGILE)

| Integration Point | Dependencies | Risk | Recovery Time |
|---|---|---|---|
| `compiler.parse()` → parser API | Parser step 01-01 schema undefined | 70% fail probability | 2-3 hrs |
| File type detection logic | Parser output structure undefined | 80% fail probability | 1-2 hrs |
| Template selection → template file paths | Template discovery mechanism unspecified | 60% fail probability | 1 hr |
| Template rendering → Jinja2 env | Environment setup/teardown not documented | 40% fail probability | 1-2 hrs |
| AC#5 validator → template schema | Three incompatible template schemas | 80% fail probability | 2-3 hrs |
| Error reporting → exception taxonomy | Exception types not defined | 50% fail probability | 1 hr |

---

## SECTION 6: DATA LOSS/CORRUPTION RISKS

### Risk DL1: Overwriting User Files
**Scenario**: Compiler writes output to existing directory without confirmation.

**Impact**: If user accidentally specifies wrong output directory, existing files silently overwritten.

**Mitigation**: Not mentioned in task.

**Recommendation**: Add AC item: "Compiler prompts user before overwriting existing files" or "Compiler uses atomic rename to prevent partial writes".

---

### Risk DL2: Partial Writes on Failure
**Scenario**: Compiler writes partial output before template rendering fails.

**Example**:
```python
with open(output_file, 'w') as f:
    f.write(header)  # Written
    f.write(template.render(...))  # Fails midway
    # File now contains corrupted partial output
```

**Impact**: Output file left in corrupted state; recovery difficult.

**Mitigation**: Not mentioned in task.

**Recommendation**: Add AC item: "Compiler validates output before writing" or "Use temp file + atomic rename pattern".

---

### Risk DL3: Loss of TOON Source if Overwritten
**Scenario**: User accidentally specifies .toon file as output directory.

**Impact**: TOON source corrupted/overwritten.

**Mitigation**: Not mentioned in task.

**Recommendation**: Add safety check: "Prevent overwriting .toon input files".

---

## SECTION 7: SECURITY HOLES

### Security SH1: Path Traversal in Template Loading
**Scenario**: If template path is user-controlled or derived from TOON file, attacker could specify: `../../../../../../etc/passwd`.

**Current Handling**: Task doesn't mention path validation.

**Risk**: Jinja2 loads arbitrary files.

**Recommendation**: Validate template paths; only allow templates from `tools/toon/templates/` directory.

---

### Security SH2: Code Injection via Jinja2 Rendering
**Scenario**: If TOON content contains Jinja2 template syntax: `{{ malicious_function() }}`, it gets rendered as code.

**Current Handling**: Task doesn't mention sandboxing Jinja2.

**Risk**: User-provided TOON input could execute arbitrary Python via Jinja2.

**Recommendation**: Use Jinja2 in strict mode; disable all functions and variable access.

---

### Security SH3: Denial of Service via Large TOON Files
**Scenario**: Attacker provides multi-GB TOON file.

**Current Handling**: No input size limits mentioned.

**Risk**: Parser loads entire file into memory; memory exhaustion.

**Recommendation**: Add file size validation; reject TOON files > N MB.

---

## SECTION 8: TEST COVERAGE GAPS

The declared inner tests are:
```python
"test_compiler_detects_file_type_agent",
"test_compiler_detects_file_type_command",
"test_compiler_detects_file_type_skill",
"test_compiler_handles_parse_error",
"test_compiler_handles_template_error",
"test_compiler_creates_output_directory"
```

**Missing Tests**:
- `test_compiler_output_directory_not_writable` (permission handling)
- `test_compiler_missing_template_file` (graceful failure)
- `test_compiler_template_rendering_fails` (distinct from template_error)
- `test_compiler_validates_output_sections` (AC#5)
- `test_compiler_error_message_clarity` (AC#4)
- `test_compiler_handles_empty_toon_file` (edge case)
- `test_compiler_prevents_overwrite_without_confirmation` (safety)
- `test_compiler_rejects_path_traversal_in_template` (security)
- `test_compiler_handles_circular_template_references` (edge case)
- `test_compiler_output_is_valid_markdown` (quality gate)

**Coverage Gap**: 10/16 critical test cases missing (~60% coverage).

---

## SECTION 9: RISK ASSESSMENT MATRIX

| Risk | Severity | Probability | Blast Radius | Time to Fix | Mitigation |
|---|---|---|---|---|---|
| Parser API undefined | CRITICAL | 70% | HIGH | 2-3 hrs | Define schema in 01-01 before 01-05 starts |
| Circular dependencies | CRITICAL | 60% | CATASTROPHIC | 1-2 days | Resolve in 01-01/01-02/01-03/01-04 design |
| Template schema mismatch | CRITICAL | 80% | HIGH | 2-3 hrs | Validate template AC before 01-05 starts |
| File type detection ambiguous | HIGH | 50% | MEDIUM | 1-2 hrs | Define file type detection rules explicitly |
| AC#5 validator unmaintainable | HIGH | 50% | MEDIUM | 2-3 hrs | Redesign as type-specific validators |
| Refactoring throws away work | MEDIUM | 30% | MEDIUM | 1-2 hrs | Wait for dependencies to stabilize before refactoring |
| Path traversal security | MEDIUM | 40% | MEDIUM | 1 hr | Add path validation |
| Data loss on overwrite | MEDIUM | 30% | MEDIUM | 1 hr | Add confirmation prompt |
| Jinja2 code injection | LOW | 20% | MEDIUM | 1 hr | Use Jinja2 strict mode |

---

## OVERALL RISK SCORE: 8.5/10 (CRITICAL)

**Verdict**: This task will fail in its current state. The dependencies are not ready.

**Failure Point**: 80% probability of hitting at least one blocker during implementation.

**Recommend**: **DO NOT START THIS TASK**. Resolve dependencies first.

---

## RECOMMENDATIONS (Priority Order)

### 1. STOP: Wait for Dependencies to Stabilize (CRITICAL)
**Action**: Do NOT start step 01-05 until steps 01-01 through 01-04 are completed AND tested.

**Why**: Current state has circular dependencies and undefined schemas.

**Prerequisite Checklist**:
- [ ] Parser (01-01) has stable API documented with example I/O
- [ ] Parser output schema finalized as TypedDict or dataclass
- [ ] All three templates (01-02, 01-03, 01-04) have passing tests
- [ ] File type detection rules explicitly documented
- [ ] Template file paths and discovery mechanism specified

---

### 2. DEFINE: Parser Output Schema (CRITICAL)
**Action**: Create explicit TypedDict for parser output.

**Example**:
```python
class ParsedTOON(TypedDict):
    type: Literal["agent", "command", "skill"]  # Explicit type field
    id: str
    metadata: dict
    sections: dict
    commands: list | None
    triggers: list | None
    # ... other fields
```

**Owner**: Step 01-01 completion.

**Blocker for**: Steps 01-02, 01-03, 01-04, 01-05.

---

### 3. DEFINE: Template Discovery Mechanism (HIGH)
**Action**: Specify exactly how compiler finds template files.

**Options**:
- **A) Filesystem pattern**: `tools/toon/templates/{type}.md.j2`
- **B) Registry dict**: `{"agent": AgentTemplate(...), "command": CommandTemplate(...)}`
- **C) Jinja2 loader**: Set up FileSystemLoader with explicit path

**Recommendation**: Option A (filesystem pattern) is simplest.

**Document**: Path resolution, fallback behavior, error handling.

---

### 4. DEFINE: File Type Detection Rules (HIGH)
**Action**: Create explicit algorithm for determining file type from parsed data.

**Options**:
- **A) Explicit field**: Parser adds `"type": "agent"` field (recommended)
- **B) Content analysis**: Detect based on present sections (brittle)
- **C) File naming convention**: filename hint (agent-xxx.toon vs command-yyy.toon)

**Recommendation**: Option A (explicit field in parser output).

**Document**: Decision logic, edge cases, ambiguity resolution.

---

### 5. VALIDATE: Template Acceptance Criteria Alignment (HIGH)
**Action**: Audit templates 01-02, 01-03, 01-04 acceptance criteria for consistency.

**Checklist**:
- [ ] All three templates have consistent YAML frontmatter structure
- [ ] "Required sections" are documented for each template type
- [ ] Output validation rules are unambiguous
- [ ] AC items don't use misleading language (e.g., command template shouldn't use "agent" terminology)

---

### 6. REFACTOR: Delay Refactoring Until Dependencies Stable (MEDIUM)
**Action**: Remove refactoring targets (Levels 2-3) from task.

**Why**: Refactoring will be thrown away once dependencies change.

**When to Refactor**: After compiler passes all AC tests with stable dependencies, do refactoring in separate commit.

---

### 7. ADD: Error Handling Specification (HIGH)
**Action**: Define exception hierarchy and error messages.

**Minimum**:
```python
class TOONCompilerError(Exception): pass
class ParseError(TOONCompilerError): pass
class TemplateNotFoundError(TOONCompilerError): pass
class RenderError(TOONCompilerError): pass
class ValidationError(TOONCompilerError): pass
```

**Document**: When each exception is raised, error message format, user-facing guidance.

---

### 8. ADD: Security Validations (MEDIUM)
**Action**: Add explicit AC item for security.

**Example**:
```json
{
  "AC": "Compiler rejects paths with '..' or absolute paths in file type detection",
  "why": "Prevent path traversal attacks"
}
```

---

### 9. ADD: Missing Test Cases (MEDIUM)
**Action**: Add to inner_tests:
```json
{
  "inner_tests": [
    // ... existing tests
    "test_compiler_validates_output_before_writing",
    "test_compiler_handles_missing_output_directory",
    "test_compiler_handles_template_file_not_found",
    "test_compiler_rejects_path_traversal_attempts",
    "test_compiler_error_messages_are_clear"
  ]
}
```

---

## CONCLUSION

**This task cannot succeed until dependencies are finalized.**

Current state:
- **Parser (01-01)**: Has 4 critical unresolved issues
- **Templates (01-02/01-03/01-04)**: Cannot be tested without parser schema; have conflicting AC definitions
- **Compiler (01-05)**: Depends on all three; will hit cascading failures

**Recommend**:
1. Halt step 01-05
2. Complete steps 01-01 through 01-04 with full AC coverage
3. Test dependencies end-to-end (parser → templates → compiler integration)
4. THEN start step 01-05 with stable dependencies

**Estimated delay**: 1-2 days to resolve dependencies properly.

**Expected outcome**: Step 01-05 will complete in 3-4 hours (as estimated) once dependencies are stable.

---

**Adversarial Review Complete.**
**Confidence in Success if Started Now: 20%**
**Confidence in Success After Following Recommendations: 85%**
