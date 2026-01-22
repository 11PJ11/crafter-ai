# Deterministic Execution System (DES) - Requirements Specification

**Version:** 1.0
**Date:** 2026-01-22
**Status:** DISCUSS Wave Complete
**Author:** Riley (Requirements Analyst)

---

## 1. Problem Statement

### 1.1 The Core Problem

When Claude Code executes multi-step workflows (Outside-In TDD, step-by-step implementations, commit sequences), there is **no guarantee** that:

1. Each step is actually executed as specified
2. Steps are not accidentally skipped without documentation
3. The reason for any skipping is captured and validated
4. The workflow state is persisted reliably across sessions
5. Critical methodology details (like 14-phase TDD) are communicated completely to sub-agents

### 1.2 The Context Dilution Problem

When nWave commands delegate work via the Task tool, important details may be lost in translation:

- **Source**: Command file contains complete 14-phase TDD specification, quality gates, review criteria
- **Orchestrator**: May or may not include all details in Task prompt
- **Sub-Agent**: May receive incomplete instructions, leading to inconsistent execution

### 1.3 User Pain Points (Domain Language)

**Marcus (Senior Developer)** describes the problem:
> "I ran `/nw:develop` yesterday and the agent skipped phases 7-11 without telling me why. Today I have failing tests and no idea what happened. I spent 2 hours debugging something that should have been caught by the review phase."

**Priya (Tech Lead)** describes the problem:
> "I can't approve PRs with confidence because I don't know if the TDD phases were actually followed. The step files show 'DONE' but there's no evidence the refactoring phases ran."

**Alex (Junior Developer)** describes the problem:
> "I'm learning TDD but the agent sometimes skips phases and I don't understand when that's okay and when it's a problem. I need clearer guidance about what's required."

### 1.4 Business Impact

| Impact Area | Current State | Desired State |
|-------------|---------------|---------------|
| Debugging time | 2+ hours per skipped phase incident | < 15 minutes with audit trail |
| Code review confidence | Low (no execution visibility) | High (complete audit trail) |
| TDD methodology compliance | Unknown (no measurement) | 100% verified execution |
| Session recovery | Manual (lost context) | Automatic (state preserved) |

---

## 2. Stakeholder Analysis

### 2.1 Primary Stakeholders

| Stakeholder | Role | Interest | Influence |
|-------------|------|----------|-----------|
| **Marcus** | Senior Developer | Reliable step execution, debugging capability | High - Daily user |
| **Priya** | Tech Lead | Execution visibility, compliance verification | High - Approver |
| **Alex** | Junior Developer | Learning support, clear phase guidance | Medium - Learner |

### 2.2 Secondary Stakeholders

| Stakeholder | Role | Interest | Influence |
|-------------|------|----------|-----------|
| Framework Maintainers | nWave Development | System reliability, extensibility | High - Implementers |
| DevOps | Infrastructure | Hook integration, monitoring | Medium - Integration |

### 2.3 Stakeholder Needs Matrix

| Need | Marcus | Priya | Alex |
|------|--------|-------|------|
| Complete phase execution | Critical | Critical | High |
| Audit trail visibility | High | Critical | Medium |
| Failure recovery guidance | Critical | High | Critical |
| Learning feedback | Low | Medium | Critical |
| PR evidence | High | Critical | Medium |

---

## 3. Functional Requirements

### 3.1 Command-Origin Filtering (FR-001)

**Requirement:** The system SHALL distinguish between Task tool invocations that originate from nWave commands versus ad-hoc invocations.

**Rationale:** Only command-originated tasks require deterministic execution validation. Ad-hoc exploration should not be constrained.

**Acceptance Criteria:**
- FR-001.1: Task invocations from `/nw:execute`, `/nw:develop` are tagged as requiring validation
- FR-001.2: Task invocations for exploration/research are NOT tagged
- FR-001.3: Tags are machine-readable (DES metadata markers)

### 3.2 Prompt Template Validation (FR-002)

**Requirement:** The system SHALL validate that all DES-tagged prompts contain mandatory sections before Task invocation.

**Rationale:** Incomplete prompts lead to context dilution and inconsistent execution.

**Mandatory Sections:**
1. DES_METADATA - Origin, step file, validation flag
2. AGENT_IDENTITY - Who the agent is
3. TASK_CONTEXT - What they're working on
4. TDD_14_PHASES - Complete phase list with criteria
5. QUALITY_GATES - G1-G6 gate definitions
6. OUTCOME_RECORDING - How to record results
7. BOUNDARY_RULES - Scope limitations
8. TIMEOUT_INSTRUCTION - Turn discipline (no max_turns available)

**Acceptance Criteria:**
- FR-002.1: Pre-invocation validation blocks Task if any mandatory section is missing
- FR-002.2: Validation produces specific error messages identifying missing sections
- FR-002.3: All 14 TDD phases must be enumerated in the prompt

### 3.3 Execution Lifecycle Management (FR-003)

**Requirement:** The system SHALL manage execution state through a defined state machine.

**States:**
- TODO: Step not started
- IN_PROGRESS: Agent actively working
- DONE: Step completed successfully
- FAILED: Step failed, needs intervention
- PARTIAL: Partial completion, can resume

**Acceptance Criteria:**
- FR-003.1: State transitions follow defined FSM rules
- FR-003.2: Invalid transitions are rejected
- FR-003.3: State changes are atomic (no partial updates)

### 3.4 Post-Execution Validation (FR-004)

**Requirement:** The system SHALL validate step file state after sub-agent completion via SubagentStop hook.

**Rationale:** Detect abandoned phases, incomplete work, and state corruption.

**Acceptance Criteria:**
- FR-004.1: SubagentStop hook fires for all sub-agent completions
- FR-004.2: Phases left in IN_PROGRESS are flagged as abandoned
- FR-004.3: Tasks marked DONE with NOT_EXECUTED phases are flagged as invalid
- FR-004.4: EXECUTED phases without outcome are flagged as incomplete

### 3.5 Audit Trail (FR-005)

**Requirement:** The system SHALL maintain an immutable audit trail of all state transitions.

**Rationale:** Enable debugging, compliance verification, and session recovery.

**Acceptance Criteria:**
- FR-005.1: All state transitions are logged with timestamp
- FR-005.2: Audit log is append-only (immutable)
- FR-005.3: Audit entries include event type, step file, and relevant data

### 3.6 Failure Recovery (FR-006)

**Requirement:** The system SHALL provide recovery mechanisms for all identified failure modes.

**Failure Modes:**
1. Agent Crash - Phases stuck in IN_PROGRESS
2. Agent Stuck - Infinite loop behavior
3. Agent Runaway - Continues beyond scope
4. Silent Completion - Returns without updating state

**Acceptance Criteria:**
- FR-006.1: Each failure mode has a documented detection mechanism
- FR-006.2: Each failure mode has a documented recovery procedure
- FR-006.3: Recovery suggestions are included in step file on failure

---

## 4. Non-Functional Requirements

### 4.1 Performance (NFR-001)

| Metric | Requirement | Rationale |
|--------|-------------|-----------|
| Pre-invocation validation | < 500ms | Must not noticeably delay workflow |
| Post-execution validation | < 2s | Hook should complete quickly |
| Audit log write | < 100ms | Must not block execution |

### 4.2 Reliability (NFR-002)

| Metric | Requirement | Rationale |
|--------|-------------|-----------|
| Hook firing rate | 100% | Every sub-agent completion must trigger validation |
| File operation atomicity | Guaranteed | No partial writes that corrupt state |
| State consistency | Eventual | State must converge to valid configuration |

### 4.3 Usability (NFR-003)

| Metric | Requirement | Rationale |
|--------|-------------|-----------|
| Error message clarity | Actionable | User can fix problem without documentation |
| Recovery guidance | Always provided | User knows what to do on failure |
| Learning feedback | Progressive | Junior developers receive appropriate guidance |

### 4.4 Maintainability (NFR-004)

| Metric | Requirement | Rationale |
|--------|-------------|-----------|
| Single source of truth | Required | Phase definitions in one canonical location |
| Module separation | Required | Validation logic separated by concern |
| Test coverage | > 80% | Validation scripts must be well-tested |

### 4.5 Compatibility (NFR-005)

| Constraint | Requirement | Rationale |
|------------|-------------|-----------|
| Claude Code version | Compatible with current | Must work with existing installation |
| Hook mechanism | SubagentStop only | Pre-Task hooks not available |
| Task tool | No max_turns parameter | CLI-only feature, not available in SDK |

---

## 5. Constraints

### 5.1 Technical Constraints (Empirically Verified)

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| **max_turns NOT available** | Cannot enforce turn limits programmatically | Prompt-based turn discipline with watchdog backup |
| **No mid-execution messages** | Cannot correct agent during work | Front-loaded validation; complete prompts upfront |
| **SubagentStop hook only** | No pre-Task hook available | Orchestrator-level validation before Task invocation |
| **Session restart required** | Hook config changes need restart | Document in setup instructions |

### 5.2 Business Constraints

| Constraint | Impact | Mitigation |
|------------|--------|------------|
| Token budget | Validation adds overhead | Defer optimization per user decision |
| Learning curve | New concepts for users | Progressive disclosure; Alex persona guidance |
| Sequential execution (MVP) | No parallel step execution | Parallel support in v2 |

### 5.3 Regulatory/Compliance Constraints

None identified for MVP.

---

## 6. Dependencies

### 6.1 Internal Dependencies

| Dependency | Description | Status |
|------------|-------------|--------|
| nWave framework | Core command infrastructure | Available |
| Step file schema | 14-phase TDD structure | Available |
| Pre-commit hook | Existing validation gate | Available |

### 6.2 External Dependencies

| Dependency | Description | Status |
|------------|-------------|--------|
| Claude Code | SubagentStop hook support | Verified working |
| Python 3.11+ | Hook script execution | Required |

---

## 7. Assumptions

1. **A-001:** SubagentStop hook continues to work in future Claude Code versions
2. **A-002:** Step file format remains stable during implementation
3. **A-003:** Users accept prompt-based turn discipline as timeout mechanism
4. **A-004:** Sequential execution is acceptable for MVP (no parallel steps)

---

## 8. Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| SubagentStop hook behavior changes | Low | High | Pin to known Claude Code version; monitor releases |
| Step file corruption | Low | High | Atomic writes with backup |
| Race condition on file access | Low | Medium | File locking for parallel v2 |
| Git state divergence | Medium | Medium | Store commit SHA in step file |
| Incomplete work passes gates | Medium | High | Multi-layer validation (Gate 1-4) |
| Agent ignores timeout instruction | Medium | Medium | External watchdog as backup |

---

## 9. Success Metrics

| Metric | Baseline | Target | Measurement |
|--------|----------|--------|-------------|
| Phase skip without documentation | Unknown | 0% | Audit trail analysis |
| Debugging time per incident | ~2 hours | < 15 min | User survey |
| PR approval confidence | Low | High | Priya satisfaction survey |
| TDD compliance rate | Unknown | 100% | Gate validation results |

---

## 10. Glossary

| Term | Definition |
|------|------------|
| **DES** | Deterministic Execution System |
| **Gate** | Validation checkpoint (G1-G6 quality gates, Gate 1-4 validation layers) |
| **Phase** | One of 14 TDD cycle stages (PREPARE through COMMIT) |
| **Step** | Atomic unit of work with associated step file |
| **SubagentStop** | Claude Code hook that fires when sub-agent completes |
| **Turn** | Single round-trip interaction with Claude API |

---

*Requirements gathered and documented by Riley (product-owner) during DISCUSS wave.*

---

## Product Owner Review

**Reviewer**: product-owner-reviewer (Sage)
**Date**: 2026-01-22
**Overall Assessment**: NEEDS_REVISION

### Review Summary (YAML)

```yaml
review_result:
  artifact_reviewed: "/mnt/c/Repositories/Projects/ai-craft/docs/feature/des/requirements.md"
  story_id: "DES-MVP"
  review_date: "2026-01-22T12:00:00Z"
  reviewer: "product-owner-reviewer"

  dor_validation:
    status: "BLOCKED"
    pass_count: 5/8
    items:
      - item: "Problem statement clear"
        status: "PASS"
        evidence: "Section 1.1-1.4 describes core problem with user pain points: 'When Claude Code executes multi-step workflows... there is no guarantee that...'"
        issue: null
        remediation: null

      - item: "User/persona identified"
        status: "PASS"
        evidence: "Three personas: Marcus (Senior Developer), Priya (Tech Lead), Alex (Junior Developer) with specific quotes and contexts"
        issue: null
        remediation: null

      - item: "3+ domain examples with real data"
        status: "PARTIAL"
        evidence: "User quotes present but acceptance criteria lack concrete data examples"
        issue: "FR examples use generic placeholders like 'Task invocations from /nw:execute' without specific data values"
        remediation: "Add concrete examples: 'Given step file 01-01.json with phases 0-5 IN_PROGRESS...'"

      - item: "UAT scenarios (3-7) with Given/When/Then"
        status: "FAIL"
        evidence: "NOT FOUND - Acceptance criteria exist as technical checkboxes (FR-001.1, FR-002.1) but no Given/When/Then format"
        issue: "No proper UAT scenarios - only technical acceptance criteria"
        remediation: |
          Add UAT scenarios for each FR:
          Given Marcus has a step file with phase 7 IN_PROGRESS
          When the SubagentStop hook fires
          Then the audit log shows 'abandoned phase' warning

      - item: "Acceptance criteria from UAT"
        status: "FAIL"
        evidence: "FR-001.1-FR-006.3 are technical requirements, not user-observable behaviors"
        issue: "Criteria describe system behavior ('State changes are atomic') not user outcomes"
        remediation: "Rewrite as user outcomes: 'Marcus can see which phase was abandoned in the audit trail'"

      - item: "Right-sized (1-3 days, 3-7 scenarios)"
        status: "FAIL"
        evidence: "6 functional requirements (FR-001 through FR-006), each with multiple acceptance criteria"
        issue: "EPIC-sized scope - estimated weeks, not days"
        remediation: "Split into 4-6 stories: (1) Command-origin tagging, (2) Prompt validation, (3) State machine, (4) SubagentStop hook, (5) Audit trail, (6) Recovery handlers"

      - item: "Technical notes present"
        status: "PASS"
        evidence: "Section 5 (Constraints) with empirically verified constraints: 'max_turns NOT available', 'SubagentStop hook only'"
        issue: null
        remediation: null

      - item: "Dependencies resolved/tracked"
        status: "PASS"
        evidence: "Section 6.1-6.2: 'Claude Code SubagentStop hook support - Verified working', 'Python 3.11+ - Required'"
        issue: null
        remediation: null

  antipattern_detection:
    patterns_found_count: 3
    patterns_found:
      - pattern: "technical_acceptance_criteria"
        severity: "high"
        location: "Section 3 - Functional Requirements"
        evidence: |
          FR-002.2: "Pre-invocation validation blocks Task if any mandatory section is missing"
          FR-003.3: "State changes are atomic (no partial updates)"
          FR-004.1: "SubagentStop hook fires for all sub-agent completions"
        remediation: |
          BAD: "State changes are atomic"
          GOOD: "Marcus never sees a step file with corrupted or partial state"

      - pattern: "giant_stories"
        severity: "critical"
        location: "Entire document scope"
        evidence: "6 functional requirements (FR-001-FR-006), each complex enough to be its own story. No effort estimate provided."
        remediation: |
          BAD: Single DES-MVP story with 6 FRs
          GOOD: Split into independent stories:
            - US-001: Command-origin filtering (1-2 days)
            - US-002: Prompt template validation (2-3 days)
            - US-003: Execution state machine (1-2 days)
            - US-004: SubagentStop validation (2-3 days)
            - US-005: Audit trail logging (1-2 days)
            - US-006: Failure recovery (2-3 days)

      - pattern: "missing_edge_cases"
        severity: "medium"
        location: "Acceptance criteria throughout"
        evidence: "Risks section mentions edge cases (SubagentStop behavior changes, race conditions) but no corresponding UAT error scenarios"
        remediation: |
          BAD: Only success scenarios in acceptance criteria
          GOOD: Add error scenarios:
            - "Given SubagentStop hook fails to fire, Then Marcus sees manual recovery instructions"
            - "Given two agents modify same step file concurrently, Then file locking prevents corruption"

  story_sizing:
    scenario_count: 0
    estimated_effort: "Not provided - estimated 2-3 weeks based on FR count"
    status: "OVERSIZED"
    issue: "EPIC-level scope - 6 major functional requirements with multiple sub-criteria each"
    remediation: "Split into 4-6 stories, each 1-3 days with 3-7 scenarios"

  uat_quality:
    total_scenarios: 0
    format_compliance:
      status: "FAIL"
      issues:
        - "No Given/When/Then scenarios found"
        - "Only technical acceptance criteria (FR-XXX.X format)"
    real_data_usage:
      status: "PARTIAL"
      issues:
        - "Personas use real names (good)"
        - "Acceptance criteria use generic references ('Task invocations', 'mandatory sections')"
    coverage:
      happy_path: false
      edge_cases: false
      error_scenarios: false
      issue: "No UAT scenarios exist - cannot assess coverage"

  domain_language:
    technical_jargon_found:
      - term: "FSM"
        location: "FR-003 - Execution Lifecycle Management"
        suggested_replacement: "state flow" or "execution flow"
      - term: "atomic (no partial updates)"
        location: "FR-003.3"
        suggested_replacement: "complete and consistent"
      - term: "SubagentStop hook"
        location: "FR-004, NFR-002"
        suggested_replacement: "post-execution checkpoint" (for user-facing docs)
    generic_language_found:
      - term: "the system"
        location: "FR-001, FR-002, FR-003, FR-005, FR-006"
        suggested_replacement: "DES" or specific component name

  approval_status: "rejected_pending_revisions"

  blocking_issues:
    - severity: "critical"
      issue: "No UAT scenarios in Given/When/Then format"
      must_fix: true
    - severity: "critical"
      issue: "EPIC-sized scope needs splitting into deliverable stories"
      must_fix: true
    - severity: "high"
      issue: "Technical acceptance criteria instead of user-observable behaviors"
      must_fix: true

  recommendations:
    - priority: "high"
      recommendation: "Add 3-5 UAT scenarios per functional requirement using Given/When/Then format with Marcus/Priya/Alex personas"
    - priority: "high"
      recommendation: "Split into 4-6 user stories, each with 1-3 day effort estimate"
    - priority: "high"
      recommendation: "Rewrite acceptance criteria as user-observable outcomes, not technical requirements"
    - priority: "medium"
      recommendation: "Add concrete data examples: specific step file names, phase numbers, expected states"
    - priority: "medium"
      recommendation: "Add error scenario UATs for each identified risk"
    - priority: "low"
      recommendation: "Replace technical jargon with domain language in user-facing sections"

  summary: |
    The requirements document has a STRONG FOUNDATION with excellent problem statement,
    well-defined personas, and comprehensive technical constraints. However, it is
    BLOCKED from proceeding to DESIGN wave due to:

    1. MISSING UAT scenarios (zero Given/When/Then format)
    2. EPIC-SIZED scope (6 FRs, estimated weeks of work)
    3. TECHNICAL acceptance criteria (system behavior, not user outcomes)

    ACTION REQUIRED: Add UAT scenarios and split into deliverable stories before
    handoff to DESIGN wave.
```

### Critiques

| # | Section | Issue | Severity | Recommendation |
|---|---------|-------|----------|----------------|
| 1 | Section 3 | No Given/When/Then UAT scenarios | HIGH | Add 3-5 UAT scenarios per FR using personas |
| 2 | Overall | EPIC-sized scope (6 FRs) | HIGH | Split into 4-6 user stories with effort estimates |
| 3 | Section 3 | Technical acceptance criteria | HIGH | Rewrite as user-observable outcomes |
| 4 | Section 3 | Generic examples in FRs | MEDIUM | Add concrete data: step file names, phase numbers |
| 5 | Section 8 | Risks without error UATs | MEDIUM | Add error scenario UATs for each risk |
| 6 | Multiple | Technical jargon (FSM, atomic) | LOW | Use domain language in user-facing sections |

### Strengths

- **Excellent problem statement**: Section 1.1-1.4 clearly articulates the core problem with specific user pain points
- **Well-defined personas**: Marcus, Priya, and Alex have specific roles, contexts, and quotes
- **Comprehensive constraints**: Section 5 documents empirically verified technical limitations
- **Clear dependency tracking**: Section 6 identifies dependencies with verification status
- **Risk assessment included**: Section 8 identifies risks with likelihood, impact, and mitigation
- **Success metrics defined**: Section 9 provides measurable targets (0% undocumented skips, <15min debugging)
- **Glossary provided**: Section 10 defines domain-specific terms

### Missing Elements

1. **UAT Scenarios**: Zero Given/When/Then format scenarios for any requirement
2. **Effort Estimates**: No story points or time estimates provided
3. **Story Breakdown**: Single EPIC instead of deliverable user stories
4. **Error Scenario UATs**: Happy path implied but no explicit error handling scenarios
5. **Concrete Data Examples**: Generic references instead of specific values (step files, phase states)

### Recommendation

**BLOCKED from DESIGN wave** - The requirements document requires revisions before proceeding:

1. **MUST ADD**: UAT scenarios in Given/When/Then format for each functional requirement
2. **MUST SPLIT**: Break into 4-6 user stories with 1-3 day effort estimates each
3. **SHOULD REWRITE**: Change technical acceptance criteria to user-observable behaviors

The problem statement, personas, and technical analysis are solid. The gap is in translating these into testable, deliverable user stories with proper acceptance criteria.

---

*Review conducted by Sage (product-owner-reviewer) as DoR Gate Enforcer*
