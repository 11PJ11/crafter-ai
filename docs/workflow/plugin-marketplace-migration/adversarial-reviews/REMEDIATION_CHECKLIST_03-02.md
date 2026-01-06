# Remediation Checklist: Step 03-02 Prerequisites

**Target**: Enable Phase 3.2 execution
**Owner**: Phase 1 Lead + QA Lead
**Timeline**: 3-4 days
**Estimated Effort**: 18-22 hours

---

## BLOCKER #1: TOON v3.0 Format Specification

**Owner**: Architecture / Phase 1 Lead
**Time**: 4 hours
**Status**: [ ] NOT STARTED

### Define TOON v3.0 Format
- [ ] Determine: Is TOON v3.0 official public format or internal project format?
  - If official: Document URL to github.com/toon-format/spec or equivalent
  - If internal: Proceed to next step
- [ ] Create `/mnt/c/Repositories/Projects/ai-craft/tools/toon/SPEC.md` containing:
  - Complete TOON v3.0 syntax definition
  - Symbol enumeration (all valid syntax elements)
  - File structure requirements
  - Size limits (if any)
  - Encoding requirements (UTF-8, etc.)
  - Examples of valid TOON v3.0 files (small, medium, large)
  - Version history (v1.0 vs v3.0 differences if applicable)

### Provide Reference Implementations
- [ ] Create `/tools/toon/examples/` directory
- [ ] Add `simple-agent.md` + `simple-agent.toon` (pair)
- [ ] Add `medium-agent.md` + `medium-agent.toon` (pair)
- [ ] Add `complex-agent.md` + `complex-agent.toon` (pair)
- [ ] Create `/tools/toon/EXAMPLES.md` showing:
  - Before/after comparison for each pair
  - Explanation of what was compressed
  - Why compression strategies were chosen

### Verify v1.0 vs v3.0 Compatibility
- [ ] Document: Are v1.0 and v3.0 compatible? Backwards compatible?
- [ ] If incompatible: Document migration path from v1.0 to v3.0
- [ ] If v1.0 exists in codebase: Confirm target is v3.0 (not v1.0)
- [ ] Add to `/tools/toon/SPEC.md`: "Compatibility Note" section

### Sign-Off
- [ ] Architecture review: TOON v3.0 spec is complete and correct
- [ ] QA review: Examples are valid v3.0 format
- [ ] Phase 1 lead: Confirms spec ready for consumption by Phase 3.2

---

## BLOCKER #2: TOON Compiler/Converter Tool

**Owner**: Phase 1 Lead / Tools Owner
**Time**: 6 hours
**Status**: [ ] NOT STARTED

### Provide Compiler/Parser
- [ ] Tool exists: TOON compiler (parser that validates v3.0 syntax)
  - [ ] Locate existing tool OR
  - [ ] Integrate library (e.g., python-toon, javascript toon parser, etc.) OR
  - [ ] Build custom Python tool: `/tools/toon/toon_compiler.py`
- [ ] Compiler can:
  - [ ] Read .toon files
  - [ ] Validate syntax against v3.0 spec
  - [ ] Produce executable/validated output
  - [ ] Return exit code 0 on success, non-zero on error
  - [ ] Provide helpful error messages on failure

### Provide Converter Tool
- [ ] Tool exists: Converter from .md agent format to .toon format
  - [ ] Locate existing tool OR
  - [ ] Build custom Python tool: `/tools/toon/converter.py`
- [ ] Converter can:
  - [ ] Read .md agent files (with YAML headers)
  - [ ] Parse agent structure (name, description, motivation, etc.)
  - [ ] Generate valid v3.0 TOON syntax
  - [ ] Write output to .toon file
  - [ ] Handle errors gracefully (unsupported structures, size limits, etc.)

### Provide Documentation
- [ ] Create `/tools/toon/README.md` containing:
  - [ ] Installation instructions for compiler and converter
  - [ ] Usage: How to compile a .toon file (command, examples)
  - [ ] Usage: How to convert .md to .toon (command, examples)
  - [ ] Example walkthrough: Converting sample-agent.md to sample-agent.toon
  - [ ] Troubleshooting guide for common errors
  - [ ] Exit codes and error messages reference

### Test Compiler & Converter
- [ ] Test 1: Compile simple-agent.toon (should succeed)
  - [ ] Command: `python /tools/toon/toon_compiler.py examples/simple-agent.toon`
  - [ ] Expected: Exit code 0, "Compilation successful" output
- [ ] Test 2: Compile invalid.toon with bad syntax (should fail)
  - [ ] Create test file with v1.0 syntax
  - [ ] Command: `python /tools/toon/toon_compiler.py invalid.toon`
  - [ ] Expected: Exit code 1 or non-zero, error message with details
- [ ] Test 3: Convert sample-agent.md to sample-agent.toon
  - [ ] Command: `python /tools/toon/converter.py sample-agent.md --output sample-agent.toon`
  - [ ] Expected: Exit code 0, file created, file compiles successfully
- [ ] Test 4: Converter handles edge cases
  - [ ] Large agents (software-crafter size: ~500 lines)
  - [ ] Agents with code blocks or nested structures
  - [ ] Agents with special characters or symbols

### Sign-Off
- [ ] Tools owner: Compiler and converter implemented and tested
- [ ] QA review: Both tools work end-to-end
- [ ] Documentation complete: `/tools/toon/README.md` usable by Phase 3.2 executor

---

## BLOCKER #3: Token Savings Measurement Methodology

**Owner**: QA Lead / Metrics Owner
**Time**: 2 hours
**Status**: [ ] NOT STARTED

### Define Measurement Approach
- [ ] Decide: What counts as a "token"?
  - [ ] Option A: Character count
  - [ ] Option B: LLM token count (specify tokenizer: tiktoken, Claude API, etc.)
  - [ ] Option C: Line count
  - [ ] Option D: Semantic token count (other methodology)
  - **Decision**: _______________

- [ ] Decide: What is baseline measurement?
  - [ ] Full file (.md size in tokens)
  - [ ] Specific sections only (description, not metadata)
  - [ ] Content only (excluding formatting, whitespace)
  - **Decision**: _______________

- [ ] Decide: Measurement tool
  - [ ] Manual: Write script to count using selected methodology
  - [ ] Tool: Use existing library (token-counter, etc.)
  - [ ] Service: Use API (Claude API token counter, etc.)
  - **Decision**: _______________

### Create Measurement Script
- [ ] Build `/tools/toon/measure_tokens.py` that:
  - [ ] Takes .md or .toon file as input
  - [ ] Counts tokens using selected methodology
  - [ ] Returns token count as output
  - [ ] Example: `python /tools/toon/measure_tokens.py file.md` → "Token count: 5432"

### Document Methodology
- [ ] Create `/tools/toon/TOKEN_SAVINGS.md` documenting:
  - [ ] Definition: What counts as a token (with rationale)
  - [ ] Baseline: What is included in baseline count
  - [ ] Tool: How to use measurement tool
  - [ ] Examples: Run measurement on 3 sample agents, show results
  - [ ] Interpretation: What "50% savings" means in practical terms
  - [ ] Limitations: Any edge cases or caveats

### Establish Baseline Expectations
- [ ] Measure token savings on example agents (from BLOCKER #1)
  - [ ] simple-agent.md → simple-agent.toon: ___% savings
  - [ ] medium-agent.md → medium-agent.toon: ___% savings
  - [ ] complex-agent.md → complex-agent.toon: ___% savings
- [ ] Document expected range: "Typical TOON compression: 45-65% token savings"
- [ ] Set acceptance threshold: Minimum 50% savings per file

### Sign-Off
- [ ] QA lead: Methodology is well-documented and reproducible
- [ ] Metrics owner: Measurement tool works correctly
- [ ] Architecture: Token savings metric aligns with project goals

---

## BLOCKER #4: Critique Dimensions & Preservation Rules

**Owner**: QA Lead / Phase 1 Lead
**Time**: 3 hours
**Status**: [ ] NOT STARTED

### Define Critique Dimensions
- [ ] For each reviewer agent type, document:
  - [ ] software-crafter-reviewer: What are "critique dimensions"?
    - [ ] Example: severity_levels, assessment_categories, recommendation_format
    - [ ] Are these required? Optional? Configurable?
  - [ ] acceptance-designer-reviewer: (repeat for each of 11 reviewers)
  - [ ] ... (all 11 reviewers)

- [ ] Create `/tools/toon/CRITIQUE_DIMENSIONS.md` documenting:
  - [ ] Definition: What "critique dimensions" means
  - [ ] Per-reviewer specification (which dimensions each reviewer must have)
  - [ ] Preservation requirements (which are MUST-PRESERVE vs optional)
  - [ ] Examples: Show expected output for each reviewer type

### Create Reviewer Template
- [ ] Create `/tools/toon/reviewer-template.toon` showing:
  - [ ] Standard TOON structure for reviewer agents
  - [ ] Required critique dimension fields
  - [ ] Expected format/syntax for dimensions
  - [ ] Annotations explaining purpose of each field

### Document Preservation Test Approach
- [ ] Create `/tools/toon/TEST_CRITIQUE_DIMENSIONS.md` documenting:
  - [ ] How to verify critique dimensions are preserved
  - [ ] Automated test: Load .toon file, parse dimensions, verify all required fields present
  - [ ] Manual checklist: Things to manually verify after conversion
  - [ ] Assertion examples: What makes test pass vs fail

### Create Validation Checklist
- [ ] Create `/tools/toon/DIMENSION_CHECKLIST.md` with:
  - [ ] Dimension names and descriptions for each reviewer type
  - [ ] Checkboxes for each dimension (verify present after conversion)
  - [ ] Space for notes if dimension was modified/adjusted

### Define Refactoring Level 1 Standards
- [ ] Create `/tools/toon/REFACTORING_L1_STANDARDS.md` documenting:
  - [ ] What "reviewer-specific abbreviations" means
  - [ ] List of abbreviations to standardize (across all 11 reviewers)
  - [ ] Standard form for each abbreviation
  - [ ] Before/after examples showing standardized abbreviations
  - [ ] Rationale for each standard choice

### Sign-Off
- [ ] Architecture: Critique dimensions definition is complete and correct
- [ ] QA: Test approach is clear and testable
- [ ] Phase 1 lead: Dimensions match actual reviewer agent structure

---

## BLOCKER #5: Test Framework Implementation

**Owner**: Step 03-02 Executor / QA
**Time**: 3 hours
**Status**: [ ] NOT STARTED

### Choose Test Framework
- [ ] Select framework: [ ] pytest  [ ] unittest  [ ] xunit  [ ] other: ______
- [ ] Rationale: Why selected framework?
  - [ ] Consistency with existing test suite
  - [ ] Features needed (parameterization, fixtures, etc.)
  - [ ] Team familiarity

### Create Test Files
- [ ] Create `/tests/test_toon_conversion.py` containing:
  - [ ] Imports and setup
  - [ ] Test class or functions
  - [ ] Fixtures (sample agent files, etc.)

- [ ] Implement test: `test_each_reviewer_compiles`
  - [ ] For each of 11 reviewers:
    - [ ] Load reviewer.md
    - [ ] Convert to reviewer.toon (using `/tools/toon/converter.py`)
    - [ ] Compile using `/tools/toon/toon_compiler.py`
    - [ ] Assert: Exit code == 0
  - [ ] Example assertion: `assert compile_result.exit_code == 0, f"Compilation failed: {compile_result.stderr}"`

- [ ] Implement test: `test_critique_dimensions_preserved`
  - [ ] For each of 11 reviewers:
    - [ ] Load converted .toon file
    - [ ] Parse TOON structure (extract dimensions)
    - [ ] Assert: All required dimensions present
  - [ ] Example assertion: `assert "severity_levels" in dimensions, "Missing severity_levels dimension"`

- [ ] Implement test: `test_token_savings`
  - [ ] For each of 11 reviewers:
    - [ ] Measure tokens in .md file (using `/tools/toon/measure_tokens.py`)
    - [ ] Measure tokens in .toon file
    - [ ] Calculate savings percentage
    - [ ] Assert: savings >= 50%
  - [ ] Example assertion: `assert savings_pct >= 50, f"Savings {savings_pct}% < 50% threshold"`

### Create Test Data
- [ ] Sample agent files for testing:
  - [ ] Copy sample-agent.md, sample-agent.toon to `/tests/fixtures/`
  - [ ] Create minimal test agent files if needed

### Run Tests Locally
- [ ] Execute test suite on sample agents first:
  - [ ] Command: `pytest tests/test_toon_conversion.py -v`
  - [ ] Expected: All 3 tests pass (on sample agents)

- [ ] Execute test suite on at least 2 real reviewers:
  - [ ] Command: `pytest tests/test_toon_conversion.py::test_each_reviewer_compiles -v`
  - [ ] Expected: All 11 reviewers compile successfully

### Document Test Approach
- [ ] Create `/tests/TEST_DOCUMENTATION.md` explaining:
  - [ ] How to run tests: `pytest tests/test_toon_conversion.py`
  - [ ] What each test verifies
  - [ ] How to interpret results
  - [ ] Troubleshooting if tests fail

### Sign-Off
- [ ] QA: All tests pass on sample agents and at least 2 real reviewers
- [ ] Developer: Code is clean, well-commented, maintainable
- [ ] Step 03-02 executor: Ready to use test suite for acceptance validation

---

## MEDIUM PRIORITY #1: Clarify Reviewer Scope

**Owner**: Product Owner / Requirements
**Time**: 1 hour
**Status**: [ ] NOT STARTED

### Determine Scope
- [ ] Confirm: How many reviewers should be converted in Phase 3.2?
  - [ ] Option A: All 13 reviewer agents (including novel-editor-reviewer, researcher-reviewer)
  - [ ] Option B: Only specified 11 reviewers (explain why other 2 excluded)
  - **Decision**: _______________

- [ ] If Option A (all 13):
  - [ ] Update step 03-02 deliverables (line 31-42) to include all 13
  - [ ] Update acceptance criteria to reference 13 agents

- [ ] If Option B (11 only):
  - [ ] Document: Why are novel-editor-reviewer and researcher-reviewer excluded?
  - [ ] Document: When/how will missing 2 reviewers be converted?
  - [ ] Document: Will they be converted in separate task or later phase?

### Update Documentation
- [ ] Update `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/03-02.json`
  - [ ] Line 12: Update description to clarify scope
  - [ ] Lines 31-42: Update files_to_create list (if scope changed)
  - [ ] Line 44: Update acceptance criteria count

### Sign-Off
- [ ] Product owner: Scope clarified and documented
- [ ] Step 03-02: Clear on exactly which reviewers to convert

---

## MEDIUM PRIORITY #2: Validate Time Estimate

**Owner**: Phase 3.2 Executor / Project Manager
**Time**: 1 hour
**Status**: [ ] NOT STARTED

### Time One Reviewer Conversion
- [ ] Select test subject: software-crafter-reviewer (most complex)
- [ ] Record start time
- [ ] Execute full workflow for single reviewer:
  - [ ] Convert .md to .toon using converter
  - [ ] Compile using compiler
  - [ ] Run test suite
  - [ ] Verify critique dimensions
  - [ ] Measure token savings
  - [ ] Apply refactoring level 1 if needed
  - [ ] Validate against acceptance criteria
- [ ] Record end time
- [ ] Actual time: _____ minutes

### Extrapolate to Full Scope
- [ ] Time per reviewer: [time from above] minutes
- [ ] Total reviewers: 11 (or 13 if scope changed)
- [ ] Raw estimate: [time] × [reviewers] = _____ minutes
- [ ] Add buffer (unknowns, interruptions): +50% = _____ minutes
- [ ] Convert to hours: _____ hours
- [ ] Updated estimate: _____ hours (vs original 5 hours)

### Update Step Documentation
- [ ] Update `/mnt/c/Repositories/Projects/ai-craft/docs/workflow/plugin-marketplace-migration/steps/03-02.json`
  - [ ] Line 14: Update estimated_hours to realistic value
  - [ ] Add note: "Estimate revised based on timing test; originally 5 hours"

### Communicate Timeline
- [ ] Notify project manager of revised timeline
- [ ] Update project schedule / gantt chart
- [ ] Alert downstream phases if timeline impacted

### Sign-Off
- [ ] Project manager: Understands revised timeline
- [ ] Phase 3+ leads: Aware of schedule impact (if any)

---

## MEDIUM PRIORITY #3: Verify Phase 1 Deliverables

**Owner**: Phase 1 Lead / QA
**Time**: 2 hours
**Status**: [ ] NOT STARTED

### Readiness Review Meeting
- [ ] Schedule: Phase 1 Lead + QA Lead + Step 03-02 Owner
- [ ] Duration: 1 hour
- [ ] Agenda:
  - [ ] Confirm TOON v3.0 spec is complete
  - [ ] Confirm compiler/converter are implemented
  - [ ] Verify token measurement methodology defined
  - [ ] Verify critique dimensions documented
  - [ ] Demonstrate full workflow on sample agent

### End-to-End Demo
- [ ] Phase 1 lead demonstrates:
  - [ ] [ ] Convert sample-agent.md → sample-agent.toon (using converter)
  - [ ] [ ] Compile sample-agent.toon (using compiler, exit code 0)
  - [ ] [ ] Measure token savings (using measurement tool)
  - [ ] [ ] Verify critique dimensions preserved
  - [ ] [ ] All steps succeed end-to-end

### Verification Checklist
- [ ] [ ] TOON v3.0 specification complete and documented
- [ ] [ ] tools/toon/ directory exists with all required files
- [ ] [ ] tools/toon/README.md is comprehensive and usable
- [ ] [ ] tools/toon/converter.py works correctly
- [ ] [ ] tools/toon/toon_compiler.py works correctly
- [ ] [ ] tools/toon/measure_tokens.py works correctly
- [ ] [ ] Example .toon files are valid and well-commented
- [ ] [ ] Test framework is implemented and working
- [ ] [ ] All tests pass on sample agents

### Readiness Sign-Off
- [ ] Phase 1 Lead: All Phase 1 deliverables complete and tested
- [ ] QA Lead: Deliverables verified and validated
- [ ] Architecture: Specifications are clear and comprehensive
- [ ] **GATE DECISION**: READY FOR PHASE 3.2? [ ] YES  [ ] NO

---

## Final Gate: Phase 3.2 Start Authorization

**Owner**: Project Manager
**Checklist**:

### Prerequisites Checklist
- [ ] BLOCKER #1: TOON v3.0 format specification ✓ COMPLETE
- [ ] BLOCKER #2: Compiler/converter tools ✓ COMPLETE
- [ ] BLOCKER #3: Token savings methodology ✓ COMPLETE
- [ ] BLOCKER #4: Critique dimensions ✓ COMPLETE
- [ ] BLOCKER #5: Test framework ✓ COMPLETE
- [ ] MEDIUM #1: Reviewer scope clarified ✓ COMPLETE
- [ ] MEDIUM #2: Time estimate validated ✓ COMPLETE
- [ ] MEDIUM #3: Phase 1 readiness verified ✓ COMPLETE

### Phase 3.2 Readiness Assessment
- [ ] All blockers resolved
- [ ] Phase 1 deliverables verified and sign-off obtained
- [ ] Step 03-02 executor has all tools and documentation
- [ ] Test infrastructure ready
- [ ] Timeline communicated to stakeholders
- [ ] Risk assessment: LOW (all prerequisites satisfied)

### Final Authorization
- [ ] Project Manager: Approve Phase 3.2 start? [ ] YES  [ ] NO
- [ ] If NO: Document remaining blockers
- [ ] If YES: Proceed with step 03-02 execution

---

## Sign-Offs

| Role | Name | Date | Status |
|------|------|------|--------|
| Phase 1 Lead | _____________ | ________ | [ ] Sign-Off |
| QA Lead | _____________ | ________ | [ ] Sign-Off |
| Project Manager | _____________ | ________ | [ ] Sign-Off |
| Architecture | _____________ | ________ | [ ] Sign-Off |

---

## Timeline

| Milestone | Target Date | Owner | Status |
|-----------|------------|-------|--------|
| BLOCKER #1 (TOON spec) | Day 1 (4h) | Phase 1 | [ ] |
| BLOCKER #2 (Compiler) | Day 2 (6h) | Phase 1 | [ ] |
| BLOCKER #3 (Token methodology) | Day 2-3 (2h) | QA | [ ] |
| BLOCKER #4 (Dimensions) | Day 3 (3h) | QA/Phase 1 | [ ] |
| BLOCKER #5 (Test framework) | Day 3 (3h) | Executor/QA | [ ] |
| MEDIUM #1 (Scope) | Day 1 (1h) | Product | [ ] |
| MEDIUM #2 (Time estimate) | Day 2 (1h) | Executor | [ ] |
| MEDIUM #3 (Phase 1 verification) | Day 3 (2h) | QA | [ ] |
| **Phase 3.2 Start Authorization** | **Day 4** | **PM** | [ ] |

**Estimated Total**: 3-4 days, 18-22 hours of work

