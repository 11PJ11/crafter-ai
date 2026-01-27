"""Test implementation of post-execution hook adapter."""

from src.des.ports.driver_ports.hook_port import HookPort, HookResult


class MockedSubagentStopHook(HookPort):
    """Test implementation of post-execution hook.

    Returns predefined results without file I/O for fast, deterministic testing.
    Tracks call history for verification in tests.
    """

    def __init__(self, predefined_result: HookResult = None):
        """Initialize with optional predefined result.

        Args:
            predefined_result: HookResult to return from on_agent_complete.
                             Defaults to PASSED status if not provided.
        """
        self._result = predefined_result or HookResult(validation_status="PASSED")
        self.call_count = 0
        self.last_step_file_path = None

    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Return predefined result without file I/O.

        Args:
            step_file_path: Path to step file (recorded but not read)

        Returns:
            Predefined HookResult configured at initialization
        """
        self.call_count += 1
        self.last_step_file_path = step_file_path
        return self._result
