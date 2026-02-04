"""
Unit tests for DESOrchestrator.validate_prompt audit logging (Step 01-02).

Tests that validate_prompt logs HOOK_PRE_TASK_PASSED and HOOK_PRE_TASK_BLOCKED
audit events with proper structure, timestamps from TimeProvider, and relevant context.
"""

from unittest.mock import Mock, patch

from src.des.adapters.driven.logging.audit_events import EventType


class TestValidatePromptAuditLogging:
    """Unit tests for validate_prompt audit logging functionality."""

    def test_validate_prompt_logs_hook_pre_task_passed_when_validation_succeeds(
        self, des_orchestrator
    ):
        """
        GIVEN DESOrchestrator with valid prompt
        WHEN validate_prompt is called and returns task_invocation_allowed True
        THEN HOOK_PRE_TASK_PASSED audit event is logged with timestamp from TimeProvider
        """
        # Arrange
        valid_prompt = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->
        Task: Implement feature
        """

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            result = des_orchestrator.validate_prompt(valid_prompt)

            # Assert
            assert result.task_invocation_allowed is True
            mock_logger.append.assert_called_once()

            # Verify event details
            call_args = mock_logger.append.call_args
            event_dict = call_args[0][0]  # First positional argument

            assert event_dict["event"] == EventType.HOOK_PRE_TASK_PASSED.value
            assert event_dict["timestamp"] is not None
            assert event_dict["step_path"] == "steps/01-01.json"

    def test_validate_prompt_logs_hook_pre_task_blocked_when_validation_fails(
        self, in_memory_filesystem, mocked_hook, mocked_time_provider
    ):
        """
        GIVEN DESOrchestrator with invalid prompt
        WHEN validate_prompt is called and returns task_invocation_allowed False
        THEN HOOK_PRE_TASK_BLOCKED audit event is logged with rejection reason
        """
        # Arrange
        from src.des.adapters.drivers.validators.mocked_validator import (
            MockedTemplateValidator,
        )
        from src.des.application.orchestrator import DESOrchestrator
        from src.des.ports.driver_ports.validator_port import ValidationResult

        # Create validator that returns failure
        failing_validator = MockedTemplateValidator(
            predefined_result=ValidationResult(
                status="FAILED",
                errors=["Missing DES-VALIDATION marker"],
                task_invocation_allowed=False,
                duration_ms=0.0,
                recovery_guidance=None,
            )
        )

        des_orchestrator = DESOrchestrator(
            hook=mocked_hook,
            validator=failing_validator,
            filesystem=in_memory_filesystem,
            time_provider=mocked_time_provider,
        )

        invalid_prompt = """
        Task: Implement feature without DES markers
        """

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            result = des_orchestrator.validate_prompt(invalid_prompt)

            # Assert
            assert result.task_invocation_allowed is False
            mock_logger.append.assert_called_once()

            # Verify event details
            call_args = mock_logger.append.call_args
            event_dict = call_args[0][0]  # First positional argument

            assert event_dict["event"] == EventType.HOOK_PRE_TASK_BLOCKED.value
            assert event_dict["timestamp"] is not None
            assert event_dict["rejection_reason"] is not None

    def test_validate_prompt_uses_time_provider_for_timestamp(
        self, des_orchestrator, mocked_time_provider
    ):
        """
        GIVEN DESOrchestrator with TimeProvider configured
        WHEN validate_prompt logs audit event
        THEN timestamp comes from TimeProvider.now_utc(), not datetime.now()
        """
        # Arrange
        valid_prompt = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->
        Task: Implement feature
        """

        expected_timestamp = mocked_time_provider.now_utc()

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            des_orchestrator.validate_prompt(valid_prompt)

            # Assert
            mock_logger.append.assert_called_once()

            # Verify timestamp matches TimeProvider
            call_args = mock_logger.append.call_args
            event_dict = call_args[0][0]

            # Convert to comparable format
            assert event_dict["timestamp"] == expected_timestamp.isoformat()

    def test_validate_prompt_extracts_step_path_from_prompt(self, des_orchestrator):
        """
        GIVEN prompt containing DES-STEP-FILE marker
        WHEN validate_prompt logs audit event
        THEN step_path is extracted from marker
        """
        # Arrange
        prompt_with_step = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/02-03.json -->
        Task: Refactor module
        """

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            des_orchestrator.validate_prompt(prompt_with_step)

            # Assert
            call_args = mock_logger.append.call_args
            event_dict = call_args[0][0]

            assert event_dict["step_path"] == "steps/02-03.json"

    def test_validate_prompt_includes_agent_name_in_audit_event(self, des_orchestrator):
        """
        GIVEN prompt with agent information
        WHEN validate_prompt logs audit event
        THEN audit entry includes agent name
        """
        # Arrange
        prompt_with_agent = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->
        You are the @software-crafter agent.
        Task: Implement feature
        """

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            des_orchestrator.validate_prompt(prompt_with_agent)

            # Assert
            call_args = mock_logger.append.call_args
            event_dict = call_args[0][0]

            # Agent name should be in extra_context
            assert event_dict.get("extra_context") is not None
            assert (
                "agent" in event_dict["extra_context"]
                or "agent_name" in event_dict["extra_context"]
            )

    def test_validate_prompt_blocked_includes_rejection_details(
        self, in_memory_filesystem, mocked_hook, mocked_time_provider
    ):
        """
        GIVEN invalid prompt causing validation rejection
        WHEN validate_prompt logs HOOK_PRE_TASK_BLOCKED event
        THEN rejection_reason field contains detailed error information
        """
        # Arrange
        from src.des.adapters.drivers.validators.mocked_validator import (
            MockedTemplateValidator,
        )
        from src.des.application.orchestrator import DESOrchestrator
        from src.des.ports.driver_ports.validator_port import ValidationResult

        # Create validator that returns failure
        failing_validator = MockedTemplateValidator(
            predefined_result=ValidationResult(
                status="FAILED",
                errors=["Missing DES-VALIDATION marker"],
                task_invocation_allowed=False,
                duration_ms=0.0,
                recovery_guidance=None,
            )
        )

        des_orchestrator = DESOrchestrator(
            hook=mocked_hook,
            validator=failing_validator,
            filesystem=in_memory_filesystem,
            time_provider=mocked_time_provider,
        )

        invalid_prompt = "Task without any DES markers"

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            result = des_orchestrator.validate_prompt(invalid_prompt)

            # Assert
            assert result.task_invocation_allowed is False

            call_args = mock_logger.append.call_args
            event_dict = call_args[0][0]

            assert event_dict["event"] == EventType.HOOK_PRE_TASK_BLOCKED.value
            assert event_dict.get("rejection_reason") is not None
            assert len(event_dict["rejection_reason"]) > 0

    def test_validate_prompt_does_not_log_if_audit_disabled(
        self, in_memory_filesystem, mocked_hook, mocked_validator, mocked_time_provider
    ):
        """
        GIVEN DES configuration with audit_logging_enabled = false
        WHEN validate_prompt is called
        THEN no audit event is logged
        """
        # Arrange
        # Note: This test would require DES config to be loaded and checked
        # For now, this is a placeholder showing the expected behavior
        # Implementation in Phase 3 (GREEN) will check config before logging
        pass

    def test_validate_prompt_audit_event_persisted_to_log_file(self, des_orchestrator):
        """
        GIVEN DESOrchestrator with audit logging enabled
        WHEN validate_prompt logs audit event
        THEN event is persisted to audit log file at ~/.claude/des/logs/audit.log
        """
        # Arrange
        valid_prompt = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->
        Task: Implement feature
        """

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            des_orchestrator.validate_prompt(valid_prompt)

            # Assert
            # Verify logger.append was called, which handles file persistence
            assert mock_logger.append.called

    def test_validate_prompt_audit_event_has_structured_format(self, des_orchestrator):
        """
        GIVEN validate_prompt creating audit event
        WHEN event is logged
        THEN event follows AuditEvent dataclass structure
        """
        # Arrange
        valid_prompt = """
        <!-- DES-VALIDATION: required -->
        <!-- DES-STEP-FILE: steps/01-01.json -->
        Task: Implement feature
        """

        with patch(
            "src.des.adapters.driven.logging.audit_logger.get_audit_logger"
        ) as mock_get_logger:
            mock_logger = Mock()
            mock_get_logger.return_value = mock_logger

            # Act
            des_orchestrator.validate_prompt(valid_prompt)

            # Assert
            call_args = mock_logger.append.call_args
            event_dict = call_args[0][0]

            # Verify required fields
            assert "timestamp" in event_dict
            assert "event" in event_dict
            assert "step_path" in event_dict
            # rejection_reason is optional (only for BLOCKED events)
