# DES Hexagonal Architecture Structure Diagrams

## Visual Architecture: Option B (Recommended)

### Layered Hexagon Model

```
┌─────────────────────────────────────────────────────────────────┐
│                        EXTERNAL WORLD                            │
│  (Hooks, Validators, File System, Time, Logging, Config)        │
└────────────────┬────────────────────────────────────────────────┘
                 │
    ┌────────────┴────────────┐
    │                         │
    ▼ (PRIMARY ADAPTERS)      ▼ (SECONDARY ADAPTERS)
┌──────────────────┐    ┌──────────────────────────┐
│ ADAPTERS/DRIVERS │    │ ADAPTERS/DRIVEN          │
├──────────────────┤    ├──────────────────────────┤
│ hooks/           │    │ filesystem/              │
│ validators/      │    │ time/                    │
└────────┬─────────┘    │ logging/                 │
         │              │ config/                  │
         │              │ task_invocation/         │
         │              └──────────┬───────────────┘
         │                         │
         │ (implements)            │ (implements)
         │                         │
         ▼                         ▼
    ┌────────────────────────────────────────┐
    │          PORTS (Abstractions)          │
    ├────────────────────────────────────────┤
    │ DRIVER_PORTS                           │
    │  • hook_port                           │
    │  • validator_port                      │
    │                                        │
    │ DRIVEN_PORTS                           │
    │  • filesystem_port                     │
    │  • time_provider_port                  │
    │  • logging_port                        │
    │  • config_port                         │
    │  • task_invocation_port                │
    └────────────────┬──────────────────────┘
                     │
                     │ (uses)
                     │
    ┌────────────────▼──────────────────────┐
    │     APPLICATION LAYER                 │
    ├───────────────────────────────────────┤
    │ • orchestrator.py (Main orchestration)│
    │ • services.py (Supporting services)   │
    └────────────────┬──────────────────────┘
                     │
                     │ (uses)
                     │
    ┌────────────────▼──────────────────────┐
    │      DOMAIN LAYER (Core Logic)        │
    ├───────────────────────────────────────┤
    │ • turn_counter.py                     │
    │ • timeout_monitor.py                  │
    │ • turn_config.py                      │
    │ • invocation_limits_validator.py      │
    └───────────────────────────────────────┘
```

### Dependency Flow (Clean Architecture)

```
Direction of Dependencies: ALWAYS INWARD

EXTERNAL SYSTEMS (Filesystem, Time, Hooks, etc.)
         ▲
         │ (dependency inversion)
         │
    ┌────────────────────┐
    │  ADAPTERS          │
    │  (Implementations) │
    └──────────┬─────────┘
               │ implements
               │
    ┌──────────▼─────────┐
    │  PORTS             │
    │  (Abstractions)    │
    └──────────┬─────────┘
               │ uses
               │
    ┌──────────▼────────────────────┐
    │  APPLICATION + DOMAIN         │
    │  (Independent of             │
    │   external concerns)          │
    └───────────────────────────────┘
```

### Directory Tree Structure

```
src/des/
│
├── 🔷 DOMAIN LAYER (Core Business Logic - NO External Dependencies)
│   ├── turn_counter.py
│   ├── timeout_monitor.py
│   ├── turn_config.py
│   ├── invocation_limits_validator.py
│   └── __init__.py
│
├── 🔶 APPLICATION LAYER (Orchestration & Services - Uses Ports)
│   ├── orchestrator.py
│   ├── services.py
│   └── __init__.py
│
├── 📋 PORTS (Abstract Interfaces - No Implementation)
│   │
│   ├── driver_ports/ (INBOUND - How external code calls us)
│   │   ├── hook_port.py
│   │   ├── validator_port.py
│   │   └── __init__.py
│   │
│   ├── driven_ports/ (OUTBOUND - How we call external systems)
│   │   ├── filesystem_port.py
│   │   ├── time_provider_port.py
│   │   ├── logging_port.py
│   │   ├── config_port.py
│   │   ├── task_invocation_port.py
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── 🔧 ADAPTERS (Concrete Implementations - Replace per environment)
│   │
│   ├── drivers/ (PRIMARY ADAPTERS - Entry Points)
│   │   │
│   │   ├── hooks/
│   │   │   ├── real_hook.py (implements hook_port)
│   │   │   └── __init__.py
│   │   │
│   │   ├── validators/
│   │   │   ├── real_validator.py (implements validator_port)
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   ├── driven/ (SECONDARY ADAPTERS - Dependencies)
│   │   │
│   │   ├── filesystem/
│   │   │   ├── real_filesystem.py (implements filesystem_port)
│   │   │   └── __init__.py
│   │   │
│   │   ├── time/
│   │   │   ├── system_time.py (implements time_provider_port)
│   │   │   └── __init__.py
│   │   │
│   │   ├── logging/
│   │   │   ├── structured_logger.py (implements logging_port)
│   │   │   ├── silent_logger.py (implements logging_port)
│   │   │   └── __init__.py
│   │   │
│   │   ├── config/
│   │   │   ├── environment_config_adapter.py (implements config_port)
│   │   │   ├── in_memory_config_adapter.py (implements config_port)
│   │   │   └── __init__.py
│   │   │
│   │   ├── task_invocation/
│   │   │   ├── claude_code_task_adapter.py (implements task_invocation_port)
│   │   │   ├── mocked_task_adapter.py (implements task_invocation_port)
│   │   │   └── __init__.py
│   │   │
│   │   └── __init__.py
│   │
│   └── __init__.py
│
└── __init__.py
```

### Test Directory Structure

```
tests/des/
│
├── 📊 adapters/ (Shared Test Doubles - Used across all test types)
│   ├── mocked_hook.py
│   ├── mocked_validator.py
│   ├── mocked_time.py
│   ├── mocked_filesystem.py
│   ├── mocked_config.py
│   └── __init__.py
│
├── 🧪 unit/ (ISOLATED - Single component in isolation)
│   │
│   ├── domain/
│   │   ├── test_turn_counter.py
│   │   ├── test_timeout_monitor.py
│   │   ├── test_turn_config.py
│   │   └── __init__.py
│   │
│   ├── application/
│   │   ├── test_orchestrator.py
│   │   ├── test_services.py
│   │   └── __init__.py
│   │
│   ├── ports/
│   │   ├── test_hook_port.py (interface contract)
│   │   ├── test_validator_port.py (interface contract)
│   │   └── __init__.py
│   │
│   └── __init__.py
│
├── 🔗 integration/ (INTERACTION - 2+ components working together)
│   ├── test_turn_discipline.py
│   ├── test_timeout_monitoring.py
│   ├── test_orchestrator_integration.py
│   ├── test_step_execution.py
│   └── __init__.py
│
├── ✅ acceptance/ (USER STORIES - Feature acceptance criteria)
│   ├── test_turn_counting.py
│   ├── test_invocation_limits.py
│   ├── test_timeout_warnings.py
│   ├── test_prompt_validation.py
│   └── __init__.py
│
├── 🌍 e2e/ (SCENARIOS - Full system end-to-end)
│   ├── test_scenario_013_timeout_warnings.py
│   ├── test_scenario_014_agent_timeout_warnings.py
│   └── __init__.py
│
├── conftest.py (Shared fixtures & configuration)
└── __init__.py
```

---

## Port/Adapter Implementation Pairing

### Visual Mapping

```
┌──────────────────────────────────────────────────────────────────┐
│                     APPLICATION CORE                             │
│  (orchestrator.py, domain logic - NO external dependencies)      │
└──────────────┬───────────────────────────────────────────────────┘
               │
               │ depends on (imports)
               │
    ┌──────────▼──────────────────────────────────────────┐
    │               PORTS (Abstractions)                   │
    │  Abstract interfaces - what core logic needs        │
    └──────┬──────────────────────────────┬───────────────┘
           │                              │
        PRIMARY                        SECONDARY
      (INBOUND)                         (OUTBOUND)
      How external                    How we call
      systems call us                 external systems
           │                              │
    ┌──────▼──────────┐          ┌────────▼────────────┐
    │ DRIVER PORTS    │          │ DRIVEN PORTS        │
    ├─────────────────┤          ├─────────────────────┤
    │ • hook_port     │          │ • filesystem_port   │
    │ • validator_port│          │ • time_provider_port│
    │                 │          │ • logging_port      │
    └────────┬────────┘          │ • config_port       │
             │                   │ • task_invocation   │
             │                   └──────────┬──────────┘
             │                             │
   ┌─────────▼──────────┐      ┌───────────▼──────────┐
   │ DRIVER ADAPTERS    │      │ DRIVEN ADAPTERS      │
   │ (Primary/Inbound)  │      │ (Secondary/Outbound) │
   ├────────────────────┤      ├────────────────────┐ │
   │ hooks/             │      │ filesystem/        │ │
   │ • real_hook.py     │      │ • real_filesystem  │ │
   │                    │      │                    │ │
   │ validators/        │      │ time/              │ │
   │ • real_validator   │      │ • system_time      │ │
   │                    │      │                    │ │
   │ "These are entry   │      │ logging/           │ │
   │  points - how      │      │ • structured_logger│ │
   │  external systems  │      │ • silent_logger    │ │
   │  call us"          │      │                    │ │
   │                    │      │ config/            │ │
   │                    │      │ • env_config_adp   │ │
   │                    │      │ • in_mem_config    │ │
   │                    │      │                    │ │
   │                    │      │ task_invocation/   │ │
   │                    │      │ • claude_code_task │ │
   │                    │      │ • mocked_task      │ │
   │                    │      │                    │ │
   │                    │      │ "These are how we  │ │
   │                    │      │  integrate with    │ │
   │                    │      │  external systems" │ │
   └────────┬───────────┘      └────────┬────────────┘
            │                           │
            │ (implements)              │ (implements)
            │                           │
    ┌───────▼────────────────────────────▼────────┐
    │         EXTERNAL SYSTEMS                     │
    │ • Agent execution framework                  │
    │ • Validation rules/templates                 │
    │ • Filesystem                                 │
    │ • System clock                               │
    │ • Logging infrastructure                     │
    │ • Configuration sources                      │
    └──────────────────────────────────────────────┘
```

### Concrete Example: Hook System

```
┌────────────────────────────────────────────┐
│     Application Core needs to call          │
│     "notify when agent completes"           │
└────────────────────────────────────────────┘
              │
              │
    ┌─────────▼──────────────────┐
    │  orchestrator.py           │
    │  calls _hook.on_agent_...()│
    │                            │
    │  (imports from ports)      │
    └─────────────┬──────────────┘
                  │
                  │ depends on
                  │
    ┌─────────────▼──────────────────────────┐
    │ ports/driver_ports/hook_port.py        │
    │                                        │
    │ class HookPort(ABC):                   │
    │     def on_agent_complete(...) -> ... │
    └──────────────┬───────────────────────┘
                   │
                   │ implemented by
                   │
    ┌──────────────▼──────────────────────────┐
    │ adapters/drivers/hooks/real_hook.py    │
    │                                        │
    │ class RealSubagentStopHook(HookPort):  │
    │     def on_agent_complete(...):        │
    │         # ACTUAL IMPLEMENTATION        │
    │         # Validates step file state    │
    │         # Detects abandoned phases     │
    │         return HookResult(...)         │
    └────────────────────────────────────────┘
            │
            │ uses (runtime dependency injection)
            │
    ┌───────▼──────────────────────────────┐
    │ External System: Step File Storage    │
    │ (JSON files, filesystem operations)   │
    └────────────────────────────────────────┘
```

---

## Import Patterns After Reorganization

### Pattern 1: Domain using Ports

```python
# src/des/domain/timeout_monitor.py
from src.des.ports.driven_ports.time_provider_port import TimeProvider

class TimeoutMonitor:
    def __init__(self, started_at: str, time_provider: TimeProvider):
        self._time_provider = time_provider  # injected dependency
```

### Pattern 2: Application using Domain and Ports

```python
# src/des/application/orchestrator.py
from src.des.domain.turn_counter import TurnCounter
from src.des.domain.timeout_monitor import TimeoutMonitor
from src.des.ports.driver_ports.hook_port import HookPort
from src.des.ports.driven_ports.filesystem_port import FileSystemPort
from src.des.ports.driven_ports.time_provider_port import TimeProvider

class DESOrchestrator:
    def __init__(
        self,
        hook: HookPort,           # injected port
        filesystem: FileSystemPort,
        time_provider: TimeProvider
    ):
        self._hook = hook
        self._filesystem = filesystem
        self._time_provider = time_provider
```

### Pattern 3: Adapters implementing Ports

```python
# src/des/adapters/drivers/hooks/real_hook.py
from src.des.ports.driver_ports.hook_port import HookPort, HookResult

class RealSubagentStopHook(HookPort):
    def on_agent_complete(self, step_file_path: str) -> HookResult:
        # Implementation
        pass
```

### Pattern 4: Dependency Injection Setup

```python
# src/des/application/orchestrator.py
@classmethod
def create_with_defaults(cls) -> "DESOrchestrator":
    from src.des.adapters.drivers.hooks.real_hook import RealSubagentStopHook
    from src.des.adapters.driven.filesystem.real_filesystem import RealFileSystem
    from src.des.adapters.driven.time.system_time import SystemTimeProvider

    hook = RealSubagentStopHook()
    filesystem = RealFileSystem()
    time_provider = SystemTimeProvider()

    return cls(
        hook=hook,
        filesystem=filesystem,
        time_provider=time_provider
    )
```

---

## Comparison: Before vs After Organization

### Before (Mixed Concerns)

```
src/des/
├── orchestrator.py          ← Where is this? Application? Domain?
├── timeout_monitor.py       ← Is this core logic or infrastructure?
├── turn_counter.py          ← Which layer?
├── validator.py             ← Application service or domain?
├── hooks.py                 ← Infrastructure - but unclear
├── ports/
└── adapters/
```

**Problem**: New developer asks "Where should my new timeout calculation logic go?" - Uncertain.

### After (Clear Layers)

```
src/des/
├── domain/
│   ├── timeout_monitor.py       ← CORE LOGIC: Phase timeout tracking
│   ├── turn_counter.py          ← CORE LOGIC: Turn count management
│   └── invocation_limits_validator.py ← CORE LOGIC: Limit validation
├── application/
│   ├── orchestrator.py          ← ORCHESTRATION: Command coordination
│   └── services.py              ← APPLICATION: High-level services
├── ports/
│   ├── driver_ports/            ← INBOUND: How external systems call us
│   └── driven_ports/            ← OUTBOUND: How we call external systems
└── adapters/
    ├── drivers/                 ← PRIMARY: Entry points (hooks, validators)
    └── driven/                  ← SECONDARY: External integrations
```

**Solution**: New developer knows exactly where to put new code based on its nature.

---

## Testing Visualization

### Test Pyramid with Organization

```
                    ▲
                   ╱ ╲
                  ╱   ╲  E2E Tests (5-10%)
                 ╱─────╲ Full system scenarios
                ╱       ╲
               ╱         ╲
              ╱───────────╲ Acceptance Tests (15-25%)
             ╱ integration ╲ Feature validation
            ╱   ╱───────╲   ╲
           ╱   ╱  ┌─────┐╲   ╲
          ╱   ╱   │  ┌─┐ │ ╲   ╲
         ╱───┼───┼──┼─┼─┤─┼────╲ Unit Tests (60-70%)
        ╱ u  │ n │  │i│ │t│ tests╲ Isolated components
       ╱─────┴───┴──┴─┴─┴─┴──────╱╲
      ╱         domain           ╱  ╲
     ╱          application      ╱    ╲
    ╱________ports_/_adapters___╱______╲
```

### Test Organization by Component

```
                 E2E Test Scenarios
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    Acceptance    Acceptance    Acceptance
    (US-001)      (US-002)      (US-003)
         │             │             │
         └─────────────┼─────────────┘
                       │
         ┌─────────────┼─────────────┐
         │             │             │
    Integration   Integration   Integration
    (Orchestrator) (Filesystem) (Timeouts)
         │             │             │
         └─────────────┼─────────────┘
                       │
    ┌──────────────────┼──────────────────┐
    │                  │                  │
Unit(Domain)     Unit(Application)   Unit(Ports)
├─ TurnCounter  ├─ Orchestrator    ├─ HookPort
├─ TimeoutMon   ├─ Services        ├─ ValidatorPort
├─ TurnConfig   └─ ConfigLoader    └─ ...
└─ ...
```

---

## Summary Table: Structure Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Code Location** | Mixed, unclear | Explicit by layer |
| **New Developer** | "Where does this go?" | Clear folder structure |
| **Port/Adapter Finding** | Search through flat adapters/ | Browse adapters/drivers/ or adapters/driven/ |
| **Test Navigation** | Flat tests/des/ | Mirrored hierarchy: unit/, integration/, acceptance/ |
| **Hexagonal Visualization** | Not apparent in filesystem | Clear in directory structure |
| **Dependency Direction** | Must trace in code | Clear in layer nesting |
| **Adding New Adapter** | Unclear where to put it | Obvious: drivers/ or driven/ subfolder |
| **Import Statements** | Short but ambiguous | Longer but explicit about layer |
