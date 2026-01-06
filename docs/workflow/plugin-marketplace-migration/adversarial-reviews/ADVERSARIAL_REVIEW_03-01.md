# Adversarial Review: Step 03-01 (Convert Primary Agents to TOON)

**Review Date**: 2026-01-05
**Reviewer**: Lyra (adversarial review mode - ruthless analysis)
**Status**: NO-GO - Multiple catastrophic blockers
**Risk Score**: 9/10 (CRITICAL)
**Blast Radius**: Phases 3-8 (entire batch migration)

---

## Executive Summary

Step 03-01 (Convert Primary Agents to TOON v3.0) attempts to batch convert 10 primary agents, but the task is **fundamentally broken** due to upstream failures that propagate catastrophically:

1. **TOON v3.0 specification is MISSING** - The entire toolchain assumes a format that hasn't been validated to exist
2. **Compiler doesn't exist** - No .toon compilation tool has been proven to work
3. **Token savings targets are UNMEASURED** - Pulling a 50-60% number from thin air
4. **Test infrastructure is UNDEFINED** - How to measure token counts? No methodology specified
5. **Dependency chain is BROKEN** - Step 2.4 (archive) has its own critical issues

**Bottom Line**: This step cannot run until upstream Phase 1-2 proves the TOON toolchain actually works with real agents.

---

## Critical Blocker #1: TOON v3.0 Specification Missing (CATASTROPHIC)

### The Problem

The task requires conversion to "TOON v3.0 format" but:
- No TOON v3.0 specification document exists in the codebase
- No parser for TOON v3.0 has been validated to work
- The only real TOON data in the repo is `agents/novel-editor-chatgpt-toon.txt` which is **v1.0**
- Phase 1 (steps 1.1-1.6) was supposed to CREATE the TOON parser infrastructure

### Why This Fails

The workflow assumes:
```
Phase 1: Build TOON parser infrastructure (steps 1.1-1.6)
Phase 2: Pilot migration - test on 1 agent (steps 2.1-2.4)
Phase 3: Batch migrate 10 agents using patterns from Phase 2 (step 3.1)
```

But Phase 1 has **CRITICAL UNRESOLVED ISSUES**:
- Step 1.1 (TOON Parser Core): Review shows version mismatch (v3.0 spec vs v1.0 test data)
- Step 1.2 (Jinja2 Template): Depends on parser output schema (undefined)
- Steps 1.3-1.6: All blocked waiting for parser validation

**Current Status**: Phase 1 is INCOMPLETE. Phase 3.1 cannot proceed.

### Detection Method

- Run: `find /mnt/c/Repositories/Projects/ai-craft -name "*3.0*" -o -name "*TOON*spec*" 2>/dev/null`
- Result: **No TOON v3.0 specification found**
- Run: `find . -name "*.toon" -type f 2>/dev/null | wc -l`
- Result: **0 TOON files exist in repo** (only test file: novel-editor-chatgpt-toon.txt which is v1.0)

### Failure Scenario

```
Developer starts Step 3.1:
  "Convert 10 primary agents to TOON v3.0"

Realizes: "What format is TOON v3.0?"

Options:
  A) Guess based on v1.0 example → Produces wrong format
  B) Wait for Phase 1 to complete → Blocking on undefined predecessor
  C) Create v3.0 spec from scratch → Duplicates Phase 1 work (3-5 hour delay)

Result: Step fails. Phases 4-8 cascade failure.
```

### Mitigation

**STOP THIS STEP. Phase 1 must complete first.**
- Confirm Phase 1.1 (Parser Core) completed and tested with real agents
- Confirm Phase 1.6 (TOON Validation) produced validated schema document
- Verify compilation pipeline tested on at least one real agent
- Document TOON v3.0 format specification with examples

**Estimated delay**: 8-12 hours (complete Phase 1 first)

---

## Critical Blocker #2: Compilation Toolchain Unvalidated (CATASTROPHIC)

### The Problem

Task Step 3 says: "Compile each TOON file to validate" (line 70)

But:
- No TOON compiler tool has been shown to exist or work
- Tools/build.py is the 5D-WAVE IDE bundle builder (NOT a TOON compiler)
- No evidence that tools/build.py can handle TOON → agent.md conversion
- Test framework (lines 51-55) references compilation but doesn't specify HOW compilation happens

### Why This Fails

The task assumes a compilation pipeline:
```
agent.toon (TOON format)
  ↓
[compiler - undefined tool]
  ↓
agent.md (Claude Code format)
  ↓
[validation test]
  ↓
Pass/Fail
```

But the [compiler] step is **completely undefined**:
- Which tool compiles TOON → agent.md?
- Does it exist? (Yes: Phase 1.2 was supposed to create it)
- Has it been tested on real agents? (Unknown - Phase 2 pilot status unclear)
- What error handling? (Not specified)
- What happens if compilation fails for 3 out of 10 agents?

### Detection Method

```bash
# Check if TOON compiler exists
ls -la /mnt/c/Repositories/Projects/ai-craft/tools/*toon* 2>/dev/null
# Result: No TOON compiler found

# Check if tools/build.py can handle TOON
grep -i "toon\|\.toon" /mnt/c/Repositories/Projects/ai-craft/tools/*.py
# Result: No references to TOON compilation (README mentions this is IDE bundle builder, not TOON compiler)

# Verify: Phase 1.2 actually created a Jinja2 template compiler?
find . -name "*1-02*" -o -name "*jinja*toon*" 2>/dev/null
# Result: Step 1.2 file exists but no evidence of working Jinja2 TOON compiler
```

### Failure Scenario

```
Developer attempts Step 3.1:
  Step 3 instruction: "Compile each TOON file to validate"
  Developer: "What tool compiles TOON files?"

  Check tools/build.py:
    - It's an IDE bundle builder
    - Not designed for TOON compilation
    - Takes agent.md, produces dist/ artifacts
    - Direction is WRONG (md → dist, not toon → md)

  Dead end. Step fails immediately on first agent.
```

### Acceptance Criteria Conflict

Task says (line 44):
```
"All 10 TOON files compile without errors"
```

But the actual tool doesn't exist. This acceptance criterion is **unachievable**.

### Mitigation

**STOP THIS STEP. Compilation pipeline must be validated in Phase 2 first.**
- Confirm Phase 1.2 (Jinja2 Template) created working TOON compiler
- Confirm Phase 2.1-2.3 successfully converted at least 1 agent using real compiler
- Document compiler tool location and invocation syntax
- Provide examples of successful compilation on real agents
- Create error handling procedure for failed compilations

**Estimated remediation**: 6-8 hours (validate Phase 1-2 toolchain)

---

## Critical Blocker #3: Token Savings Target Contradictory & Unmeasured (HIGH)

### The Problem

Task specifies contradictory metrics:
- Line 26 (SC7): "~60% token savings in source files" (estimate/target)
- Line 46 (Acceptance Criteria): "Token savings >= 50% per file" (hard gate)

**Neither has measurement data**:
- No baseline token counts from Phase 2 pilot agents
- No methodology for measuring tokens (which tool? which definition?)
- No evidence that 50-60% is achievable

### Why This Fails

Two critical gaps:

**Gap 1: No Baseline Measurements**
```
Phase 2.4 was supposed to archive original agents.
But no measurement was taken:
  - agent.md file size / token count BEFORE conversion

If we don't know the baseline, we can't prove 50% savings.

Example failure:
  Original product-owner.md: 47KB, ~12,000 tokens
  Converted product-owner.toon: 22KB, ~6,000 tokens
  Result: 50% savings (meets criteria)

  But what if:
  - TOON format actually produces 15KB (.toon is more verbose)
  - Result: 68% savings (still meets criteria)

  OR worse:
  - TOON + compiled output = 30KB (20KB .toon + 10KB compiled)
  - Result: 36% savings (FAILS criteria)
```

**Gap 2: No Token Counting Methodology**
```
Task says "Token savings >= 50%" but doesn't specify:
  - Which token counter? (OpenAI? Anthropic? Character count?)
  - What counts? (.toon file only? compiled output? both?)
  - When measured? (compressed? with metadata?)
  - Per which agent? (average? minimum? all?)
```

### Detection Method

```bash
# Check if baseline measurements exist
find /mnt/c/Repositories/Projects/ai-craft/docs/workflow -name "*baseline*" -o -name "*measurement*" 2>/dev/null
# Result: No baseline measurement documents

# Verify Phase 2.4 actually measured
grep -r "token\|size\|count\|baseline" /mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/02-04.json
# Result: No measurements in archival step (only archival, no measurement)

# Check if any .toon example exists with measurements
find . -name "*.toon" -exec wc -c {} \;
# Result: No .toon files exist (can't measure)
```

### Failure Scenario

```
Developer completes 10 agent conversions to TOON:
  Step 4: Measure token savings per agent
  Result for 3 agents:
    - product-owner: 48% savings (FAILS 50% gate)
    - solution-architect: 62% savings (passes)
    - acceptance-designer: 45% savings (FAILS 50% gate)

  Task failed. Need to:
    A) Optimize TOON format (rework Phase 1)
    B) Accept 48% is good enough (changes acceptance criteria - requires approval)
    C) Switch to v1.0 TOON which might have different compression

Result: 3-5 hour delay at step 3.1 due to unclear acceptance criteria.
```

### Acceptance Criteria Problem

Line 46 says: "Token savings >= 50% per file"

But this assumes:
- TOON format is size-optimal (UNPROVEN)
- Current .md format has no compression (BASELINE UNKNOWN)
- Measurement applies to ALL 10 agents equally (OPTIMISTIC)

Reality: Different agents have different complexity. A large agent (76KB agent-builder.md) might compress 60%, but a small agent (37KB novel-editor.md) might only compress 40%.

### Mitigation

**CLARIFY BEFORE PROCEEDING**:
1. Measure baseline token counts for all source agents:
   ```bash
   for agent in /mnt/c/Repositories/Projects/ai-craft/5d-wave/agents/*.md; do
     echo "$agent: $(wc -c < $agent) bytes"
   done
   ```
   **Result**: Get actual baseline measurements

2. Specify token counting methodology:
   - Define "tokens": Bytes? Characters? Claude token count? Tiktoken?
   - Tool: Which token counter to use?
   - Scope: File size only? Compiled output? Both?

3. Measure TOON format on pilot agents (Phase 2):
   - If Phase 2.1 successfully converted product-owner to product-owner.toon, measure:
     - product-owner.md size: X bytes
     - product-owner.toon size: Y bytes
     - Savings: (X-Y)/X * 100%
   - If result < 50%, gate is unachievable with current TOON design

4. Resolve contradiction:
   - Is target 50% (hard gate) or 60% (estimate)?
   - If 10 agents only achieve 48% average, what happens?

**Estimated remediation**: 2-3 hours (measurement + clarification)

---

## Critical Blocker #4: Test Specifications Too Vague (HIGH)

### The Problem

TDD tests (lines 51-55) are dangerously underspecified:
```json
"inner_tests": [
  "test_each_agent_compiles",
  "test_each_agent_has_commands",
  "test_token_savings_per_agent"
]
```

These names tell us NOTHING about how to pass/fail:
- What is "compiles"? Compiles without syntax errors? With warnings?
- What is "has_commands"? How many commands? Which names?
- What is "token_savings"? How measured? What's acceptable variance?

### Why This Fails

Ambiguous tests → Executor makes assumptions → Tests pass for wrong reasons → Integration failures downstream.

**Example 1: test_each_agent_compiles**
```
Assumption A: "Compiles = no syntax errors"
  Result: product-owner.toon has syntax error, step fails immediately

Assumption B: "Compiles = runs without exception"
  Result: Test passes but output has wrong schema
  Phase 3.2 expects field X, gets field Y → Cascade failure

Assumption C: "Compiles = produces valid agent.md"
  Result: Test passes, but compiled output doesn't match original behavior
  Phase 4+ validation fails with silent failures (no assertions about behavior)

Assumption D: "Compiles = file doesn't error AND output matches schema"
  Result: ONLY this assumption is safe, but test doesn't specify it
```

**Example 2: test_token_savings_per_agent**
```
Assumption A: ">= 50% for each of 10 agents"
  Result: 3 agents save 48%, step fails

Assumption B: ">= 50% on average across 10 agents"
  Result: Average is 52% but 3 agents save 35%, step passes
  But Phase 4 expects ALL agents to meet 50%, fails

Assumption C: ">= 50% OR file is smaller than X bytes threshold"
  Result: Vague, executor guesses, tests meaningless
```

### Detection Method

```bash
# Verify no test file exists with actual assertions
find /mnt/c/Repositories/Projects/ai-craft -name "*test*03*01*" -o -name "*spec*03*01*" 2>/dev/null
# Result: No test file exists (tests only named, not implemented)

# Check if token counting tool is specified anywhere
grep -r "token.*count\|measure.*token\|token.*metric" /mnt/c/Repositories/Projects/ai-craft/tools --include="*.py" 2>/dev/null
# Result: No token counting infrastructure found
```

### Failure Scenario

```
Developer implements tests based on names alone:

test_each_agent_compiles():
  for agent in toon_files:
    result = compile(agent.toon)
    assert result.exit_code == 0

  All 10 pass! ✓ (But we don't know if output is valid)

test_token_savings_per_agent():
  for agent in compiled_agents:
    original_size = get_original_size(agent)
    new_size = get_compiled_size(agent)
    savings = (original_size - new_size) / original_size
    assert savings >= 0.50  # Vague threshold, no context

  3 agents fail (savings = 0.48). Step fails.
  OR developer lowers threshold to 0.40 to pass. Acceptance criteria violated but tests green.
```

### Mitigation

**REWRITE TESTS WITH EXPLICIT ASSERTIONS**:

```python
def test_each_agent_compiles():
    """
    Acceptance: All 10 .toon files compile to valid agent.md
    Assertion: Each agent.md must:
      1. Have valid YAML frontmatter with required fields:
         - project_id, step_id, phase, deliverables, etc.
      2. Have valid Claude Code markdown
      3. Be valid UTF-8
      4. Not contain compilation error markers
    """
    for toon_file in toon_files:
        compiled = compile_toon(toon_file)

        # Validate YAML
        assert compiled.metadata['project_id']
        assert compiled.metadata['step_id']

        # Validate markdown
        assert is_valid_markdown(compiled.content)

        # Validate no errors
        assert 'ERROR' not in compiled.content
        assert 'FAILED' not in compiled.content

def test_token_savings_per_agent():
    """
    Acceptance: >= 50% token savings per agent
    Assertion: For each agent, tokens_saved / original_tokens >= 0.50
    Methodology: Use Anthropic token counter
    """
    for agent in agents:
        original_md = load_agent(f"5d-wave/agents/{agent}.md")
        compiled_toon = compile_toon(f"5d-wave/agents/{agent}.toon")

        original_tokens = count_tokens(original_md)  # Anthropic API
        toon_tokens = count_tokens(compiled_toon)    # Anthropic API

        savings_ratio = (original_tokens - toon_tokens) / original_tokens

        assert savings_ratio >= 0.50, \
            f"{agent}: {savings_ratio:.1%} savings (expected >= 50%)"

def test_each_agent_has_commands():
    """
    Acceptance: Each agent.md has command definitions
    Assertion: Agent must have >= 3 commands in agent.commands section
    """
    for agent in compiled_agents:
        assert agent.commands, f"{agent}: No commands found"
        assert len(agent.commands) >= 3, \
            f"{agent}: {len(agent.commands)} commands (expected >= 3)"
```

**Estimated remediation**: 4-6 hours (implement proper test framework)

---

## Critical Blocker #5: Dependency Chain Broken (HIGH)

### The Problem

Step 03-01 depends on:
- Line 28: `"dependencies": ["2.4"]`

But Step 2.4 has UNRESOLVED CRITICAL ISSUES documented in its own review:

From 02-04.json review:
```
- CRITICAL: Source location ambiguity (archive wrong files?)
- HIGH: Incomplete acceptance criteria (no file verification)
- HIGH: No rollback procedure defined
- MEDIUM: Archive path structure unclear
```

**If Step 2.4 fails or archives wrong files, Step 3.1 has corrupted baseline data.**

### Why This Fails

Dependency chain failure:
```
Phase 2: Pilot Migration
  2.1: Profile agent-builder agent ← Should establish baseline
  2.2: Create TOON transformation rules ← Depends on 2.1
  2.3: Convert agent-builder to TOON ← Depends on 2.2
  2.4: Archive original files ← CRITICAL DATA PRESERVATION

  Status of 2.4: NEEDS_CLARIFICATION with 1 CRITICAL + 2 HIGH issues

Phase 3: Batch Migration
  3.1: Convert 10 agents ← Depends on 2.4 artifacts and patterns

Problem: If 2.4 archives wrong files (distribution versions instead of source versions),
then 3.1 baseline comparison is INVALID.
```

### Detection Method

```bash
# Check if 2.4 has been executed successfully
ls -la /mnt/c/Repositories/Projects/ai-craft/archive/pre-toon-migration/ 2>/dev/null
# If empty or missing: 2.4 not complete

# Verify which agent files exist in sources
ls /mnt/c/Repositories/Projects/ai-craft/5d-wave/agents/*.md | wc -l
# Result: 28 agents in source (this is expected)

# Check if any evidence of 2.4 execution
grep -r "archive\|pre-toon" /mnt/c/Repositories/Projects/ai-craft/docs/workflow --include="*.md" --include="*.json" 2>/dev/null
# Result: Only references TO archival, no evidence OF archival
```

### Failure Scenario

```
Step 2.4 execution (unclear source path):
  Developer archives files from dist/ide/agents/dw/ (WRONG - 32 compiled files)
  Instead of 5d-wave/agents/ (CORRECT - 28 source files)

Step 3.1 begins:
  Instruction: "Apply conversion patterns from pilot (step 2.4)"
  Pattern for product-owner based on: archive/pre-toon-migration/agents/product-owner.md

  But which product-owner.md?
  - From dist/ide/: post-compilation, has embedded dependencies, different structure
  - From 5d-wave/: original source, clean structure

  Developer converts using wrong baseline → Output has different schema/structure
  Phase 3.2 (Secondary Agents) expects pattern consistency → Fails
```

### Mitigation

**VERIFY STEP 2.4 COMPLETION FIRST**:
1. Check archive directory exists with correct files:
   ```bash
   ls -la /mnt/c/Repositories/Projects/ai-craft/archive/pre-toon-migration/agents/ | wc -l
   # Should show 28 files
   ```

2. Verify 2.4 is PASSING (not just NEEDS_CLARIFICATION):
   - All 28 agents archived from correct source (5d-wave/agents/)
   - Archive verified in commit (git log shows 2.4 execution)
   - Baseline measurements recorded from archives

3. Confirm Phase 2.1-2.3 produced working reference patterns:
   - Phase 2.1 profiling complete (agent-builder metrics)
   - Phase 2.2 transformation rules documented with examples
   - Phase 2.3 pilot conversion successful (agent-builder.md → agent-builder.toon working)
   - Pilot compilation verified

**Estimated remediation**: Depends on 2.4 status. If 2.4 incomplete: 2-4 hours. If 2.4 corrupted: 4-8 hours (recovery).

---

## Additional Failure Modes (Not Showstoppers But Critical)

### 6. Estimated Hours Dangerously Optimistic (MEDIUM)

**Claim**: Step 3.1 "estimated_hours": "5" (line 14)

**Reality Check**:
- 5 hours ÷ 10 agents = 30 minutes per agent
- Includes: Converting .md to .toon format, compiling, testing, validation per agent
- 30 minutes assumes perfect execution with zero errors

**Actual breakdown**:
```
Per agent (realistic):
  - Convert format: 15 min (if patterns clear)
  - Compile: 5 min (if compiler fast)
  - Run tests: 5 min (if tests defined)
  - Debug failures: 15-30 min (inevitable with 10 agents)
  - Commit: 5 min
  ___________
  Total per agent: 45-60 min (not 30)

10 agents × 50 min = 500 minutes = 8.3 hours

But also:
  - Test framework setup/debugging: 1-2 hours
  - First agent failing, debug, retry: 2-3 hours
  - Incremental compilation issues: 1-2 hours

Realistic total: 10-15 hours (not 5)
```

**Impact**: Schedule slip. User expects 5 hours, needs 10-15. Detected late in execution.

### 7. No Rollback Procedure Defined (MEDIUM)

**Scenario**: During batch conversion, agent 7 of 10 fails to compile.

**Current procedure**: Not defined.

**Possible outcomes**:
- A) Continue with remaining 3 agents (inconsistent state)
- B) Halt conversion (no guidance on recovery)
- C) Revert last convert and retry (what if retry fails?)
- D) Switch to manual debugging (what if unfixable?)

**Task doesn't specify which**. Executor makes assumption. Wrong assumption cascades failure.

### 8. No Error Message Specification (MEDIUM)

When agent X fails compilation, what info is available?
```
Bad error: "Agent failed to compile"
Better: "Agent product-owner failed: Undefined symbol 'command.execute' at line 45"
Best: "Product-owner.toon has undefined reference to 'command.execute' (step 3.2 defines this). See step 3.2 execution order requirement in execution_guidance line 67."
```

Task doesn't specify error message detail level or what developer should do with error info.

### 9. Parallel Execution Unclear (LOW)

Can multiple agents be converted in parallel?
- Task doesn't specify
- If yes: Coordination needed (shared test framework)
- If no: Sequential only (slower)

Not blockers, but adds ambiguity.

### 10. No Evidence Phase 2 Produced Patterns (HIGH)

Task says (line 68): "Apply conversion patterns from tools/toon/README.md"

But:
- tools/toon/README.md doesn't exist (verified: not found in repo)
- Phase 2.2 was supposed to "Create TOON transformation rules" but no evidence they exist
- No reference patterns document in /docs/workflow/plugin-marketplace-migration/

**If patterns weren't created in Phase 2, this step is BLINDFOLDED**.

---

## Contradiction Matrix

| Aspect | Requirement A | Requirement B | Impact |
|--------|---------------|---------------|--------|
| **TOON Format** | TOON v3.0 assumed | Only v1.0 example exists | Undefined target format |
| **Token Target** | ~60% (estimate) | >=50% (hard gate) | Moving target, ambiguous pass/fail |
| **Compilation** | "Compile each agent" | No compiler tool exists | Unachievable acceptance criterion |
| **Test Specs** | 3 test names | No implementation/assertions | Tests meaningless without definitions |
| **Baseline Data** | Phase 2.4 archive needed | No evidence 2.4 completed | Measurements invalid if baseline corrupted |
| **Patterns** | Reference patterns required | Phase 2.2 patterns not documented | Developer blindfolded on what format to create |

---

## Risk Assessment

```
Risk Score: 9/10 (CRITICAL)

Components:
  - TOON v3.0 missing: 10/10 (showstopper)
  - Compiler undefined: 10/10 (showstopper)
  - Baseline unmeasured: 8/10 (can cause failure at acceptance criteria)
  - Tests undefined: 7/10 (can pass for wrong reasons)
  - Dependency issues: 7/10 (corrupted baseline → cascade failure)
  - Time estimate wrong: 5/10 (late discovery, schedule slip)

Combined: 9/10 (Multiple showstoppers, any one blocks entire step)

Blast Radius: PHASES 3-8
  - Phase 3.1: BLOCKED
  - Phase 3.2: Can't start without 3.1 patterns
  - Phases 4-8: All depend on 3.x completion

Critical Path Impact: 40-60 hour delay (2-3 weeks of work)
```

---

## Failure Scenarios (Pick Your Poison)

### Scenario A: Developer Ignores Undefined State ("Fake It Till You Make It")
```
Developer assumes TOON v3.0 format based on v1.0 example.
Creates agent.toon files using best guess.
Tests all pass (tests are vague enough to not catch the issue).

Phase 3.2 starts: "Validate compiled outputs"
  Compiled .md files have wrong schema → Cascade failures

Damage: 8 hours invested in Phase 3.1, all 10 agents UNUSABLE
Remediation: Revert Phase 3.1, start over with correct format
Total cost: 16 hours (8 wasted + 8 rework)
```

### Scenario B: Developer Waits for Phase 1 To Complete ("Do It Right")
```
Developer recognizes Step 3.1 dependencies on undefined Phase 1.
Escalates for Phase 1 completion.

Phase 1.1-1.6 restart: 12-16 hours to build working TOON infrastructure
Phase 2.1-2.4 retry: 8-10 hours to pilot with working toolchain
Phase 3.1 starts on firm foundation: 10-15 hours actual work

Total cost: 30-40 hours (current 5-hour estimate becomes 40-hour reality)
Schedule impact: 2-3 week delay
```

### Scenario C: Acceptance Criteria Fail
```
Developer completes 10 agent conversions.

Testing reveals:
  - 3 agents achieve only 48% token savings (fail 50% gate)
  - Test outputs are ambiguous (which agents are truly valid?)

Step 3.1 fails. Options:
  A) Optimize TOON format (redesign Phase 1, 6-8 hour rework)
  B) Lower acceptance criteria (requires user approval, architectural decision)
  C) Debug why savings are too low (investigate if compression is correct)

Result: 4-8 hours blocked on acceptance criteria ambiguity
```

### Scenario D: Integration Cascade Failure
```
Phase 3.1 completes (all tests green, seems successful)
Phase 4 starts validation
  Phase 4 test: "Verify compiled agents execute in CLI mode"
  Result: Compiled agents fail (wrong schema, missing fields, incompatible with Phase 4 expectations)

Damage: Phase 4 blocked, all Phase 3.1 output discovered to be INVALID
Escalation: Revert Phase 3, redesign TOON format, retry
Total cost: 15 hours Phase 3 (wasted) + 16 hours redesign + 15 hours Phase 3 retry = 46 hours
```

---

## Recommended Actions (Priority Order)

### IMMEDIATE (Before Starting Step 3.1)

**1. STOP - Phase 1 Validation Required [4 hours]**
   - Confirm Phase 1.1 (TOON Parser) completed and working
   - Confirm Phase 1.2 (Jinja2 Compiler) creates valid output
   - Confirm Phase 1.6 (Validation) passed on real agent
   - Document TOON v3.0 specification with examples
   - **Gate**: No step 3.1 until Phase 1 artifact review passes

**2. Verify Phase 2 Pilot Results [2 hours]**
   - Confirm Phase 2.1 profiling complete (baseline metrics)
   - Confirm Phase 2.3 pilot agent (agent-builder.toon) exists and compiles
   - Measure actual token savings on pilot: (original_tokens - compiled_tokens) / original_tokens
   - Document patterns extracted from pilot conversion
   - **Gate**: If pilot savings < 50%, clarify if 50% gate is realistic

**3. Baseline Measurements [1 hour]**
   - Measure and record token counts for all 28 source agents:
     ```bash
     for agent in /mnt/c/Repositories/Projects/ai-craft/5d-wave/agents/*.md; do
       name=$(basename "$agent")
       size=$(wc -c < "$agent")
       echo "$name: $size bytes"
     done > /tmp/baseline_metrics.txt
     ```
   - Commit baseline to archive for Phase 8 comparison
   - Define token counting methodology (Anthropic counter, bytes, characters, etc.)
   - **Gate**: No acceptance criteria finalized without baseline

### SHORT TERM (Clarifications)

**4. Resolve TOON Format Ambiguity [2 hours]**
   - Get explicit answer: Is target TOON v3.0 or TOON v1.0?
   - If v3.0: Provide specification document
   - If v1.0: Provide format specification with examples
   - Explain relationship between v1.0 (existing test data) and v3.0 (requirement)
   - **Output**: Format specification document in /docs/workflow/

**5. Clarify Compilation Pipeline [1 hour]**
   - Specify exact command to compile TOON → agent.md
   - Example: `python tools/toon_compiler.py agent.toon -o agent.md`
   - Specify where compiler lives
   - Document expected output format
   - **Output**: Compiler documentation in /docs/workflow/

**6. Rewrite Test Specifications [4 hours]**
   - Replace vague test names with explicit assertions
   - Define token counting methodology
   - Specify acceptance criteria for compilation success
   - Add examples of passing/failing test scenarios
   - **Output**: test_03_01.py with runnable test suite

### MEDIUM TERM (If Proceeding)

**7. Implement Rollback Procedure [2 hours]**
   - Define: "If agent X fails, do Y"
   - Create rollback automation (revert failed agent to .md)
   - Document escalation path for unrecoverable failures
   - **Output**: Rollback procedure in execution_guidance

**8. Update Time Estimate [0.5 hours]**
   - Change from "5 hours" to realistic "10-15 hours"
   - Document assumptions (parallel? sequential? debugging time?)
   - Account for 20-30% contingency buffer
   - **Gate**: User approval on revised estimate before starting

---

## Verdict

**STATUS: NO-GO - CRITICAL BLOCKERS**

**DO NOT PROCEED with Step 3.1 until**:
1. ✓ Phase 1 (TOON infrastructure) proven to work on real agents
2. ✓ Phase 2.4 (Archive) completed with verified baseline metrics
3. ✓ TOON v3.0 specification clarified or v1.0 confirmed as target
4. ✓ Compilation pipeline tested and documented
5. ✓ Test specifications rewritten with explicit assertions
6. ✓ Token savings target validated against pilot results
7. ✓ Time estimate updated to realistic 10-15 hours

**Current Status**: 7/7 blockers UNRESOLVED

**Estimated Remediation Time**: 8-12 hours (complete upstream phases properly)

**Do not bypass this review. Phase 3.1 cannot succeed with current upstream state.**

---

## Appendix: Questions for Project Lead

1. **TOON Format**: Is the target TOON v3.0 or v1.0? If v3.0, where is the specification?
2. **Compiler**: Which tool compiles TOON files? Phase 1.2 (Jinja2) or something else?
3. **Phase 2 Status**: Has Phase 2.4 (archive) been executed? Can you verify files in `archive/pre-toon-migration/`?
4. **Token Baseline**: What are the actual token counts for the 28 agents? Do we have Phase 2.1 profiling data?
5. **Acceptance Criteria**: If pilot agents achieve 48% savings but criteria requires 50%, what happens?
6. **Time Estimate**: Acknowledge that 5 hours is optimistic and 10-15 hours is realistic?
7. **Phase 1 Completion**: Can you confirm Phase 1.1-1.6 are complete and the parser/compiler work?

---

**END ADVERSARIAL REVIEW**

