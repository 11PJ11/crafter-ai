"""
RecoveryGuidanceHandler: Central recovery guidance system for task failure scenarios.

Provides recovery suggestions for different failure modes, helping developers
understand and resolve execution failures through educational context.
"""

import json
from pathlib import Path
from typing import List, Dict, Any, Optional


class SuggestionFormatter:
    """
    Formats recovery suggestions with WHY + HOW + actionable structure.

    Ensures consistent formatting across all recovery suggestions to improve
    readability and help junior developers understand:
    - WHY: Educational explanation of failure cause
    - HOW: Specific steps to fix the issue
    - ACTIONABLE: Command or file path to execute fix
    """

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
                "WHY: Your agent stopped during {phase} and left it marked IN_PROGRESS.\n"
                "HOW: Reset the phase status to NOT_EXECUTED so the system knows it can retry.\n"
                "ACTION: Review {transcript_path} for what went wrong, then run `/nw:execute` to try {phase} again.",
                "WHY: A phase stuck IN_PROGRESS blocks your system from continuing.\n"
                "HOW: Resetting clears the incomplete state and lets execution continue.\n"
                "ACTION: Update your step file: change state.tdd_cycle.{phase}.status to 'NOT_EXECUTED'.",
                "WHY: You need to understand why the agent stopped to fix the real problem.\n"
                "HOW: The transcript contains the error details and what the agent was doing.\n"
                "ACTION: Check the transcript at {transcript_path}, then run `/nw:execute @software-crafter '{step_file}'` to retry.",
            ],
        },
        "silent_completion": {
            "description": "Agent returned without updating step file",
            "suggestions": [
                "WHY: Your agent finished but didn't update the step file with what it did.\n"
                "HOW: Check the transcript to see if the agent hit an error or if it finished the work so that you understand what happened.\n"
                "ACTION: Review {transcript_path} to understand what happened, then manually update the phases based on what you see.",
                "WHY: The system doesn't know what phases were completed if the agent doesn't update them.\n"
                "HOW: Your prompt needs to tell the agent to save its progress to the step file, ensuring the state is tracked.\n"
                "ACTION: Make sure OUTCOME_RECORDING section is in your prompt with clear instructions to update the step file.",
                "WHY: Without phase updates, you can't see your progress or know what to do next.\n"
                "HOW: Add the missing phase status updates to match what the agent actually completed, so that progress is recorded.\n"
                "ACTION: Based on the transcript at {transcript_path}, manually set each completed phase's status and outcome.",
            ],
        },
        "missing_section": {
            "description": "Validation found missing mandatory section",
            "suggestions": [
                "WHY: Your prompt is missing {section_name}, which the agent needs to work properly.\n"
                "HOW: Add this section to your prompt template with the required content.\n"
                "ACTION: Update your prompt to include the {section_name} section with its required fields.",
                "WHY: Every section has a specific job - missing ones break the agent's workflow.\n"
                "HOW: Check what {section_name} should contain by looking at the format guide.\n"
                "ACTION: See docs/feature/des/discuss/prompt-specification.md for {section_name} format, then add it to your prompt.",
            ],
        },
        "invalid_outcome": {
            "description": "Phase marked EXECUTED without outcome",
            "suggestions": [
                "WHY: Your step file marks {phase} done but doesn't say what was done.\n"
                "HOW: Add a description of what happened in that phase.\n"
                "ACTION: Update state.tdd_cycle.{phase}.outcome with a brief description of what was completed.",
                "WHY: Without outcome descriptions, you can't review what each phase accomplished.\n"
                "HOW: Write what happened - tests passed, code refactored, bugs fixed, etc.\n"
                "ACTION: Add outcome text to {phase} describing the results and what was produced.",
            ],
        },
        "missing_phase": {
            "description": "TDD phase missing from implementation",
            "suggestions": [
                "WHY: Your step file is missing the {phase} phase, which is needed in the TDD cycle.\n"
                "HOW: Add it to the phase_execution_log in the right position following the 14-phase sequence.\n"
                "ACTION: Insert {phase} with status='NOT_EXECUTED' in the correct order in phase_execution_log.",
                "WHY: Every TDD phase has a job - skipping one creates gaps in code quality and testing.\n"
                "HOW: Check what {phase} does by reviewing the TDD template to understand why it's needed.\n"
                "ACTION: Add {phase} to your step file and execute it as part of your development workflow.",
            ],
        },
        "timeout_failure": {
            "description": "Task execution exceeded configured timeout threshold",
            "suggestions": [
                "WHY: Your task ran {actual_runtime_minutes} minutes but the timeout was set to {configured_timeout_minutes} minutes.\n"
                "HOW: Either speed up the code or increase the timeout limit.\n"
                "ACTION: Review {transcript_path} to find slow parts, optimize the code, then retry.",
                "WHY: The timeout is too short for your task. It ran {actual_runtime_minutes} minutes but needs at least that long.\n"
                "HOW: Increasing the timeout lets the task complete without interruption.\n"
                "ACTION: Set your timeout to {actual_runtime_minutes} minutes or higher, then retry.",
                "WHY: Timeout means your code or task is slower than expected.\n"
                "HOW: Make your code faster by removing unnecessary work or simplifying logic.\n"
                "ACTION: Profile the code at {transcript_path}, find bottlenecks, optimize them, and retry.",
            ],
        },
        "agent_crash": {
            "description": "Agent crashed with known transcript location",
            "suggestions": [
                "WHY: Your agent crashed during {phase}, leaving the work incomplete.\n"
                "HOW: Read the transcript to see what error happened.\n"
                "ACTION: Check {transcript_path} for the error message that caused the crash.",
                "WHY: Understanding what caused the crash helps you fix the problem.\n"
                "HOW: The transcript shows the full history and error that stopped the agent.\n"
                "ACTION: Review {transcript_path}, identify the failure, then decide: fix the error and retry, or adjust your configuration.",
                "WHY: Your {phase} phase can't continue until you fix the crash issue.\n"
                "HOW: Once you know the cause, reset the phase and retry with better conditions.\n"
                "ACTION: After reviewing {transcript_path}, reset {phase} to NOT_EXECUTED and run `/nw:execute` again.",
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
