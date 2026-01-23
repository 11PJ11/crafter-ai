"""
DES Orchestrator for command-origin task filtering.

This module implements the orchestrator that determines whether to apply
DES validation based on command origin (execute/develop vs research/ad-hoc).
"""


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
