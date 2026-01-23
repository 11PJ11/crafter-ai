# Deterministic Execution System (DES) - User Stories

**Version:** 1.0
**Date:** 2026-01-22
**Status:** DISCUSS Wave Complete

---

## Personas

### Marcus (Senior Developer)
- **Experience:** 8+ years, TDD practitioner
- **Context:** Executes `/nw:develop` workflows daily for feature implementation
- **Pain:** Phases get skipped without explanation; debugging is time-consuming
- **Goal:** Reliable, predictable step execution with clear visibility

### Priya (Tech Lead)
- **Experience:** 12+ years, code review gatekeeper
- **Context:** Reviews PRs and approves code quality
- **Pain:** Cannot verify TDD compliance; no execution evidence
- **Goal:** Complete audit trail for confident PR approval

### Alex (Junior Developer)
- **Experience:** 1 year, learning TDD methodology
- **Context:** Uses nWave to learn proper TDD discipline
- **Pain:** Confused when phases are skipped; unclear what's required
- **Goal:** Clear guidance on phase execution and learning feedback

---

## User Stories

### US-001: Command-Origin Task Filtering

**As** Marcus (Senior Developer),
**I want** DES to only validate Task invocations that come from nWave commands,
**So that** my ad-hoc exploration with Task tool isn't blocked by unnecessary validation.

**Story Points:** 3
**Priority:** P0 (Must Have)

#### Problem (The Pain)
Marcus frequently uses Task tool for quick research and exploration. He finds it frustrating when these exploratory tasks trigger heavy validation that slows him down and produces irrelevant errors.

#### Who (The User)
- Senior developer familiar with nWave commands
- Uses both command-driven workflows AND ad-hoc exploration
- Values efficiency and clear separation of concerns

#### Solution (What We Build)
DES metadata markers that distinguish command-originated tasks from ad-hoc tasks. Only tasks with `DES-VALIDATION: required` marker go through validation gates.

#### Domain Examples

**Example 1: Command Task Gets Validated**
Marcus runs `/nw:execute @software-crafter "steps/01-01.json"`.
The orchestrator generates a prompt with `<!-- DES-VALIDATION: required -->` marker.
DES pre-invocation validation runs, verifying all 14 TDD phases are embedded.
Validation passes, Task tool is invoked.

**Example 2: Ad-hoc Task Bypasses Validation**
Marcus wants quick research: `Task(prompt="Find all uses of UserRepository")`.
No DES markers in prompt.
DES validation is skipped entirely.
Task executes immediately without delay.

**Example 3: Partial Command Gets Appropriate Treatment**
Marcus runs `/nw:research "authentication patterns"`.
The command is not in the validation-required list.
Task executes without full DES validation.

#### Acceptance Criteria

- [ ] AC-001.1: Prompts containing `<!-- DES-VALIDATION: required -->` trigger full validation
- [ ] AC-001.2: Prompts without DES markers execute without validation delay
- [ ] AC-001.3: Command registration defines which commands require validation
- [ ] AC-001.4: Non-command Task invocations never blocked by DES

---

### US-002: Pre-Invocation Template Validation

**As** Priya (Tech Lead),
**I want** DES to block Task invocation if mandatory sections are missing from the prompt,
**So that** sub-agents always receive complete instructions and cannot claim ignorance.

**Story Points:** 5
**Priority:** P0 (Must Have)

#### Problem (The Pain)
Priya reviews PRs where developers claim "the agent skipped the review phase because it wasn't in the instructions." She has no way to verify whether the orchestrator actually included all required sections. This leads to blame-shifting and inconsistent quality.

#### Who (The User)
- Tech Lead responsible for code quality
- Reviews PRs and holds team accountable
- Needs evidence that methodology was communicated

#### Solution (What We Build)
Pre-invocation validation that checks for 8 mandatory sections (DES_METADATA, AGENT_IDENTITY, TASK_CONTEXT, TDD_14_PHASES, QUALITY_GATES, OUTCOME_RECORDING, BOUNDARY_RULES, TIMEOUT_INSTRUCTION) before allowing Task invocation.

#### Domain Examples

**Example 1: Complete Prompt Passes Validation**
The orchestrator generates a prompt for step 01-01 with all 8 mandatory sections.
Pre-invocation validation scans for each section marker.
All sections found, all 14 TDD phases enumerated.
Validation PASSES, Task invocation proceeds.

**Example 2: Missing TDD Phase Detected**
The orchestrator accidentally omits REFACTOR_L3 phase from the prompt.
Pre-invocation validation scans TDD_14_PHASES section.
Error: "INCOMPLETE: TDD phase 'REFACTOR_L3' not mentioned"
Task invocation is BLOCKED.
Orchestrator receives specific error with missing phase name.

**Example 3: Missing Mandatory Section Detected**
The orchestrator generates a prompt without TIMEOUT_INSTRUCTION section.
Pre-invocation validation scans for all 8 sections.
Error: "MISSING: Mandatory section 'TIMEOUT_INSTRUCTION' not found"
Task invocation is BLOCKED.
Orchestrator can fix the template.

#### Acceptance Criteria

- [ ] AC-002.1: All 8 mandatory sections must be present for validation to pass
- [ ] AC-002.2: All 14 TDD phases must be explicitly mentioned
- [ ] AC-002.3: Validation errors are specific and actionable (name the missing element)
- [ ] AC-002.4: Task tool is NOT invoked if validation fails
- [ ] AC-002.5: Validation completes in < 500ms

---

### US-003: Post-Execution State Validation

**As** Marcus (Senior Developer),
**I want** DES to automatically detect when phases are left abandoned (IN_PROGRESS) after sub-agent completion,
**So that** I'm immediately alerted to incomplete work instead of discovering it hours later.

**Story Points:** 8
**Priority:** P0 (Must Have)

#### Problem (The Pain)
Marcus ran `/nw:execute` yesterday. The agent appeared to finish but actually crashed during GREEN_UNIT phase. The step file shows GREEN_UNIT as "IN_PROGRESS" - meaning it was started but never completed. Marcus didn't notice until today when tests started failing. He spent 2 hours debugging.

#### Who (The User)
- Senior developer executing step workflows
- Expects reliable completion or clear failure notification
- Cannot afford to discover abandoned work hours later

#### Solution (What We Build)
SubagentStop hook that validates step file state after every sub-agent completion. Detects abandoned IN_PROGRESS phases, DONE tasks with NOT_EXECUTED phases, and EXECUTED phases without outcomes.

#### Domain Examples

**Example 1: Abandoned Phase Detected**
Software-crafter agent was working on step 01-01.
Agent crashed during GREEN_UNIT phase (status: IN_PROGRESS).
SubagentStop hook fires.
Hook reads step file, finds GREEN_UNIT with status "IN_PROGRESS".
Error logged: "Phase GREEN_UNIT left IN_PROGRESS (abandoned)"
Step file state set to FAILED with recovery suggestions.
Marcus is notified immediately.

**Example 2: Silent Completion Detected**
Software-crafter agent returned without updating step file.
All phases still show "NOT_EXECUTED".
Task status shows "IN_PROGRESS".
SubagentStop hook detects mismatch.
Error: "Agent completed without updating step file"
Recovery suggestions provided.

**Example 3: Clean Completion Passes**
Software-crafter agent completes all 14 phases.
Each phase shows "EXECUTED" with outcome.
Step file status is "DONE".
SubagentStop hook validates successfully.
Audit log records successful completion.

#### Acceptance Criteria

- [ ] AC-003.1: SubagentStop hook fires for every sub-agent completion
- [ ] AC-003.2: Phases with status "IN_PROGRESS" after completion are flagged as abandoned
- [ ] AC-003.3: Tasks marked "DONE" with "NOT_EXECUTED" phases are flagged as invalid
- [ ] AC-003.4: "EXECUTED" phases without outcome field are flagged as incomplete
- [ ] AC-003.5: "SKIPPED" phases must have valid `blocked_by` reason
- [ ] AC-003.6: Validation errors trigger FAILED state with recovery suggestions

---

### US-004: Audit Trail for Compliance Verification

**As** Priya (Tech Lead),
**I want** DES to maintain a complete audit trail of all state transitions,
**So that** I can verify TDD compliance during PR review with concrete evidence.

**Story Points:** 3
**Priority:** P0 (Must Have)

#### Problem (The Pain)
Priya reviews a PR that claims full TDD compliance. The step file shows "DONE" for all phases, but she has no way to verify the order of execution, timestamps, or whether phases were actually run versus just marked complete. She must take the developer's word for it.

#### Who (The User)
- Tech Lead who approves PRs
- Needs verifiable evidence of process compliance
- Cannot rely on trust alone for quality assurance

#### Solution (What We Build)
Append-only daily audit logs (`audit-YYYY-MM-DD.log`) that record every state transition with timestamp, event type, and relevant data. Daily rotation prevents single files from growing too large. Immutable logs that cannot be retroactively modified.

#### Domain Examples

**Example 1: Complete Execution Audit**
Marcus runs `/nw:execute @software-crafter "steps/01-01.json"` on 2026-01-22.
Audit log `audit-2026-01-22.log` captures: TASK_INVOCATION_STARTED, TASK_INVOCATION_VALIDATED.
For each phase: PHASE_STARTED, PHASE_COMPLETED (with outcome).
Finally: SUBAGENT_STOP_VALIDATION (success), COMMIT_VALIDATION_PASSED.
Priya reviews daily audit log and sees complete execution history with timestamps.

**Example 2: Failed Validation Audit**
Marcus runs `/nw:execute` with incomplete prompt.
Audit log captures: TASK_INVOCATION_STARTED, TASK_INVOCATION_REJECTED (with specific errors).
Priya can see exactly why the execution was blocked.

**Example 3: Crash Recovery Audit**
Marcus's session crashes during execution.
Audit log shows: PHASE_STARTED for RED_UNIT, no PHASE_COMPLETED.
Later: SUBAGENT_STOP_VALIDATION (error: abandoned phase).
Priya can see exactly where execution stopped.

#### Acceptance Criteria

- [ ] AC-004.1: All state transitions are logged with ISO timestamp
- [ ] AC-004.2: Audit log is append-only (no modifications to existing entries)
- [ ] AC-004.3: Event types include: TASK_INVOCATION_*, PHASE_*, SUBAGENT_STOP_*, COMMIT_*
- [ ] AC-004.4: Each entry includes step file path and relevant event data
- [ ] AC-004.5: Audit log is human-readable (JSONL format)
- [ ] AC-004.6: Audit logs rotate daily (`audit-YYYY-MM-DD.log` naming convention)

---

### US-005: Failure Recovery Guidance

**As** Alex (Junior Developer),
**I want** DES to provide clear recovery guidance when execution fails,
**So that** I know exactly what to do instead of being stuck with a cryptic error.

**Story Points:** 5
**Priority:** P1 (Should Have)

#### Problem (The Pain)
Alex ran `/nw:execute` and got an error: "Phase GREEN_UNIT left IN_PROGRESS (abandoned)". He doesn't know what this means or what to do. He's afraid to modify the step file manually because he might break something. He spends 30 minutes searching documentation before asking for help.

#### Who (The User)
- Junior developer learning TDD methodology
- Needs explicit guidance, not just error messages
- Benefits from educational context

#### Solution (What We Build)
Recovery suggestions embedded in step file on failure. Each failure mode has a documented recovery procedure that is automatically provided. Suggestions are actionable and specific.

#### Domain Examples

**Example 1: Crash Recovery Guidance**
Alex's agent crashed during GREEN_UNIT.
Step file updated with:
```json
{
  "state": {
    "status": "FAILED",
    "failure_reason": "Agent crashed during GREEN_UNIT phase",
    "recovery_suggestions": [
      "Review agent transcript for error details",
      "Reset GREEN_UNIT phase status to NOT_EXECUTED",
      "Run `/nw:execute` again to resume from GREEN_UNIT"
    ]
  }
}
```
Alex follows suggestions step by step.

**Example 2: Validation Failure Guidance**
Alex's orchestrator produced incomplete prompt.
Error message: "MISSING: Mandatory section 'TDD_14_PHASES' not found"
Recovery suggestion: "Update the prompt template to include TDD_14_PHASES section with all 14 phases enumerated."
Alex knows exactly what to fix.

**Example 3: Silent Completion Guidance**
Agent returned without updating state.
Recovery suggestions:
- "Check agent transcript at {path} for errors"
- "Verify prompt contained OUTCOME_RECORDING instructions"
- "Manually update phase status based on transcript evidence"
Alex has a clear debugging path.

#### Acceptance Criteria

- [ ] AC-005.1: Every failure mode has associated recovery suggestions
- [ ] AC-005.2: Suggestions are stored in step file `recovery_suggestions` array
- [ ] AC-005.3: Suggestions are actionable (specific commands or file paths)
- [ ] AC-005.4: Validation errors include fix guidance in error message
- [ ] AC-005.5: Recovery suggestions include explanatory text (minimum 1 sentence) describing WHY the error occurred and HOW the fix resolves it

---

### US-006: Turn Discipline Without max_turns

**As** Marcus (Senior Developer),
**I want** DES to include turn discipline instructions in every prompt,
**So that** agents self-regulate their execution time even though max_turns is unavailable.

**Story Points:** 3
**Priority:** P0 (Must Have)

#### Problem (The Pain)
Marcus discovered that Task tool doesn't accept max_turns parameter (it's CLI-only). Without a turn limit, an agent could loop indefinitely trying to fix an unfixable issue. Marcus needs a mechanism to prevent runaway execution.

#### Who (The User)
- Senior developer who understands the technical constraint
- Needs reliable timeout mechanism
- Accepts prompt-based discipline as workaround

#### Solution (What We Build)
TIMEOUT_INSTRUCTION section in every DES-validated prompt. Includes turn budget guidance, progress checkpoints, and early exit protocol. External watchdog as backup detection.

#### Domain Examples

**Example 1: Agent Self-Regulates**
Software-crafter agent receives prompt with TIMEOUT_INSTRUCTION.
Instruction: "Aim to complete within 50 turns. If stuck, save progress and return."
Agent reaches turn 40 and realizes it's stuck on a failing test.
Agent saves partial progress, sets phase to IN_PROGRESS with notes.
Agent returns with status "PARTIAL_COMPLETION".
Marcus can review and provide guidance.

**Example 2: Watchdog Detects Stale Execution**
Marcus's agent has been running for 45 minutes on a step that should take 15.
External watchdog checks for stale IN_PROGRESS phases.
Watchdog finds step 01-01 with RED_UNIT IN_PROGRESS for 45 minutes.
Alert: "Possible stuck execution detected"
Marcus is notified and can intervene.

**Example 3: Progress Checkpoints Observed**
Agent follows checkpoint guidance:
- Turn 10: PREPARE and RED phases complete (on track)
- Turn 25: GREEN phases complete (on track)
- Turn 40: REFACTOR phases complete (on track)
- Turn 48: COMMIT phase starting (finishing on time)

#### Acceptance Criteria

- [ ] AC-006.1: All DES-validated prompts include TIMEOUT_INSTRUCTION section
- [ ] AC-006.2: Turn budget (approximately 50) is specified in instructions
- [ ] AC-006.3: Progress checkpoints are defined (turn ~10, ~25, ~40, ~50)
- [ ] AC-006.4: Early exit protocol is documented in prompt
- [ ] AC-006.5: Prompt instructs agent to log turn count at each phase transition

---

### US-007: Boundary Rules for Scope Enforcement

**As** Priya (Tech Lead),
**I want** DES to include explicit boundary rules in prompts,
**So that** agents cannot accidentally expand scope beyond the assigned step.

**Story Points:** 2
**Priority:** P1 (Should Have)

#### Problem (The Pain)
Priya reviewed a PR where the agent was supposed to implement one small feature but ended up refactoring three other files "while it was there." This scope creep caused merge conflicts and delayed the release.

#### Who (The User)
- Tech Lead responsible for controlled changes
- Needs predictable, scoped modifications
- Values discipline over "helpful" overreach

#### Solution (What We Build)
BOUNDARY_RULES section in prompts that explicitly defines ALLOWED and FORBIDDEN actions. Clear scope limitation to the assigned step only.

#### Domain Examples

**Example 1: Agent Stays In Scope**
Software-crafter working on step 01-01 for UserRepository.
BOUNDARY_RULES specify: Only modify files matching `**/UserRepository*`
Agent sees opportunity to "improve" AuthService while working.
Agent respects boundary: Does not modify AuthService.
Only UserRepository files are changed.

**Example 2: Scope Violation Detected**
Agent modified OrderService.py while working on UserRepository step.
SubagentStop hook runs scope validation.
Git diff shows changes outside allowed patterns.
Warning: "Unexpected modification: src/services/OrderService.py"
Priya is alerted to scope creep.

**Example 3: Clear Completion Boundary**
Agent completes step 01-01 successfully.
Agent could continue to step 01-02 "for efficiency."
BOUNDARY_RULES: "Return control IMMEDIATELY after step completion."
Agent returns with execution summary.
Marcus explicitly starts next step when ready.

#### Acceptance Criteria

- [ ] AC-007.1: BOUNDARY_RULES section included in all step execution prompts
- [ ] AC-007.2: ALLOWED actions explicitly enumerated (step file, task files, tests)
- [ ] AC-007.3: FORBIDDEN actions explicitly enumerated (other steps, other files)
- [ ] AC-007.4: Scope validation runs post-execution (compare git diff to allowed patterns)
- [ ] AC-007.5: Scope violations logged as warnings in audit trail

---

### US-008: Session-Scoped Stale Execution Detection

**As** Priya (Tech Lead),
**I want** DES to detect stale executions during my work session,
**So that** stuck agents are caught early without requiring external daemons or databases.

**Story Points:** 2
**Priority:** P1 (Should Have)

#### Problem (The Pain)
Sometimes agents get stuck despite prompt-based turn discipline (network issues, model errors, infinite loops). Without detection, Marcus might start new work while a previous execution is still "in progress" (actually abandoned).

#### Who (The User)
- Tech Lead responsible for system reliability
- Wants lightweight, zero-dependency solution
- Prefers session-scoped checks over persistent daemons

#### Solution (What We Build)
Session-scoped stale execution check that:
1. Runs automatically **before** each `/nw:execute` command
2. Scans step files for abandoned IN_PROGRESS phases older than threshold
3. Alerts user and blocks execution if stale work found
4. **Terminates with the session** - no persistent daemon required

No databases, no external services, no installation required. Pure file scanning.

#### Domain Examples

**Example 1: Pre-Execution Stale Check**
Marcus runs `/nw:execute @software-crafter "steps/02-01.json"`.
Before starting, DES scans for stale executions.
Finds step 01-01 with RED_UNIT IN_PROGRESS since 45 min ago (abandoned from previous session).
Alert: "Stale execution found: step 01-01.json, phase RED_UNIT (45 min). Resolve before proceeding."
Marcus must address the stale step before starting new work.

**Example 2: Clean Start**
Marcus runs `/nw:execute @software-crafter "steps/01-01.json"`.
Pre-execution scan finds no stale IN_PROGRESS phases.
Execution proceeds normally.
No daemon running in background - check completes and control returns.

**Example 3: Resolve and Continue**
Marcus resolves stale step 01-01 (marks as ABANDONED with recovery suggestions).
Runs `/nw:execute` again.
Pre-execution scan passes - no stale phases found.
New execution starts on step 02-01.

#### Acceptance Criteria

- [ ] AC-008.1: Stale check runs automatically before each `/nw:execute` invocation
- [ ] AC-008.2: Stale threshold is configurable (default 30 minutes, env var or config)
- [ ] AC-008.3: Detection blocks execution with clear alert (step file, phase, age)
- [ ] AC-008.4: User can resolve stale step (mark ABANDONED) to unblock
- [ ] AC-008.5: No external dependencies - pure file scanning, session-scoped

---

### US-009: Learning Feedback for TDD Phase Execution

**As** Alex (Junior Developer),
**I want** DES to provide educational feedback during phase execution,
**So that** I learn proper TDD methodology while getting work done.

**Story Points:** 3
**Priority:** P1 (Should Have)

#### Problem (The Pain)
Alex is learning TDD but often doesn't understand WHY phases are executed in a certain order or WHAT makes a good phase outcome. He completes steps but doesn't internalize the methodology. When something goes wrong, he doesn't have the context to understand the failure.

#### Who (The User)
- Junior developer learning TDD
- Benefits from contextual explanations
- Needs to understand "why" not just "what"

#### Solution (What We Build)
Educational annotations in phase execution log that explain the purpose of each phase and common mistakes to avoid. Learning mode that adds more verbose explanations.

#### Domain Examples

**Example 1: Phase Purpose Explanation**
Alex reviews step file after execution.
Each phase has an "educational_note" field:
```json
{
  "phase_name": "RED_ACCEPTANCE",
  "educational_note": "This phase verifies the acceptance test FAILS before implementation. A failing test proves we're testing real business logic, not infrastructure. If the test passes here, it means either the feature already exists or the test is broken."
}
```

**Example 2: Common Mistake Warning**
Alex's RED_UNIT phase passes immediately (bad sign).
Warning added: "Test passed immediately - this usually means the test isn't actually testing new behavior. Common causes: testing existing functionality, assertion too weak, or wrong test target."
Alex learns to recognize this pattern.

**Example 3: Success Pattern Explanation**
Alex completes GREEN_UNIT successfully.
Note: "Good work! The test now passes with minimal implementation. This is the 'simplest thing that could possibly work' - resist the urge to add extra features here. Those belong in refactoring phases."

#### Acceptance Criteria

- [ ] AC-009.1: Each of 14 TDD phases has an educational_note explaining its purpose
- [ ] AC-009.2: Common mistake patterns are detected and warnings provided
- [ ] AC-009.3: Success patterns are recognized with positive reinforcement
- [ ] AC-009.4: Learning mode can be enabled/disabled per execution
- [ ] AC-009.5: Educational content uses business language, not just technical jargon

---

### Infrastructure Configuration User Stories

### US-INF-001: Database Schema Migration Without Tests

**As** Marcus (Senior Developer),
**I want** to apply database schema migrations using configuration_setup workflow,
**So that** I don't waste time writing acceptance tests for one-time schema changes.

**Story Points:** 3
**Priority:** P1 (Should Have)

#### Problem (The Pain)

Marcus needs to add a new column to the `users` table. This is a one-time infrastructure change, not a feature. Writing full TDD cycle with acceptance tests and 14 phases is overkill for schema migrations that won't have test coverage.

#### Who (The User)

- Senior developer executing database migrations
- Understands SQL and schema versioning
- Values efficiency for infrastructure tasks

#### Solution (What We Build)

Configuration setup workflow that validates database migrations on test databases before production, documents rollback procedures, and provides verification without requiring acceptance test scaffolding.

#### Domain Examples

**Example 1: Add Timestamp Column**
```sql
-- Migration
ALTER TABLE users ADD COLUMN last_login_at TIMESTAMP DEFAULT NULL;

-- Rollback
ALTER TABLE users DROP COLUMN last_login_at;
```
- **Verification**: `SELECT last_login_at FROM users LIMIT 1` returns NULL (column exists)
- **Safety**: Non-destructive (adding column with default NULL)

**Example 2: Add Index for Performance**
```sql
-- Migration
CREATE INDEX idx_orders_customer_id ON orders(customer_id);

-- Rollback
DROP INDEX idx_orders_customer_id;
```
- **Verification**: `EXPLAIN SELECT * FROM orders WHERE customer_id = 123` shows index usage
- **Safety**: Non-destructive (index creation)

**Example 3: Alter Column Type (Destructive)**
```sql
-- Migration
ALTER TABLE products ALTER COLUMN price TYPE DECIMAL(10,2);

-- Rollback
ALTER TABLE products ALTER COLUMN price TYPE INTEGER;
```
- **Verification**: `SELECT price FROM products WHERE id = 1` returns decimal (e.g., 19.99)
- **Safety**: DESTRUCTIVE (data loss if rollback - pennies truncated)

#### Acceptance Criteria

- [ ] AC-INF-001.1: VALIDATE phase runs migration against TEST database only (not production)
- [ ] AC-INF-001.2: Verification query confirms schema change applied successfully
- [ ] AC-INF-001.3: Step file includes verification evidence (query output screenshot or log)
- [ ] AC-INF-001.4: Documentation includes migration SQL, rollback SQL, business reason, and impact analysis
- [ ] AC-INF-001.5: Production migration flagged as manual step (DBA applies separately)
- [ ] AC-INF-001.6: Safety classification documented (is_destructive, rollback_plan, affects_production)

---

### US-INF-002: Environment Variable Configuration

**As** Priya (Tech Lead),
**I want** to configure environment variables using configuration_setup workflow,
**So that** deployment prerequisites are documented and verified systematically.

**Story Points:** 2
**Priority:** P1 (Should Have)

#### Problem (The Pain)

Multiple services need `.env` files with API keys, database URLs, and feature flags. Current setup is manual and error-prone. No verification that values are in correct format. Developers forget steps, leading to runtime failures.

#### Who (The User)

- Tech Lead responsible for environment consistency
- Manages multiple environments (dev, staging, prod)
- Needs audit trail for configuration changes

#### Solution (What We Build)

Configuration setup workflow that validates environment variable formats (regex), tests functional connectivity (database connections, API calls), redacts sensitive values from logs, and documents variable purposes.

#### Domain Examples

**Example 1: Database URL Configuration**
```bash
# .env
DATABASE_URL=postgresql://user:password@localhost:5432/mydb

# Verification
echo $DATABASE_URL | grep -E '^postgresql://[^:]+:[^@]+@[^:]+:[0-9]+/[^/]+$'
```
- **Format validation**: Regex checks protocol, user, password, host, port, database
- **Safety**: Non-destructive (setting environment variable)

**Example 2: Stripe API Key with Format Validation**
```bash
# .env
API_KEY_STRIPE=sk_test_51Abc...

# Verification
if [[ $API_KEY_STRIPE =~ ^sk_(test|live)_ ]]; then
  echo "Valid Stripe key format"
  # API call to verify key works
  curl -u "$API_KEY_STRIPE:" https://api.stripe.com/v1/balance
else
  echo "Invalid Stripe key format"
  exit 1
fi
```
- **Format validation**: Starts with sk_test_ or sk_live_
- **Functional validation**: API call returns 200 OK
- **Safety**: Non-destructive, but sensitive (key not logged)

**Example 3: Feature Flag with Boolean Validation**
```bash
# .env
FEATURE_FLAG_NEW_CHECKOUT=true

# Verification
if [[ "$FEATURE_FLAG_NEW_CHECKOUT" =~ ^(true|false)$ ]]; then
  echo "Valid boolean flag"
else
  echo "Invalid value - must be 'true' or 'false'"
  exit 1
fi
```
- **Format validation**: Only "true" or "false" allowed
- **Safety**: Non-destructive

#### Acceptance Criteria

- [ ] AC-INF-002.1: VALIDATE phase checks environment variable format using regex validation
- [ ] AC-INF-002.2: Functional verification tests connectivity (database connection, API call success)
- [ ] AC-INF-002.3: Step file includes verification evidence (connection success log, API response)
- [ ] AC-INF-002.4: Sensitive values NOT logged - audit log shows "[REDACTED]" for API keys and passwords
- [ ] AC-INF-002.5: Documentation explains purpose of each variable, acceptable formats, and how to obtain sensitive values
- [ ] AC-INF-002.6: Environment-specific variations documented (dev vs staging vs prod differences)

---

### US-INF-003: Third-Party Service Provisioning

**As** Alex (Junior Developer),
**I want** to provision third-party services (Auth0, Stripe, SendGrid) using configuration_setup workflow,
**So that** I follow a consistent process with verification instead of ad-hoc manual setup.

**Story Points:** 5
**Priority:** P2 (Could Have)

#### Problem (The Pain)

Alex needs to create a Stripe test account, configure webhooks, and generate API keys. He's done this before but always forgets steps (e.g., setting correct webhook URL, restricting key permissions). No checklist or verification. Leads to runtime errors when webhooks fail.

#### Who (The User)

- Junior developer setting up development environment
- Needs explicit step-by-step guidance
- Benefits from automated verification

#### Solution (What We Build)

Configuration setup workflow that provides interactive checklists for manual provisioning steps, runs verification scripts to confirm service configuration, and stores credentials securely with documented locations.

#### Domain Examples

**Example 1: Create Stripe Test Account**
```bash
# Manual steps (EXECUTE phase checklist):
1. Go to https://dashboard.stripe.com/register
2. Sign up with team email (team+stripe-test@example.com)
3. Skip business verification (test mode)
4. Copy Account ID from dashboard

# Verification (VALIDATE phase):
curl https://api.stripe.com/v1/account \
  -u sk_test_...: \
  | jq -r '.id' \
  | grep '^acct_test_'

# Expected: Account ID starts with "acct_test_" (confirms test mode)
```
- **Verification**: API call confirms account exists and is test account
- **Safety**: Non-destructive (creating test account, not production)

**Example 2: Configure Stripe Webhook**
```bash
# Manual steps (EXECUTE phase checklist):
1. Navigate to Developers → Webhooks in Stripe Dashboard
2. Click "Add endpoint"
3. Enter URL: https://api.example.com/webhooks/stripe
4. Select events: charge.succeeded, charge.failed
5. Copy webhook signing secret (whsec_...)

# Verification (VALIDATE phase):
curl -X POST https://api.example.com/webhooks/stripe \
  -H "Content-Type: application/json" \
  -d '{"type": "ping"}' \
  | grep '200 OK'

# Expected: Webhook endpoint returns 200 OK
```
- **Verification**: POST request to webhook URL returns 200 (endpoint accessible)
- **Safety**: Non-destructive (configuring webhook, not production)

**Example 3: Generate Restricted Stripe API Key**
```bash
# Manual steps (EXECUTE phase checklist):
1. Navigate to Developers → API keys in Stripe Dashboard
2. Click "Create restricted key"
3. Name: "Test Environment - Charge Write Only"
4. Permissions: Write access to Charges only (no refunds, no customers)
5. Copy restricted key (rk_test_...)

# Verification (VALIDATE phase):
# Test 1: Verify key has charge:write permission
curl https://api.stripe.com/v1/charges \
  -u rk_test_...: \
  -X POST -d "amount=100" -d "currency=usd" -d "source=tok_visa" \
  | jq -r '.id' \
  | grep '^ch_'

# Expected: Charge created (key has write permission)

# Test 2: Verify key LACKS refund permission
curl https://api.stripe.com/v1/refunds \
  -u rk_test_...: \
  -X POST -d "charge=ch_..." \
  | grep 'Invalid API Key'

# Expected: API returns error (key correctly restricted)
```
- **Verification**: API calls confirm permissions (charge works, refund blocked)
- **Safety**: Non-destructive (test key with restricted permissions)

#### Acceptance Criteria

- [ ] AC-INF-003.1: EXECUTE phase provides step-by-step checklist with expected outcomes for each step
- [ ] AC-INF-003.2: Checklist includes screenshot references where helpful
- [ ] AC-INF-003.3: VALIDATE phase makes API calls to verify provisioning (account ID format, webhook endpoint, key permissions)
- [ ] AC-INF-003.4: Step file includes verification evidence (API responses showing successful verification)
- [ ] AC-INF-003.5: DOCUMENT phase captures credentials location (1Password vault path, not actual secrets)
- [ ] AC-INF-003.6: Rollback procedure documented (delete webhook, revoke API key, close test account)
- [ ] AC-INF-003.7: Verification includes negative tests (confirm key LACKS unwanted permissions)

---

## Story Dependencies

```
US-001 (Command Filtering) ─────┐
                                ├──► US-002 (Pre-Invocation Validation)
US-006 (Turn Discipline) ───────┘
        │
        ▼
US-003 (Post-Execution Validation)
        │
        ├──► US-004 (Audit Trail)
        │
        ├──► US-005 (Failure Recovery)
        │
        └──► US-007 (Boundary Rules)  ← depends on US-003, not US-005
              │
              ▼
        US-008 (External Watchdog)  ← NEW: separated from US-006
```

---

## Implementation Priority

### Sprint 1: Foundation (P0)
- US-001: Command-Origin Task Filtering
- US-002: Pre-Invocation Template Validation
- US-006: Turn Discipline

### Sprint 2: Validation (P0)
- US-003: Post-Execution State Validation
- US-004: Audit Trail

### Sprint 3: Polish (P1)
- US-005: Failure Recovery Guidance
- US-007: Boundary Rules
- US-008: External Watchdog
- US-009: Learning Feedback

---

*User stories created by Riley (product-owner) during DISCUSS wave.*

---

## Product Owner Review

**Reviewer**: product-owner-reviewer (Sage)
**Date**: 2026-01-22
**Overall Assessment**: APPROVED_WITH_REVISIONS

### INVEST Compliance Matrix

| Story | I | N | V | E | S | T | Status |
|-------|---|---|---|---|---|---|--------|
| US-001 | Y | Y | Y | Y | Y | Y | PASS |
| US-002 | ~ | Y | Y | Y | Y | Y | PASS |
| US-003 | ~ | Y | Y | Y | ~ | Y | REVIEW |
| US-004 | ~ | Y | Y | Y | Y | Y | PASS |
| US-005 | ~ | Y | Y | Y | Y | ~ | REVIEW |
| US-006 | Y | Y | Y | Y | Y | ~ | REVIEW |
| US-007 | ~ | Y | Y | Y | Y | Y | PASS |

**Legend**: Y = Yes, ~ = Partial/Conditional

### Critiques

| # | Story | Issue | Severity | Recommendation |
|---|-------|-------|----------|----------------|
| 1 | US-006 | AC-006.5 (External Watchdog) introduces a separate feature outside story scope. Story focuses on "prompt-based discipline" but AC adds monitoring system. | HIGH | Extract AC-006.5 into separate story "US-008: Stale Execution Watchdog" with its own acceptance criteria, examples, and story points. |
| 2 | All | Alex persona underrepresented - only 1/7 stories (US-005) addresses junior developer learning needs. | HIGH | Add learning-focused AC to existing stories OR create new story "US-009: Learning Feedback for Phase Execution" targeting Alex. |
| 3 | US-003 | 8 story points and 6 AC suggest story may be too large. Combines state validation AND recovery triggering. | MEDIUM | Consider splitting into US-003a "Post-Execution State Detection" (AC 1-4) and US-003b "Recovery State Management" (AC 5-6). |
| 4 | Deps | Dependency diagram shows US-007 depending on US-005, but Boundary Rules do not logically require Failure Recovery Guidance. | MEDIUM | Correct dependency: US-007 depends on US-003 (needs validation hooks for scope checking), not US-005. |
| 5 | US-005 | AC-005.5 "Educational context provided for junior developers" is not measurable or testable. | MEDIUM | Revise to: "AC-005.5: Recovery suggestions include explanatory text (minimum 1 sentence) describing WHY the error occurred and HOW the fix resolves it." |
| 6 | US-003,004 | Technical jargon ("SubagentStop hook", "JSONL", "append-only") may confuse Alex persona without explanation. | MEDIUM | Add glossary section OR inline explanations in story descriptions. |
| 7 | US-001 | Example 3 references "validation-required list" but no AC explicitly defines this registry mechanism. | LOW | Add AC-001.5: "A configuration file defines which nWave commands require DES validation (whitelist approach)." |

### Strengths

- **Excellent domain examples**: All stories use concrete scenarios with named personas (Marcus, Priya, Alex) and realistic situations
- **Clear problem statements**: Each story articulates specific user pain that justifies the solution
- **Well-calibrated story points**: Estimates are reasonable and differentiated appropriately (2-8 range)
- **Good acceptance criteria format**: Most AC are specific, actionable, and verifiable
- **Sprint planning alignment**: P0/P1 prioritization with logical sprint groupings
- **Dependency diagram provided**: Visual representation aids understanding
- **Consistent template**: All stories follow identical structure

### Gaps

1. **Alex persona coverage**: Junior developer learning needs are only addressed in US-005. Consider:
   - Adding learning-focused AC to US-003 (explain validation errors educationally)
   - Creating dedicated "onboarding guidance" story for Alex

2. **Explicit happy path AC**: Some stories focus on error detection but don't explicitly verify normal operation. For example:
   - US-003 should include AC for "clean completion passes validation silently"
   - US-007 should include AC for "in-scope modifications are not flagged"

3. **Watchdog as separate feature**: US-006's external watchdog deserves dedicated story with:
   - Its own problem statement (separate from prompt discipline)
   - Acceptance criteria for detection thresholds, alerting mechanisms
   - Integration examples with monitoring systems

4. **Glossary or technical term definitions**: No explanation of hooks, JSONL format, or other technical concepts for non-technical personas

### Recommendation

**Status**: APPROVED_WITH_REVISIONS

The user stories provide a solid foundation for DES implementation. The three HIGH/MEDIUM issues require attention before DESIGN wave handoff:

**Required Actions (must address):**
1. Extract US-006 AC-006.5 into separate US-008 story (HIGH)
2. Address Alex persona underrepresentation - add learning AC or new story (HIGH)

**Recommended Actions (should address):**
3. Consider splitting US-003 into two smaller stories (MEDIUM)
4. Correct dependency diagram: US-007 depends on US-003, not US-005 (MEDIUM)
5. Make AC-005.5 measurable with specific criteria (MEDIUM)

**Optional Improvements:**
6. Add technical glossary for non-developer personas (MEDIUM)
7. Add AC-001.5 for command whitelist configuration (LOW)

Once required actions are addressed, stories are ready for DESIGN wave handoff to solution-architect.
