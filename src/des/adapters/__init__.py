"""
DES Adapters Layer - Infrastructure and external dependency implementations.

Adapters implement the port interfaces, providing concrete implementations
for both production and test environments. Organized into driver (inbound)
and driven (outbound) adapters following hexagonal architecture.
"""

from src.des.adapters.driven import (
    ClaudeCodeTaskAdapter,
    EnvironmentConfigAdapter,
    InMemoryConfigAdapter,
    MockedTaskAdapter,
    RealFileSystem,
    SilentLogger,
    StructuredLogger,
    SystemTime,
)
from src.des.adapters.drivers import (
    RealSubagentStopHook,
    RealTemplateValidator,
)


__all__ = [
    "ClaudeCodeTaskAdapter",
    # Driven adapters (outbound)
    "EnvironmentConfigAdapter",
    "InMemoryConfigAdapter",
    "MockedTaskAdapter",
    "RealFileSystem",
    # Driver adapters (inbound)
    "RealSubagentStopHook",
    "RealTemplateValidator",
    "SilentLogger",
    "StructuredLogger",
    "SystemTime",
]
