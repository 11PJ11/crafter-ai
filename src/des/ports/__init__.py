"""Ports package for DES hexagonal architecture.

Ports define the interfaces through which the application core communicates
with external systems and infrastructure.

Re-exports all port abstractions from driver and driven port layers for convenience.
"""

from src.des.ports.driver_ports import (
    HookPort,
    ValidatorPort,
)

from src.des.ports.driven_ports import (
    ConfigPort,
    FileSystemPort,
    LoggingPort,
    TaskInvocationPort,
    TimeProvider,
)

__all__ = [
    # Driver ports (inbound)
    "HookPort",
    "ValidatorPort",
    # Driven ports (outbound)
    "ConfigPort",
    "FileSystemPort",
    "LoggingPort",
    "TaskInvocationPort",
    "TimeProvider",
]
