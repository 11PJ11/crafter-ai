"""Command template validator for nWave framework rationalization.

This module provides comprehensive validation of nWave command files against
COMMAND_TEMPLATE.yaml standards and framework rationalization requirements.
"""

import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class SeverityLevel(Enum):
    """Severity classification for validation violations."""

    BLOCKER = "BLOCKER"
    CRITICAL = "CRITICAL"
    MAJOR = "MAJOR"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class ValidationViolation:
    """Represents a single validation violation."""

    category: str
    severity: SeverityLevel
    message: str
    location: str | None = None
    line_number: int | None = None
    remediation: str | None = None


@dataclass
class SizeMetrics:
    """Command file size metrics."""

    total_lines: int
    content_lines: int
    violation_factor: float
    category: str  # COMPLIANT, MINOR, MAJOR, CRITICAL
    within_range: bool


@dataclass
class ValidationResult:
    """Complete validation result for a command file."""

    command_file: str
    compliance_status: str = "NOT_EVALUATED"  # COMPLIANT, NON_COMPLIANT, BLOCKED
    violations: list[ValidationViolation] = field(default_factory=list)
    size_metrics: SizeMetrics | None = None
    embedded_workflows: dict[str, list[str]] = field(default_factory=dict)
    approval_decision: str = "NOT_EVALUATED"
    feedback: list[str] = field(default_factory=list)

    def is_approved(self) -> bool:
        """Check if validation results in approval."""
        return self.approval_decision == "APPROVED"

    def has_blockers(self) -> bool:
        """Check if any BLOCKER violations exist."""
        return any(v.severity == SeverityLevel.BLOCKER for v in self.violations)

    def has_critical_violations(self) -> bool:
        """Check if any CRITICAL violations exist."""
        return any(
            v.severity in (SeverityLevel.BLOCKER, SeverityLevel.CRITICAL)
            for v in self.violations
        )


class CommandTemplateValidator:
    """Validates nWave command files against COMMAND_TEMPLATE.yaml standards."""

    # Size validation ranges
    OPTIMAL_MIN = 50
    OPTIMAL_MAX = 60
    MINOR_THRESHOLD = 150
    MAJOR_THRESHOLD = 500

    # Anti-pattern detection patterns
    PROCEDURAL_STEP_PATTERN = re.compile(r"^\s*(?:STEP|Step)\s+\d+:", re.MULTILINE)
    PROGRESS_TRACKING_PATTERN = re.compile(
        r"(?:phase|state|status|tracking).*?:.*?(?:PENDING|IN_PROGRESS|COMPLETED)",
        re.IGNORECASE,
    )
    ORCHESTRATION_PATTERN = re.compile(
        r"(?:coordinator|orchestrator|orchestration|orchestrate)", re.IGNORECASE
    )
    PARAMETER_PARSING_PATTERN = re.compile(
        r"(?:extract|parse|parse.*parameter|validate.*parameter)", re.IGNORECASE
    )
    MEASUREMENT_PROTOCOL_PATTERN = re.compile(
        r"(?:measurement|metric.*collection|baseline|quantitative)", re.IGNORECASE
    )

    # Required sections in command files
    REQUIRED_SECTIONS = [
        "Agent Activation Metadata",
        "Task Header",
        "Context Files",
        "Agent Invocation",
        "Success Criteria",
        "ORCHESTRATOR BRIEFING",
    ]

    def __init__(self, command_file_path: str):
        """Initialize validator with command file path."""
        self.command_file_path = Path(command_file_path)
        self.content = self._load_file()
        self.lines = self.content.split("\n")

    def _load_file(self) -> str:
        """Load command file content."""
        if not self.command_file_path.exists():
            raise FileNotFoundError(f"Command file not found: {self.command_file_path}")
        return self.command_file_path.read_text(encoding="utf-8")

    def validate(self) -> ValidationResult:
        """Run complete validation workflow."""
        result = ValidationResult(command_file=str(self.command_file_path))

        # Step 1: Size compliance
        result.size_metrics = self._validate_size()

        # Step 2: Structure validation
        structure_violations = self._validate_structure()
        result.violations.extend(structure_violations)

        # Step 3: Workflow duplication check
        workflow_violations, embedded_workflows = self._detect_workflow_duplication()
        result.violations.extend(workflow_violations)
        result.embedded_workflows = embedded_workflows

        # Step 4: Delegation principle
        delegation_violations = self._validate_delegation_principle()
        result.violations.extend(delegation_violations)

        # Step 5: Context bundling
        bundling_violations = self._validate_context_bundling()
        result.violations.extend(bundling_violations)

        # Step 6: Agent invocation pattern
        invocation_violations = self._validate_invocation_pattern()
        result.violations.extend(invocation_violations)

        # Determine compliance status
        result.compliance_status = self._determine_compliance_status(result)

        # Generate approval decision and feedback
        result.approval_decision = self._determine_approval(result)
        result.feedback = self._generate_feedback(result)

        return result

    def _validate_size(self) -> SizeMetrics:
        """Validate command file size."""
        total_lines = len(self.lines)
        content_lines = sum(1 for line in self.lines if line.strip())

        within_range = self.OPTIMAL_MIN <= total_lines <= self.OPTIMAL_MAX

        if total_lines <= self.OPTIMAL_MAX:
            category = "COMPLIANT"
            violation_factor = 1.0
        elif total_lines <= self.MINOR_THRESHOLD:
            category = "MINOR"
            violation_factor = total_lines / self.OPTIMAL_MAX
        elif total_lines <= self.MAJOR_THRESHOLD:
            category = "MAJOR"
            violation_factor = total_lines / self.OPTIMAL_MAX
        else:
            category = "CRITICAL"
            violation_factor = total_lines / self.OPTIMAL_MAX

        return SizeMetrics(
            total_lines=total_lines,
            content_lines=content_lines,
            violation_factor=violation_factor,
            category=category,
            within_range=within_range,
        )

    def _validate_structure(self) -> list[ValidationViolation]:
        """Validate command structure."""
        violations = []

        # Check for ORCHESTRATOR BRIEFING
        if "ORCHESTRATOR BRIEFING" not in self.content:
            violations.append(
                ValidationViolation(
                    category="structure",
                    severity=SeverityLevel.BLOCKER,
                    message="ORCHESTRATOR BRIEFING section is missing (mandatory)",
                    remediation="Add ORCHESTRATOR BRIEFING section with subagent constraints",
                )
            )

        # Check for minimal required sections
        for section in self.REQUIRED_SECTIONS[
            :-1
        ]:  # Exclude ORCHESTRATOR BRIEFING (already checked)
            if section.lower() not in self.content.lower():
                violations.append(
                    ValidationViolation(
                        category="structure",
                        severity=SeverityLevel.WARNING,
                        message=f"{section} section not found",
                        remediation=f"Add {section} section",
                    )
                )

        return violations

    def _detect_workflow_duplication(
        self,
    ) -> tuple[list[ValidationViolation], dict[str, list[str]]]:
        """Detect embedded workflows."""
        violations = []
        embedded_workflows = {}

        # Check for procedural steps
        procedural_matches = list(self.PROCEDURAL_STEP_PATTERN.finditer(self.content))
        if len(procedural_matches) >= 5:
            locations = [
                f"Line {self.content[: m.start()].count(chr(10)) + 1}"
                for m in procedural_matches[:3]
            ]
            embedded_workflows["procedural_steps"] = locations
            violations.append(
                ValidationViolation(
                    category="workflow_duplication",
                    severity=SeverityLevel.BLOCKER,
                    message=f"Embedded procedural steps detected ({len(procedural_matches)} found)",
                    location=", ".join(locations),
                    remediation="Extract procedural steps to agent specification",
                )
            )
        elif procedural_matches:
            embedded_workflows["procedural_steps"] = [
                f"Line {self.content[: m.start()].count(chr(10)) + 1}"
                for m in procedural_matches
            ]

        # Check for progress tracking
        progress_matches = list(self.PROGRESS_TRACKING_PATTERN.finditer(self.content))
        if progress_matches:
            embedded_workflows["progress_tracking"] = [
                f"Line {self.content[: m.start()].count(chr(10)) + 1}"
                for m in progress_matches[:3]
            ]
            violations.append(
                ValidationViolation(
                    category="workflow_duplication",
                    severity=SeverityLevel.WARNING,
                    message="Progress tracking state machine detected",
                    remediation="Move progress tracking to agent specification",
                )
            )

        # Check for orchestration patterns
        orch_matches = list(self.ORCHESTRATION_PATTERN.finditer(self.content))
        if len(orch_matches) >= 3:
            embedded_workflows["orchestration"] = [
                f"Line {self.content[: m.start()].count(chr(10)) + 1}"
                for m in orch_matches[:3]
            ]
            violations.append(
                ValidationViolation(
                    category="workflow_duplication",
                    severity=SeverityLevel.BLOCKER,
                    message="Orchestration coordination logic detected",
                    remediation="Move orchestration to orchestrator agent specification",
                )
            )

        # Check for parameter parsing
        param_matches = list(self.PARAMETER_PARSING_PATTERN.finditer(self.content))
        if param_matches:
            embedded_workflows["parameter_parsing"] = [
                f"Line {self.content[: m.start()].count(chr(10)) + 1}"
                for m in param_matches[:3]
            ]
            violations.append(
                ValidationViolation(
                    category="workflow_duplication",
                    severity=SeverityLevel.WARNING,
                    message="Parameter parsing logic detected",
                    remediation="Move parameter extraction to command parser infrastructure",
                )
            )

        return violations, embedded_workflows

    def _validate_delegation_principle(self) -> list[ValidationViolation]:
        """Validate delegation principle is followed."""
        violations = []

        # Check if command is thin (primarily metadata)
        # Commands should mostly contain YAML and brief descriptions
        code_blocks = len(re.findall(r"```", self.content))
        if code_blocks > 2:
            violations.append(
                ValidationViolation(
                    category="delegation",
                    severity=SeverityLevel.MAJOR,
                    message="Excessive code blocks in command file (should be in agent)",
                    remediation="Move code examples to agent specification",
                )
            )

        return violations

    def _validate_context_bundling(self) -> list[ValidationViolation]:
        """Validate context files are explicitly bundled."""
        violations = []

        # Check for explicit context definition with section header and file paths
        # Must have "Context Files" section with explicit file paths
        has_context_section = (
            re.search(r"##\s+Context Files", self.content, re.IGNORECASE) is not None
        )
        has_file_paths = (
            re.search(
                r"^-\s+[a-zA-Z0-9_\-./]+\.(md|yaml|yml|json)",
                self.content,
                re.MULTILINE,
            )
            is not None
        )

        if not (has_context_section and has_file_paths):
            violations.append(
                ValidationViolation(
                    category="context_bundling",
                    severity=SeverityLevel.WARNING,
                    message="No explicit context file definition found",
                    remediation="Add explicit context files list (Context Files Section)",
                )
            )

        return violations

    def _validate_invocation_pattern(self) -> list[ValidationViolation]:
        """Validate agent invocation pattern."""
        violations = []

        # Check for proper invocation pattern (@agent-id or Skill tool)
        if "@" not in self.content and "Skill" not in self.content:
            violations.append(
                ValidationViolation(
                    category="invocation_pattern",
                    severity=SeverityLevel.WARNING,
                    message="No clear agent invocation pattern found",
                    remediation="Use @agent-id or Skill tool invocation pattern",
                )
            )

        return violations

    def _determine_compliance_status(self, result: ValidationResult) -> str:
        """Determine overall compliance status."""
        if result.has_blockers():
            return "BLOCKED"
        elif result.violations:
            return "NON_COMPLIANT"
        else:
            return "COMPLIANT"

    def _determine_approval(self, result: ValidationResult) -> str:
        """Determine approval decision."""
        if result.has_blockers():
            return "REJECTED_PENDING_REVISIONS"
        elif result.has_critical_violations():
            return "CONDITIONALLY_APPROVED"
        elif result.size_metrics and result.size_metrics.within_range:
            return "APPROVED"
        else:
            return "CONDITIONALLY_APPROVED"

    def _generate_feedback(self, result: ValidationResult) -> list[str]:
        """Generate actionable feedback."""
        feedback = []

        # Size feedback
        if result.size_metrics:
            if result.size_metrics.within_range:
                feedback.append(
                    f"✓ Size compliant: {result.size_metrics.total_lines} lines "
                    f"(target range: {self.OPTIMAL_MIN}-{self.OPTIMAL_MAX})"
                )
            else:
                factor = result.size_metrics.violation_factor
                feedback.append(
                    f"✗ Size violation: {result.size_metrics.total_lines} lines "
                    f"({factor:.1f}x target, category: {result.size_metrics.category})"
                )

        # Violation feedback
        for violation in sorted(
            result.violations, key=lambda v: (v.severity.value, v.category)
        ):
            severity_icon = (
                "✗"
                if violation.severity in (SeverityLevel.BLOCKER, SeverityLevel.CRITICAL)
                else "⚠"
            )
            feedback.append(
                f"{severity_icon} [{violation.severity.value}] {violation.message}"
            )
            if violation.remediation:
                feedback.append(f"  → {violation.remediation}")

        if not feedback:
            feedback.append("✓ All validation checks passed")

        return feedback

    def format_report(self, result: ValidationResult) -> str:
        """Format validation result as human-readable report."""
        lines = [
            "=" * 70,
            "COMMAND TEMPLATE VALIDATION REPORT",
            f"File: {result.command_file}",
            f"Status: {result.compliance_status}",
            f"Approval: {result.approval_decision}",
            "=" * 70,
            "",
        ]

        if result.size_metrics:
            lines.extend(
                [
                    "SIZE METRICS:",
                    f"  Total lines: {result.size_metrics.total_lines}",
                    f"  Content lines: {result.size_metrics.total_lines}",
                    f"  Category: {result.size_metrics.category}",
                    f"  Violation factor: {result.size_metrics.violation_factor:.2f}x",
                    "",
                ]
            )

        if result.embedded_workflows:
            lines.extend(
                [
                    "EMBEDDED WORKFLOWS DETECTED:",
                    *[f"  - {k}: {v}" for k, v in result.embedded_workflows.items()],
                    "",
                ]
            )

        if result.violations:
            lines.extend(["VIOLATIONS:", *[f"  {fb}" for fb in result.feedback], ""])
        else:
            lines.extend([*result.feedback, ""])

        lines.append("=" * 70)
        return "\n".join(lines)


def validate_command(command_file_path: str) -> ValidationResult:
    """Convenience function to validate a command file."""
    validator = CommandTemplateValidator(command_file_path)
    return validator.validate()
