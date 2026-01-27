"""
DES Adapters Layer - Infrastructure and external dependency implementations.

Adapters implement the port interfaces, providing concrete implementations
for both production and test environments. Organized into driver (inbound)
and driven (outbound) adapters following hexagonal architecture.
"""

from src.des.adapters.drivers import (
    RealSubagentStopHook,
    RealTemplateValidator,
)

from src.des.adapters.driven import (
    EnvironmentConfigAdapter,
    InMemoryConfigAdapter,
    RealFileSystem,
    SilentLogger,
    StructuredLogger,
    ClaudeCodeTaskAdapter,
    MockedTaskAdapter,
    SystemTime,
)

__all__ = [
    # Driver adapters (inbound)
    "RealSubagentStopHook",
    "RealTemplateValidator",
    # Driven adapters (outbound)
    "EnvironmentConfigAdapter",
    "InMemoryConfigAdapter",
    "RealFileSystem",
    "SilentLogger",
    "StructuredLogger",
    "ClaudeCodeTaskAdapter",
    "MockedTaskAdapter",
    "SystemTime",
]
