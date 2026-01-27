"""Adapters for DES Hexagonal Architecture.

This package contains concrete implementations of Port interfaces:

Production Adapters (real I/O):
- RealSubagentStopHook: Post-execution validation with comprehensive checks
- RealTemplateValidator: Template validation for pre-invocation checks
- RealFileSystem: File system operations using Python's standard library
- SystemTimeProvider: System time provider using datetime.now()

Test Adapters (in-memory, deterministic):
- MockedSubagentStopHook: Predefined validation results for testing
- MockedTemplateValidator: Predefined validation results for testing
- InMemoryFileSystem: In-memory file storage for fast, deterministic tests
- MockedTimeProvider: Controllable time for timeout testing

Usage:
    # Production
    from des.adapters import RealFileSystem, SystemTimeProvider

    # Testing
    from des.adapters import InMemoryFileSystem, MockedTimeProvider
"""

from des.adapters.real_hook import RealSubagentStopHook
from des.adapters.real_validator import RealTemplateValidator
from des.adapters.real_filesystem import RealFileSystem
from des.adapters.system_time import SystemTimeProvider

from des.adapters.mocked_hook import MockedSubagentStopHook
from des.adapters.mocked_validator import MockedTemplateValidator
from des.adapters.in_memory_filesystem import InMemoryFileSystem
from des.adapters.mocked_time import MockedTimeProvider

__all__ = [
    # Production adapters
    'RealSubagentStopHook',
    'RealTemplateValidator',
    'RealFileSystem',
    'SystemTimeProvider',
    # Test adapters
    'MockedSubagentStopHook',
    'MockedTemplateValidator',
    'InMemoryFileSystem',
    'MockedTimeProvider',
]
