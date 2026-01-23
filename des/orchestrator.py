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

    def _get_validation_level(self, command: str) -> str:
        """
        Determine validation level based on command type.

        Args:
            command: Command string (e.g., "/nw:execute", "/nw:research")

        Returns:
            "full" for execute/develop commands requiring DES validation
            "none" for research and other exploratory commands
        """
        if command in self.VALIDATION_COMMANDS:
            return "full"
        return "none"

    def _generate_des_markers(self, command: str, step_file: str) -> str:
        """
        Generate DES validation markers for execute/develop commands.

        Args:
            command: Command type (e.g., "/nw:execute", "/nw:develop")
            step_file: Path to step file

        Returns:
            Formatted DES marker string with validation, step file, and origin markers
        """
        markers = [
            "<!-- DES-VALIDATION: required -->",
            f"<!-- DES-STEP-FILE: {step_file} -->",
            f"<!-- DES-ORIGIN: command:{command} -->",
        ]
        return "\n".join(markers)

    def render_prompt(
        self,
        command: str,
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
        """
        validation_level = self._get_validation_level(command)

        if validation_level == "full":
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
