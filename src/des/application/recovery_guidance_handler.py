"""
RecoveryGuidanceHandler: Central recovery guidance system for task failure scenarios.

Provides recovery suggestions for different failure modes, helping developers
understand and resolve execution failures through educational context.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class RecoveryGuidanceHandler:
    """
    Handles recovery guidance generation for various failure scenarios.

    Provides:
    - generate_recovery_suggestions: Creates suggestions for different failure modes
    - handle_failure: Persists suggestions to step file state
    - format_suggestion: Formats suggestions with WHY + HOW + actionable elements
    """

    # Failure mode templates with recovery guidance
    FAILURE_MODE_TEMPLATES = {
        "abandoned_phase": {
            "description": "Agent crashed during phase execution",
            "suggestions": [
                "WHY: The agent left {phase} in IN_PROGRESS state, indicating it started but did not complete. This typically occurs when the agent encounters an unhandled error or timeout.\n"
                "HOW: Resetting the phase to NOT_EXECUTED allows the execution framework to retry the phase from scratch, ensuring a clean state for the next attempt.\n"
                "ACTION: Review agent transcript at {transcript_path} for error details, then run `/nw:execute` to resume from {phase}.",
                "WHY: A phase left IN_PROGRESS represents incomplete work that may have corrupted the step file state.\n"
                "HOW: Resetting the phase status clears any partial state changes made before the failure.\n"
                "ACTION: Run `/nw:execute @software-crafter '{step_file}'` to retry the {phase} phase.",
                "WHY: The orchestrator will not progress past an IN_PROGRESS phase without manual intervention.\n"
                "HOW: Marking the phase as NOT_EXECUTED signals that the phase is ready for another execution attempt.\n"
                "ACTION: Manually update the step file JSON: set state.tdd_cycle.{phase}.status = 'NOT_EXECUTED'.",
            ],
        },
        "silent_completion": {
            "description": "Agent returned without updating step file",
            "suggestions": [
                "WHY: The agent completed execution but did not update any phase status, leaving the task state unchanged. This typically indicates the agent did not include OUTCOME_RECORDING instructions or encountered prompt parsing issues.\n"
                "HOW: Verifying the prompt contains clear OUTCOME_RECORDING instructions ensures the agent knows to update phase status.\n"
                "ACTION: Check agent transcript at {transcript_path} for errors or early termination.",
                "WHY: Silent completion prevents the orchestrator from knowing what work was completed.\n"
                "HOW: Manually updating phase status based on transcript evidence reconstructs the execution record.\n"
                "ACTION: Review the transcript and manually update phase status based on evidence of what the agent completed.",
                "WHY: The OUTCOME_RECORDING section instructs the agent to persist step file updates after each phase.\n"
                "HOW: Including this section in the prompt ensures the agent knows to update the step file.\n"
                "ACTION: Verify the prompt includes OUTCOME_RECORDING section with explicit update instructions.",
            ],
        },
        "missing_section": {
            "description": "Validation found missing mandatory section",
            "suggestions": [
                "WHY: Mandatory sections are required to provide the agent with complete context and instructions.\n"
                "HOW: Adding the missing section provides the agent with necessary guidance for execution.\n"
                "ACTION: Update the prompt template to include the missing {section_name} section with all required content.",
                "WHY: Each mandatory section serves a specific purpose in the execution context.\n"
                "HOW: Reviewing the documentation for {section_name} ensures the section is correctly implemented.\n"
                "ACTION: Consult docs/feature/des/discuss/prompt-specification.md for {section_name} format and content requirements.",
            ],
        },
        "invalid_outcome": {
            "description": "Phase marked EXECUTED without outcome",
            "suggestions": [
                "WHY: Outcomes document what work was completed in each phase, essential for understanding execution progress.\n"
                "HOW: Adding outcome details creates an audit trail of what was accomplished.\n"
                "ACTION: Update the step file: set state.tdd_cycle.{phase}.outcome to describe what was completed.",
                "WHY: Empty outcomes indicate incomplete phase documentation.\n"
                "HOW: Filling in outcome details enables the orchestrator to validate phase completion.\n"
                "ACTION: Manually add outcome text describing the phase results and artifacts produced.",
            ],
        },
        "missing_phase": {
            "description": "TDD phase missing from implementation",
            "suggestions": [
                "WHY: The {phase} phase is a required step in the 14-phase TDD cycle - it serves a critical purpose in the development workflow.\n"
                "HOW: Add the missing phase to the phase_execution_log by following the 14-phase sequence defined in the nWave methodology.\n"
                "ACTION: Review the step file to locate where {phase} should be inserted in the TDD cycle sequence, then add its execution record with appropriate status and outcomes.",
                "WHY: Each TDD phase is necessary for ensuring proper code quality, testing rigor, and refactoring discipline - skipping phases creates gaps in the development process.\n"
                "HOW: Consult the 14-phase TDD template to understand what {phase} requires and why it is important for your feature implementation.\n"
                "ACTION: Add the {phase} phase to your development workflow to ensure complete coverage of all required development steps and quality validations.",
            ],
        },
    }

    def generate_recovery_suggestions(
        self,
        failure_type: str,
        context: Dict[str, Any],
    ) -> List[str]:
        """
        Generate recovery suggestions for a specific failure type.

        Args:
            failure_type: Type of failure (e.g., 'abandoned_phase', 'silent_completion')
            context: Dictionary with contextual information (phase, step_file, transcript_path, etc.)

        Returns:
            List of recovery suggestions as strings with actionable guidance
        """
        if failure_type not in self.FAILURE_MODE_TEMPLATES:
            return [f"Unknown failure mode: {failure_type}. Please consult documentation."]

        template = self.FAILURE_MODE_TEMPLATES[failure_type]
        suggestion_templates = template["suggestions"]

        # Format suggestions with context values, providing defaults for optional fields
        suggestions = []
        for suggestion_template in suggestion_templates:
            # Create a safe format context with defaults
            safe_context = {
                "phase": context.get("phase", "UNKNOWN_PHASE"),
                "step_file": context.get("step_file", "unknown_step_file.json"),
                "transcript_path": context.get("transcript_path", "/path/to/transcript.log"),
                "section_name": context.get("section_name", "section"),
            }
            # Add any other context values not in defaults
            for key, value in context.items():
                if key not in safe_context:
                    safe_context[key] = value

            formatted = suggestion_template.format(**safe_context)
            suggestions.append(formatted)

        return suggestions

    def format_suggestion(
        self,
        why_text: str,
        how_text: str,
        actionable_command: str,
    ) -> str:
        """
        Format a recovery suggestion with WHY, HOW, and actionable elements.

        Args:
            why_text: Explanation of why the error occurred
            how_text: Explanation of how the fix resolves the issue
            actionable_command: Specific command or action to take

        Returns:
            Formatted suggestion string combining all components
        """
        return f"WHY: {why_text}\n\nHOW: {how_text}\n\nACTION: {actionable_command}"

    def handle_failure(
        self,
        step_file_path: str,
        failure_type: str,
        context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Handle a failure by generating and persisting recovery suggestions to step file.

        Args:
            step_file_path: Path to the step file JSON
            failure_type: Type of failure
            context: Context dictionary with failure details (phase, transcript_path, etc.)

        Returns:
            Dictionary with updated state including recovery_suggestions
        """
        # Generate suggestions
        suggestions = self.generate_recovery_suggestions(failure_type, context)

        # Load step file
        step_file = Path(step_file_path)
        step_data = json.loads(step_file.read_text())

        # Update step state with recovery suggestions
        if "state" not in step_data:
            step_data["state"] = {}

        step_data["state"]["recovery_suggestions"] = suggestions

        # Add failure reason if provided
        if "failure_reason" in context:
            step_data["state"]["failure_reason"] = context["failure_reason"]

        # Persist to file
        step_file.write_text(json.dumps(step_data, indent=2))

        return step_data["state"]
