"""Backward compatibility import for ClaudeCodeTaskAdapter.

Re-exports ClaudeCodeTaskAdapter from driven adapters for backward compatibility with old import paths.
Old code using: from src.des.adapters.claude_code_task_adapter import ClaudeCodeTaskAdapter
Will continue to work with this module.
"""

from src.des.adapters.driven.task_invocation.claude_code_task_adapter import ClaudeCodeTaskAdapter

__all__ = ["ClaudeCodeTaskAdapter"]
