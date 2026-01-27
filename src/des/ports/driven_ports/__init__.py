"""
DES Driven Ports - Outbound/Secondary port abstractions.

Exports all driven port interfaces (ports that DES depends on).
"""

from src.des.ports.driven_ports.config_port import ConfigPort
from src.des.ports.driven_ports.filesystem_port import FileSystemPort
from src.des.ports.driven_ports.logging_port import LoggingPort
from src.des.ports.driven_ports.task_invocation_port import TaskInvocationPort
from src.des.ports.driven_ports.time_provider_port import TimeProvider

__all__ = [
    "ConfigPort",
    "FileSystemPort",
    "LoggingPort",
    "TaskInvocationPort",
    "TimeProvider",
]
