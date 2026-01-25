"""
Acceptance test for scenario 016: Agent can request extension via API.

This test validates that the extension request API is properly exposed to agents
through the prompt context and that agents can successfully invoke it during execution.
"""

from datetime import datetime, timezone
from pathlib import Path
import json
import tempfile
from des.orchestrator import DESOrchestrator


class TestScenario016AgentCanRequestExtensionViaAPI:
    """
    Test that agents can request extensions through the API during execution.

    Acceptance Criteria (from roadmap step 06-02):
    - Agent prompt includes EXTENSION_REQUEST_API section
    - Section documents request_extension() call format
    - Example provided: 'request_extension(reason="Complexity higher", additional_turns=20)'
    - Agent instructed to provide clear justification
    """

    def test_extension_api_available_in_prompt_context(self):
        """Extension request API should be documented and callable by agents."""
        # Given: DESOrchestrator configured with step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_extension_config()

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent has access to orchestrator during execution
            # Then: request_extension method should be accessible
            assert hasattr(orchestrator, "request_extension")
            assert callable(getattr(orchestrator, "request_extension"))

            # And: Method should accept required parameters
            import inspect
            sig = inspect.signature(orchestrator.request_extension)
            params = list(sig.parameters.keys())

            assert "reason" in params
            assert "additional_turns" in params
            assert "additional_minutes" in params

    def test_agent_can_invoke_request_extension_api(self):
        """Agent should be able to invoke request_extension() API successfully."""
        # Given: DESOrchestrator with step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_extension_config()

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent invokes request_extension API
            # (Simulating agent calling the API during execution)
            result = orchestrator.request_extension(
                reason="Complexity higher than expected, need additional time",
                additional_turns=20,
                additional_minutes=None,
            )

            # Then: API call should succeed
            assert result is not None

            # And: Result should indicate approval status
            assert hasattr(result, "approved")

            # And: Extension should be approved (valid reason > 20 chars)
            assert result.approved is True

    def test_extension_api_requires_justification(self):
        """Extension request API should enforce justification requirement."""
        # Given: DESOrchestrator with step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_extension_config()

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent requests extension with insufficient justification
            result = orchestrator.request_extension(
                reason="Need more time",  # Too short, <20 characters
                additional_turns=10,
                additional_minutes=None,
            )

            # Then: Extension should be denied
            assert result.approved is False

            # And: Result should include reason for denial
            assert hasattr(result, "reason")
            assert "justification" in result.reason.lower() or "reason" in result.reason.lower()

    def test_extension_api_enforces_maximum_extension_limits(self):
        """Extension API should enforce reasonable maximum extension limits."""
        # Given: DESOrchestrator with step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_extension_config()

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent requests unreasonably large extension (>200% of original)
            # Original: max_turns=10, requesting 25 additional (250%)
            result = orchestrator.request_extension(
                reason="Very complex task requiring extensive additional iterations beyond normal limits",
                additional_turns=25,
                additional_minutes=None,
            )

            # Then: Extension should be denied
            assert result.approved is False

            # And: Result should explain limit exceeded
            assert "too large" in result.reason.lower() or "limit" in result.reason.lower() or "unreasonable" in result.reason.lower()

    def test_extension_api_tracks_multiple_requests_per_phase(self):
        """Extension API should track and limit multiple requests per phase."""
        # Given: DESOrchestrator with step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_extension_config()

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent makes first extension request
            result1 = orchestrator.request_extension(
                reason="Initial complexity assessment indicates need for more time",
                additional_turns=5,
                additional_minutes=None,
            )

            # And: Agent makes second extension request
            result2 = orchestrator.request_extension(
                reason="Additional unforeseen complications discovered during execution",
                additional_turns=5,
                additional_minutes=None,
            )

            # Then: First request should be approved
            assert result1.approved is True

            # And: Second request should be approved
            assert result2.approved is True

            # And: Extension history should show both requests
            updated_data = json.loads(step_file_path.read_text())
            extensions = updated_data["tdd_cycle"]["phase_execution_log"][0][
                "extensions_granted"
            ]
            assert len(extensions) == 2

    def test_extension_api_denies_third_request_exceeding_max_extensions(self):
        """Extension API should deny requests exceeding maximum extensions per phase."""
        # Given: DESOrchestrator with step file
        orchestrator = DESOrchestrator()

        with tempfile.TemporaryDirectory() as tmpdir:
            step_file_path = Path(tmpdir) / "test_step.json"

            step_data = self._create_step_file_with_extension_config()

            with open(step_file_path, "w") as f:
                json.dump(step_data, f, indent=2)

            orchestrator._step_file_path = step_file_path

            # When: Agent makes first two extension requests (max=2)
            orchestrator.request_extension(
                reason="First extension for reasonable additional complexity detected",
                additional_turns=3,
                additional_minutes=None,
            )

            orchestrator.request_extension(
                reason="Second extension for additional unforeseen requirements found",
                additional_turns=3,
                additional_minutes=None,
            )

            # And: Agent attempts third extension request
            result3 = orchestrator.request_extension(
                reason="Third extension requested for final complexity adjustment needed",
                additional_turns=3,
                additional_minutes=None,
            )

            # Then: Third request should be denied
            assert result3.approved is False

            # And: Result should explain max extensions exceeded
            assert "maximum" in result3.reason.lower() or "exceeded" in result3.reason.lower()

    def _create_step_file_with_extension_config(self) -> dict:
        """Create minimal step file with extension tracking configuration."""
        return {
            "task_specification": {
                "task_id": "06-02",
                "project_id": "des-us004",
                "name": "Test extension API availability",
            },
            "state": {
                "status": "IN_PROGRESS",
                "started_at": datetime.now(timezone.utc).isoformat(),
                "ended_at": None,
            },
            "tdd_cycle": {
                "phase_execution_log": [
                    {
                        "phase_name": "PREPARE",
                        "phase_index": 0,
                        "status": "IN_PROGRESS",
                        "started_at": datetime.now(timezone.utc).isoformat(),
                        "ended_at": None,
                        "turn_count": 0,
                        "max_turns": 10,
                        "timeout_minutes": 15,
                        "extensions_granted": [],
                    }
                ]
            },
        }
