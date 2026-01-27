"""Backward compatibility import for TaskInvocationPort.

Re-exports TaskInvocationPort from driven_ports for backward compatibility with old import paths.
Old code using: from src.des.ports.task_invocation_port import TaskInvocationPort
Will continue to work with this module.
"""

from src.des.ports.driven_ports.task_invocation_port import TaskInvocationPort

__all__ = ["TaskInvocationPort"]
