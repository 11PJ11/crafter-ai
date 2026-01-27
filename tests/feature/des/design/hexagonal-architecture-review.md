# DES Hexagonal Architecture - Comprehensive Review

**Review Date:** 2026-01-26
**Reviewer:** solution-architect-reviewer (Atlas)
**Artifact:** DES System Architecture (orchestrator.py, hooks.py, validator.py, and supporting modules)
**Scope:** COMPLETE system review for hexagonal architecture compliance
**User Request:** Italian: "la /nw:review deve essere fatta su tutto il design per capire come riorganizzare affinche sia veramente esagonale in tutti i suoi componenti"

---

## Executive Summary

**Overall Assessment:** NEEDS_REVISION (HIGH severity)

The DES system currently exhibits significant violations of hexagonal architecture principles. While FileSystemPort and TimeProvider are correctly specified in the design document, the **actual implementation reveals 7 additional external dependencies** that lack Port abstractions. The domain layer (DESOrchestrator, SubagentStopHook) is tightly coupled to infrastructure concerns, violating the core principle of hexagonal architecture: **business logic isolation**.

**Critical Finding:** DESOrchestrator directly instantiates concrete adapters (`SubagentStopHook()`, `TemplateValidator()`) and performs I/O operations (file reads, JSON parsing, datetime operations), making it **untestable with in-memory adapters** and violating dependency inversion.

---

## Review Findings

### 1. CRITICAL: Domain Layer Infrastructure Dependencies (HIGH)

**Issue:** DESOrchestrator directly depends on concrete infrastructure implementations

**Evidence from orchestrator.py:**

```python
# Lines 63-68
def __init__(self):
    """Initialize orchestrator with template validator and hook."""
    self._validator = TemplateValidator()  # VIOLATION: Concrete instantiation
    self._hook = SubagentStopHook()        # VIOLATION: Concrete instantiation
    self._subagent_lifecycle_completed = False
    self._step_file_path: Optional[Path] = None
```

**Violations:**

1. **Direct instantiation** of `TemplateValidator()` and `SubagentStopHook()` inside domain layer
2. **No dependency injection** through constructor parameters
3. **Impossible to test** with mock validators or hooks
4. **Tight coupling** between domain logic and infrastructure components

**Impact:** Cannot test DESOrchestrator independently; cannot swap implementations; violates Open/Closed Principle

**Severity:** HIGH - Blocks hexagonal architecture completely

---

### 2. CRITICAL: Missing HookPort Abstraction (HIGH)

**Issue:** SubagentStopHook is used directly without Port interface

**User Explicitly Mentioned:** "non solo il sistema di hook, quello e' solo un altro esempio"

**Current Implementation (orchestrator.py lines 229-242):**

```python
def on_subagent_complete(self, step_file_path: str) -> HookResult:
    """Invoke SubagentStopHook after sub-agent completion."""
    return self._hook.on_agent_complete(step_file_path)  # Direct concrete call
```

**Missing Port Specification:**

```python
# REQUIRED: HookPort interface
from abc import ABC, abstractmethod

class HookPort(ABC):
    """Port for post-execution validation hooks."""

    @abstractmethod
    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Validate step file after sub-agent completion.

        Args:
            step_file_path: Absolute path to step JSON file

        Returns:
            HookResult with validation status, errors, and recovery suggestions
        """
        pass
```

**Required Adapters:**

1. **RealSubagentStopHook** (Production):
   - Reads step file from filesystem
   - Validates phase execution log
   - Updates step file state on failure
   - Returns HookResult

2. **MockedSubagentStopHook** (Testing):
   - Returns predefined HookResult
   - No filesystem I/O
   - Configurable validation outcomes
   - Tracks invocation count/parameters

**Constructor Injection Required:**

```python
def __init__(self, hook: HookPort, validator: ValidatorPort):
    """Initialize with injected dependencies."""
    self._hook = hook          # Injected, not instantiated
    self._validator = validator # Injected, not instantiated
```

**Severity:** HIGH - User explicitly requested this fix

---

### 3. CRITICAL: Missing ValidatorPort Abstraction (HIGH)

**Issue:** TemplateValidator is used directly without Port interface

**Current Implementation (orchestrator.py line 83):**

```python
def validate_prompt(self, prompt: str) -> ValidationResult:
    result = self._validator.validate_prompt(prompt)  # Direct concrete call
```

**Missing Port Specification:**

```python
class ValidatorPort(ABC):
    """Port for template validation."""

    @abstractmethod
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate prompt for mandatory sections and TDD phases.

        Args:
            prompt: Full prompt text to validate

        Returns:
            ValidationResult with status, errors, task_invocation_allowed flag
        """
        pass
```

**Required Adapters:**

1. **RealTemplateValidator** (Production):
   - Parses prompt for DES sections
   - Validates TDD phase presence
   - Validates execution log format
   - Real regex parsing and validation logic

2. **MockedTemplateValidator** (Testing):
   - Returns predefined ValidationResult
   - No actual parsing
   - Configurable pass/fail outcomes
   - Fast execution for unit tests

**Severity:** HIGH - Core domain dependency needs abstraction

---

### 4. HIGH: Direct File I/O in Domain Layer (HIGH)

**Issue:** DESOrchestrator performs file operations directly

**Evidence from orchestrator.py:**

```python
# Lines 368-371
def _load_step_file(self, step_file_path: Path) -> dict:
    """Load and parse step file JSON."""
    with open(step_file_path, 'r') as f:  # VIOLATION: Direct filesystem access
        return json.load(f)

# Lines 400-404
def _persist_turn_count(self, step_file_path: Path, step_data: dict, ...):
    """Persist turn count to step file."""
    current_phase["turn_count"] = turn_count
    with open(step_file_path, 'w') as f:  # VIOLATION: Direct filesystem write
        json.dump(step_data, f, indent=2)
```

**Missing Port:** FileSystemPort (mentioned in design but not enforced in code)

**Required Refactoring:**

```python
class FileSystemPort(ABC):
    """Port for file operations."""

    @abstractmethod
    def read_json(self, path: Path) -> dict:
        """Read and parse JSON file."""
        pass

    @abstractmethod
    def write_json(self, path: Path, data: dict) -> None:
        """Write data as JSON file."""
        pass

# Constructor injection
def __init__(self, filesystem: FileSystemPort, ...):
    self._filesystem = filesystem

# Usage in methods
def _load_step_file(self, step_file_path: Path) -> dict:
    return self._filesystem.read_json(step_file_path)

def _persist_turn_count(self, step_file_path: Path, step_data: dict, ...):
    current_phase["turn_count"] = turn_count
    self._filesystem.write_json(step_file_path, step_data)
```

**Severity:** HIGH - Multiple file operations throughout orchestrator

---

### 5. HIGH: Direct Time Operations in Domain Layer (HIGH)

**Issue:** TimeoutMonitor uses datetime.now() directly

**Evidence from timeout_monitor.py lines 38-46:**

```python
def get_elapsed_seconds(self) -> float:
    """Calculate elapsed seconds from phase start to now."""
    now = datetime.now(timezone.utc)  # VIOLATION: Direct system time access
    elapsed = (now - self.started_at).total_seconds()
    return elapsed
```

**Missing Port:** TimeProvider (mentioned in design but not enforced in code)

**Required Refactoring:**

```python
class TimeProvider(ABC):
    """Port for time operations."""

    @abstractmethod
    def now_utc(self) -> datetime:
        """Get current UTC time."""
        pass

# Adapters
class SystemTimeProvider(TimeProvider):
    def now_utc(self) -> datetime:
        return datetime.now(timezone.utc)

class MockedTimeProvider(TimeProvider):
    def __init__(self, fixed_time: datetime):
        self._time = fixed_time

    def now_utc(self) -> datetime:
        return self._time

    def advance(self, seconds: float):
        self._time += timedelta(seconds=seconds)

# Constructor injection in TimeoutMonitor
def __init__(self, started_at: str, time_provider: TimeProvider):
    self._time_provider = time_provider
    # ...

def get_elapsed_seconds(self) -> float:
    now = self._time_provider.now_utc()
    elapsed = (now - self.started_at).total_seconds()
    return elapsed
```

**Severity:** HIGH - Time dependency prevents deterministic testing

---

### 6. MEDIUM: Missing LoggingPort Abstraction (MEDIUM)

**Issue:** No explicit logging abstraction (implicit through print statements)

**Current State:** No structured logging in DES components

**Observation:** While not currently used, production systems require logging. Should be designed into hexagonal architecture upfront.

**Required Port Specification:**

```python
class LoggingPort(ABC):
    """Port for logging operations."""

    @abstractmethod
    def log_validation_result(self, result: ValidationResult, context: dict) -> None:
        """Log validation outcome."""
        pass

    @abstractmethod
    def log_hook_execution(self, result: HookResult, step_file: str) -> None:
        """Log hook validation outcome."""
        pass

    @abstractmethod
    def log_error(self, error: Exception, context: dict) -> None:
        """Log error with context."""
        pass
```

**Required Adapters:**

1. **StructuredLogger** (Production): JSON logging to file/stdout
2. **SilentLogger** (Testing): No-op implementation

**Severity:** MEDIUM - Future requirement, not blocking current functionality

---

### 7. MEDIUM: Task Invocation Mechanism (MEDIUM)

**Issue:** No abstraction for Task tool invocation

**Current State:** DES orchestrator prepares prompts but doesn't directly invoke Task

**Observation:** While orchestrator doesn't directly call Task tool, the system assumes Task invocation happens outside orchestrator. For complete hexagonal architecture, this should be a Port.

**Recommended Port:**

```python
class TaskInvocationPort(ABC):
    """Port for sub-agent task invocation."""

    @abstractmethod
    def invoke_task(self, prompt: str, agent: str) -> TaskResult:
        """Invoke sub-agent with prompt.

        Args:
            prompt: Complete DES prompt
            agent: Target agent identifier

        Returns:
            TaskResult with execution outcome
        """
        pass
```

**Adapters:**

1. **ClaudeCodeTaskAdapter** (Production): Calls actual Task tool
2. **MockedTaskAdapter** (Testing): Returns predefined results

**Severity:** MEDIUM - Not critical for current testing strategy, but improves completeness

---

### 8. LOW: Configuration Access (LOW)

**Issue:** No abstraction for configuration/environment variables

**Current State:** DES uses hardcoded configuration

**Observation:** Future scaling may require environment-specific configuration

**Recommended Port:**

```python
class ConfigPort(ABC):
    """Port for configuration access."""

    @abstractmethod
    def get_max_turns_default(self) -> int:
        """Get default max turns configuration."""
        pass

    @abstractmethod
    def get_timeout_threshold_default(self) -> int:
        """Get default timeout threshold in minutes."""
        pass
```

**Severity:** LOW - No immediate impact, future scalability concern

---

## Complete Port Inventory

### Critical Ports (MUST HAVE)

1. **HookPort** - Post-execution validation hooks
   - Production: RealSubagentStopHook
   - Test: MockedSubagentStopHook

2. **ValidatorPort** - Template validation
   - Production: RealTemplateValidator
   - Test: MockedTemplateValidator

3. **FileSystemPort** - File I/O operations
   - Production: RealFileSystem
   - Test: InMemoryFileSystem

4. **TimeProvider** - Time/datetime operations
   - Production: SystemTimeProvider
   - Test: MockedTimeProvider

### Important Ports (SHOULD HAVE)

5. **LoggingPort** - Structured logging
   - Production: StructuredLogger
   - Test: SilentLogger

6. **TaskInvocationPort** - Sub-agent invocation
   - Production: ClaudeCodeTaskAdapter
   - Test: MockedTaskAdapter

### Optional Ports (NICE TO HAVE)

7. **ConfigPort** - Configuration access
   - Production: EnvironmentConfigAdapter
   - Test: InMemoryConfigAdapter

---

## Recommended Architecture Changes

### Phase 1: Critical Refactoring (Blocking Issues)

**Goal:** Achieve true hexagonal architecture for core domain logic

**Steps:**

1. **Create Port Interfaces** (2 hours)
   - Define `HookPort` interface
   - Define `ValidatorPort` interface
   - Define `FileSystemPort` interface (already in design, needs enforcement)
   - Define `TimeProvider` interface (already in design, needs enforcement)

2. **Implement Adapters** (4 hours)
   - `RealSubagentStopHook` (rename existing SubagentStopHook)
   - `MockedSubagentStopHook` (new test adapter)
   - `RealTemplateValidator` (rename existing TemplateValidator)
   - `MockedTemplateValidator` (new test adapter)
   - `RealFileSystem` (new production adapter)
   - `InMemoryFileSystem` (new test adapter)
   - `SystemTimeProvider` (new production adapter)
   - `MockedTimeProvider` (new test adapter)

3. **Refactor DESOrchestrator** (3 hours)
   - Add constructor parameters for all Ports
   - Remove all direct instantiations
   - Remove all direct file I/O
   - Inject dependencies through constructor

4. **Refactor TimeoutMonitor** (1 hour)
   - Add TimeProvider constructor parameter
   - Replace `datetime.now()` with `time_provider.now_utc()`

5. **Update Tests** (4 hours)
   - Use mocked adapters in unit tests
   - Remove all test file creation
   - Use in-memory adapters throughout
   - Verify tests run without filesystem access

**Total Effort:** ~14 hours

---

### Phase 2: Enhanced Architecture (Nice to Have)

**Goal:** Complete hexagonal architecture for production readiness

**Steps:**

1. **Add LoggingPort** (2 hours)
   - Define interface
   - Implement StructuredLogger
   - Implement SilentLogger
   - Inject into orchestrator

2. **Add TaskInvocationPort** (Optional, 3 hours)
   - Define interface
   - Implement ClaudeCodeTaskAdapter
   - Implement MockedTaskAdapter
   - Integrate with orchestrator

3. **Add ConfigPort** (Optional, 2 hours)
   - Define interface
   - Implement EnvironmentConfigAdapter
   - Implement InMemoryConfigAdapter

**Total Effort:** ~7 hours (optional)

---

## Hexagonal Architecture Compliance Checklist

### Core Principles

- [ ] **Domain Layer Purity**: DESOrchestrator depends ONLY on Port interfaces
- [ ] **Dependency Inversion**: All infrastructure injected through constructor
- [ ] **Test Independence**: Domain layer testable with in-memory adapters
- [ ] **Adapter Symmetry**: Each Port has production and test adapter

### Port Coverage

**Critical (MUST):**
- [ ] HookPort with RealSubagentStopHook and MockedSubagentStopHook
- [ ] ValidatorPort with RealTemplateValidator and MockedTemplateValidator
- [ ] FileSystemPort with RealFileSystem and InMemoryFileSystem
- [ ] TimeProvider with SystemTimeProvider and MockedTimeProvider

**Important (SHOULD):**
- [ ] LoggingPort with StructuredLogger and SilentLogger
- [ ] TaskInvocationPort with ClaudeCodeTaskAdapter and MockedTaskAdapter

**Optional (NICE TO HAVE):**
- [ ] ConfigPort with adapters

### Constructor Injection

```python
# REQUIRED: Full dependency injection
def __init__(
    self,
    hook: HookPort,
    validator: ValidatorPort,
    filesystem: FileSystemPort,
    time_provider: TimeProvider,
    logger: LoggingPort | None = None
):
    self._hook = hook
    self._validator = validator
    self._filesystem = filesystem
    self._time_provider = time_provider
    self._logger = logger or SilentLogger()
```

### Zero Concrete Dependencies

**Forbidden in Domain Layer:**
- ❌ `open()` calls
- ❌ `json.load()` / `json.dump()`
- ❌ `datetime.now()`
- ❌ Direct `SubagentStopHook()` instantiation
- ❌ Direct `TemplateValidator()` instantiation
- ❌ Any infrastructure imports in domain classes

**Allowed in Domain Layer:**
- ✅ Port interface calls
- ✅ Pure business logic
- ✅ Data structure manipulation
- ✅ Validation rules

---

## Migration Roadmap

### Step 1: Create Ports Directory Structure

```
des/
├── ports/
│   ├── __init__.py
│   ├── hook_port.py           # HookPort interface
│   ├── validator_port.py      # ValidatorPort interface
│   ├── filesystem_port.py     # FileSystemPort interface
│   └── time_provider_port.py  # TimeProvider interface
├── adapters/
│   ├── __init__.py
│   ├── real_hook.py           # RealSubagentStopHook
│   ├── mocked_hook.py         # MockedSubagentStopHook
│   ├── real_validator.py      # RealTemplateValidator
│   ├── mocked_validator.py    # MockedTemplateValidator
│   ├── real_filesystem.py     # RealFileSystem
│   ├── in_memory_filesystem.py # InMemoryFileSystem
│   ├── system_time.py         # SystemTimeProvider
│   └── mocked_time.py         # MockedTimeProvider
├── orchestrator.py            # Refactored with DI
├── hooks.py                   # Rename to real_hook.py
├── validator.py               # Rename to real_validator.py
└── timeout_monitor.py         # Refactored with TimeProvider
```

### Step 2: Define Port Interfaces (Code Examples)

**File: des/ports/hook_port.py**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional

@dataclass
class HookResult:
    """Result from hook validation."""
    validation_status: str
    hook_fired: bool = True
    abandoned_phases: List[str] = field(default_factory=list)
    incomplete_phases: List[str] = field(default_factory=list)
    invalid_skips: List[str] = field(default_factory=list)
    error_count: int = 0
    error_type: Optional[str] = None
    error_message: Optional[str] = None
    recovery_suggestions: List[str] = field(default_factory=list)
    not_executed_phases: int = 0
    turn_limit_exceeded: bool = False
    timeout_exceeded: bool = False

class HookPort(ABC):
    """Port for post-execution validation hooks."""

    @abstractmethod
    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Validate step file after sub-agent completion.

        Args:
            step_file_path: Absolute path to step JSON file

        Returns:
            HookResult with validation status and any errors found
        """
        pass
```

**File: des/ports/validator_port.py**

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationResult:
    """Result of template validation."""
    status: str
    errors: List[str]
    task_invocation_allowed: bool
    duration_ms: float
    recovery_guidance: Optional[List[str]] = None

class ValidatorPort(ABC):
    """Port for template validation."""

    @abstractmethod
    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate prompt for mandatory sections and TDD phases.

        Args:
            prompt: Full prompt text to validate

        Returns:
            ValidationResult with status, errors, and task invocation flag
        """
        pass
```

**File: des/ports/filesystem_port.py**

```python
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any

class FileSystemPort(ABC):
    """Port for file system operations."""

    @abstractmethod
    def read_json(self, path: Path) -> dict:
        """Read and parse JSON file.

        Args:
            path: Absolute path to JSON file

        Returns:
            Parsed JSON data as dictionary

        Raises:
            FileNotFoundError: If file doesn't exist
            JSONDecodeError: If file is not valid JSON
        """
        pass

    @abstractmethod
    def write_json(self, path: Path, data: dict) -> None:
        """Write data as formatted JSON file.

        Args:
            path: Absolute path to target JSON file
            data: Dictionary to write as JSON
        """
        pass

    @abstractmethod
    def exists(self, path: Path) -> bool:
        """Check if path exists.

        Args:
            path: Path to check

        Returns:
            True if path exists
        """
        pass
```

**File: des/ports/time_provider_port.py**

```python
from abc import ABC, abstractmethod
from datetime import datetime

class TimeProvider(ABC):
    """Port for time operations."""

    @abstractmethod
    def now_utc(self) -> datetime:
        """Get current UTC time.

        Returns:
            Current datetime in UTC timezone
        """
        pass
```

### Step 3: Implement Adapters

**File: des/adapters/real_hook.py** (Rename existing hooks.py)

```python
# Move SubagentStopHook class here, rename to RealSubagentStopHook
# Add implements HookPort
from des.ports.hook_port import HookPort, HookResult
import json

class RealSubagentStopHook(HookPort):
    """Production implementation of post-execution hook."""

    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Validate step file after agent completion."""
        with open(step_file_path, 'r') as f:
            step_data = json.load(f)

        # ... existing validation logic ...

        return result
```

**File: des/adapters/mocked_hook.py**

```python
from des.ports.hook_port import HookPort, HookResult

class MockedSubagentStopHook(HookPort):
    """Test implementation of post-execution hook."""

    def __init__(self, predefined_result: HookResult = None):
        self._result = predefined_result or HookResult(
            validation_status="PASSED"
        )
        self.call_count = 0
        self.last_step_file_path = None

    def on_agent_complete(self, step_file_path: str) -> HookResult:
        """Return predefined result without file I/O."""
        self.call_count += 1
        self.last_step_file_path = step_file_path
        return self._result
```

**File: des/adapters/in_memory_filesystem.py**

```python
from des.ports.filesystem_port import FileSystemPort
from pathlib import Path
from typing import Dict

class InMemoryFileSystem(FileSystemPort):
    """In-memory file system for testing."""

    def __init__(self):
        self._files: Dict[str, dict] = {}

    def read_json(self, path: Path) -> dict:
        """Read JSON from memory."""
        key = str(path)
        if key not in self._files:
            raise FileNotFoundError(f"File not found: {path}")
        return self._files[key].copy()

    def write_json(self, path: Path, data: dict) -> None:
        """Write JSON to memory."""
        self._files[str(path)] = data.copy()

    def exists(self, path: Path) -> bool:
        """Check if path exists in memory."""
        return str(path) in self._files

    def seed_file(self, path: Path, data: dict) -> None:
        """Test helper: Add file to memory."""
        self._files[str(path)] = data
```

**File: des/adapters/mocked_time.py**

```python
from des.ports.time_provider_port import TimeProvider
from datetime import datetime, timedelta

class MockedTimeProvider(TimeProvider):
    """Mocked time provider for deterministic testing."""

    def __init__(self, fixed_time: datetime):
        self._time = fixed_time

    def now_utc(self) -> datetime:
        """Return fixed/advanced time."""
        return self._time

    def advance(self, seconds: float) -> None:
        """Test helper: Advance time by seconds."""
        self._time += timedelta(seconds=seconds)
```

### Step 4: Refactor DESOrchestrator

**File: des/orchestrator.py**

```python
from des.ports.hook_port import HookPort
from des.ports.validator_port import ValidatorPort
from des.ports.filesystem_port import FileSystemPort
from des.ports.time_provider_port import TimeProvider

class DESOrchestrator:
    """Orchestrates DES validation with injected dependencies."""

    def __init__(
        self,
        hook: HookPort,
        validator: ValidatorPort,
        filesystem: FileSystemPort,
        time_provider: TimeProvider
    ):
        """Initialize with injected ports.

        Args:
            hook: Post-execution validation hook
            validator: Template validation
            filesystem: File I/O operations
            time_provider: Time operations
        """
        self._hook = hook
        self._validator = validator
        self._filesystem = filesystem
        self._time_provider = time_provider
        self._subagent_lifecycle_completed = False
        self._step_file_path = None

    def validate_prompt(self, prompt: str) -> ValidationResult:
        """Validate prompt using injected validator."""
        return self._validator.validate_prompt(prompt)

    def on_subagent_complete(self, step_file_path: str) -> HookResult:
        """Invoke hook using injected port."""
        return self._hook.on_agent_complete(step_file_path)

    def _load_step_file(self, step_file_path: Path) -> dict:
        """Load step file using injected filesystem."""
        return self._filesystem.read_json(step_file_path)

    def _persist_turn_count(self, step_file_path: Path, step_data: dict, ...):
        """Persist using injected filesystem."""
        current_phase["turn_count"] = turn_count
        self._filesystem.write_json(step_file_path, step_data)
```

### Step 5: Update Production Factory

**File: des/factory.py** (NEW)

```python
from des.orchestrator import DESOrchestrator
from des.adapters.real_hook import RealSubagentStopHook
from des.adapters.real_validator import RealTemplateValidator
from des.adapters.real_filesystem import RealFileSystem
from des.adapters.system_time import SystemTimeProvider

def create_production_orchestrator() -> DESOrchestrator:
    """Factory for production DESOrchestrator with real adapters."""
    return DESOrchestrator(
        hook=RealSubagentStopHook(),
        validator=RealTemplateValidator(),
        filesystem=RealFileSystem(),
        time_provider=SystemTimeProvider()
    )
```

### Step 6: Update Tests

**File: tests/test_orchestrator.py**

```python
from des.orchestrator import DESOrchestrator
from des.adapters.mocked_hook import MockedSubagentStopHook
from des.adapters.mocked_validator import MockedTemplateValidator
from des.adapters.in_memory_filesystem import InMemoryFileSystem
from des.adapters.mocked_time import MockedTimeProvider
from datetime import datetime, timezone

def test_execute_step_with_mocked_adapters():
    """Test orchestrator with in-memory adapters."""
    # Setup
    filesystem = InMemoryFileSystem()
    step_file_path = Path("/project/steps/01-01.json")
    filesystem.seed_file(step_file_path, {
        "tdd_cycle": {
            "phase_execution_log": [{
                "phase_name": "PREPARE",
                "status": "NOT_EXECUTED",
                "started_at": "2026-01-26T10:00:00Z"
            }],
            "max_turns": 50,
            "duration_minutes": 30
        }
    })

    # Create orchestrator with mocked dependencies
    orchestrator = DESOrchestrator(
        hook=MockedSubagentStopHook(),
        validator=MockedTemplateValidator(),
        filesystem=filesystem,
        time_provider=MockedTimeProvider(datetime(2026, 1, 26, 10, 0, 0, tzinfo=timezone.utc))
    )

    # Execute
    result = orchestrator.execute_step(
        command="/nw:execute",
        agent="@software-crafter",
        step_file="steps/01-01.json",
        project_root=Path("/project"),
        simulated_iterations=5
    )

    # Assert - NO FILESYSTEM ACCESS OCCURRED
    assert result.turn_count == 5
    assert result.phase_name == "PREPARE"
```

---

## ADR Updates Required

The architecture design document should be updated with the following ADRs:

### ADR-001: Hexagonal Architecture with Dependency Injection

**Status:** APPROVED

**Context:**
DES domain logic (DESOrchestrator, SubagentStopHook, TimeoutMonitor) was tightly coupled to infrastructure (filesystem, time, hooks). This violated hexagonal architecture principles and made unit testing require filesystem access.

**Decision:**
Adopt hexagonal architecture with:
1. Port interfaces for all external dependencies
2. Production adapters for real infrastructure
3. Test adapters for in-memory operations
4. Constructor dependency injection throughout

**Consequences:**
- ✅ Domain layer testable without filesystem
- ✅ Zero external dependencies in business logic
- ✅ Easy to swap implementations
- ✅ Follows SOLID principles
- ⚠️ Requires refactoring existing code
- ⚠️ More files/interfaces to maintain

### ADR-002: FileSystemPort for File I/O Abstraction

**Status:** APPROVED

**Context:**
DESOrchestrator and SubagentStopHook directly call `open()`, `json.load()`, `json.dump()`, making them dependent on real filesystem.

**Decision:**
Create FileSystemPort with:
- `read_json(path)` for reading step files
- `write_json(path, data)` for persisting updates
- Production adapter: RealFileSystem
- Test adapter: InMemoryFileSystem

**Consequences:**
- ✅ Tests run without creating files
- ✅ Faster test execution
- ✅ No test file cleanup needed
- ⚠️ All file access must go through port

### ADR-003: HookPort for Post-Execution Validation

**Status:** APPROVED

**Context:**
SubagentStopHook was directly instantiated in DESOrchestrator, preventing test isolation and violating dependency inversion.

**Decision:**
Create HookPort interface with:
- `on_agent_complete(step_file_path) -> HookResult`
- Production adapter: RealSubagentStopHook (existing SubagentStopHook)
- Test adapter: MockedSubagentStopHook (returns predefined results)

**Consequences:**
- ✅ Hook validation testable without filesystem
- ✅ Can inject different hook implementations
- ✅ Test-specific validation scenarios
- ⚠️ Requires refactoring SubagentStopHook

### ADR-004: TimeProvider for Deterministic Time Testing

**Status:** APPROVED

**Context:**
TimeoutMonitor calls `datetime.now()` directly, making timeout tests dependent on real wall-clock time and non-deterministic.

**Decision:**
Create TimeProvider port with:
- `now_utc() -> datetime`
- Production adapter: SystemTimeProvider (wraps `datetime.now()`)
- Test adapter: MockedTimeProvider (fixed time + advance())

**Consequences:**
- ✅ Timeout tests are deterministic
- ✅ Can simulate time passage in tests
- ✅ No sleep() in tests
- ⚠️ TimeoutMonitor requires refactoring

---

## External Validity Check

**Question:** After implementing all Port abstractions and dependency injection, will DESOrchestrator be INVOCABLE with in-memory adapters?

**Answer:** YES

**Validation:**
1. ✅ **Constructor takes Port interfaces** - Can inject mocked adapters
2. ✅ **No direct file I/O** - All filesystem access through FileSystemPort
3. ✅ **No direct time access** - All datetime through TimeProvider
4. ✅ **No direct hook instantiation** - Hook injected through HookPort
5. ✅ **Tests can run in-memory** - InMemoryFileSystem + MockedTimeProvider + MockedHook
6. ✅ **Unit tests are deterministic** - No randomness, no real time, no filesystem state

**Example Test Invocation:**

```python
orchestrator = DESOrchestrator(
    hook=MockedSubagentStopHook(predefined_result=passing_result),
    validator=MockedTemplateValidator(always_pass=True),
    filesystem=InMemoryFileSystem(),
    time_provider=MockedTimeProvider(fixed_time=test_start_time)
)

result = orchestrator.execute_step(...)  # INVOCABLE with no side effects
```

---

## Review Summary

### Issues Identified

| Issue | Severity | Component | Impact |
|-------|----------|-----------|--------|
| Domain layer has concrete dependencies | HIGH | DESOrchestrator | Cannot test independently |
| Missing HookPort abstraction | HIGH | SubagentStopHook | User explicitly requested |
| Missing ValidatorPort abstraction | HIGH | TemplateValidator | Core domain coupling |
| Direct file I/O in domain layer | HIGH | DESOrchestrator | Filesystem dependency |
| Direct time operations | HIGH | TimeoutMonitor | Non-deterministic tests |
| Missing LoggingPort | MEDIUM | All components | Future production need |
| No Task invocation abstraction | MEDIUM | DESOrchestrator | Completeness gap |
| No configuration abstraction | LOW | All components | Future scalability |

### Approval Status

**NEEDS_REVISION** - HIGH severity issues block hexagonal architecture

**Blocking Items:**
1. Create HookPort interface
2. Create ValidatorPort interface
3. Enforce FileSystemPort (already in design)
4. Enforce TimeProvider (already in design)
5. Refactor DESOrchestrator with dependency injection
6. Refactor TimeoutMonitor with TimeProvider injection

**Recommendation:**
Complete Phase 1 refactoring (14 hours estimated) before considering architecture production-ready. All tests must run with in-memory adapters to validate true hexagonal architecture compliance.

---

## Reviewer Notes

This review was conducted per the user's explicit request (Italian): "la /nw:review deve essere fatta su tutto il design per capire come riorganizzare affinche sia veramente esagonale in tutti i suoi componenti" ("the review must be done on the entire design to understand how to reorganize so that it is truly hexagonal in all its components").

The review identified 7 external dependencies requiring Port abstractions. Only FileSystemPort and TimeProvider were mentioned in the design document; the remaining 5 dependencies (HookPort, ValidatorPort, LoggingPort, TaskInvocationPort, ConfigPort) were discovered through source code analysis.

**User explicitly mentioned the hook system** as an example of missing abstraction but emphasized it's not the only issue - a comprehensive review was required.

---

**Review Completed:** 2026-01-26
**Reviewer Signature:** Atlas (solution-architect-reviewer)
