# Adversarial Review: Step 01-01 (TOON Parser Core)

**Review Date**: 2026-01-05
**Reviewer**: Lyra (adversarial review mode)
**Status**: NO-GO - Blocking issues identified
**Severity**: CRITICAL (8/10 risk)

---

## Executive Summary

Step 01-01 (Create TOON Parser Core) has a **comprehensive embedded review** that identified critical gaps, but that review itself is **incomplete and missed several meta-level failure modes**.

**Bottom Line**: This step cannot proceed until 5 blocking issues are resolved. Estimated remediation time: 2-3 hours.

---

## What the Embedded Review Got Right

The embedded review_findings (in 01-01.json lines 99-323) correctly identified:

- **Library dependency not pre-validated** - python-toon availability must be verified before estimating
- **Parser output schema undefined** - no structure specification for downstream step 1.2 (Jinja2 template)
- **TOON symbols list incomplete** - vague acceptance criteria ("arrows, pipes, checkmarks") without enumeration
- **No test data reference** - agents/novel-editor-chatgpt-toon.txt exists but not explicitly mentioned

These findings are solid. The blocking_prerequisite_check section (lines 243-282) provides actionable remediation steps.

---

## What the Embedded Review Missed (CRITICAL)

The metareview identified 10 additional failure modes the original review didn't catch:

### 1. TOON Version Mismatch (CATASTROPHIC)

**The Problem**:
- Task requires parser for "TOON v3.0"
- Only test data available is "TOON v1.0" (confirmed: agents/novel-editor-chatgpt-toon.txt line 1)
- These are incompatible formats

**Why This Matters**:
- Unit tests will pass with synthetic v3.0 data
- Integration test with real agent file (v1.0) will fail silently
- Steps 1.2-1.6 all depend on parser working with real files

**Failure Mode**:
```
Step 1.1: "Parser is ready, all tests pass ✓"
Step 1.2: "Template designed for v3.0 schema"
Integration: "Real agents are v1.0 → parser fails"
Result: Complete workflow redesign required
```

**Remediation**: STOP and resolve FIRST
- Does TOON v3.0 actually exist? (Check github.com/toon-format/spec)
- Should task use v1.0 instead of v3.0?
- Will we need backward compatibility?

---

### 2. Library Validation Command is Deprecated (MEDIUM)

**The Problem**:
- Embedded review suggests: `pip search python-toon`
- Problem: `pip search` was disabled in 2021 due to server load

**Why This Matters**:
- Developer will try command, get error, be confused
- Blocking prerequisite check becomes blocked

**Remediation**:
Use one of:
```bash
# Option A: Check PyPI directly
pip index versions python-toon

# Option B: Direct install test
pip install python-toon && python -c "import toon; print(toon.__version__)"

# Option C: Check PyPI REST API
curl https://pypi.org/pypi/python-toon/json
```

---

### 3. Custom Parser Contingency is Underestimated (HIGH)

**The Problem**:
- Task says: "~8 additional hours" if custom parser needed
- Reality check: Parser must handle sections, key-value pairs, nested structures, Unicode symbols, multiline content, comments, error handling
- That's: lexer + parser + semantic validator = 12-16 hours minimum

**Why This Matters**:
- 50% budget overrun if custom path chosen
- Late discovery of schedule slip

**Remediation**:
Revise contingency estimate to "12-16 hours including lexer, parser, semantic validation, and error handling. Requires expertise in parsing/compiler theory."

---

### 4. No Rollback Plan for Schema Incompatibility (HIGH)

**The Problem**:
- Step 1.1 (parser) defines output schema
- Step 1.2 (Jinja2 template) consumes that schema
- If schema is wrong, both steps need rework

**Why This Matters**:
- Cascading rework: parser redesign (4-6 hrs) + template redesign (2-3 hrs) = 6-9 hours wasted
- No validation gate between steps

**Failure Mode**:
```
1.1 Complete: {id, role, commands} ✓
1.2 Start: "Need {id, role, commands, metadata, sections, dependencies}"
1.1 Redesign Required
```

**Remediation**:
Add validation gate: "After step 1.1 completion, schema review by 01-02 owner before committing. If incompatible, rework 1.1 before starting 1.2."

---

### 5. Circular Dependency in Schema Design (MEDIUM)

**The Problem**:
- Embedded review says: "Define parser output schema before 1.2"
- But: 1.2 hasn't been designed yet, so we don't know what schema it needs
- Chicken-and-egg problem

**Why This Matters**:
- Schema designed in isolation, then template implementation reveals missing fields
- Forces rework cycle

**Remediation**:
1.2 owner provides template requirements (even as sketch) before 1.1 schema is finalized.

---

### Additional Failure Modes (MEDIUM priority)

**6. Test Isolation Risk** - Multiline content tests may leak state in parallel pytest execution
**7. Version Detection Missing** - No error handling for v1.0 vs v3.0 format mismatch
**8. No Coverage Requirement** - AC doesn't specify coverage target (70%? 85%? 95%?)
**9. Dependency Management** - requirements.txt doesn't list python-toon
**10. Unicode Encoding** - No AC specifies UTF-8 assumption or encoding validation

---

## Risk Assessment

| Factor | Score | Details |
|--------|-------|---------|
| **Blocking Issues** | 5/5 | Version mismatch, schema undefined, library validation command broken |
| **Cascade Impact** | High | Parser failure blocks 1.2-1.6 (entire phase 1) |
| **Hidden Assumptions** | High | Assumes v3.0 exists, assumes library available, assumes clean input |
| **Estimation Risk** | High | 8-hour contingency is 50% underestimated |
| **Test Completeness** | Medium | No coverage requirement, no error handling tests |
| **Overall Risk Score** | 8/10 | CRITICAL - Do not proceed |

---

## Blast Radius Analysis

**If this step fails:**

- Phase 1 TOON Infrastructure blocked (steps 1.2-1.6 cannot start)
- 26 agent files cannot be migrated
- Entire plugin marketplace migration timeline slips
- Estimated rework: 12-20 hours

**Critical Path Impact**: 🔴 HIGH - This is the first step; any failure cascades through entire phase 1

---

## GO/NO-GO Decision

### Current Status: **NO-GO**

### Blocking Items (Must Resolve Before Starting):

1. **TOON v1.0 vs v3.0 mismatch** - Resolve which version is actual target
2. **Library validation command** - Update to working command (pip index or direct test)
3. **Custom parser estimate** - Revise from 8 to 12-16 hours
4. **Schema design coordination** - Get 1.2 requirements before finalizing schema
5. **Error handling spec** - Define malformed input behavior

### Estimated Remediation Time: 2-3 hours total

**Do not start implementation until these are resolved.**

---

## Recommended Actions (Priority Order)

### CRITICAL - Do First (30 mins each):

1. **Resolve TOON version**
   - Check if v3.0 spec exists at github.com/toon-format/spec
   - Confirm which version is actual requirement
   - If v1.0 is correct, update task to use v1.0

2. **Get 1.2 requirements sketch**
   - Ask 1.2 (Jinja2 template) owner: what fields do you need from parser?
   - Document minimal schema needed
   - Use to drive parser schema design

3. **Update library validation**
   - Replace `pip search` with `pip install python-toon && python -c "import toon"`
   - Add to blocking prerequisites

### HIGH - Do Before Implementation (15 mins each):

4. **Enumerate TOON symbols**
   - Create explicit list: {→, ⟷, ≠, ✓, ✗, ⚠️, ...}
   - Add to acceptance criteria

5. **Define error handling**
   - Add AC: "Parser raises ToonParseError on invalid syntax with line number and suggestion"
   - Add test: test_parse_detects_malformed_toon

6. **Add coverage requirement**
   - AC: "Tests achieve ≥85% coverage, critical logic ≥95%"

### MEDIUM - Do Before Implementation (10 mins each):

7. **Add Python version constraint** - "≥3.9"
8. **Add test isolation check** - "Run with pytest -n (parallel mode)"
9. **Document dependency decision** - "Update requirements.txt if library chosen"

---

## Validation Checklist Before Execution

- [ ] TOON version resolved (v1.0 or v3.0 confirmed)
- [ ] Library availability tested (pip install successful OR custom path confirmed)
- [ ] Parser schema reviewed and approved by 1.2 owner
- [ ] TOON symbols enumerated in acceptance criteria
- [ ] Error handling behavior specified in AC
- [ ] Coverage requirement added (≥85% general, ≥95% critical)
- [ ] Test isolation plan added (parallel execution tested)
- [ ] Python version requirement documented (≥3.9)
- [ ] requirements.txt update plan documented
- [ ] All blockers marked as resolved in task file

---

## Reference Files

- Task file: `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/01-01.json`
- Test data: `/mnt/c/Repositories/Projects/ai-craft/agents/novel-editor-chatgpt-toon.txt` (TOON v1.0)
- Downstream: `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/01-02.json` (Jinja2 template)
- Dependencies: `/mnt/c/Repositories/Projects/ai-craft/tools/requirements.txt`

---

## Key Takeaway

The embedded review did excellent foundational analysis, but **missed the most critical issue: TOON v1.0 vs v3.0 version mismatch**. This single issue could cause complete workflow failure if unaddressed.

**Recommendation**: Have technical lead resolve version question and coordinate schema design with step 1.2 owner before assigning work to developer.

---

*Review completed by Lyra (adversarial review mode) - 2026-01-05*
*Detailed findings in 01-01.json adversarial_metareview section*
