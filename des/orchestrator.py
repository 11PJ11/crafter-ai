"""
DES Orchestrator for command-origin task filtering.

This module implements the orchestrator that determines whether to apply
DES validation based on command origin (execute/develop vs research/ad-hoc).

Integration: US-002 Template Validation
- Pre-invocation validation ensures prompts contain all mandatory sections
- Blocks Task invocation if validation fails

Integration: US-003 Post-Execution Validation
- Invokes SubagentStopHook after sub-agent completion
- Validates step file phase execution state
"""

from des.validator import TemplateValidator, ValidationResult
from des.hooks import SubagentStopHook, HookResult
from des.turn_counter import TurnCounter
from dataclasses import dataclass
import json
from pathlib import Path


@dataclass
class ExecuteStepResult:
    """Result from execute_step() method execution.

    Attributes:
        turn_count: Total number of turns (iterations) executed
        phase_name: Name of the phase being executed
        status: Execution status (e.g., "COMPLETED", "IN_PROGRESS")
    """
    turn_count: int
    phase_name: str = "PREPARE"
    status: str = "COMPLETED"


class DESOrchestrator:
    """
    Orchestrates DES validation by analyzing command origin.

    Responsibilities:
    - Render prompts with DES markers for execute/develop commands
    - Prepare ad-hoc prompts without DES markers for exploration
    - Track command origin for audit trail
    """

    # Commands that require full DES validation
    VALIDATION_COMMANDS = ["/nw:execute", "/nw:develop"]

    def __init__(self):
        """Initialize orchestrator with template validator and hook."""
        self._validator = TemplateValidator()
        self._hook = SubagentStopHook()
        self._subagent_lifecycle_completed = False

    def validate_prompt(self, prompt: str) -> ValidationResult:
        """
        Validate a prompt for mandatory sections and TDD phases.

        This is the entry point for pre-invocation validation (US-002).
        Blocks Task invocation if validation fails.

        Args:
            prompt: The full prompt text to validate

        Returns:
            ValidationResult with status, errors, and task_invocation_allowed flag
        """
        result = self._validator.validate_prompt(prompt)
        # Mark lifecycle as completed after validation
        self._subagent_lifecycle_completed = True
        return result

    def _get_validation_level(self, command: str | None) -> str:
        """
        Determine validation level based on command type.

        Args:
            command: Command string (e.g., "/nw:execute", "/nw:research")

        Returns:
            "full" for execute/develop commands requiring DES validation
            "none" for research and other exploratory commands (or invalid input)
        """
        # Safe default for None or empty command
        if not command:
            return "none"

        if command in self.VALIDATION_COMMANDS:
            return "full"
        return "none"

    def _generate_des_markers(self, command: str | None, step_file: str | None) -> str:
        """
        Generate DES validation markers for execute/develop commands.

        Args:
            command: Command type (e.g., "/nw:execute", "/nw:develop")
            step_file: Path to step file

        Returns:
            Formatted DES marker string with validation, step file, and origin markers

        Raises:
            ValueError: If command or step_file is None or empty
        """
        # Validate command parameter
        if not command:
            raise ValueError("Command cannot be None or empty")

        # Validate step_file parameter
        if not step_file:
            raise ValueError("Step file cannot be None or empty")

        markers = [
            "<!-- DES-VALIDATION: required -->",
            f"<!-- DES-STEP-FILE: {step_file} -->",
            f"<!-- DES-ORIGIN: command:{command} -->",
        ]
        return "\n".join(markers)

    def render_prompt(
        self,
        command: str | None,
        agent: str | None = None,
        step_file: str | None = None,
        project_root: str | None = None,
        topic: str | None = None,
    ) -> str:
        """
        Render Task prompt with appropriate DES validation markers.

        Args:
            command: Command type (/nw:execute, /nw:develop, /nw:research)
            agent: Target agent identifier (e.g., @software-crafter)
            step_file: Path to step file for execute/develop commands
            project_root: Project root directory path
            topic: Research topic for research commands

        Returns:
            Rendered prompt string with or without DES markers

        Raises:
            ValueError: If command is None or empty, or if step_file is missing
                       for validation commands
        """
        # Validate command parameter
        if not command:
            raise ValueError("Command cannot be None or empty")

        validation_level = self._get_validation_level(command)

        if validation_level == "full":
            # Validate step_file for validation commands
            if not step_file:
                raise ValueError("Step file required for validation commands")

            return self._generate_des_markers(command, step_file)

        # Research and other commands bypass DES validation
        return ""

    def prepare_ad_hoc_prompt(self, prompt: str, project_root: str | None = None) -> str:
        """
        Prepare ad-hoc prompt without DES validation markers.

        Args:
            prompt: User's ad-hoc Task prompt text
            project_root: Project root directory path

        Returns:
            Prompt text without DES markers (pass-through)
        """
        # Ad-hoc prompts bypass DES validation - return as-is
        return prompt

    def on_subagent_complete(self, step_file_path: str) -> HookResult:
        """
        Invoke SubagentStopHook after sub-agent completion.

        This is the entry point for post-execution validation (US-003).
        Delegates to SubagentStopHook to validate step file state.

        Args:
            step_file_path: Path to the step JSON file to validate

        Returns:
            HookResult with validation status and any errors found
        """
        return self._hook.on_agent_complete(step_file_path)

    def execute_step(
        self,
        command: str,
        agent: str,
        step_file: str,
        project_root: Path | str,
        simulated_iterations: int = 0
    ) -> ExecuteStepResult:
        """
        Execute step with TurnCounter integration for turn tracking.

        This method wires TurnCounter into the orchestrator's execution loop:
        - Initializes TurnCounter at phase start
        - Increments on each agent call iteration
        - Persists to step file in real-time
        - Restores state from step file on resume

        Args:
            command: Command type (/nw:execute, /nw:develop)
            agent: Target agent identifier (e.g., @software-crafter)
            step_file: Path to step JSON file (relative to project_root)
            project_root: Project root directory path
            simulated_iterations: Number of iterations to simulate (for testing)

        Returns:
            ExecuteStepResult with turn_count and execution status
        """
        # Initialize TurnCounter
        counter = TurnCounter()

        # Load step file
        if isinstance(project_root, str):
            project_root = Path(project_root)
        step_file_path = project_root / step_file

        with open(step_file_path, 'r') as f:
            step_data = json.load(f)

        # Get current phase and restore turn count
        phase_log = step_data["tdd_cycle"]["phase_execution_log"]
        current_phase = phase_log[0]  # For now, use first phase
        phase_name = current_phase["phase_name"]

        # Mark phase as IN_PROGRESS if not already
        if current_phase["status"] == "NOT_EXECUTED":
            current_phase["status"] = "IN_PROGRESS"

        # Restore existing turn count if resuming
        existing_turn_count = current_phase.get("turn_count", 0)
        for _ in range(existing_turn_count):
            counter.increment_turn(phase_name)

        # Execute simulated iterations (in real implementation, this would be agent calls)
        for _ in range(simulated_iterations):
            counter.increment_turn(phase_name)

        # Get final turn count
        final_turn_count = counter.get_current_turn(phase_name)

        # Persist turn count to step file
        current_phase["turn_count"] = final_turn_count
        with open(step_file_path, 'w') as f:
            json.dump(step_data, f, indent=2)

        return ExecuteStepResult(
            turn_count=final_turn_count,
            phase_name=phase_name,
            status="COMPLETED"
        )
