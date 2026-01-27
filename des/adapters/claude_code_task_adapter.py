"""
ClaudeCodeTaskAdapter - production task invocation implementation.

Provides integration with the actual Claude Code Task tool for invoking
sub-agents in production environments.
"""
from typing import Dict, Any
from des.ports.task_invocation_port import TaskInvocationPort


class ClaudeCodeTaskAdapter(TaskInvocationPort):
    """
    Production task invocation adapter that uses the actual Task tool.

    This adapter integrates with Claude Code's Task tool to invoke
    sub-agents and return their results.
    """

    def invoke_task(self, prompt: str, agent: str) -> Dict[str, Any]:
        """
        Invoke a sub-agent task using the Claude Code Task tool.

        Args:
            prompt: The prompt to send to the sub-agent
            agent: The agent identifier to invoke

        Returns:
            Task result dictionary with keys:
            - success: bool
            - output: str (if successful)
            - error: str (if failed)
        """
        # TODO: Integrate with actual Task tool when available
        # For now, raise NotImplementedError to indicate production integration needed
        raise NotImplementedError(
            "ClaudeCodeTaskAdapter requires integration with actual Task tool. "
            "Use MockedTaskAdapter for testing."
        )
