# DES Module Import Patterns Reference

Quick guide to importing from reorganized DES module after Option B restructuring.

---

## Backward Compatibility (Existing Code - Unchanged)

**Benefit**: Existing imports continue to work without modification.

```python
# These imports work the same before and after restructuring
# via convenience re-exports in src/des/__init__.py

from src.des import (
    DESOrchestrator,
    TurnCounter,
    TimeoutMonitor,
    TurnLimitConfig,
    ConfigLoader,
    InvocationLimitsValidator,
    InvocationLimitsResult,
    HookPort,
    HookResult,
    ValidatorPort,
    ValidationResult,
    FileSystemPort,
    TimeProvider,
    LoggingPort,
    TaskInvocationPort,
    ConfigPort,
    RealSubagentStopHook,
    RealTemplateValidator,
    RealFileSystem,
    SystemTimeProvider,
)

# Usage
orchestrator = DESOrchestrator.create_with_defaults()
counter = TurnCounter()
```

---

## New Code Patterns (Explicit Layer Imports)

For clarity in new code, import from specific layers.

### Pattern 1: Application Layer Imports

**When**: Creating or updating orchestration/service logic

```python
# Main application orchestrator
from src.des.application.orchestrator import DESOrchestrator, ExecuteStepResult

# Instantiate with defaults
orchestrator = DESOrchestrator.create_with_defaults()

# Or provide custom dependencies
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.time.system_time import SystemTimeProvider

hook = RealSubagentStopHook()
filesystem = RealFileSystem()
time_provider = SystemTimeProvider()

orchestrator = DESOrchestrator(
    hook=hook,
    filesystem=filesystem,
    time_provider=time_provider
)
```

### Pattern 2: Domain Layer Imports

**When**: Using core business logic components

```python
# Turn counting domain logic
from src.des.domain.turn_counter import TurnCounter

counter = TurnCounter()
counter.increment_turn("PREPARE")
current_turn = counter.get_current_turn("PREPARE")

# Timeout monitoring domain logic
from src.des.domain.timeout_monitor import TimeoutMonitor
from src.des.adapters.driven.time.system_time import SystemTimeProvider

started_at = "2026-01-27T10:00:00Z"
time_provider = SystemTimeProvider()
monitor = TimeoutMonitor(started_at=started_at, time_provider=time_provider)
crossed = monitor.check_thresholds([5, 10, 15])

# Configuration domain logic
from src.des.domain.turn_config import TurnLimitConfig, ConfigLoader

config_data = {
    "turn_limits": {
        "quick": 20,
        "standard": 50,
        "complex": 100
    }
}
loader = ConfigLoader()
config = loader.load_from_dict(config_data)
limit = config.get_limit_for_type("standard")

# Invocation limits validation
from src.des.domain.invocation_limits_validator import InvocationLimitsValidator
from pathlib import Path

validator = InvocationLimitsValidator()
result = validator.validate_limits(Path("steps/01-01.json"))
if not result.is_valid:
    print("Errors:", result.errors)
    print("Guidance:", result.guidance)
```

### Pattern 3: Port Abstractions (Contracts)

**When**: Defining dependencies or testing components

```python
# Port abstractions define what components need
# Import ports when defining interfaces or testing

from src.des.ports.driver_ports.hook_port import HookPort, HookResult
from src.des.ports.driver_ports.validator_port import ValidatorPort, ValidationResult
from src.des.ports.driven_ports.filesystem_port import FileSystemPort
from src.des.ports.driven_ports.time_provider_port import TimeProvider
from src.des.ports.driven_ports.logging_port import LoggingPort
from src.des.ports.driven_ports.task_invocation_port import TaskInvocationPort
from src.des.ports.driven_ports.config_port import ConfigPort

# Use in type hints and dependency injection
def process_step(
    hook: HookPort,
    filesystem: FileSystemPort,
    time_provider: TimeProvider
) -> HookResult:
    """Process step with injected dependencies."""
    return hook.on_agent_complete("step_file.json")
```

### Pattern 4: Adapter Implementations (Specific Technologies)

**When**: Creating new adapters, unit testing with mocks, or swapping implementations

```python
# Production adapters
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator
from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.time.system_time import SystemTimeProvider
from src.des.adapters.driven.logging.structured_logger import StructuredLogger
from src.des.adapters.driven.logging.silent_logger import SilentLogger
from src.des.adapters.driven.config.environment_config_adapter import EnvironmentConfigAdapter
from src.des.adapters.driven.config.in_memory_config_adapter import InMemoryConfigAdapter
from src.des.adapters.driven.task_invocation.claude_code_task_adapter import ClaudeCodeTaskAdapter

# Setup production environment
hook = RealSubagentStopHook()
validator = RealTemplateValidator()
filesystem = RealFileSystem()
time_provider = SystemTimeProvider()
logger = StructuredLogger()
config = EnvironmentConfigAdapter()
task_adapter = ClaudeCodeTaskAdapter()

# Or swap for testing/different environments
silent_logger = SilentLogger()
memory_config = InMemoryConfigAdapter()

# Test adapters (mocks)
from tests.des.adapters.mocked_hook import MockedHook
from tests.des.adapters.mocked_validator import MockedValidator
from tests.des.adapters.mocked_time import MockedTimeProvider
from tests.des.adapters.mocked_filesystem import InMemoryFileSystem

# Use in testing
test_hook = MockedHook()
test_time = MockedTimeProvider(now="2026-01-27T10:00:00Z")
test_fs = InMemoryFileSystem()
```

---

## Testing Patterns

### Unit Tests: Import from Domain/Application

**Location**: `tests/des/unit/domain/test_turn_counter.py`

```python
# Test isolated domain components
from src.des.domain.turn_counter import TurnCounter

def test_turn_counter_increments():
    counter = TurnCounter()
    counter.increment_turn("PREPARE")
    assert counter.get_current_turn("PREPARE") == 1

def test_turn_counter_per_phase():
    counter = TurnCounter()
    counter.increment_turn("PREPARE")
    counter.increment_turn("RED_UNIT")
    counter.increment_turn("RED_UNIT")

    assert counter.get_current_turn("PREPARE") == 1
    assert counter.get_current_turn("RED_UNIT") == 2
```

### Integration Tests: Mix Components + Mocks

**Location**: `tests/des/integration/test_timeout_monitoring.py`

```python
# Test interaction between domain + infrastructure
from src.des.domain.timeout_monitor import TimeoutMonitor
from tests.des.adapters.mocked_time import MockedTimeProvider

def test_timeout_monitor_with_mocked_time():
    # Inject mock time provider
    time_provider = MockedTimeProvider(now="2026-01-27T10:00:00Z")

    # Create domain component with mocked dependency
    monitor = TimeoutMonitor(
        started_at="2026-01-27T10:00:00Z",
        time_provider=time_provider
    )

    # Move time forward
    time_provider.advance_seconds(300)  # 5 minutes

    # Verify behavior
    crossed = monitor.check_thresholds([5, 10])
    assert 5 in crossed
    assert 10 not in crossed
```

### Acceptance Tests: Application Level

**Location**: `tests/des/acceptance/test_turn_counting.py`

```python
# Test user stories end-to-end
from src.des.application.orchestrator import DESOrchestrator
from pathlib import Path
from tests.des.adapters.mocked_time import MockedTimeProvider
from tests.des.adapters.mocked_filesystem import InMemoryFileSystem

def test_user_story_001_turn_counting():
    # Setup test environment
    fs = InMemoryFileSystem()
    time_provider = MockedTimeProvider()

    # Load test data
    step_file_path = Path("steps/01-01.json")
    fs.write_json(step_file_path, {
        "tdd_cycle": {
            "phase_execution_log": [
                {"phase_name": "PREPARE", "status": "NOT_EXECUTED"}
            ]
        }
    })

    # Create orchestrator with test adapters
    from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
    from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator

    orchestrator = DESOrchestrator(
        hook=RealSubagentStopHook(),
        validator=RealTemplateValidator(),
        filesystem=fs,
        time_provider=time_provider
    )

    # Execute
    result = orchestrator.execute_step(
        command="/nw:execute",
        agent="@software-crafter",
        step_file=str(step_file_path),
        project_root="/tmp/test",
        simulated_iterations=5,
        timeout_thresholds=[5, 10]
    )

    # Verify
    assert result.turn_count == 5
    assert "turn_counting" in result.features_validated
```

---

## Port Contracts Reference

### Driver Ports (Inbound)

```python
from src.des.ports.driver_ports.hook_port import HookPort, HookResult
from src.des.ports.driver_ports.validator_port import ValidatorPort, ValidationResult

# HookPort contract
class MyHookImplementation(HookPort):
    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Called when agent completes execution."""
        pass

# ValidatorPort contract
class MyValidatorImplementation(ValidatorPort):
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate prompt before Task invocation."""
        pass
```

### Driven Ports (Outbound)

```python
from src.des.ports.driven_ports.filesystem_port import FileSystemPort
from src.des.ports.driven_ports.time_provider_port import TimeProvider
from src.des.ports.driven_ports.logging_port import LoggingPort
from src.des.ports.driven_ports.config_port import ConfigPort
from src.des.ports.driven_ports.task_invocation_port import TaskInvocationPort

# FileSystemPort contract
class MyFileSystemImplementation(FileSystemPort):
    def read_json(self, path: Path) -> dict:
        """Read JSON file."""
        pass

    def write_json(self, path: Path, data: dict) -> None:
        """Write JSON file."""
        pass

# TimeProvider contract
class MyTimeProviderImplementation(TimeProvider):
    def now_utc(self) -> datetime:
        """Get current UTC time."""
        pass

# LoggingPort contract
class MyLoggingImplementation(LoggingPort):
    def log(self, level: str, message: str, **kwargs) -> None:
        """Log message."""
        pass

# ConfigPort contract
class MyConfigImplementation(ConfigPort):
    def get(self, key: str, default=None):
        """Get configuration value."""
        pass

# TaskInvocationPort contract
class MyTaskImplementation(TaskInvocationPort):
    def invoke(self, command: str, **kwargs) -> Any:
        """Invoke task."""
        pass
```

---

## Common Import Groups

### Setup for Testing

```python
# Typical test file setup
from pathlib import Path
from src.des.domain.turn_counter import TurnCounter
from src.des.domain.timeout_monitor import TimeoutMonitor
from src.des.application.orchestrator import DESOrchestrator
from tests.des.adapters.mocked_time import MockedTimeProvider
from tests.des.adapters.mocked_filesystem import InMemoryFileSystem
from tests.des.adapters.mocked_hook import MockedHook
from tests.des.adapters.mocked_validator import MockedValidator

# Ready for test
@pytest.fixture
def orchestrator():
    return DESOrchestrator(
        hook=MockedHook(),
        validator=MockedValidator(),
        filesystem=InMemoryFileSystem(),
        time_provider=MockedTimeProvider()
    )
```

### Setup for Production

```python
# Typical production setup
from src.des.application.orchestrator import DESOrchestrator
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
from src.des.adapters.drivers.validators.real_validator import RealTemplateValidator
from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
from src.des.adapters.driven.time.system_time import SystemTimeProvider
from src.des.adapters.driven.logging.structured_logger import StructuredLogger

# Create production orchestrator
orchestrator = DESOrchestrator(
    hook=RealSubagentStopHook(),
    validator=RealTemplateValidator(),
    filesystem=RealFileSystem(),
    time_provider=SystemTimeProvider()
)

# Use it
result = orchestrator.execute_step(
    command="/nw:execute",
    agent="@software-crafter",
    step_file="docs/feature/des/steps/01-01.json",
    project_root="/path/to/project"
)
```

---

## Migration Checklist: Update Your Imports

When updating code after restructuring:

- [ ] Check where code is used (domain, application, test, external)
- [ ] Use convenience imports for backward compatibility
- [ ] Consider using explicit imports for clarity in new code
- [ ] Update test fixtures to use new adapter paths
- [ ] Verify all imports work with: `python3 -c "from ... import ..."`
- [ ] Run tests to confirm: `pytest tests/des/`

---

## Anti-Patterns (What NOT to Do)

❌ **DON'T**: Import adapters from application layer
```python
# WRONG - breaks hexagonal architecture
from src.des.application.orchestrator import DESOrchestrator
from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook  # ← Don't import adapters here

# RIGHT - let DESOrchestrator.create_with_defaults() handle adapters
orchestrator = DESOrchestrator.create_with_defaults()
```

❌ **DON'T**: Import application from domain
```python
# WRONG - domain shouldn't know about application
from src.des.domain.turn_counter import TurnCounter
from src.des.application.orchestrator import DESOrchestrator  # ← Don't do this in domain

# RIGHT - application uses domain, not vice versa
from src.des.domain.turn_counter import TurnCounter
```

❌ **DON'T**: Have circular imports
```python
# WRONG - creates circular dependency
# orchestrator.py imports from turn_counter.py
# turn_counter.py imports from orchestrator.py

# RIGHT - dependencies flow one direction
# orchestrator.py imports from turn_counter.py
# turn_counter.py imports only from ports and other domain files
```

❌ **DON'T**: Import concrete implementations when testing with different provider
```python
# WRONG - forces production adapter
from src.des.adapters.driven.time.system_time import SystemTimeProvider

# RIGHT - use mocked time provider for testing
from tests.des.adapters.mocked_time import MockedTimeProvider
```

---

## Dependency Diagram

```
EXTERNAL CODE
    │
    └─→ from src.des import *           (backward compat)
    └─→ from src.des.application import *
            │
            ├─→ uses domain/
            │   └─→ imports ports/driven_ports
            │
            └─→ uses ports/
                    │
                    ├─→ implemented by adapters/drivers/
                    └─→ implemented by adapters/driven/


TEST CODE
    │
    ├─→ from src.des.domain import *    (test domain isolation)
    ├─→ from tests.des.adapters import * (mock implementations)
    └─→ from src.des.application import * (integration testing)
```

---

## Quick Import Search

Need to find an import?

| I want to import | Location | Example |
|------------------|----------|---------|
| **TurnCounter** | domain | `from src.des.domain.turn_counter import TurnCounter` |
| **DESOrchestrator** | application | `from src.des.application.orchestrator import DESOrchestrator` |
| **HookPort** | driver_ports | `from src.des.ports.driver_ports.hook_port import HookPort` |
| **TimeProvider** | driven_ports | `from src.des.ports.driven_ports.time_provider_port import TimeProvider` |
| **RealFileSystem** | driven/filesystem | `from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem` |
| **MockedHook** | tests/adapters | `from tests.des.adapters.mocked_hook import MockedHook` |

---

## Summary

| Use Case | Import Style | Example |
|----------|--------------|---------|
| Existing code (no changes) | Convenience import | `from src.des import DESOrchestrator` |
| New domain component | Explicit layer import | `from src.des.domain.turn_counter import TurnCounter` |
| Creating service | Application import | `from src.des.application.orchestrator import DESOrchestrator` |
| Testing | Mock adapters | `from tests.des.adapters.mocked_time import MockedTimeProvider` |
| Understanding interface | Port import | `from src.des.ports.driven_ports.filesystem_port import FileSystemPort` |
