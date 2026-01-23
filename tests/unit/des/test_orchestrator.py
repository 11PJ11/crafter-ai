"""
Unit tests for DESOrchestrator class.

Tests the orchestrator's ability to render prompts with DES validation markers
based on command type (execute, develop, research, ad-hoc).
"""


class TestDESOrchestrator:
    """Unit tests for DESOrchestrator class."""

    def test_orchestrator_has_render_prompt_method(self):
        """
        GIVEN DESOrchestrator class instantiated
        WHEN checking for render_prompt method
        THEN method should exist and be callable
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        assert hasattr(orchestrator, "render_prompt")
        assert callable(orchestrator.render_prompt)

    def test_orchestrator_has_prepare_ad_hoc_prompt_method(self):
        """
        GIVEN DESOrchestrator class instantiated
        WHEN checking for prepare_ad_hoc_prompt method
        THEN method should exist and be callable
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        assert hasattr(orchestrator, "prepare_ad_hoc_prompt")
        assert callable(orchestrator.prepare_ad_hoc_prompt)

    def test_render_prompt_returns_string(self):
        """
        GIVEN DESOrchestrator instance
        WHEN render_prompt is called
        THEN it should return a string
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        result = orchestrator.render_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            step_file="steps/01-01.json",
            project_root="/tmp/test",
        )
        assert isinstance(result, str)

    def test_prepare_ad_hoc_prompt_returns_string(self):
        """
        GIVEN DESOrchestrator instance
        WHEN prepare_ad_hoc_prompt is called
        THEN it should return a string
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        result = orchestrator.prepare_ad_hoc_prompt(
            prompt="Find all uses of UserRepository", project_root="/tmp/test"
        )
        assert isinstance(result, str)

    def test_execute_command_includes_validation_marker(self):
        """
        GIVEN /nw:execute command
        WHEN render_prompt is called
        THEN prompt includes <!-- DES-VALIDATION: required --> marker
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        prompt = orchestrator.render_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            step_file="steps/01-01.json",
            project_root="/tmp/test",
        )
        assert "<!-- DES-VALIDATION: required -->" in prompt

    def test_execute_command_includes_step_file_marker(self):
        """
        GIVEN /nw:execute command with step file
        WHEN render_prompt is called
        THEN prompt includes step file marker
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        prompt = orchestrator.render_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            step_file="steps/01-01.json",
            project_root="/tmp/test",
        )
        assert "<!-- DES-STEP-FILE: steps/01-01.json -->" in prompt

    def test_execute_command_includes_origin_marker(self):
        """
        GIVEN /nw:execute command
        WHEN render_prompt is called
        THEN prompt includes origin marker
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        prompt = orchestrator.render_prompt(
            command="/nw:execute",
            agent="@software-crafter",
            step_file="steps/01-01.json",
            project_root="/tmp/test",
        )
        assert "<!-- DES-ORIGIN: command:/nw:execute -->" in prompt

    def test_develop_command_includes_validation_marker(self):
        """
        GIVEN /nw:develop command
        WHEN render_prompt is called
        THEN prompt includes DES-VALIDATION marker
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        prompt = orchestrator.render_prompt(
            command="/nw:develop",
            agent="@software-crafter",
            step_file="steps/01-01.json",
            project_root="/tmp/test",
        )
        assert "<!-- DES-VALIDATION: required -->" in prompt

    def test_research_command_excludes_validation_marker(self):
        """
        GIVEN /nw:research command
        WHEN render_prompt is called
        THEN prompt does NOT include DES-VALIDATION marker
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        prompt = orchestrator.render_prompt(
            command="/nw:research",
            topic="authentication patterns",
            project_root="/tmp/test",
        )
        assert "<!-- DES-VALIDATION:" not in prompt

    def test_ad_hoc_prompt_excludes_des_markers(self):
        """
        GIVEN ad-hoc prompt
        WHEN prepare_ad_hoc_prompt is called
        THEN prompt does NOT include any DES markers
        """
        from des.orchestrator import DESOrchestrator

        orchestrator = DESOrchestrator()
        prompt = orchestrator.prepare_ad_hoc_prompt(
            prompt="Find all uses of UserRepository", project_root="/tmp/test"
        )
        assert "<!-- DES-VALIDATION:" not in prompt
        assert "<!-- DES-STEP-FILE:" not in prompt
        assert "<!-- DES-ORIGIN:" not in prompt
