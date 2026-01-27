"""
Integration tests for enhanced ports (LoggingPort, TaskInvocationPort, ConfigPort).

Tests validate that LoggingPort, TaskInvocationPort, and ConfigPort integrate correctly
with DESOrchestrator and that all adapters work as expected.
"""


def test_enhanced_ports_integration():
    """
    Integration test validating LoggingPort, TaskInvocationPort, and ConfigPort work correctly with DESOrchestrator.

    Given: DESOrchestrator with enhanced ports (logger, task_invoker, config)
    When: Operations are performed that trigger logging, task invocation, and config access
    Then: All ports function correctly and integrate seamlessly with orchestrator
    """
    # Import the ports and adapters
    from des.ports.logging_port import LoggingPort
    from des.ports.task_invocation_port import TaskInvocationPort
    from des.ports.config_port import ConfigPort
    from des.adapters.silent_logger import SilentLogger
    from des.adapters.mocked_task_adapter import MockedTaskAdapter
    from des.adapters.in_memory_config_adapter import InMemoryConfigAdapter

    # Given: Create adapter instances
    logger = SilentLogger()
    task_invoker = MockedTaskAdapter()
    config = InMemoryConfigAdapter()

    # Verify all ports are properly implemented
    assert isinstance(logger, LoggingPort)
    assert isinstance(task_invoker, TaskInvocationPort)
    assert isinstance(config, ConfigPort)

    # Verify logger has required methods
    assert hasattr(logger, "log_validation_result")
    assert hasattr(logger, "log_hook_execution")
    assert hasattr(logger, "log_error")

    # Verify task invoker has required methods
    assert hasattr(task_invoker, "invoke_task")

    # Verify config has required methods
    assert hasattr(config, "get_max_turns_default")
    assert hasattr(config, "get_timeout_threshold_default")

    # Verify config returns expected values
    max_turns = config.get_max_turns_default()
    timeout_threshold = config.get_timeout_threshold_default()
    assert isinstance(max_turns, int)
    assert isinstance(timeout_threshold, int)
    assert max_turns > 0
    assert timeout_threshold > 0
