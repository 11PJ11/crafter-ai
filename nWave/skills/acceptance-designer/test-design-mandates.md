---
name: test-design-mandates
description: Three design mandates for acceptance tests - hexagonal boundary enforcement, business language abstraction, user journey completeness, and walking skeleton strategy
---

# Acceptance Test Design Mandates

These three mandates are enforced during peer review. All must pass before handoff to software-crafter.

## Mandate 1: Hexagonal Boundary Enforcement

Tests invoke through driving ports (entry points), never internal components.

### Driving Ports (Test Through These)
- Application services / orchestrators
- API controllers / CLI handlers
- Message consumers / event handlers
- Public API facade classes

### Not Entry Points (Never Test Directly)
- Internal validators, parsers, formatters
- Domain entities or value objects
- Repository implementations
- Internal service components

### Correct Pattern

```python
# Invoke through system entry point (driving port)
from myapp.orchestrator import AppOrchestrator

def when_user_performs_action(self):
    orchestrator = AppOrchestrator()
    self.result = orchestrator.perform_action(
        context=self.context
    )
```

### Violation Pattern

```python
# Invoking internal component directly
from myapp.validator import InputValidator  # INTERNAL

def when_user_validates_input(self):
    validator = InputValidator()  # WRONG BOUNDARY
    self.result = validator.validate(self.input)
```

### Why It Matters
Testing internal components creates Testing Theater: tests pass but users cannot access the feature through the actual entry point. Integration wiring bugs remain hidden.

## Mandate 2: Business Language Abstraction

Step methods speak business language, abstract all technical details.

### Three Abstraction Layers

**Layer 1 - Gherkin**: Pure business language, accessible to all stakeholders.
- Use domain terms from ubiquitous language
- Zero technical jargon (no HTTP, database, API, JSON terms)
- Describe WHAT user does, not HOW system does it

```gherkin
Scenario: Customer places order for available product
  Given customer has items in shopping cart
  When customer submits order
  Then order is confirmed
  And customer receives confirmation email
```

**Layer 2 - Step Methods**: Business service delegation, abstract infrastructure.
- Method names use business domain terms
- Delegate to business service layer (OrderService, not HTTP client)
- Assert business outcomes (order.is_confirmed()), not technical state (status_code == 201)

```python
def when_customer_submits_order(self):
    self.result = self.order_service.place_order(
        customer=self.customer, items=self.cart_items
    )

def then_order_is_confirmed(self):
    assert self.result.is_confirmed()
    assert self.result.has_order_number()
```

**Layer 3 - Business Services**: Production services handle technical implementation.
Technical details (HTTP calls, database transactions, SMTP) hidden inside service layer.

### Test Smell Indicators
- `requests.post()` in step method
- `db.execute()` in step method
- `assert response.status_code`
- Technical terms in Gherkin (HTTP, REST, JSON, database)

## Mandate 3: User Journey Completeness

Tests validate complete user journeys with business value, not isolated technical operations.

### Complete Journey Structure

Every scenario includes:
- **User trigger**: Given/When - what user does or business event occurs
- **Business logic**: When - system processes business rules
- **Observable outcome**: Then - user sees result
- **Business value**: Then - value delivered (confirmation, data, access)

### Correct Example

```gherkin
Scenario: Customer successfully completes purchase
  Given customer has selected products worth $150
  And customer has valid payment method
  When customer submits order
  Then order is confirmed with order number
  And customer receives email confirmation
  And order appears in customer's order history
```

### Violation Example

```gherkin
Scenario: Order validator accepts valid order data
  Given valid order JSON exists
  When validator.validate() is called
  Then validation passes
# Tests isolated validation, not user journey
```

### Scenario Name Test
Does the scenario name express user value or a technical operation? "Customer completes purchase" = correct. "Validator accepts JSON" = violation.

## Walking Skeleton Strategy

Balance E2E integration tests with focused boundary tests.

### Walking Skeletons (2-5 per feature)
- Complete E2E integration touching all system layers
- Validate critical happy paths
- Prove system wiring works
- Characteristics: UI > Services > DB > Email (full stack)

### Focused Scenarios (15-20 per feature, majority of suite)
- Test specific business rules at driving port boundary
- Use test doubles for external dependencies (faster, isolated)
- Cover business rule variations and edge cases
- Invoke through entry point (OrderService, Orchestrator)

### Recommended Ratio

For a typical feature with 20 acceptance scenarios:
- 2-3 walking skeletons (E2E integration)
- 17-18 focused scenarios (boundary tests with test doubles)

Walking skeletons prove integration works. Focused scenarios run fast and cover breadth. Both use business language and invoke through entry points.

## Mandate Compliance Verification

Handoff to software-crafter includes proof that all three mandates pass:

- **CM-A**: All test files import entry points (driving ports), zero internal component imports
- **CM-B**: Gherkin scenarios use business terms only, step methods delegate to services
- **CM-C**: Scenarios validate complete user journeys with business value

Evidence format: import listings, grep results for technical terms, walking skeleton identification and focused scenario count.
