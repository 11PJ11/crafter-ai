"""
Unit tests for TIMEOUT_INSTRUCTION generation in DESOrchestrator.render_full_prompt().

These tests verify that the orchestrator correctly generates the TIMEOUT_INSTRUCTION
section when rendering prompts for validation commands (/nw:execute, /nw:develop).

Test Coverage:
- render_full_prompt() generates TIMEOUT_INSTRUCTION section
- Section includes all 4 required elements (budget, checkpoints, early exit, logging)
- Section only generated for validation commands (not research/ad-hoc)
- Integration with TimeoutInstructionTemplate.render()
"""

import pytest


class TestOrchestratorTimeoutInstruction:
    """Unit tests for TIMEOUT_INSTRUCTION generation in orchestrator."""

    def test_render_full_prompt_includes_timeout_instruction_for_execute(
        self, des_orchestrator, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN /nw:execute command
        WHEN render_full_prompt is called
        THEN prompt includes TIMEOUT_INSTRUCTION section header
        """
        # GIVEN
        command = "/nw:execute"
        agent = "@software-crafter"
        step_file = str(minimal_step_file.relative_to(tmp_project_root))

        # WHEN
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent=agent,
            step_file=step_file,
            project_root=tmp_project_root,
        )

        # THEN
        assert "TIMEOUT_INSTRUCTION" in prompt
        assert "## TIMEOUT_INSTRUCTION" in prompt or "# TIMEOUT_INSTRUCTION" in prompt

    def test_render_full_prompt_includes_timeout_instruction_for_develop(
        self, des_orchestrator, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN /nw:develop command
        WHEN render_full_prompt is called
        THEN prompt includes TIMEOUT_INSTRUCTION section header
        """
        # GIVEN
        command = "/nw:develop"
        agent = "@software-crafter"
        step_file = str(minimal_step_file.relative_to(tmp_project_root))

        # WHEN
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent=agent,
            step_file=step_file,
            project_root=tmp_project_root,
        )

        # THEN
        assert "TIMEOUT_INSTRUCTION" in prompt

    def test_render_full_prompt_timeout_includes_turn_budget(
        self, des_orchestrator, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN /nw:execute command
        WHEN render_full_prompt is called
        THEN TIMEOUT_INSTRUCTION includes turn budget (~50)
        """
        # GIVEN
        command = "/nw:execute"
        step_file = str(minimal_step_file.relative_to(tmp_project_root))

        # WHEN
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent="@software-crafter",
            step_file=step_file,
            project_root=tmp_project_root,
        )

        # THEN
        turn_budget_patterns = ["50 turn", "approximately 50", "~50", "around 50"]
        assert any(
            pattern in prompt.lower() for pattern in turn_budget_patterns
        ), "Turn budget (~50) not found in TIMEOUT_INSTRUCTION"

    def test_render_full_prompt_timeout_includes_progress_checkpoints(
        self, des_orchestrator, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN /nw:execute command
        WHEN render_full_prompt is called
        THEN TIMEOUT_INSTRUCTION includes progress checkpoints
        """
        # GIVEN
        command = "/nw:execute"
        step_file = str(minimal_step_file.relative_to(tmp_project_root))

        # WHEN
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent="@software-crafter",
            step_file=step_file,
            project_root=tmp_project_root,
        )

        # THEN
        checkpoint_indicators = [
            "turn 10" in prompt.lower() or "~10" in prompt,
            "turn 25" in prompt.lower() or "~25" in prompt,
            "turn 40" in prompt.lower() or "~40" in prompt,
        ]
        assert any(checkpoint_indicators), "Progress checkpoints not found"

    def test_render_full_prompt_timeout_includes_early_exit_protocol(
        self, des_orchestrator, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN /nw:execute command
        WHEN render_full_prompt is called
        THEN TIMEOUT_INSTRUCTION includes early exit protocol
        """
        # GIVEN
        command = "/nw:execute"
        step_file = str(minimal_step_file.relative_to(tmp_project_root))

        # WHEN
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent="@software-crafter",
            step_file=step_file,
            project_root=tmp_project_root,
        )

        # THEN
        early_exit_indicators = [
            "early exit" in prompt.lower(),
            "cannot complete" in prompt.lower(),
            "save progress" in prompt.lower(),
        ]
        assert any(early_exit_indicators), "Early exit protocol not found"

    def test_render_full_prompt_timeout_includes_turn_logging(
        self, des_orchestrator, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN /nw:execute command
        WHEN render_full_prompt is called
        THEN TIMEOUT_INSTRUCTION includes turn logging instruction
        """
        # GIVEN
        command = "/nw:execute"
        step_file = str(minimal_step_file.relative_to(tmp_project_root))

        # WHEN
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent="@software-crafter",
            step_file=step_file,
            project_root=tmp_project_root,
        )

        # THEN
        logging_indicators = [
            "log" in prompt.lower() and "turn" in prompt.lower(),
            "[turn" in prompt.lower(),
        ]
        assert any(logging_indicators), "Turn logging instruction not found"

    def test_render_full_prompt_raises_for_non_validation_command(
        self, des_orchestrator, tmp_project_root
    ):
        """
        GIVEN non-validation command (/nw:research)
        WHEN render_full_prompt is called
        THEN ValueError is raised
        """
        # GIVEN
        command = "/nw:research"
        agent = "@researcher"
        step_file = "steps/research.json"

        # WHEN/THEN
        with pytest.raises(ValueError, match="only supports validation commands"):
            des_orchestrator.render_full_prompt(
                command=command,
                agent=agent,
                step_file=step_file,
                project_root=tmp_project_root,
            )

    def test_render_full_prompt_includes_des_markers(
        self, des_orchestrator, tmp_project_root, minimal_step_file
    ):
        """
        GIVEN /nw:execute command
        WHEN render_full_prompt is called
        THEN prompt includes DES validation markers
        """
        # GIVEN
        command = "/nw:execute"
        step_file = str(minimal_step_file.relative_to(tmp_project_root))

        # WHEN
        prompt = des_orchestrator.render_full_prompt(
            command=command,
            agent="@software-crafter",
            step_file=step_file,
            project_root=tmp_project_root,
        )

        # THEN
        assert "<!-- DES-VALIDATION: required -->" in prompt
        assert f"<!-- DES-STEP-FILE: {step_file} -->" in prompt
        assert "<!-- DES-ORIGIN: command:/nw:execute -->" in prompt
