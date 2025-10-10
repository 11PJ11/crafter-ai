# BDD for Acceptance Designer: Practical E2E Test Creation Patterns

**Agent**: acceptance-designer
**Purpose**: Practical guidance for creating executable acceptance tests using BDD principles
**Research Date**: 2025-10-09
**Sources**: Cucumber.io, pytest-bdd, Serenity BDD, Dan North, Gojko Adzic, Property-Based Testing

---

## Core Philosophy: Testing Behavior, Not Implementation

### The Fundamental Principle

**Test units of behavior, not units of code.** Acceptance tests should validate business outcomes through public interfaces, remaining completely decoupled from implementation details to enable fearless refactoring.

**Key Insight**: "If you're not having conversations, you're not doing BDD." - Liz Keogh

Source: https://lizkeogh.com/2011/09/22/conversational-patterns-in-bdd/ (Accessed 2025-10-09)

---

## Double-Loop TDD: Outside-In Development

### Understanding the Two Loops

**Outer Loop (Acceptance/BDD Level)**
- Timescale: Hours to days
- Perspective: User/customer viewpoint
- Language: Business domain terms
- Purpose: Define what "done" looks like from user perspective
- Tools: Cucumber, pytest-bdd, SpecFlow

**Inner Loop (Unit/TDD Level)**
- Timescale: Minutes
- Perspective: Developer implementation
- Language: Technical terms
- Purpose: Design and implement granular functionality
- Tools: pytest, unittest, xUnit frameworks

**Workflow Pattern**:
1. Write failing acceptance test (outer loop) describing desired behavior
2. Drop to inner loop: write unit tests to implement required components
3. Iterate inner loop until components satisfy acceptance test
4. Return to outer loop: verify acceptance test passes
5. Repeat for next behavior

Source: https://sammancoaching.org/learning_hours/bdd/double_loop_tdd.html (Accessed 2025-10-09)

**Critical Relationship**: Outer loop guides "what to build", inner loop drives "how to build it". Always start outside-in, never bottom-up.

---

## Given-When-Then: The Anatomy of Executable Specifications

### Pattern Structure

```gherkin
Scenario: [Clear business-focused title describing the behavior]
  Given [Initial context/preconditions - system state]
  When [Action/event that triggers behavior]
  Then [Expected outcome/observable result]
```

### Writing Effective Scenarios

#### Rule 1: One Scenario, One Behavior
**Anti-Pattern**: Testing multiple outcomes in single scenario
```gherkin
# WRONG - Tests multiple behaviors
Scenario: User management
  Given I am an admin
  When I create a user
  Then the user exists
  When I delete the user
  Then the user is deleted
```

**Pattern**: Single, focused purpose
```gherkin
# CORRECT - One behavior per scenario
Scenario: Admin creates new user account
  Given I am authenticated as an admin
  When I create a user with email "user@example.com"
  Then a user account with email "user@example.com" exists
```

Source: https://cucumber.io/docs/guides/anti-patterns/ (Accessed 2025-10-09)

#### Rule 2: Declarative, Not Imperative
**Anti-Pattern**: UI-coupled implementation details
```gherkin
# WRONG - Coupled to UI implementation
Scenario: Login
  Given I open "https://app.example.com"
  And I click the "Login" button
  And I enter "user@example.com" in field "email"
  And I enter "password123" in field "password"
  And I click "Submit"
  Then I see "Welcome" on the page
```

**Pattern**: Business behavior focus
```gherkin
# CORRECT - Behavior-focused, UI-agnostic
Scenario: User authenticates with valid credentials
  Given I have a registered account
  When I log in with valid credentials
  Then I am authenticated and see my dashboard
```

Source: https://cucumber.io/blog/bdd/cucumber-antipatterns-part-one/ (Accessed 2025-10-09)

**Why This Matters**: UI changes frequently. Business logic changes rarely. Test the stable layer (behavior) not the volatile layer (UI).

#### Rule 3: Concrete Examples, Not Abstractions
**Anti-Pattern**: Overly abstract scenarios
```gherkin
# WRONG - Too abstract, no real example
Scenario: User purchases item
  Given the user has sufficient funds
  When the user purchases an item
  Then the purchase succeeds
```

**Pattern**: Concrete, illustrative examples
```gherkin
# CORRECT - Concrete values create understanding
Scenario: Customer with $100 purchases $45 book
  Given my account balance is $100.00
  When I purchase "Clean Code" priced at $45.00
  Then my order is confirmed
  And my account balance is $55.00
```

Source: https://gojko.net/2020/03/17/sbe-10-years.html (Accessed 2025-10-09)

**Critical Insight**: Abstract scenarios express rules but don't aid understanding. Concrete examples reveal assumptions and edge cases.

#### Rule 4: Keep Scenarios Short and Focused
**Target**: 3-5 steps per scenario maximum. If longer, you're testing multiple behaviors or including irrelevant details.

**Rambling Scenario Anti-Pattern**:
```gherkin
# WRONG - Too many incidental details
Scenario: Check bank balance
  Given I have an account with number "12345678"
  And I registered on "2023-01-15"
  And my password is "SecurePass123!"
  And my security question is "Mother's maiden name"
  And I have 2-factor authentication enabled
  When I log in with username "john@example.com" and password "SecurePass123!"
  And I navigate to accounts page
  And I click on account "12345678"
  Then I see balance "$1,234.56"
```

**Focused Scenario Pattern**:
```gherkin
# CORRECT - Only relevant details
Scenario: Authenticated user views account balance
  Given I am authenticated
  And my savings account balance is $1,234.56
  When I view my savings account
  Then the displayed balance is $1,234.56
```

Source: https://cucumber.io/blog/bdd/cucumber-antipatterns-part-one/ (Accessed 2025-10-09)

---

## pytest-bdd Implementation Patterns

### Step Definition Best Practices

#### Pattern 1: Fixture Integration for Context
```python
# Step definitions leverage pytest fixtures for dependency injection
from pytest_bdd import scenarios, given, when, then, parsers

# Load all scenarios from feature file
scenarios('../features/account.feature')

@given("I am authenticated", target_fixture="authenticated_user")
def authenticated_user(user_factory, auth_service):
    """Create authenticated user without coupling to auth mechanism."""
    user = user_factory.create(email="test@example.com")
    token = auth_service.authenticate(user)
    return {"user": user, "token": token}

@given(parsers.parse('my account balance is {amount:Number}'),
       target_fixture="account")
def account_with_balance(authenticated_user, account_repository, amount):
    """Given step that modifies fixture state."""
    account = account_repository.create_for_user(
        user=authenticated_user["user"],
        initial_balance=amount
    )
    return account
```

**Key Principle**: Steps access fixtures through argument injection. This decouples test specification (feature file) from test implementation (step definitions).

Source: https://pytest-bdd.readthedocs.io/en/latest/ (Accessed 2025-10-09)

#### Pattern 2: Background for Common Setup
```gherkin
Feature: Account Management
  Background:
    Given I am authenticated as a customer
    And I have an active checking account

  Scenario: View account balance
    When I request my account balance
    Then I see my current balance

  Scenario: Transfer funds between accounts
    Given I have a savings account
    When I transfer $100 from checking to savings
    Then my checking balance decreases by $100
    And my savings balance increases by $100
```

**Important Constraint**: Background should ONLY contain `Given` steps. Never use `When` or `Then` in Background.

**Rationale**: Background establishes context. Actions (`When`) and validations (`Then`) belong in scenarios.

Source: https://pytest-bdd.readthedocs.io/en/latest/ (Accessed 2025-10-09)

#### Pattern 3: Parsers for Flexible Step Matching
```python
from pytest_bdd import parsers

# String parser with custom type converters
@given(parsers.parse('my account balance is ${amount:Number}'))
def account_balance(amount):
    # amount automatically converted to Number type
    pass

# Regular expression parser for complex patterns
@when(parsers.re(r'I transfer \$(?P<amount>\d+(?:\.\d{2})?) from (?P<from_account>\w+) to (?P<to_account>\w+)'))
def transfer_funds(amount, from_account, to_account):
    # Captured groups become function arguments
    pass

# Custom type converter
from pytest_bdd.parsers import parse

parse.with_pattern(r"\d+(?:\.\d{2})?", name="Number",
                   type=lambda s: float(s))
```

**Best Practice**: Use `parsers.parse()` for simple extraction, `parsers.re()` for complex patterns. Register custom types for domain concepts (Money, Email, etc.).

Source: https://pytest-bdd.readthedocs.io/en/latest/ (Accessed 2025-10-09)

---

## Integration with Architecture: Reading Context to Inform Tests

### Architectural Context Principles

**Rule 1: Test Through Public Interfaces Only**

Acceptance tests should interact with the system exactly as real users/clients do:
- Web applications: HTTP API endpoints
- Libraries: Public module/package APIs
- Services: Message queues, RPC interfaces

**Never test**:
- Private methods
- Internal classes
- Database schemas directly
- Implementation details

**Why**: Public interfaces are contracts. Implementation is subject to change. Testing through public interfaces enables refactoring without breaking tests.

### Pattern: Service Integration in Tests

```python
# Configuration for test environment
# tests/acceptance/conftest.py

import pytest
from myapp import create_app
from myapp.infrastructure import DatabaseConnection, MessageQueue

@pytest.fixture(scope="session")
def app_config():
    """Production-like configuration for acceptance tests."""
    return {
        "database": "postgresql://localhost/test_db",
        "message_queue": "amqp://localhost",
        "cache": "redis://localhost:6379/1",
        # Use real implementations, in-memory where possible
        "environment": "test"
    }

@pytest.fixture(scope="session")
def app(app_config):
    """Application instance with production-like setup."""
    app = create_app(app_config)
    # Initialize database schema
    with app.app_context():
        app.db.create_all()
    yield app
    # Cleanup
    with app.app_context():
        app.db.drop_all()

@pytest.fixture
def client(app):
    """HTTP client for testing REST API."""
    return app.test_client()

@pytest.fixture(autouse=True)
def clean_database(app):
    """Ensure clean state for each test."""
    yield
    # Cleanup after test
    with app.app_context():
        for table in reversed(app.db.metadata.sorted_tables):
            app.db.session.execute(table.delete())
        app.db.session.commit()
```

**Pattern**: Use production-like services (real database, real message queue) with test data. Avoid mocks at acceptance test level - mocks couple tests to implementation.

Source: https://pytest-bdd.readthedocs.io/en/latest/ (Accessed 2025-10-09)

### Layered Architecture and Test Scope

```
┌─────────────────────────────────────────────────┐
│ Acceptance Tests (BDD/Outside-In)              │
│ Test through: Public API / HTTP endpoints      │
│ Verify: End-to-end business behavior           │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Application Layer                               │
│ - Use Cases / Application Services              │
│ - Orchestrates business logic                   │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Domain Layer (Unit Tests - TDD)                │
│ - Entities, Value Objects, Domain Services      │
│ - Pure business logic                           │
└─────────────────────────────────────────────────┘
                     ↓
┌─────────────────────────────────────────────────┐
│ Infrastructure Layer                            │
│ - Repositories, External Services               │
│ - Database, Message Queue, HTTP clients         │
└─────────────────────────────────────────────────┘
```

**Acceptance Test Strategy**:
1. Exercise system through Application Layer entry points (API endpoints, commands)
2. Verify outcomes through observable outputs (API responses, database state, messages sent)
3. Never reach into Domain or Infrastructure layers directly
4. Use real implementations where possible, test doubles only for external dependencies

---

## Business Validation Patterns

### Pattern 1: Golden Path + Key Alternatives

For each business capability, test:
1. **Happy path**: Most common, successful flow
2. **Alternative paths**: Valid but less common flows
3. **Error paths**: Invalid inputs, authorization failures, constraint violations

```gherkin
Feature: Fund Transfer Between Accounts

  Scenario: Successful transfer between own accounts (Happy Path)
    Given I have a checking account with balance $500.00
    And I have a savings account with balance $100.00
    When I transfer $50.00 from checking to savings
    Then my checking balance is $450.00
    And my savings balance is $150.00
    And I receive a transfer confirmation

  Scenario: Transfer with insufficient funds (Error Path)
    Given I have a checking account with balance $10.00
    And I have a savings account
    When I attempt to transfer $50.00 from checking to savings
    Then the transfer is rejected with reason "insufficient funds"
    And my checking balance remains $10.00

  Scenario: Transfer to external account requires verification (Alternative Path)
    Given I have a checking account with balance $500.00
    When I initiate a transfer of $100.00 to external account "12345678"
    Then I am prompted for two-factor authentication
```

**Key Insight**: Don't test every possible combination. Select representative examples that reveal different business rules.

Source: https://gojko.net/2020/03/17/sbe-10-years.html (Accessed 2025-10-09)

### Pattern 2: Scenario Outlines for Boundary Testing

```gherkin
Scenario Outline: Account minimum balance validation
  Given I have an account with balance $<initial_balance>
  When I attempt to withdraw $<withdrawal_amount>
  Then the withdrawal is <result>

  Examples: Valid withdrawals
    | initial_balance | withdrawal_amount | result   |
    | 100.00         | 50.00            | accepted |
    | 25.00          | 25.00            | accepted |
    | 100.00         | 99.00            | accepted |

  Examples: Invalid withdrawals
    | initial_balance | withdrawal_amount | result                      |
    | 100.00         | 101.00           | rejected (insufficient funds)|
    | 25.00          | 30.00            | rejected (insufficient funds)|
    | 0.00           | 1.00             | rejected (insufficient funds)|
```

**When to Use Scenario Outlines**:
- Testing boundary conditions (min/max values)
- Validating calculation logic across multiple inputs
- Exploring edge cases discovered during example mapping

**When NOT to Use**:
- Scenario becomes difficult to read due to many parameters
- Examples don't share the same structure
- You're just trying to achieve code coverage (examples should reveal understanding)

Source: https://pytest-bdd.readthedocs.io/en/latest/ (Accessed 2025-10-09)

---

## Property-Based Testing Integration

### When BDD Examples Aren't Enough

**Example-Based BDD**: Illustrates specific behaviors through concrete scenarios
**Property-Based Testing**: Verifies rules hold across wide range of generated inputs

**Use Property-Based Tests For**:
1. Discovering edge cases not obvious from example mapping
2. Testing invariants that should always hold
3. Exploring input space more thoroughly than manual examples allow

### Pattern: Combining BDD and Property-Based Testing

```python
# Feature file remains example-based for understanding
# features/transfer.feature
"""
Scenario: Transfer preserves total balance
  Given I have account A with balance $500.00
  And I have account B with balance $300.00
  When I transfer $100.00 from account A to account B
  Then account A balance is $400.00
  And account B balance is $400.00
  And total balance across accounts is $800.00
"""

# Step definition uses property-based testing for thorough verification
# tests/acceptance/steps/test_transfer.py

from pytest_bdd import scenarios, given, when, then
from hypothesis import given as hypothesis_given, strategies as st
import pytest

scenarios('../features/transfer.feature')

@pytest.fixture
def account_pair():
    """Fixture provides two accounts."""
    return {
        "A": Account(balance=Decimal("500.00")),
        "B": Account(balance=Decimal("300.00"))
    }

# Example-based step for scenario
@when(parsers.parse('I transfer ${amount:Number} from account A to account B'))
def transfer_funds(account_pair, amount):
    transfer_service = TransferService()
    transfer_service.transfer(
        from_account=account_pair["A"],
        to_account=account_pair["B"],
        amount=Decimal(str(amount))
    )

# Property-based test verifies invariant
@hypothesis_given(
    initial_balance_a=st.decimals(min_value=0, max_value=10000, places=2),
    initial_balance_b=st.decimals(min_value=0, max_value=10000, places=2),
    transfer_amount=st.decimals(min_value=0, max_value=10000, places=2)
)
def test_transfer_preserves_total_balance_property(
    initial_balance_a,
    initial_balance_b,
    transfer_amount
):
    """Property: Transfer never changes total balance across accounts."""
    account_a = Account(balance=initial_balance_a)
    account_b = Account(balance=initial_balance_b)

    total_before = account_a.balance + account_b.balance

    if account_a.balance >= transfer_amount:
        # Only test valid transfers
        transfer_service = TransferService()
        transfer_service.transfer(account_a, account_b, transfer_amount)

        total_after = account_a.balance + account_b.balance
        assert total_after == total_before, \
            "Transfer violated invariant: total balance changed"
```

Source: https://gasparnagy.com/2016/11/property-based-bdd-examples-with-specflow-and-fscheck/ (Accessed 2025-10-09)

**Key Insight**: Use BDD scenarios to understand and communicate requirements. Use property-based tests to verify rules hold universally. Both are complementary, not competing approaches.

---

## Living Documentation: Scenarios as Executable Specs

### The Dual Nature of BDD Scenarios

BDD scenarios serve two purposes simultaneously:
1. **Executable Tests**: Automated verification of system behavior
2. **Living Documentation**: Human-readable specification that stays current

**Living Documentation Requirements**:
- Organized hierarchically: Capabilities → Features → Scenarios
- Uses ubiquitous language from domain model
- Structured by business value, not technical architecture
- Generated automatically from test results
- Includes both passing and failing scenarios

### Hierarchical Organization Pattern

```
└── Account Management (Capability)
    ├── Fund Transfers (Feature)
    │   ├── Transfer between own accounts
    │   ├── Transfer to external account
    │   └── Scheduled recurring transfers
    ├── Balance Inquiries (Feature)
    │   ├── View current balance
    │   └── View transaction history
    └── Account Maintenance (Feature)
        ├── Update contact information
        └── Set account preferences
```

**Traceability Structure**:
```
Business Goal → Capability → Feature → Scenario → Test
```

Each scenario should trace back to business capability, enabling stakeholders to see:
- Which capabilities are implemented
- Which features are tested
- Test results for each scenario
- Overall requirement coverage

Source: https://serenity-bdd.github.io/docs/reporting/living_documentation (Accessed 2025-10-09)

### Making Scenarios Documentation-Grade

**Bad Scenario**: Technical jargon, unclear business value
```gherkin
Scenario: POST /api/accounts returns 201
  When I POST to "/api/accounts" with payload {"balance": 100}
  Then response status is 201
  And response contains "id" field
```

**Good Scenario**: Business language, clear value
```gherkin
Scenario: New customer opens checking account with initial deposit
  Given I am a new customer
  When I open a checking account with initial deposit of $100.00
  Then my checking account is active
  And my balance is $100.00
```

**Transformation Guidelines**:
1. Replace HTTP verbs with business actions
2. Replace JSON with domain concepts
3. Replace status codes with business outcomes
4. Add context about WHO and WHY

---

## Common Anti-Patterns and Solutions

### Anti-Pattern 1: Testing Through UI
**Problem**: UI changes break tests frequently. Tests become slow and brittle.

**Solution**: Test through service/API layer. Reserve UI testing for critical user journeys only.

```gherkin
# AVOID - Brittle, slow, coupled to UI
Scenario: Update profile
  Given I am on the profile page
  When I click "Edit Profile"
  And I enter "John Smith" in the "Full Name" field
  And I click "Save"
  Then I see "Profile updated successfully"

# PREFER - Stable, fast, behavior-focused
Scenario: Customer updates profile information
  Given I am authenticated
  When I update my profile name to "John Smith"
  Then my profile reflects the name "John Smith"
```

Source: https://cucumber.io/docs/guides/anti-patterns/ (Accessed 2025-10-09)

### Anti-Pattern 2: Feature-Coupled Step Definitions
**Problem**: Steps can't be reused across features. Leads to code duplication.

**Solution**: Organize steps by domain concept, not by feature file.

```
# BAD STRUCTURE
steps/
  test_login_steps.py
  test_transfer_steps.py
  test_account_steps.py

# GOOD STRUCTURE
steps/
  authentication_steps.py  # All auth-related steps
  account_steps.py         # All account-related steps
  transaction_steps.py     # All transaction-related steps
```

**Example of Reusable Steps**:
```python
# authentication_steps.py - reused across ALL features
@given("I am authenticated")
def authenticated_user(auth_service):
    # Implementation used by login, transfer, account features
    pass

@given("I am not authenticated")
def unauthenticated_user():
    # Also widely reused
    pass
```

Source: https://cucumber.io/docs/guides/anti-patterns/ (Accessed 2025-10-09)

### Anti-Pattern 3: Conjunction Steps
**Problem**: Using "And" to cram multiple actions/assertions into one step.

```gherkin
# WRONG - Obscures what's being tested
Given I have shades and a brand new Mustang
```

**Solution**: Break into atomic steps
```gherkin
# CORRECT - Clear, focused, reusable
Given I have shades
And I have a brand new Mustang
```

Source: https://cucumber.io/docs/guides/anti-patterns/ (Accessed 2025-10-09)

### Anti-Pattern 4: Incidental Details
**Problem**: Including information irrelevant to behavior being tested.

```gherkin
# WRONG - Why do we need to know the password format?
Scenario: Check account balance
  Given I have an account with password "SecureP@ss123!"
  When I check my balance
  Then I see $100.00
```

**Solution**: Only include details that affect outcome
```gherkin
# CORRECT - Password format irrelevant to balance check
Scenario: Authenticated user views account balance
  Given I am authenticated
  And my account balance is $100.00
  When I check my balance
  Then I see $100.00
```

Source: https://cucumber.io/blog/bdd/cucumber-antipatterns-part-one/ (Accessed 2025-10-09)

---

## Practical Workflow: From Architecture to Tests

### Step-by-Step Process

**1. Read Architectural Context**
- Review system architecture documentation
- Identify public interfaces (APIs, commands, events)
- Understand bounded contexts and domain model
- Note integration points with external services

**2. Identify Testable Behaviors**
- Focus on use cases/application services
- Each use case → one or more scenarios
- Ignore implementation details (repositories, database schema)

**3. Write Scenarios Using Example Mapping Output**
- Convert rules (blue cards) → Scenario titles
- Convert examples (green cards) → Scenario steps
- Convert questions (red cards) → Test TODOs or scenario outlines

**4. Implement Step Definitions**
- Use pytest fixtures for shared context
- Leverage dependency injection for services
- Access system through public interfaces only
- Use real implementations (database, services) with test data

**5. Run Tests Outside-In**
- Acceptance test fails initially (red)
- Drop to unit tests (inner loop TDD)
- Implement domain logic to satisfy acceptance test
- Acceptance test passes (green)
- Refactor with confidence

**6. Generate Living Documentation**
- Organize scenarios hierarchically (capabilities → features)
- Generate reports from test results
- Share with stakeholders for validation

---

## Tool-Specific Guidance: pytest-bdd

### Project Structure
```
project/
├── features/
│   ├── authentication.feature
│   ├── transfers.feature
│   └── accounts.feature
├── tests/
│   ├── acceptance/
│   │   ├── conftest.py          # Shared fixtures
│   │   ├── steps/
│   │   │   ├── authentication_steps.py
│   │   │   ├── account_steps.py
│   │   │   └── transaction_steps.py
│   │   └── test_*.py            # Test runners (one per feature)
│   └── unit/                    # Inner loop tests
└── src/
    └── myapp/
```

### Fixture Scopes for Performance

```python
# conftest.py

@pytest.fixture(scope="session")
def database_engine():
    """Create database engine once per test session."""
    engine = create_engine("postgresql://localhost/test")
    yield engine
    engine.dispose()

@pytest.fixture(scope="module")
def database_schema(database_engine):
    """Create schema once per test module."""
    Base.metadata.create_all(database_engine)
    yield
    Base.metadata.drop_all(database_engine)

@pytest.fixture(scope="function", autouse=True)
def clean_database(database_engine):
    """Clean data after each test."""
    yield
    # Truncate all tables
    with database_engine.begin() as conn:
        for table in reversed(Base.metadata.sorted_tables):
            conn.execute(table.delete())
```

**Performance Pattern**:
- Session scope: Expensive setup (database engine, application instance)
- Module scope: Schema creation
- Function scope: Data cleanup (use autouse=True)

### Running Scenarios Selectively

```bash
# Run all acceptance tests
pytest tests/acceptance/

# Run specific feature
pytest tests/acceptance/test_transfers.py

# Run scenarios by tag
pytest -m "critical_path"

# Run with verbose output
pytest -v tests/acceptance/
```

**Tag Pattern in Feature Files**:
```gherkin
@critical_path @smoke
Scenario: User logs in with valid credentials
  Given I have a registered account
  When I log in with valid credentials
  Then I am authenticated
```

Source: https://pytest-bdd.readthedocs.io/en/latest/ (Accessed 2025-10-09)

---

## Quality Checklist for Acceptance Tests

### Before Committing Scenarios

- [ ] **Business Language**: Scenarios use domain terminology, not technical jargon
- [ ] **Single Behavior**: Each scenario tests exactly one business behavior
- [ ] **Declarative Steps**: Steps describe "what", not "how" (no UI actions)
- [ ] **Concrete Examples**: Uses specific values, not abstractions
- [ ] **Focused Length**: 3-5 steps maximum; no rambling
- [ ] **Public Interface**: Tests through APIs/commands, not internal classes
- [ ] **No Incidental Details**: Only includes information relevant to behavior
- [ ] **Living Documentation**: Readable by non-technical stakeholders
- [ ] **Hierarchical Organization**: Traces to capabilities and features
- [ ] **Reusable Steps**: Step definitions organized by domain, not feature

### Before Committing Step Implementations

- [ ] **Fixture Injection**: Uses pytest fixtures for dependencies
- [ ] **Real Services**: Uses production-like implementations (not mocks)
- [ ] **Isolated Tests**: Each test runs independently, clean state
- [ ] **Fast Execution**: Acceptance tests complete in seconds, not minutes
- [ ] **No Test Coupling**: Tests don't depend on execution order
- [ ] **Error Messages**: Failures provide clear, actionable information
- [ ] **Domain Language**: Step implementations use ubiquitous language
- [ ] **Property Tests**: Edge cases covered by property-based tests where appropriate

---

## Key Takeaways

1. **Test behavior through public interfaces** - enables refactoring without breaking tests
2. **Outside-in with double-loop TDD** - acceptance tests guide implementation
3. **Scenarios are specifications AND tests** - living documentation that stays current
4. **Concrete examples over abstractions** - reveal assumptions and edge cases
5. **Declarative, not imperative** - describe business outcomes, not UI interactions
6. **One scenario, one behavior** - focused, maintainable tests
7. **Leverage architecture** - test through application services, not infrastructure
8. **Combine example-based and property-based** - examples for understanding, properties for thoroughness
9. **Organize by domain** - reusable steps, hierarchical features
10. **Production-like test environment** - real services, isolated data

---

## References

- Cucumber BDD Documentation: https://cucumber.io/docs/bdd/ (Accessed 2025-10-09)
- pytest-bdd Documentation: https://pytest-bdd.readthedocs.io/en/latest/ (Accessed 2025-10-09)
- Cucumber Anti-Patterns: https://cucumber.io/docs/guides/anti-patterns/ (Accessed 2025-10-09)
- Liz Keogh - Conversational Patterns in BDD: https://lizkeogh.com/2011/09/22/conversational-patterns-in-bdd/ (Accessed 2025-10-09)
- Gojko Adzic - Specification by Example 10 Years Later: https://gojko.net/2020/03/17/sbe-10-years.html (Accessed 2025-10-09)
- Serenity BDD Living Documentation: https://serenity-bdd.github.io/docs/reporting/living_documentation (Accessed 2025-10-09)
- Double-Loop TDD: https://sammancoaching.org/learning_hours/bdd/double_loop_tdd.html (Accessed 2025-10-09)
- Property-Based BDD with SpecFlow and FsCheck: https://gasparnagy.com/2016/11/property-based-bdd-examples-with-specflow-and-fscheck/ (Accessed 2025-10-09)
- Property-Based Testing Introduction: https://fsharpforfunandprofit.com/pbt/ (Accessed 2025-10-09)
