# DES Extension Request API

## Overview

The Extension Request API provides a standardized interface for requesting additional computational budget (turns or time) from the Dynamic Extension System (DES).

## API Components

### ExtensionRequest Dataclass

```python
@dataclass
class ExtensionRequest:
    reason: str
    additional_turns: Optional[int]
    additional_minutes: Optional[int]
```

**Fields:**

- `reason` (str): Human-readable explanation for why the extension is needed
- `additional_turns` (Optional[int]): Number of additional turns requested (None if not requesting turns)
- `additional_minutes` (Optional[int]): Additional time in minutes requested (None if not requesting time)

**Constraints:**

- At least one of `additional_turns` or `additional_minutes` must be specified (not both None)
- `reason` is required and must be non-empty

### request_extension() Function

```python
def request_extension(
    reason: str,
    additional_turns: Optional[int] = None,
    additional_minutes: Optional[int] = None,
) -> ExtensionRequest
```

**Parameters:**

- `reason` (str): Explanation for why extension is needed
- `additional_turns` (Optional[int], default=None): Number of extra turns requested
- `additional_minutes` (Optional[int], default=None): Extra time in minutes requested

**Returns:**

- `ExtensionRequest`: Configured extension request instance

## Usage Examples

### Request Additional Turns

```python
from des.extension_api import request_extension

# Request 5 additional turns for complex refactoring
request = request_extension(
    reason="Need more turns to complete systematic refactoring with full test coverage",
    additional_turns=5
)
```

### Request Additional Time

```python
from des.extension_api import request_extension

# Request 10 additional minutes
request = request_extension(
    reason="Complex integration testing requires more time",
    additional_minutes=10
)
```

### Request Both Turns and Time

```python
from des.extension_api import request_extension

# Request both additional turns and time
request = request_extension(
    reason="Large-scale refactoring with comprehensive mutation testing",
    additional_turns=3,
    additional_minutes=15
)
```

## Design Rationale

### Why Dataclass?

- **Type Safety**: Static type checking via type hints
- **Immutability**: Dataclass instances are value objects
- **Serialization**: Easy conversion to/from JSON for persistence
- **Documentation**: Self-documenting structure

### Why Factory Function?

- **Encapsulation**: Hide dataclass construction details
- **Validation**: Centralized place for future validation logic
- **Flexibility**: Can evolve implementation without breaking API
- **Testability**: Easier to mock/stub in tests

### Why Optional Fields?

- **Flexibility**: Extensions may need turns OR time, not necessarily both
- **Clarity**: Explicit None vs omission distinguishes "not requested" from "zero requested"
- **Future-Proof**: Additional extension types can be added without breaking changes

## Integration Points

### Orchestrator Integration

The orchestrator will use this API to:

1. Detect approaching budget limits (turns or time)
2. Create extension requests with business context
3. Submit requests to DES hooks for processing
4. Apply approved extensions to current session budget

### Hooks Integration

DES hooks will:

1. Receive ExtensionRequest instances
2. Evaluate request validity and business rules
3. Return approval/denial decisions
4. Track extension history for audit

## Future Enhancements

Potential extensions to the API:

- Validation constraints (min/max values for turns/minutes)
- Priority levels (urgent, normal, low)
- Auto-extension policies based on task complexity
- Extension request history tracking
- Cost/benefit analysis integration

## API Stability

**Version**: 1.0.0

**Stability**: Experimental

This API is under active development for DES US004. Breaking changes may occur until marked stable.

## See Also

- [DES Orchestrator Design](orchestrator_design.md) - How extensions are orchestrated
- [DES Hooks Design](hooks_design.md) - Extension approval logic
- [DES Validator Design](validator_design.md) - Budget validation integration
