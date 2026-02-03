"""Production implementation of template validator adapter."""

import re
import time
from typing import List

from src.des.ports.driver_ports.validator_port import ValidationResult, ValidatorPort


class RealTemplateValidator(ValidatorPort):
    """Production implementation of template validation.

    Validates that prompts contain all mandatory sections and TDD phases
    before allowing Task invocation.
    """

    MANDATORY_SECTIONS = [
        "DES_METADATA",
        "AGENT_IDENTITY",
        "TASK_CONTEXT",
        "TDD_7_PHASES",  # Schema v3.0: 7-phase canonical TDD cycle
        "QUALITY_GATES",
        "OUTCOME_RECORDING",
        "BOUNDARY_RULES",
        "TIMEOUT_INSTRUCTION",
    ]

    MANDATORY_PHASES = [
        "PREPARE",
        "RED_ACCEPTANCE",
        "RED_UNIT",
        "GREEN",  # Merged GREEN_UNIT + GREEN_ACCEPTANCE
        "REVIEW",  # Expanded scope (includes POST_REFACTOR_REVIEW)
        "REFACTOR_CONTINUOUS",  # Merged L1+L2+L3
        "COMMIT",  # Absorbs FINAL_VALIDATE
    ]

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

    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate prompt for mandatory sections and TDD phases.

        Args:
            prompt: Full prompt text to validate

        Returns:
            ValidationResult with status, errors, and task invocation flag
        """
        start_time = time.perf_counter()

        all_errors = []

        # Check mandatory sections
        section_errors = self._validate_sections(prompt)
        all_errors.extend(section_errors)

        # Check TDD phases
        phase_errors = self._validate_phases(prompt)
        all_errors.extend(phase_errors)

        # Generate recovery guidance
        recovery_guidance = None
        if all_errors:
            recovery_guidance = self._generate_recovery_guidance(all_errors)

        duration_ms = (time.perf_counter() - start_time) * 1000

        status = "PASSED" if not all_errors else "FAILED"
        task_invocation_allowed = not all_errors

        return ValidationResult(
            status=status,
            errors=all_errors,
            task_invocation_allowed=task_invocation_allowed,
            duration_ms=duration_ms,
            recovery_guidance=recovery_guidance,
        )

    def _validate_sections(self, prompt: str) -> list[str]:
        """Validate that all mandatory sections are present."""
        errors = []
        for section in self.MANDATORY_SECTIONS:
            section_marker = f"# {section}"
            if section_marker not in prompt:
                errors.append(f"MISSING: Mandatory section '{section}' not found")
        return errors

    def _validate_phases(self, prompt: str) -> List[str]:
        """Validate that all 7 TDD phases (schema v3.0) are mentioned."""
        # Check for shorthand pattern first
        if re.search(
            r"(?i)all\s+7\s+phases?\s+(listed|mentioned|included|present)", prompt
        ):
            return []

        errors = []
        for phase in self.MANDATORY_PHASES:
            phase_lines = []
            for line in prompt.split("\n"):
                if phase in line:
                    phase_lines.append(line.strip())

            found = False
            if phase_lines:
                for line in phase_lines:
                    # Skip if it's a "MISSING" comment
                    if (
                        re.search(rf"\(.*\b{phase}\b.*\)", line)
                        or re.search(
                            rf"\b(without|missing|no)\s+{phase}\b", line, re.IGNORECASE
                        )
                        or re.search(rf"# MISSING:\s*{phase}", line)
                    ):
                        continue
                    if phase in line:
                        found = True
                        break

            if not found:
                errors.append(f"INCOMPLETE: TDD phase '{phase}' not mentioned")

        return errors

    def _generate_recovery_guidance(self, errors: list[str]) -> list[str]:
        """Generate actionable recovery guidance for validation errors."""
        guidance_items = []

        for error in errors:
            if "MISSING: Mandatory section" in error:
                for section in self.MANDATORY_SECTIONS:
                    if section in error:
                        guidance = self.RECOVERY_GUIDANCE_MAP.get(section)
                        if guidance:
                            guidance_items.append(guidance)
                        break

        return guidance_items if guidance_items else None
