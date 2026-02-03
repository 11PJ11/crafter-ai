"""
Pre-Invocation Template Validator with Schema Version Support

Validates that DES prompts contain all mandatory sections and appropriate TDD phases
before Task invocation, preventing incomplete instructions from reaching sub-agents.

Schema Version Support (US-005-03):
- v1.0: 14-phase TDD cycle (legacy)
- v2.0: 8-phase TDD cycle (optimized)
- v3.0: 7-phase TDD cycle (canonical, L4-L6 moved to orchestrator Phase 2.25)

Auto-detects schema version from step file to validate correct phase set.

MANDATORY SECTIONS (8):
1. DES_METADATA
2. AGENT_IDENTITY
3. TASK_CONTEXT
4. TDD_PHASES (14, 8, or 7 depending on schema version)
5. QUALITY_GATES
6. OUTCOME_RECORDING
7. BOUNDARY_RULES
8. TIMEOUT_INSTRUCTION

MANDATORY TDD PHASES - Schema v1.0 (14 phases):
1. PREPARE, 2. RED_ACCEPTANCE, 3. RED_UNIT, 4. GREEN_UNIT, 5. CHECK_ACCEPTANCE
6. GREEN_ACCEPTANCE, 7. REVIEW, 8. REFACTOR_L1, 9. REFACTOR_L2, 10. REFACTOR_L3
11. REFACTOR_L4, 12. POST_REFACTOR_REVIEW, 13. FINAL_VALIDATE, 14. COMMIT

MANDATORY TDD PHASES - Schema v2.0 (8 phases):
1. PREPARE, 2. RED_ACCEPTANCE, 3. RED_UNIT, 4. GREEN
5. REVIEW, 6. REFACTOR_CONTINUOUS, 7. REFACTOR_L4, 8. COMMIT

MANDATORY TDD PHASES - Schema v3.0 (7 phases):
1. PREPARE, 2. RED_ACCEPTANCE, 3. RED_UNIT, 4. GREEN (merged GREEN_UNIT + GREEN_ACCEPTANCE)
5. REVIEW (expanded scope, includes POST_REFACTOR_REVIEW), 6. REFACTOR_CONTINUOUS (merged L1+L2+L3)
7. COMMIT (absorbs FINAL_VALIDATE)
Note: L4-L6 refactoring moved to orchestrator Phase 2.25 (runs once after all steps)
"""

import re
import time
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of template validation."""

    status: str  # "PASSED" or "FAILED"
    errors: list[str]
    task_invocation_allowed: bool
    duration_ms: float
    recovery_guidance: list[str] = (
        None  # Actionable guidance for fixing validation errors
    )


class MandatorySectionChecker:
    """
    Validates that all 8 mandatory sections are present in prompt.

    Mandatory sections ensure prompts contain complete instructions for sub-agents,
    preventing "I didn't know about X" excuses during execution.
    """

    MANDATORY_SECTIONS = [
        "DES_METADATA",  # Step metadata and command
        "AGENT_IDENTITY",  # Which agent executes this step
        "TASK_CONTEXT",  # What needs to be implemented
        "TDD_7_PHASES",  # All 7 TDD phases to execute (schema v3.0 canonical)
        "QUALITY_GATES",  # Quality validation criteria
        "OUTCOME_RECORDING",  # How to track progress
        "BOUNDARY_RULES",  # Scope and file modifications allowed
        "TIMEOUT_INSTRUCTION",  # Turn budget and exit conditions
    ]

    # Recovery guidance for each mandatory section
    RECOVERY_GUIDANCE_MAP = {
        "DES_METADATA": "Add DES_METADATA section with step file path and command name",
        "AGENT_IDENTITY": "Add AGENT_IDENTITY section specifying which agent executes this step",
        "TASK_CONTEXT": "Add TASK_CONTEXT section describing what needs to be implemented",
        "TDD_7_PHASES": "Add TDD_7_PHASES section listing all 7 phases: PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN, REVIEW, REFACTOR_CONTINUOUS, COMMIT",
        "QUALITY_GATES": "Add QUALITY_GATES section defining validation criteria (G1-G6)",
        "OUTCOME_RECORDING": "Add OUTCOME_RECORDING section describing how to track phase completion",
        "BOUNDARY_RULES": "Add BOUNDARY_RULES section specifying which files can be modified",
        "TIMEOUT_INSTRUCTION": "Add TIMEOUT_INSTRUCTION section with turn budget guidance",
    }

    def validate(self, prompt: str) -> list[str]:
        """
        Validate that all mandatory sections are present in prompt.

        Args:
            prompt: The full prompt text to validate

        Returns:
            List of error messages (empty if all sections present)
        """
        errors = []

        for section in self.MANDATORY_SECTIONS:
            section_marker = f"# {section}"
            if section_marker not in prompt:
                errors.append(f"MISSING: Mandatory section '{section}' not found")

        return errors

    def get_recovery_guidance(self, errors: list[str]) -> list[str]:
        """
        Generate actionable recovery guidance for validation errors.

        Args:
            errors: List of error messages from validation

        Returns:
            List of recovery guidance strings for all missing sections,
            each prefixed with "FIX: " to integrate inline with error messages.
        """
        if not errors:
            return None

        guidance_items = []
        for error in errors:
            if "MISSING: Mandatory section" in error:
                # Extract section name from error message
                for section in self.MANDATORY_SECTIONS:
                    if section in error:
                        guidance = self.RECOVERY_GUIDANCE_MAP.get(section)
                        if guidance:
                            # Append FIX: prefix for inline error message integration (AC-005.4)
                            guidance_items.append(f"FIX: {guidance}")
                        break

        if guidance_items:
            return guidance_items
        return None


class TDDPhaseValidator:
    """
    Validates that required TDD phases are mentioned in prompt.

    Supports both v1.0 (14 phases) and v2.0 (8 phases) schema versions.
    Detects schema version and validates appropriate phase set.

    v1.0 (14 phases): PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN_UNIT, CHECK_ACCEPTANCE,
                      GREEN_ACCEPTANCE, REVIEW, REFACTOR_L1-L4, POST_REFACTOR_REVIEW,
                      FINAL_VALIDATE, COMMIT

    v2.0 (8 phases): PREPARE, RED_ACCEPTANCE, RED_UNIT, GREEN, REVIEW,
                     REFACTOR_CONTINUOUS, REFACTOR_L4, COMMIT
    """

    # Schema v1.0: Legacy 14-phase TDD cycle
    MANDATORY_PHASES_V1 = [
        "PREPARE",  # Enable test, verify setup
        "RED_ACCEPTANCE",  # E2E test fails before implementation
        "RED_UNIT",  # Unit tests fail before code
        "GREEN_UNIT",  # Minimal code to pass unit tests
        "CHECK_ACCEPTANCE",  # Check E2E progress
        "GREEN_ACCEPTANCE",  # E2E tests pass
        "REVIEW",  # Peer review of implementation
        "REFACTOR_L1",  # Readability refactoring
        "REFACTOR_L2",  # Complexity reduction
        "REFACTOR_L3",  # Responsibility organization
        "REFACTOR_L4",  # Abstraction refinement
        "POST_REFACTOR_REVIEW",  # Review refactoring changes
        "FINAL_VALIDATE",  # Document test results
        "COMMIT",  # Create git commit
    ]

    # Schema v2.0: Optimized 8-phase TDD cycle (US-005-03)
    MANDATORY_PHASES_V2 = [
        "PREPARE",  # Enable test, verify setup
        "RED_ACCEPTANCE",  # E2E test fails before implementation
        "RED_UNIT",  # Unit tests fail before code
        "GREEN",  # Implementation + acceptance validation (merged)
        "REVIEW",  # Peer review (expanded scope)
        "REFACTOR_CONTINUOUS",  # L1+L2+L3 refactoring (merged)
        "REFACTOR_L4",  # Architecture patterns (optional)
        "COMMIT",  # Create git commit
    ]

    # Schema v3.0: Canonical 7-phase TDD cycle (from step-tdd-cycle-schema.json v3.0)
    MANDATORY_PHASES_V3 = [
        "PREPARE",  # Enable test, verify setup
        "RED_ACCEPTANCE",  # E2E test fails before implementation
        "RED_UNIT",  # Unit tests fail before code
        "GREEN",  # Merged GREEN_UNIT + GREEN_ACCEPTANCE
        "REVIEW",  # Expanded scope (includes POST_REFACTOR_REVIEW)
        "REFACTOR_CONTINUOUS",  # Merged L1+L2+L3
        "COMMIT",  # Absorbs FINAL_VALIDATE
    ]
    # Note: REFACTOR_L4-L6 moved to orchestrator Phase 2.25 (runs once after all steps)

    # Default to v1.0 for backward compatibility
    MANDATORY_PHASES = MANDATORY_PHASES_V1

    def detect_schema_version_from_prompt(self, prompt: str) -> str:
        """
        Detect schema version from prompt text.

        Looks for version indicators in the prompt:
        - "schema_version: 3.0" or "schema_v3.0" or "v3.0" -> v3.0
        - "7-phase" or "7 phases" -> v3.0
        - "schema_version: 2.0" or "schema_v2.0" or "v2.0" -> v2.0
        - "8-phase" or "8 phases" -> v2.0
        - Default to v1.0 if not found

        Args:
            prompt: The full prompt text

        Returns:
            Schema version string ("1.0", "2.0", or "3.0")
        """
        # Check for explicit v3.0 indicators (highest priority)
        if re.search(r"(?i)(schema_version.*?3\.0|7[\s-]phase|v3\.0|7 phases)", prompt):
            return "3.0"

        # Check for explicit v2.0 indicators
        if re.search(r"(?i)(schema_version.*?2\.0|8[\s-]phase|v2\.0|8 phases)", prompt):
            return "2.0"

        # Default to v1.0
        return "1.0"

    def validate(self, prompt: str) -> list[str]:
        """
        Validate that all required TDD phases are mentioned in prompt.

        Auto-detects schema version (v1.0 for 14 phases, v2.0 for 8 phases, v3.0 for 7 phases)
        and validates appropriate phase set.

        Detects phases by looking for patterns:
        - Numbered list items (e.g., "1. PREPARE")
        - Phase names in text (e.g., "PREPARE")
        - Shorthand references like "All 14 phases listed", "All 8 phases listed", or "All 7 phases listed"

        But excludes comments mentioning missing phases (e.g., "# MISSING: REFACTOR_L3")

        Args:
            prompt: The full prompt text to validate

        Returns:
            List of error messages (empty if all phases present)
        """
        # Detect schema version
        schema_version = self.detect_schema_version_from_prompt(prompt)

        # Select appropriate phase list
        if schema_version == "3.0":
            phases_to_validate = self.MANDATORY_PHASES_V3
            shorthand_pattern = (
                r"(?i)all\s+7\s+phases?\s+(listed|mentioned|included|present)"
            )
        elif schema_version == "2.0":
            phases_to_validate = self.MANDATORY_PHASES_V2
            shorthand_pattern = (
                r"(?i)all\s+8\s+phases?\s+(listed|mentioned|included|present)"
            )
        else:
            phases_to_validate = self.MANDATORY_PHASES_V1
            shorthand_pattern = (
                r"(?i)all\s+14\s+phases?\s+(listed|mentioned|included|present)"
            )

        # Check for shorthand pattern first
        if re.search(shorthand_pattern, prompt):
            return []  # Accept shorthand as valid

        errors = []

        for phase in phases_to_validate:
            # Check if phase appears in a non-comment context
            # Specifically exclude lines starting with "# MISSING:" or containing "MISSING:"

            # Find all lines with the phase
            phase_lines = []
            for line in prompt.split("\n"):
                if phase in line:
                    phase_lines.append(line.strip())

            # Check if any line contains the phase but is NOT a comment about it being missing
            found = False
            if phase_lines:
                for line in phase_lines:
                    # Skip if it's a "MISSING" comment about this phase or descriptive text mentioning it
                    if (
                        re.search(
                            rf"\(.*\b{phase}\b.*\)", line
                        )  # (missing COMMIT) format
                        or re.search(
                            rf"\b(without|missing|no)\s+{phase}\b", line, re.IGNORECASE
                        )  # descriptive text
                        or re.search(rf"# MISSING:\s*{phase}", line)
                    ):  # comment format
                        continue
                    # Phase found in non-missing context
                    if phase in line:
                        found = True
                        break

            if not found:
                errors.append(f"INCOMPLETE: TDD phase '{phase}' not mentioned")

        return errors


class DESMarkerValidator:
    """
    Validates the DES-VALIDATION marker format in prompts.

    Ensures prompts contain a valid HTML comment marker:
    <!-- DES-VALIDATION: required -->

    The marker value MUST be exactly 'required' (case-sensitive).
    """

    def validate(self, prompt: str) -> list:
        """
        Validate DES-VALIDATION marker in prompt.

        Args:
            prompt: The full prompt text to validate

        Returns:
            List of error messages (empty if marker is valid)
        """
        errors = []

        # Pattern for DES-VALIDATION marker: <!-- DES-VALIDATION: value -->
        pattern = r"<!--\s*DES-VALIDATION\s*:\s*(\w+)\s*-->"
        match = re.search(pattern, prompt)

        if not match:
            # Marker not found
            errors.append("INVALID_MARKER: DES-VALIDATION marker not found")
            return errors

        # Extract value and normalize whitespace
        value = match.group(1).strip()

        # Value MUST be exactly 'required' (case-sensitive)
        if value != "required":
            errors.append(
                f"INVALID_MARKER: DES-VALIDATION value must be 'required', got '{value}'"
            )

        return errors


class ExecutionLogValidator:
    """
    Validates phase execution log for state violations and schema compliance.

    Supports both v1.0 (14 phases) and v2.0 (8 phases) schemas.
    Detects abandoned phases, missing required fields, and invalid state sequences
    to ensure phase execution logs are complete and consistent.

    For v2.0 schemas, validates:
    - Exactly 8 phases in log (not 14)
    - GREEN phase present (merged GREEN_UNIT + GREEN_ACCEPTANCE)
    - REFACTOR_CONTINUOUS phase present (merged L1+L2+L3)
    """

    def validate(
        self,
        phase_log: list[dict],
        schema_version: str = "1.0",
        skip_schema_validation: bool = False,
    ) -> list[str]:
        """
        Validate phase execution log for state violations and schema compliance.

        Checks:
        1. Correct number of phases for schema version (7 for v3.0, 8 for v2.0, 14 for v1.0)
           - SKIPPED if phase_log is empty (no execution log found in prompt)
           - SKIPPED if skip_schema_validation is True
        2. Required phases present for schema version
           - SKIPPED if phase_log is empty
           - SKIPPED if skip_schema_validation is True
        3. No IN_PROGRESS phases (abandoned state)
        4. EXECUTED phases must have outcome field (PASS/FAIL)
        5. SKIPPED phases must have blocked_by reason
        6. No NOT_EXECUTED phases in log

        Args:
            phase_log: List of phase execution records
            schema_version: Schema version (default "1.0" for backward compatibility)
            skip_schema_validation: If True, skip phase count/presence validation.
                Useful for unit tests that only test individual phase state rules.

        Returns:
            List of error messages (empty if all valid)
        """
        errors = []

        # Skip phase count and presence validation if phase_log is empty
        # This happens when no EXECUTION_LOG_* sections are found in the prompt
        # (prompts don't always include execution logs, especially before execution starts)
        if not phase_log:
            return errors

        # Skip schema-level validation if requested (for unit testing individual rules)
        if not skip_schema_validation:
            # Validate phase count matches schema version
            if schema_version == "3.0":
                expected_phases = 7
                required_phases = {
                    "PREPARE",
                    "RED_ACCEPTANCE",
                    "RED_UNIT",
                    "GREEN",
                    "REVIEW",
                    "REFACTOR_CONTINUOUS",
                    "COMMIT",
                }
            elif schema_version == "2.0":
                expected_phases = 8
                required_phases = {
                    "PREPARE",
                    "RED_ACCEPTANCE",
                    "RED_UNIT",
                    "GREEN",
                    "REVIEW",
                    "REFACTOR_CONTINUOUS",
                    "REFACTOR_L4",
                    "COMMIT",
                }
            else:
                expected_phases = 14
                required_phases = {
                    "PREPARE",
                    "RED_ACCEPTANCE",
                    "RED_UNIT",
                    "GREEN_UNIT",
                    "CHECK_ACCEPTANCE",
                    "GREEN_ACCEPTANCE",
                    "REVIEW",
                    "REFACTOR_L1",
                    "REFACTOR_L2",
                    "REFACTOR_L3",
                    "REFACTOR_L4",
                    "POST_REFACTOR_REVIEW",
                    "FINAL_VALIDATE",
                    "COMMIT",
                }

            # Check phase count
            if len(phase_log) != expected_phases:
                errors.append(
                    f"INVALID: Phase log has {len(phase_log)} phases for schema v{schema_version}, "
                    f"expected {expected_phases} phases"
                )

            # Check for required phases
            present_phases = {
                phase.get("phase_name")
                for phase in phase_log
                if phase.get("phase_name")
            }
            missing_phases = required_phases - present_phases
            if missing_phases:
                errors.append(
                    f"INCOMPLETE: Missing required phases for schema v{schema_version}: {', '.join(sorted(missing_phases))}"
                )

        for phase in phase_log:
            phase_name = phase.get("phase_name", "unknown")
            status = phase.get("status")

            # Check 1: Detect IN_PROGRESS (abandoned state)
            if status == "IN_PROGRESS":
                errors.append(
                    f"INCOMPLETE: Phase {phase_name} left in IN_PROGRESS state - "
                    f"task may have been abandoned"
                )

            # Check 2: EXECUTED must have outcome
            elif status == "EXECUTED":
                if "outcome" not in phase or phase.get("outcome") is None:
                    errors.append(
                        f"ERROR: Phase {phase_name} EXECUTED but missing outcome field. "
                        f"Must specify outcome (PASS or FAIL)"
                    )

            # Check 3: SKIPPED must have blocked_by
            elif status == "SKIPPED":
                if "blocked_by" not in phase or not phase.get("blocked_by"):
                    errors.append(
                        f"ERROR: Phase {phase_name} SKIPPED but missing blocked_by reason. "
                        f"Must explain why phase was skipped"
                    )

            # Check 4: Reject NOT_EXECUTED
            elif status == "NOT_EXECUTED":
                errors.append(
                    f"ERROR: Phase {phase_name} NOT_EXECUTED. "
                    f"Cannot mark task complete with unexecuted phases"
                )

        return errors

    def get_recovery_guidance(self, errors: list[str]) -> list[str]:
        """
        Generate actionable recovery guidance for validation errors.

        Args:
            errors: List of error messages from validate()

        Returns:
            List of recovery steps for fixing errors, each prefixed with "FIX: "
            for inline integration with error messages (AC-005.4)
        """
        if not errors:
            return None

        guidance_items = []

        for error in errors:
            if "IN_PROGRESS" in error:
                # Extract phase name from error message
                if "Phase" in error:
                    parts = error.split("Phase ")
                    if len(parts) > 1:
                        phase_name = parts[1].split(" ")[ 1]
                        guidance_items.append(
                            f"FIX: Complete or rollback the IN_PROGRESS phase {phase_name}"
                        )
            elif "SKIPPED" in error and "blocked_by" in error.lower():
                if "Phase" in error:
                    parts = error.split("Phase ")
                    if len(parts) > 1:
                        phase_name = parts[1].split(" ")[0]
                        guidance_items.append(
                            f"FIX: Add blocked_by reason explaining why phase {phase_name} was skipped"
                        )
            elif "EXECUTED" in error and "outcome" in error.lower():
                if "Phase" in error:
                    parts = error.split("Phase ")
                    if len(parts) > 1:
                        phase_name = parts[1].split(" ")[0]
                        guidance_items.append(
                            f"FIX: Add outcome field (PASS/FAIL) to phase {phase_name}"
                        )
            elif "NOT_EXECUTED" in error:
                guidance_items.append(
                    "FIX: Cannot complete task with NOT_EXECUTED phases. "
                    "All required phases must be EXECUTED or explicitly SKIPPED with reason"
                )

        if guidance_items:
            return guidance_items
        return None


class TemplateValidator:
    """
    Main entry point for template validation.

    Validates that prompts contain all mandatory sections and TDD phases
    before allowing Task invocation.
    """

    def __init__(self):
        """Initialize validator with checkers."""
        self.marker_validator = DESMarkerValidator()
        self.section_checker = MandatorySectionChecker()
        self.phase_validator = TDDPhaseValidator()
        self.execution_log_validator = ExecutionLogValidator()

    def validate_prompt(self, prompt: str) -> ValidationResult:
        """
        Validate a complete prompt for mandatory sections and phases.

        Supports both schema v1.0 (14 phases) and v2.0 (8 phases).
        Auto-detects schema version and validates appropriate phase set.

        Args:
            prompt: The full prompt text to validate

        Returns:
            ValidationResult with status, errors, and task invocation permission
        """
        start_time = time.perf_counter()

        # Detect schema version
        schema_version = self.phase_validator.detect_schema_version_from_prompt(prompt)

        # Check marker (first - foundational validation)
        marker_errors = self.marker_validator.validate(prompt)

        # Check sections
        section_errors = self.section_checker.validate(prompt)

        # Check phases (validates appropriate phase set based on detected schema version)
        phase_errors = self.phase_validator.validate(prompt)

        # Extract and parse phase_execution_log from prompt
        execution_log_data = self._extract_execution_log_from_prompt(prompt)
        # Validate with schema-aware logic
        execution_log_errors = self.execution_log_validator.validate(
            execution_log_data, schema_version
        )

        # Combine all errors (marker first, then sections, then phases, then execution log)
        all_errors = (
            marker_errors + section_errors + phase_errors + execution_log_errors
        )

        # Generate recovery guidance for errors
        recovery_guidance = []
        if section_errors:
            section_guidance = self.section_checker.get_recovery_guidance(
                section_errors
            )
            if section_guidance:
                recovery_guidance.extend(section_guidance)
        if execution_log_errors:
            log_guidance = self.execution_log_validator.get_recovery_guidance(
                execution_log_errors
            )
            if log_guidance:
                recovery_guidance.extend(log_guidance)

        # Return None if no guidance was generated
        if not recovery_guidance:
            recovery_guidance = None

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Determine if invocation is allowed
        status = "PASSED" if not all_errors else "FAILED"
        task_invocation_allowed = not all_errors

        return ValidationResult(
            status=status,
            errors=all_errors,
            task_invocation_allowed=task_invocation_allowed,
            duration_ms=duration_ms,
            recovery_guidance=recovery_guidance,
        )

    def _extract_execution_log_from_prompt(self, prompt: str) -> list[dict]:
        """
        Extract and parse phase execution log from prompt text.

        Searches for section markers (# EXECUTION_LOG_*) and parses multiple
        text format variations into structured phase execution data.

        Supports three distinct format variations:

        Format A (Narrative):
            "Phase REFACTOR_L2 status: IN_PROGRESS (context)"
            → {"phase_name": "REFACTOR_L2", "status": "IN_PROGRESS"}

        Format B (List):
            "EXECUTED: PREPARE, RED_ACCEPTANCE, ...
             NOT_EXECUTED: GREEN_ACCEPTANCE, ..."
            → Multiple dicts, one per phase with respective status

        Format C (Key-Value):
            "Phase RED_UNIT: status=EXECUTED, outcome=null, blocked_by=reason"
            → {"phase_name": "RED_UNIT", "status": "EXECUTED", "outcome": None, "blocked_by": "reason"}

        Args:
            prompt: The full prompt text containing execution log sections

        Returns:
            List[dict] where each dict has:
            - phase_name: str (required)
            - status: str (required, one of: EXECUTED, SKIPPED, IN_PROGRESS, NOT_EXECUTED)
            - outcome: Optional[str] (for EXECUTED phases: PASS or FAIL)
            - blocked_by: Optional[str] (for SKIPPED phases: reason text)

            Returns empty list if no execution log sections found
        """
        import re

        phase_log = []
        section_markers = [
            "# EXECUTION_LOG_STATUS",
            "# EXECUTION_LOG_ISSUE",
            "# EXECUTION_LOG_PROBLEM",
            "# EXECUTION_LOG_ERRORS",
            "# EXECUTION_LOG_WITH_SKIP",
            "# EXECUTION_LOG_COMPLETE",
        ]

        # Search for all execution log sections in the prompt
        for marker in section_markers:
            if marker not in prompt:
                continue

            # Extract section content (from marker to next # section or end of text)
            marker_index = prompt.find(marker)
            if marker_index == -1:
                continue

            # Find end of section (next # marker or end of string)
            section_start = marker_index + len(marker)
            next_marker_index = prompt.find("\n#", section_start)
            if next_marker_index == -1:
                section_content = prompt[section_start:]
            else:
                section_content = prompt[section_start:next_marker_index]

            # Parse Format A: Narrative style
            # Pattern: "Phase PHASE_NAME status: STATUS (optional context)"
            format_a_matches = re.findall(
                r"Phase\s+(\w+)\s+status:\s+(\w+)",
                section_content,
            )
            for phase_name, status in format_a_matches:
                phase_log.append({"phase_name": phase_name, "status": status})

            # Parse Format B: List style
            # Pattern: "STATUS: PHASE1, PHASE2, ... \n STATUS: PHASE3, ..."
            # Split by status keywords: EXECUTED, SKIPPED, IN_PROGRESS, NOT_EXECUTED
            statuses = ["EXECUTED", "SKIPPED", "IN_PROGRESS", "NOT_EXECUTED"]
            for status in statuses:
                pattern = (
                    status
                    + r":\s+([A-Z0-9_,\s\-]+?)(?=\n|$|EXECUTED|SKIPPED|IN_PROGRESS|NOT_EXECUTED)"
                )
                matches = re.findall(pattern, section_content)
                for match in matches:
                    # Split phase names by comma
                    phase_names = [p.strip() for p in match.split(",") if p.strip()]
                    for phase_name in phase_names:
                        # Allow hyphens and numbers in phase names (e.g., REFACTOR_L1-L4)
                        if phase_name and re.match(r"^[A-Z0-9_\-]+$", phase_name):
                            phase_log.append(
                                {"phase_name": phase_name, "status": status}
                            )

            # Parse Format C: Key-value style
            # Pattern: "Phase PHASE_NAME: status=STATUS, outcome=VALUE, blocked_by=REASON"
            format_c_pattern = r"Phase\s+(\w+):\s+status=(\w+)(?:,\s+outcome=(\w+))?(?:,\s+blocked_by=([^\n,]+))?"
            format_c_matches = re.findall(format_c_pattern, section_content)
            for phase_name, status, outcome, blocked_by in format_c_matches:
                entry = {"phase_name": phase_name, "status": status}

                # Convert "null" string to None
                if outcome and outcome.lower() != "null":
                    entry["outcome"] = outcome

                # Convert "null" string to None for blocked_by
                # Handle cases like "null", "null (INVALID)", etc.
                if blocked_by:
                    blocked_by = blocked_by.strip()
                    # If blocked_by starts with "null" (case-insensitive), treat as missing
                    if not blocked_by.lower().startswith("null"):
                        entry["blocked_by"] = blocked_by
                    # If blocked_by starts with "null", don't add it to entry (treat as missing)

                phase_log.append(entry)

        # Remove duplicates while preserving order (by checking phase_name+status combination)
        seen = set()
        unique_phase_log = []
        for entry in phase_log:
            # Create hashable key from phase_name and status
            key = (entry.get("phase_name"), entry.get("status"))
            if key not in seen:
                seen.add(key)
                unique_phase_log.append(entry)

        return unique_phase_log
