"""Backward compatibility import for MockedTaskAdapter.

Re-exports MockedTaskAdapter from driven adapters for backward compatibility with old import paths.
Old code using: from src.des.adapters.mocked_task_adapter import MockedTaskAdapter
Will continue to work with this module.
"""

from src.des.adapters.driven.task_invocation.mocked_task_adapter import MockedTaskAdapter

__all__ = ["MockedTaskAdapter"]
