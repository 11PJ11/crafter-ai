"""
E2E Acceptance Tests: US-007 Boundary Rules for Scope Enforcement

PERSONA: Priya (Tech Lead)
STORY: As a tech lead, I want DES to include explicit boundary rules in prompts,
       so that agents cannot accidentally expand scope beyond the assigned step.

PROBLEM: Priya reviewed a PR where the agent was supposed to implement one small
         feature but ended up refactoring three other files "while it was there."
         This scope creep caused merge conflicts and delayed the release.

SOLUTION: BOUNDARY_RULES section in prompts that explicitly defines ALLOWED and
          FORBIDDEN actions. Clear scope limitation to the assigned step only.
          Post-execution scope validation comparing git diff to allowed patterns.

BUSINESS VALUE:
- Prevents scope creep that causes merge conflicts and release delays
- Ensures predictable, controlled modifications
- Provides audit trail of scope violations for PR review
- Allows Priya to catch unauthorized file changes before they cause problems

SOURCE:
- docs/feature/des/discuss/user-stories.md (US-007)
- Acceptance Criteria AC-007.1 through AC-007.5

WAVE: DISTILL (Acceptance Test Creation)
STATUS: RED (Outside-In TDD - awaiting DEVELOP wave implementation)

TEST ARCHITECTURE PRINCIPLES:
- These tests validate FEATURE BEHAVIOR, not DES execution mechanics
- Acceptance tests define the CONTRACT (what the system does)
- DES workflow mechanics are IMPLEMENTATION DETAILS (how we build it)
- Tests should NOT break when we optimize DES workflow internals
- Focus: Prompt rendering, boundary rules functionality, business logic
- Avoid: Step file assertions, execution-status tracking, DES state management
"""

import pytest


class TestBoundaryRulesInclusion:
    """
    E2E acceptance tests for BOUNDARY_RULES section inclusion in prompts.

    Validates that all step execution prompts contain explicit boundary rules
    defining what agents are ALLOWED and FORBIDDEN to do.
    """

    # =========================================================================
    # AC-007.1: BOUNDARY_RULES section included in all step execution prompts
    # Scenario 1: Step execution prompt includes BOUNDARY_RULES section
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_001_step_execution_prompt_includes_boundary_rules_section(
        self, tmp_project_root, des_orchestrator
    ):
        """
        GIVEN /nw:execute command invoked with scope for UserRepository
        WHEN orchestrator renders the full Task prompt
        THEN prompt contains BOUNDARY_RULES section header

        Business Context:
        Priya needs assurance that every agent receives explicit scope
        limitations. Without BOUNDARY_RULES, agents might "helpfully"
        modify unrelated files, causing merge conflicts.

        Domain Example:
        Software-crafter working on UserRepository receives prompt with
        BOUNDARY_RULES section defining what files it can touch.

        TEST ARCHITECTURE:
        - NO step file references (DES internal)
        - Pass scope directly to orchestrator
        - Focus on BOUNDARY_RULES presence in prompt
        """
        # GIVEN: /nw:execute command with scope
        command = "/nw:execute"
        agent = "@software-crafter"
        scope = {"allowed_patterns": ["**/UserRepository*"]}

        # WHEN: Orchestrator renders full Task prompt
        # NOTE: This will fail until DEVELOP wave implements full prompt rendering
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent=agent,
            scope=scope,
            project_root=tmp_project_root,
        )

        # THEN: Prompt contains BOUNDARY_RULES section
        assert (
            "BOUNDARY_RULES" in prompt
        ), "BOUNDARY_RULES section missing - agents cannot know their scope limitations"

        # Verify section is properly formatted with header marker
        assert (
            "## BOUNDARY_RULES" in prompt or "# BOUNDARY_RULES" in prompt
        ), "BOUNDARY_RULES must be a proper section header (## or #)"


class TestAllowedActionEnumeration:
    """
    E2E acceptance tests for ALLOWED action enumeration in BOUNDARY_RULES.

    Validates that ALLOWED actions are explicitly listed so agents know
    exactly which files and operations are permitted.
    """

    # =========================================================================
    # AC-007.2: ALLOWED actions explicitly enumerated (step file, task files, tests)
    # Scenario 2: ALLOWED section specifies permitted files
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_002_boundary_rules_enumerate_allowed_actions(
        self, tmp_project_root, des_orchestrator
    ):
        """
        GIVEN /nw:execute command for step targeting UserRepository
        WHEN orchestrator renders the full Task prompt
        THEN BOUNDARY_RULES section explicitly lists ALLOWED files/patterns

        Business Context:
        Agents need an explicit whitelist of permitted modifications.
        This includes task implementation files and test files matching
        the feature being implemented.

        Domain Example:
        ALLOWED section contains:
        - Task files: **/UserRepository*
        - Test files: **/test_user_repository*

        Without explicit ALLOWED list, agents might assume they can
        modify anything, leading to scope creep.

        TEST ARCHITECTURE:
        - NO assertions on step file existence/structure (DES internal)
        - Focus on BOUNDARY_RULES content in rendered prompt
        """
        # GIVEN: /nw:execute command with scope targeting UserRepository
        scope = {
            "target_files": ["src/repositories/UserRepository.py"],
            "test_files": ["tests/unit/test_user_repository.py"],
            "allowed_patterns": ["**/UserRepository*", "**/test_user_repository*"],
        }

        # WHEN: Orchestrator renders full Task prompt
        prompt = des_orchestrator.render_full_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            scope=scope,
            project_root=tmp_project_root,
        )

        # THEN: ALLOWED section present with file patterns
        assert "ALLOWED" in prompt, "ALLOWED section missing from BOUNDARY_RULES"

        # Verify target files are specified (could be patterns or explicit paths)
        allowed_patterns_found = any(
            pattern in prompt.lower()
            for pattern in [
                "userrepository",
                "user_repository",
                "task file",
                "implementation",
            ]
        )
        assert allowed_patterns_found, (
            "ALLOWED section must specify target files/patterns "
            "(e.g., **/UserRepository* or task implementation files)"
        )

        # Verify test files are permitted
        test_allowed = any(
            pattern in prompt.lower() for pattern in ["test", "spec", "_test", "test_"]
        )
        assert test_allowed, "Test files must be in ALLOWED list for TDD workflow"

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_003_allowed_patterns_match_scope_target_files(
        self, tmp_project_root, des_orchestrator
    ):
        """
        GIVEN scope specifies target files: ["src/repositories/UserRepository.py"]
        WHEN orchestrator renders the full Task prompt
        THEN ALLOWED patterns include the target file paths or matching patterns

        Business Context:
        The ALLOWED patterns should be derived from the scope definition,
        ensuring agents can only modify files relevant to the assigned task.

        Domain Example:
        Step 01-01 targets UserRepository implementation.
        ALLOWED: "src/repositories/UserRepository.py", "tests/unit/test_user_repository.py"

        TEST ARCHITECTURE:
        - NO assertions on step file structure (DES internal)
        - Pass scope directly to orchestrator
        - Focus on prompt content validation
        """
        # GIVEN: Scope with explicit target files
        scope = {
            "target_files": [
                "src/repositories/UserRepository.py",
                "src/repositories/interfaces/IUserRepository.py",
            ],
            "test_files": [
                "tests/unit/test_user_repository.py",
                "tests/integration/test_user_repository_integration.py",
            ],
        }

        # WHEN: Orchestrator renders full Task prompt
        prompt = des_orchestrator.render_full_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            scope=scope,
            project_root=tmp_project_root,
        )

        # THEN: ALLOWED section includes target files or patterns matching them
        assert "UserRepository" in prompt or "user_repository" in prompt.lower(), (
            "ALLOWED patterns must include scope target files. "
            "Expected UserRepository in ALLOWED list."
        )

        # Verify test file patterns included
        assert (
            "test_user_repository" in prompt.lower() or "test" in prompt.lower()
        ), "ALLOWED patterns must include test files from scope."


class TestForbiddenActionEnumeration:
    """
    E2E acceptance tests for FORBIDDEN action enumeration in BOUNDARY_RULES.

    Validates that FORBIDDEN actions are explicitly listed to prevent
    accidental scope expansion.
    """

    # =========================================================================
    # AC-007.3: FORBIDDEN actions explicitly enumerated (other steps, other files)
    # Scenario 4: FORBIDDEN section specifies prohibited actions
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_004_boundary_rules_enumerate_forbidden_actions(
        self, tmp_project_root, des_orchestrator
    ):
        """
        GIVEN /nw:execute command with scope
        WHEN orchestrator renders the full Task prompt
        THEN BOUNDARY_RULES section explicitly lists FORBIDDEN actions

        Business Context:
        Priya saw an agent "improve" AuthService while working on
        UserRepository, causing merge conflicts. Explicit FORBIDDEN
        list prevents such well-intentioned scope creep.

        Domain Example:
        FORBIDDEN section contains:
        - Unrelated source files (AuthService, OrderService, etc.)
        - Configuration files (unless explicitly in scope)
        - Production deployment files

        TEST ARCHITECTURE:
        - NO step file references (eliminated in Phase 1)
        - Pass scope directly to orchestrator
        - Focus on FORBIDDEN section content
        """
        # GIVEN: /nw:execute command with scope
        command = "/nw:execute"
        scope = {"allowed_patterns": ["**/UserRepository*"]}

        # WHEN: Orchestrator renders full Task prompt
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent="@software-crafter",
            scope=scope,
            project_root=tmp_project_root,
        )

        # THEN: FORBIDDEN section present
        assert "FORBIDDEN" in prompt, "FORBIDDEN section missing from BOUNDARY_RULES"

        # Verify unrelated files are forbidden
        unrelated_forbidden = any(
            phrase in prompt.lower()
            for phrase in ["other file", "unrelated", "outside scope", "not in scope"]
        )
        assert (
            unrelated_forbidden
        ), "FORBIDDEN must include reference to files outside scope"

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_005_forbidden_includes_continuation_prohibition(
        self, tmp_project_root, des_orchestrator
    ):
        """
        GIVEN /nw:execute command with scope
        WHEN orchestrator renders the full Task prompt
        THEN FORBIDDEN section includes prohibition against scope expansion

        Business Context:
        After completing assigned work, an agent might think it's "efficient"
        to continue to other tasks. This violates the principle of returning
        control to user for explicit next-task initiation.

        Domain Example:
        FORBIDDEN: "Continue to additional work after completion. Return control
        IMMEDIATELY after task completion. User will explicitly start
        the next task when ready."

        TEST ARCHITECTURE:
        - NO step file references (DES internal)
        - Pass scope directly to orchestrator
        - Focus on return control instruction
        """
        # GIVEN: /nw:execute command with scope
        scope = {"allowed_patterns": ["**/UserRepository*"]}

        # WHEN: Orchestrator renders full Task prompt
        prompt = des_orchestrator.render_full_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            scope=scope,
            project_root=tmp_project_root,
        )

        # THEN: Continuation is forbidden
        continuation_forbidden = any(
            phrase in prompt.lower()
            for phrase in [
                "return control",
                "return immediately",
                "stop after",
                "complete assigned",
            ]
        )
        assert continuation_forbidden, (
            "FORBIDDEN must include prohibition against continuing beyond assigned scope. "
            "Agent must return control after completion, not continue autonomously."
        )


class TestScopeValidationPostExecution:
    """
    E2E acceptance tests for post-execution scope validation.

    Validates that DES checks git diff against allowed patterns after
    agent execution completes.
    """

    # =========================================================================
    # AC-007.4: Scope validation runs post-execution (compare git diff to allowed patterns)
    # Scenario 6: Post-execution scope validation detects out-of-scope changes
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_006_scope_validation_detects_out_of_scope_modification(
        self, tmp_project_root
    ):
        """
        GIVEN agent completed work for UserRepository
        AND agent also modified OrderService.py (out of scope)
        WHEN SubagentStop hook runs post-execution validation
        THEN scope violation is detected for OrderService.py

        Business Context:
        Priya's nightmare scenario: agent "helpfully" improves unrelated
        files. Post-execution scope validation catches this before merge,
        preventing the release delay she experienced.

        Domain Example:
        Agent was working on UserRepository but modified:
        - src/repositories/UserRepository.py (ALLOWED - in scope)
        - src/services/OrderService.py (VIOLATION - out of scope)

        Warning: "Unexpected modification: src/services/OrderService.py"

        TEST ARCHITECTURE:
        - NO step file creation/validation (DES internal)
        - Pass scope directly to validator
        - Focus on scope validation logic
        """
        from src.des.validation import ScopeValidator

        # GIVEN: Scope definition and out-of-scope file modification
        scope = {"allowed_patterns": ["**/UserRepository*", "**/test_user_repository*"]}

        # Simulate agent modifying out-of-scope file
        out_of_scope_file = tmp_project_root / "src" / "services" / "OrderService.py"
        out_of_scope_file.parent.mkdir(parents=True, exist_ok=True)
        out_of_scope_file.write_text("# Modified by agent out of scope")

        # WHEN: Post-execution scope validation runs
        validator = ScopeValidator()
        result = validator.validate_scope(
            scope=scope,
            project_root=tmp_project_root,
            git_diff_files=[
                "src/repositories/UserRepository.py",
                "src/services/OrderService.py",
            ],
        )

        # THEN: Scope violation detected
        assert result.has_violations is True
        assert "src/services/OrderService.py" in result.out_of_scope_files
        assert "OrderService" in result.violation_message
        assert result.violation_severity == "WARNING"

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_007_in_scope_modifications_pass_validation(
        self, tmp_project_root
    ):
        """
        GIVEN agent completed work for UserRepository
        AND agent only modified files matching allowed patterns
        WHEN SubagentStop hook runs post-execution validation
        THEN scope validation passes (no violations)

        Business Context:
        When agents stay within scope, validation should pass silently.
        This is the happy path - Priya sees clean scope adherence
        during PR review.

        Domain Example:
        Agent modified only:
        - src/repositories/UserRepository.py (matches **/UserRepository*)
        - tests/unit/test_user_repository.py (matches **/test_user_repository*)

        Both files match ALLOWED patterns, so validation passes.

        TEST ARCHITECTURE:
        - NO step file assertions (DES internal)
        - Pass scope directly to validator
        - Focus on validation behavior
        """
        from src.des.validation import ScopeValidator

        # GIVEN: Scope definition and in-scope file modifications
        scope = {"allowed_patterns": ["**/UserRepository*", "**/test_user_repository*"]}

        in_scope_files = [
            "src/repositories/UserRepository.py",
            "tests/unit/test_user_repository.py",
        ]

        # WHEN: Post-execution scope validation runs
        validator = ScopeValidator()
        result = validator.validate_scope(
            scope=scope, project_root=tmp_project_root, git_diff_files=in_scope_files
        )

        # THEN: No violations
        assert result.has_violations is False
        assert result.out_of_scope_files == []
        assert result.validation_status == "PASSED"

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_008_DES_internal_files_handled_separately(self, tmp_project_root):
        """
        GIVEN agent completed work
        AND agent modified DES internal tracking files
        WHEN SubagentStop hook runs post-execution validation
        THEN DES internal files are excluded from scope validation

        Business Context:
        DES internal files (execution status, metadata) are managed
        by the DES system itself. Scope validation focuses on
        production code and tests, not DES implementation details.

        Domain Example:
        Agent interacts with DES system, which may update:
        - .des/execution-status.yaml (DES internal)
        - .des/audit/*.log (DES internal)

        These are DES mechanics, not user code, so excluded from validation.

        TEST ARCHITECTURE:
        - NO step file assertions (step files eliminated in Phase 1)
        - Focus on production code scope validation
        - DES internals not part of business contract
        """
        from src.des.validation import ScopeValidator

        # GIVEN: Scope definition and DES internal file modifications
        scope = {"allowed_patterns": ["**/UserRepository*"]}

        # DES internal files (should be excluded from validation)
        modified_files = [
            ".des/execution-status.yaml",
            ".des/audit/audit-2026-01-29.log",
        ]

        # WHEN: Post-execution scope validation runs
        validator = ScopeValidator()
        result = validator.validate_scope(
            scope=scope, project_root=tmp_project_root, git_diff_files=modified_files
        )

        # THEN: DES internal files excluded from validation
        assert result.has_violations is False
        assert result.validation_status == "PASSED"
        # Validator should ignore .des/* files entirely


class TestScopeViolationAuditLogging:
    """
    E2E acceptance tests for audit logging of scope violations.

    Validates that scope violations are logged as warnings in the audit trail
    for Priya's PR review.
    """

    # =========================================================================
    # AC-007.5: Scope violations logged as warnings in audit trail
    # Scenario 9: Scope violation logged to audit trail
    # =========================================================================

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_009_scope_violation_logged_to_audit_trail(self, tmp_project_root):
        """
        GIVEN agent modified OrderService.py (out of scope during UserRepository work)
        WHEN SubagentStop hook detects scope violation
        THEN warning is logged to audit trail with file path and context

        Business Context:
        Priya reviews the audit log during PR review. Scope violations
        are logged as WARNINGS (not errors) because:
        1. The work itself may be valid (just misplaced)
        2. Priya can decide whether to accept or reject

        Audit Entry Format:
        {
            "event_type": "SCOPE_VIOLATION",
            "severity": "WARNING",
            "out_of_scope_file": "src/services/OrderService.py",
            "allowed_patterns": ["**/UserRepository*"],
            "timestamp": "2026-01-22T14:30:00Z"
        }

        TEST ARCHITECTURE:
        - NO step file references (eliminated in Phase 1)
        - Focus on audit log behavior
        - Pass scope directly to validator
        """
        from src.des.validation import ScopeValidator
        from src.des.audit import AuditLog

        # GIVEN: Scope definition and out-of-scope modification
        scope = {"allowed_patterns": ["**/UserRepository*"]}
        out_of_scope_files = ["src/services/OrderService.py"]

        # WHEN: Scope validation runs with audit logging
        validator = ScopeValidator()
        audit_log = AuditLog(project_root=tmp_project_root)

        _result = validator.validate_scope(
            scope=scope,
            project_root=tmp_project_root,
            git_diff_files=out_of_scope_files,
            audit_log=audit_log,
        )

        # THEN: Violation logged to audit trail
        log_entries = audit_log.get_entries_by_type("SCOPE_VIOLATION")
        assert len(log_entries) >= 1

        violation_entry = log_entries[-1]
        assert violation_entry["severity"] == "WARNING"
        assert "OrderService.py" in violation_entry["out_of_scope_file"]
        assert violation_entry["timestamp"] is not None

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_010_multiple_scope_violations_all_logged(self, tmp_project_root):
        """
        GIVEN agent modified multiple out-of-scope files
        WHEN SubagentStop hook detects scope violations
        THEN each violation is logged as separate audit entry

        Business Context:
        If an agent went "rogue" and modified many files, Priya needs
        to see all violations, not just the first one. Each out-of-scope
        file gets its own audit entry for complete transparency.

        Domain Example:
        Agent modified:
        - src/services/OrderService.py (VIOLATION)
        - src/services/PaymentService.py (VIOLATION)
        - config/database.yml (VIOLATION)

        Three separate SCOPE_VIOLATION entries in audit log.

        TEST ARCHITECTURE:
        - NO step file creation (DES internal)
        - Pass scope directly to validator
        - Focus on audit log completeness
        """
        from src.des.validation import ScopeValidator
        from src.des.audit import AuditLog

        # GIVEN: Scope definition and multiple out-of-scope modifications
        scope = {"allowed_patterns": ["**/UserRepository*"]}
        out_of_scope_files = [
            "src/services/OrderService.py",
            "src/services/PaymentService.py",
            "config/database.yml",
        ]

        # WHEN: Scope validation runs
        validator = ScopeValidator()
        audit_log = AuditLog(project_root=tmp_project_root)

        _result = validator.validate_scope(
            scope=scope,
            project_root=tmp_project_root,
            git_diff_files=out_of_scope_files,
            audit_log=audit_log,
        )

        # THEN: All violations logged
        log_entries = audit_log.get_entries_by_type("SCOPE_VIOLATION")
        assert len(log_entries) >= 3

        logged_files = [entry["out_of_scope_file"] for entry in log_entries]
        assert any("OrderService" in f for f in logged_files)
        assert any("PaymentService" in f for f in logged_files)
        assert any("database.yml" in f for f in logged_files)

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_011_no_violations_no_warning_logs(self, tmp_project_root):
        """
        GIVEN agent only modified in-scope files
        WHEN SubagentStop hook validates scope
        THEN no SCOPE_VIOLATION entries appear in audit log

        Business Context:
        Clean executions should not clutter the audit log with
        false warnings. Only actual violations get logged.

        TEST ARCHITECTURE:
        - NO step file creation (DES internal)
        - Pass scope directly to validator
        - Focus on audit log cleanliness
        """
        from src.des.validation import ScopeValidator
        from src.des.audit import AuditLog

        # GIVEN: Scope definition and only in-scope modifications
        scope = {"allowed_patterns": ["**/UserRepository*"]}
        in_scope_files = ["src/repositories/UserRepository.py"]

        # WHEN: Scope validation runs
        validator = ScopeValidator()
        audit_log = AuditLog(project_root=tmp_project_root)

        _result = validator.validate_scope(
            scope=scope,
            project_root=tmp_project_root,
            git_diff_files=in_scope_files,
            audit_log=audit_log,
        )

        # THEN: No violation entries
        log_entries = audit_log.get_entries_by_type("SCOPE_VIOLATION")
        assert len(log_entries) == 0


class TestBoundaryRulesCompleteness:
    """
    Integration tests verifying BOUNDARY_RULES section completeness.

    These tests verify that BOUNDARY_RULES contains all required
    components as a cohesive section.
    """

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_012_boundary_rules_has_complete_structure(
        self, tmp_project_root, des_orchestrator
    ):
        """
        GIVEN /nw:execute command with scope
        WHEN orchestrator renders full prompt
        THEN BOUNDARY_RULES section contains:
             - ALLOWED subsection with file patterns
             - FORBIDDEN subsection with prohibited actions
             - Return control instruction

        Business Context:
        Complete boundary definition requires both positive (ALLOWED)
        and negative (FORBIDDEN) constraints, plus explicit instruction
        about returning control after completion.

        TEST ARCHITECTURE:
        - NO step file references (DES internal)
        - Pass scope directly to orchestrator
        - Focus on BOUNDARY_RULES structure
        """
        # GIVEN: /nw:execute command with scope
        scope = {"allowed_patterns": ["**/UserRepository*"]}

        # WHEN: Orchestrator renders full prompt
        prompt = des_orchestrator.render_full_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            scope=scope,
            project_root=tmp_project_root,
        )

        # THEN: All required components present
        # Section header
        assert "BOUNDARY_RULES" in prompt, "Section header missing"

        # ALLOWED subsection
        assert "ALLOWED" in prompt, "ALLOWED subsection missing"

        # FORBIDDEN subsection
        assert "FORBIDDEN" in prompt, "FORBIDDEN subsection missing"

        # Return control instruction
        return_control_present = any(
            phrase in prompt.lower()
            for phrase in ["return control", "return immediately", "hand back control"]
        )
        assert return_control_present, (
            "Return control instruction missing - agent must know to "
            "stop after completion"
        )

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_013_develop_command_also_includes_boundary_rules(
        self, tmp_project_root, des_orchestrator
    ):
        """
        GIVEN /nw:develop command with scope
        WHEN orchestrator renders full prompt
        THEN prompt includes BOUNDARY_RULES (same as execute)

        Business Context:
        Both /nw:execute and /nw:develop are production workflows
        requiring full DES validation. BOUNDARY_RULES must be present
        for both command types to ensure consistent scope enforcement.

        TEST ARCHITECTURE:
        - NO step file usage (DES internal)
        - Pass scope directly to orchestrator
        - Verify behavior parity between commands
        """
        # GIVEN: /nw:develop command with scope
        scope = {"allowed_patterns": ["**/UserRepository*"]}

        # WHEN: Orchestrator renders full prompt
        prompt = des_orchestrator.render_full_prompt(
            command="/nw:develop",
            agent="@software-crafter",
            scope=scope,
            project_root=tmp_project_root,
        )

        # THEN: BOUNDARY_RULES present
        assert (
            "BOUNDARY_RULES" in prompt
        ), "/nw:develop command must include BOUNDARY_RULES like /nw:execute"

        # Verify it has same structure
        assert (
            "ALLOWED" in prompt
        ), "ALLOWED section must be present for develop command"
        assert (
            "FORBIDDEN" in prompt
        ), "FORBIDDEN section must be present for develop command"


class TestBoundaryRulesValidation:
    """
    Tests for BOUNDARY_RULES validation during pre-invocation checks.

    Per US-002, BOUNDARY_RULES is one of 8 mandatory sections.
    These tests verify validation correctly handles its presence/absence.
    """

    @pytest.mark.skip(reason="Outside-In TDD RED state - awaiting DEVELOP wave")
    def test_scenario_014_missing_boundary_rules_blocks_invocation(
        self, tmp_project_root
    ):
        """
        GIVEN orchestrator generates prompt missing BOUNDARY_RULES
        WHEN pre-invocation validation runs
        THEN validation FAILS with specific error message
        AND Task invocation is BLOCKED

        Business Context:
        Without boundary rules, agents have no scope constraints.
        Pre-invocation validation must catch this before Task tool
        is invoked, preventing unconstrained agent execution.

        Expected Error:
        "MISSING: Mandatory section 'BOUNDARY_RULES' not found"

        TEST ARCHITECTURE:
        - NO DES-STEP-FILE marker (step files eliminated)
        - NO step_id in metadata (DES internal)
        - Focus on BOUNDARY_RULES validation
        """
        from src.des.validation import PromptValidator

        # GIVEN: Prompt missing BOUNDARY_RULES
        incomplete_prompt = """
        <!-- DES-VALIDATION: required -->

        ## DES_METADATA
        command: /nw:execute
        agent: @software-crafter

        ## AGENT_IDENTITY
        You are software-crafter

        ## TASK_CONTEXT
        Implement feature X

        ## TDD_8_PHASES
        PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN, REVIEW,
        REFACTOR_CONTINUOUS, REFACTOR_L4, COMMIT

        ## QUALITY_GATES
        G1-G6 definitions here

        ## OUTCOME_RECORDING
        Record outcomes in execution-status.yaml

        ## TIMEOUT_INSTRUCTION
        Complete within 50 turns

        <!-- NOTE: BOUNDARY_RULES intentionally omitted -->
        """

        # WHEN: Pre-invocation validation runs
        validator = PromptValidator()
        result = validator.validate(incomplete_prompt)

        # THEN: Validation fails with specific error
        assert (
            not result.is_valid
        ), "Validation should FAIL when BOUNDARY_RULES is missing"

        assert any(
            "BOUNDARY_RULES" in error for error in result.errors
        ), "Error message must identify BOUNDARY_RULES as the missing section"

        assert any(
            "MISSING" in error.upper() for error in result.errors
        ), "Error should indicate the section is MISSING, not incomplete"


# =============================================================================
# Test Data Builders (Helper Functions)
# =============================================================================
# NOTE: Step file builders removed in Phase 3 (token-minimal architecture)
# Tests now pass scope directly to orchestrator/validator
# No step file creation needed - DES workflow mechanics are implementation details
