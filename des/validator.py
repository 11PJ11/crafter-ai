"""
Pre-Invocation Template Validator

Validates that DES prompts contain all mandatory sections and 14 TDD phases
before Task invocation, preventing incomplete instructions from reaching sub-agents.

MANDATORY SECTIONS (8):
1. DES_METADATA
2. AGENT_IDENTITY
3. TASK_CONTEXT
4. TDD_14_PHASES
5. QUALITY_GATES
6. OUTCOME_RECORDING
7. BOUNDARY_RULES
8. TIMEOUT_INSTRUCTION

MANDATORY TDD PHASES (14):
1. PREPARE
2. RED_ACCEPTANCE
3. RED_UNIT
4. GREEN_UNIT
5. CHECK_ACCEPTANCE
6. GREEN_ACCEPTANCE
7. REVIEW
8. REFACTOR_L1
9. REFACTOR_L2
10. REFACTOR_L3
11. REFACTOR_L4
12. POST_REFACTOR_REVIEW
13. FINAL_VALIDATE
14. COMMIT
"""

import time
from dataclasses import dataclass
from typing import List


@dataclass
class ValidationResult:
    """Result of template validation."""

    status: str  # "PASSED" or "FAILED"
    errors: List[str]
    task_invocation_allowed: bool
    duration_ms: float


class MandatorySectionChecker:
    """
    Validates that all 8 mandatory sections are present in prompt.

    Mandatory sections ensure prompts contain complete instructions for sub-agents,
    preventing "I didn't know about X" excuses during execution.
    """

    MANDATORY_SECTIONS = [
        "DES_METADATA",       # Step metadata and command
        "AGENT_IDENTITY",     # Which agent executes this step
        "TASK_CONTEXT",       # What needs to be implemented
        "TDD_14_PHASES",      # All 14 TDD phases to execute
        "QUALITY_GATES",      # Quality validation criteria
        "OUTCOME_RECORDING",  # How to track progress
        "BOUNDARY_RULES",     # Scope and file modifications allowed
        "TIMEOUT_INSTRUCTION" # Turn budget and exit conditions
    ]

    def validate(self, prompt: str) -> List[str]:
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


class TDDPhaseValidator:
    """
    Validates that all 14 TDD phases are mentioned in prompt.

    All 14 phases are mandatory to ensure sub-agents execute complete TDD cycle
    and don't claim ignorance about refactoring levels or review phases.
    """

    MANDATORY_PHASES = [
        "PREPARE",               # Enable test, verify setup
        "RED_ACCEPTANCE",        # E2E test fails before implementation
        "RED_UNIT",              # Unit tests fail before code
        "GREEN_UNIT",            # Minimal code to pass unit tests
        "CHECK_ACCEPTANCE",      # Check E2E progress
        "GREEN_ACCEPTANCE",      # E2E tests pass
        "REVIEW",                # Peer review of implementation
        "REFACTOR_L1",           # Readability refactoring
        "REFACTOR_L2",           # Complexity reduction
        "REFACTOR_L3",           # Responsibility organization
        "REFACTOR_L4",           # Abstraction refinement
        "POST_REFACTOR_REVIEW",  # Review refactoring changes
        "FINAL_VALIDATE",        # Document test results
        "COMMIT"                 # Create git commit
    ]

    def validate(self, prompt: str) -> List[str]:
        """
        Validate that all 14 TDD phases are mentioned in prompt.

        Args:
            prompt: The full prompt text to validate

        Returns:
            List of error messages (empty if all phases present)
        """
        errors = []

        for phase in self.MANDATORY_PHASES:
            if phase not in prompt:
                errors.append(f"INCOMPLETE: TDD phase '{phase}' not mentioned")

        return errors


class TemplateValidator:
    """
    Main entry point for template validation.

    Validates that prompts contain all mandatory sections and TDD phases
    before allowing Task invocation.
    """

    def __init__(self):
        """Initialize validator with checkers."""
        self.section_checker = MandatorySectionChecker()
        self.phase_validator = TDDPhaseValidator()

    def validate_prompt(self, prompt: str) -> ValidationResult:
        """
        Validate a complete prompt for mandatory sections and phases.

        Args:
            prompt: The full prompt text to validate

        Returns:
            ValidationResult with status, errors, and task invocation permission
        """
        start_time = time.perf_counter()

        # Check sections
        section_errors = self.section_checker.validate(prompt)

        # Check phases
        phase_errors = self.phase_validator.validate(prompt)

        # Combine all errors
        all_errors = section_errors + phase_errors

        # Calculate duration
        duration_ms = (time.perf_counter() - start_time) * 1000

        # Determine if invocation is allowed
        status = "PASSED" if not all_errors else "FAILED"
        task_invocation_allowed = not all_errors

        return ValidationResult(
            status=status,
            errors=all_errors,
            task_invocation_allowed=task_invocation_allowed,
            duration_ms=duration_ms
        )
