"""
DES (Deterministic Execution System) - Post-execution validation and phase tracking.

This package provides deterministic validation hooks that fire when sub-agents complete
execution, ensuring phase progression is tracked accurately and deviations are detected.

Follows hexagonal architecture with:
  - Domain: Core business logic and entities
  - Application: Use cases and orchestration
  - Ports: Abstract interfaces (driver and driven)
  - Adapters: Concrete implementations (drivers and driven)

Core Components:
  - DESOrchestrator: Main DES coordination engine
  - TimeoutMonitor: Domain entity for timeout management
  - ConfigPort: Configuration abstractions
  - HookPort/ValidatorPort: Driver port abstractions
  - RealSubagentStopHook/RealTemplateValidator: Driver implementations
  - EnvironmentConfigAdapter/InMemoryConfigAdapter: Driven implementations

For backward compatibility, this module re-exports all key classes and interfaces.
New code should import from the specific layer packages:
  - from src.des.domain import TimeoutMonitor, TurnCounter
  - from src.des.application import DESOrchestrator
  - from src.des.ports.driver_ports import HookPort, ValidatorPort
  - from src.des.ports.driven_ports import ConfigPort, FileSystemPort, TimeProvider
  - from src.des.adapters.drivers import RealSubagentStopHook, RealTemplateValidator
  - from src.des.adapters.driven import EnvironmentConfigAdapter
"""

# Re-export all key classes for backward compatibility
from src.des.domain import (
    TimeoutMonitor,
    TurnCounter,
    InvocationLimitsValidator,
    InvocationLimitsResult,
)
from src.des.application.orchestrator import DESOrchestrator
from src.des.application.config_loader import ConfigLoader
from src.des.application.hooks import SubagentStopHook
from src.des.application.validator import TDDPhaseValidator
from src.des.ports.driver_ports import HookPort, ValidatorPort
from src.des.ports.driven_ports import (
    ConfigPort,
    FileSystemPort,
    LoggingPort,
    TaskInvocationPort,
    TimeProvider,
)
from src.des.adapters.drivers import RealSubagentStopHook, RealTemplateValidator
from src.des.adapters.driven import (
    EnvironmentConfigAdapter,
    InMemoryConfigAdapter,
    RealFileSystem,
    SilentLogger,
    StructuredLogger,
    ClaudeCodeTaskAdapter,
    MockedTaskAdapter,
    SystemTimeProvider,
)

# Backward compatibility aliases
RealHook = RealSubagentStopHook
RealValidator = RealTemplateValidator
RealFilesystem = RealFileSystem
SystemTime = SystemTimeProvider

__all__ = [
    # Domain
    "TimeoutMonitor",
    "TurnCounter",
    "InvocationLimitsValidator",
    "InvocationLimitsResult",
    # Application
    "DESOrchestrator",
    "ConfigLoader",
    "SubagentStopHook",
    "TDDPhaseValidator",
    # Driver ports
    "HookPort",
    "ValidatorPort",
    # Driven ports
    "ConfigPort",
    "FileSystemPort",
    "LoggingPort",
    "TaskInvocationPort",
    "TimeProvider",
    # Driver adapters
    "RealSubagentStopHook",
    "RealTemplateValidator",
    # Backward compatibility aliases
    "RealHook",
    "RealValidator",
    # Driven adapters
    "EnvironmentConfigAdapter",
    "InMemoryConfigAdapter",
    "RealFilesystem",
    "SilentLogger",
    "StructuredLogger",
    "ClaudeCodeTaskAdapter",
    "MockedTaskAdapter",
    "SystemTime",
]
