# Test Refactoring Guide - Six-Level Hierarchy for Test Code

## Overview

### Test Code as First-Class Code

Test code is not second-class code that can be left messy while production code is kept clean. Tests are the executable specification of your system's behavior, the safety net that enables confident refactoring, and the living documentation that explains what the system does. **Test code quality directly impacts:**

- **Maintainability**: Poorly written tests become a maintenance burden, slowing down feature development
- **Reliability**: Obscure or complex tests may pass when they should fail, or fail for unclear reasons
- **Documentation value**: Clear tests serve as examples showing how to use the system correctly
- **Refactoring confidence**: Well-organized tests make it safe to refactor production code

### Why Test Refactoring Matters

The same forces that degrade production code quality also affect test code:

- **Test duplication**: Copy-pasted test setup code across multiple tests
- **Obscure intent**: Test names and assertions that don't reveal business scenarios
- **Complexity creep**: Tests accumulating conditional logic and excessive setup over time
- **Poor organization**: Large test classes mixing unrelated concerns

**Without systematic test refactoring**, test suites become:
- Slow to run (excessive duplication, over-setup)
- Hard to understand (obscure names, magic numbers)
- Brittle (coupling to implementation details)
- Incomplete (gaps in coverage hidden by complexity)

### Integration with TDD Refactor Phase

Test refactoring is integrated into the **7-phase TDD cycle** at Phase 5 (REFACTOR_CONTINUOUS):

```
PREPARE → RED(Acceptance) → RED(Unit) → GREEN → REVIEW → REFACTOR_CONTINUOUS → COMMIT
```

**During REFACTOR_CONTINUOUS (L1+L2+L3):**
1. Apply L1 (naming) to BOTH production code AND test code
2. Apply L2 (complexity) to BOTH production code AND test code
3. Apply L3 (organization) to BOTH production code AND test code
4. Run ALL tests after each refactoring level
5. Revert if any test fails, retry with smaller steps

**Key principle**: Test refactoring is NOT optional—it's part of the refactor phase discipline.

### Six-Level Hierarchy Applied to Tests

The same 6-level refactoring hierarchy that applies to production code applies to test code:

| Level | Focus | Test Code Application |
|-------|-------|----------------------|
| **L1** | Foundation (Readability) | Test naming, hard-coded test data, assertion messages |
| **L2** | Complexity Reduction | Eager tests, test duplication, conditional test logic |
| **L3** | Responsibility Organization | Test class bloat, mystery guest, fixture organization |
| **L4** | Abstraction Refinement | Test data builders, parameter objects in tests |
| **L5** | Design Pattern Application | Test patterns (Object Mother, Builder, etc.) |
| **L6** | SOLID++ Principles | Test architecture patterns |

**This guide focuses on L1-L3** (continuous refactoring levels executed together in every TDD cycle).

---

## Test Code Smell Taxonomy

### L1 Test Smells (Naming/Readability)

#### 1. Obscure Test

**Problem**: Test method name doesn't reveal what business scenario is being tested or what the expected outcome is.

**Detection**:
- Generic names like `Test1()`, `TestMethod()`, `ProcessOrderTest()`
- Names that require reading the test body to understand intent
- Names that don't follow Given_When_Then or should_do_something pattern
- Names using implementation terms instead of business language

**Solution**:
- Rename to reveal business scenario
- Use naming patterns:
  - **C#/xUnit**: `MethodUnderTest_StateUnderTest_ExpectedBehavior`
  - **C#/BDD**: `Given_Precondition_When_Action_Then_Outcome`
  - **TypeScript/Jest**: `should_do_expected_thing_when_condition`
  - **Python/pytest**: `test_method_under_test_state_under_test_expected_behavior`

**Example (C#)**:
```csharp
// ❌ Before: Obscure Test
[Fact]
public void Test1()
{
    var customer = new Customer { Type = "premium", YearsActive = 5 };
    var order = new Order { Amount = 1000 };

    var result = _processor.ProcessOrder(customer, order);

    Assert.Equal(850, result.TotalWithDiscount);
}

// ✅ After: Clear Intent
[Fact]
public void ProcessOrder_PremiumCustomerWith5YearsLoyalty_Applies15PercentDiscount()
{
    var customer = new Customer { Type = "premium", YearsActive = 5 };
    var order = new Order { Amount = 1000 };

    var result = _processor.ProcessOrder(customer, order);

    Assert.Equal(850, result.TotalWithDiscount);
}
```

**Impact**: Reading test failure output immediately reveals which business scenario failed without reading test code.

---

#### 2. Hard-Coded Test Data

**Problem**: Magic numbers and strings obscure business rules being tested. Test values lack business meaning.

**Detection**:
- Literal numbers like `1000`, `0.15`, `850` without explanation
- String values like `"premium"`, `"USD"` embedded directly in assertions
- Test values that don't reveal the business rule they represent
- Comments asking "What discount?" or "Why this value?"

**Solution**:
- Extract to named constants that reveal business meaning
- Use descriptive constant names that document the rule
- Make calculations explicit to show how expected values are derived

**Example (C#)**:
```csharp
// ❌ Before: Hard-Coded Test Data
[Fact]
public void ProcessOrder_PremiumCustomer_AppliesDiscount()
{
    var customer = new Customer { Type = "premium", YearsActive = 5 };
    var order = new Order { Amount = 1000 };

    var result = _processor.ProcessOrder(customer, order);

    Assert.Equal(850, result.TotalWithDiscount); // What discount rate?
}

// ✅ After: Named Constants
[Fact]
public void ProcessOrder_PremiumCustomer_AppliesCorrectDiscount()
{
    const string PREMIUM_CUSTOMER_TYPE = "premium";
    const int LOYALTY_TIER_3_YEARS = 5;
    const decimal ORDER_AMOUNT = 1000m;
    const decimal TIER_3_DISCOUNT_RATE = 0.15m;
    const decimal EXPECTED_TOTAL = ORDER_AMOUNT * (1 - TIER_3_DISCOUNT_RATE);

    var customer = new Customer {
        Type = PREMIUM_CUSTOMER_TYPE,
        YearsActive = LOYALTY_TIER_3_YEARS
    };
    var order = new Order { Amount = ORDER_AMOUNT };

    var result = _processor.ProcessOrder(customer, order);

    Assert.Equal(EXPECTED_TOTAL, result.TotalWithDiscount);
}
```

**Impact**: Test constants document business rules. The 15% discount for 5-year premium customers is now self-documenting.

---

#### 3. Assertion Roulette

**Problem**: Multiple assertions without descriptive messages make test failures unclear. When one of 10 assertions fails, which business expectation was violated?

**Detection**:
- Multiple `Assert.*` calls without message parameter
- Test output shows "Expected: 5, Actual: 3" without context
- Developer must read test code to understand what failed
- Test has many assertions but no clear documentation of what each verifies

**Solution**:
- Add descriptive message to each assertion explaining expected business outcome
- Message should describe WHAT business rule failed, not HOW it was calculated
- Use assertion libraries that support fluent messages (FluentAssertions, Shouldly)

**Example (C#)**:
```csharp
// ❌ Before: Assertion Roulette
[Fact]
public void ProcessOrder_ComplexScenario_CalculatesCorrectly()
{
    var result = _processor.ProcessOrder(customer, order);

    Assert.Equal(850, result.Subtotal);
    Assert.Equal(42.5, result.Tax);
    Assert.Equal(892.5, result.Total);
    Assert.Equal("premium", result.CustomerTier);
    Assert.True(result.IsEligibleForFreeShipping);
}

// ✅ After: Descriptive Assertions
[Fact]
public void ProcessOrder_PremiumCustomerHighValueOrder_AppliesAllBenefits()
{
    var result = _processor.ProcessOrder(customer, order);

    Assert.Equal(850, result.Subtotal,
        "Premium customers receive 15% discount on orders over $500");
    Assert.Equal(42.5, result.Tax,
        "Tax is 5% of discounted subtotal in this jurisdiction");
    Assert.Equal(892.5, result.Total,
        "Total should be discounted subtotal plus tax");
    Assert.Equal("premium", result.CustomerTier,
        "Customer tier should reflect premium status");
    Assert.True(result.IsEligibleForFreeShipping,
        "Premium customers with orders over $500 qualify for free shipping");
}
```

**Impact**: Test failure messages immediately explain which business rule was violated and why it matters.

---

### L2 Test Smells (Complexity)

#### 4. Eager Test

**Problem**: Single test method verifies multiple unrelated behaviors, making it hard to identify what failed and violating single responsibility principle.

**Detection**:
- Multiple arrange/act/assert cycles in one test method
- Test name uses "And" to describe multiple concerns
- Assertions testing completely different aspects (discount AND shipping AND tax)
- Test failure doesn't clearly identify which behavior is broken

**Solution**:
- Split into focused tests, one per business scenario
- Each test should verify exactly one business behavior
- Test names should be specific to single concern
- Prefer many small focused tests over few large tests

**Example (TypeScript/Jest)**:
```typescript
// ❌ Before: Eager Test
it('ProcessOrderTest', () => {
    const customer = createPremiumCustomer();
    const order = createOrder(1000);

    const result = processor.processOrder(customer, order);

    // Testing discount
    expect(result.discountAmount).toBe(150);

    // Testing shipping
    expect(result.shippingCost).toBe(0);
    expect(result.shippingMethod).toBe('express');

    // Testing tax calculation
    expect(result.taxAmount).toBe(42.5);
    expect(result.taxRate).toBe(0.05);
});

// ✅ After: Focused Tests
describe('Order Processing for Premium Customers', () => {
    it('should apply 15% discount for premium customers', () => {
        const customer = createPremiumCustomer();
        const order = createOrder(1000);

        const result = processor.processOrder(customer, order);

        expect(result.discountAmount).toBe(150);
    });

    it('should provide free express shipping for premium customers', () => {
        const customer = createPremiumCustomer();
        const order = createOrder(1000);

        const result = processor.processOrder(customer, order);

        expect(result.shippingCost).toBe(0);
        expect(result.shippingMethod).toBe('express');
    });

    it('should calculate tax on discounted amount', () => {
        const customer = createPremiumCustomer();
        const order = createOrder(1000);

        const result = processor.processOrder(customer, order);

        expect(result.taxAmount).toBe(42.5);
        expect(result.taxRate).toBe(0.05);
    });
});
```

**Impact**: Test failures now clearly identify which specific business behavior is broken. Tests can be run independently.

---

#### 5. Test Code Duplication

**Problem**: Repeated test setup logic across multiple tests creates maintenance burden and obscures test intent.

**Detection**:
- Same object creation code appears in 3+ test methods
- Mock setup code copy-pasted across tests
- Data builder patterns duplicated instead of extracted
- Changes to setup require modifying multiple tests

**Solution**:
- Extract helper methods with business-meaningful names
- Create test-specific factory methods: `CreatePremiumCustomer()`, `CreateHighValueOrder()`
- Use test fixture setup for truly shared initialization
- Keep duplication if it improves test clarity (occasional duplication OK)

**Example (TypeScript/Jest)**:
```typescript
// ❌ Before: Test Code Duplication
it('should apply discount for premium customer', () => {
    const customer = {
        id: '123',
        type: 'premium',
        yearsActive: 5,
        email: 'test@example.com',
        preferences: { notifications: true }
    };
    const order = {
        id: '456',
        items: [{ sku: 'ABC', quantity: 1, price: 1000 }],
        currency: 'USD'
    };

    const result = processor.processOrder(customer, order);
    expect(result.discountAmount).toBe(150);
});

it('should provide free shipping for premium customer', () => {
    const customer = {
        id: '123',
        type: 'premium',
        yearsActive: 5,
        email: 'test@example.com',
        preferences: { notifications: true }
    };
    const order = {
        id: '456',
        items: [{ sku: 'ABC', quantity: 1, price: 1000 }],
        currency: 'USD'
    };

    const result = processor.processOrder(customer, order);
    expect(result.shippingCost).toBe(0);
});

// ✅ After: Extract Helpers
function createPremiumCustomer(): Customer {
    return {
        id: '123',
        type: 'premium',
        yearsActive: 5,
        email: 'test@example.com',
        preferences: { notifications: true }
    };
}

function createHighValueOrder(): Order {
    return {
        id: '456',
        items: [{ sku: 'ABC', quantity: 1, price: 1000 }],
        currency: 'USD'
    };
}

it('should apply discount for premium customer', () => {
    const customer = createPremiumCustomer();
    const order = createHighValueOrder();

    const result = processor.processOrder(customer, order);
    expect(result.discountAmount).toBe(150);
});

it('should provide free shipping for premium customer', () => {
    const customer = createPremiumCustomer();
    const order = createHighValueOrder();

    const result = processor.processOrder(customer, order);
    expect(result.shippingCost).toBe(0);
});
```

**Impact**: Reduced duplication from 12 lines per test to 3 lines. Clearer test intent. Single point of change for test data.

---

#### 6. Conditional Test Logic

**Problem**: if/switch statements or loops in test code make tests non-deterministic and hard to understand.

**Detection**:
- `if`, `switch`, `for`, `while` statements in test methods
- Test behavior varies based on runtime conditions
- Tests that aren't guaranteed to execute same assertions every time
- Complex test logic that requires its own unit tests

**Solution**:
- Replace with parameterized tests to test multiple cases
- Use test framework features: `[Theory]` (C#), `pytest.mark.parametrize` (Python), `it.each` (Jest)
- Extract complex logic to production code or test helpers
- Each test run should be deterministic

**Example (Python/pytest)**:
```python
# ❌ Before: Conditional Test Logic
def test_discount_calculation():
    test_cases = [
        ('regular', 0, 0.0),
        ('premium', 3, 0.10),
        ('premium', 5, 0.15),
        ('vip', 1, 0.20),
    ]

    for customer_type, years, expected_discount in test_cases:
        customer = Customer(type=customer_type, years_active=years)
        order = Order(amount=1000)

        result = processor.process_order(customer, order)

        if expected_discount > 0:
            assert result.discount_amount == 1000 * expected_discount
        else:
            assert result.discount_amount == 0

# ✅ After: Parameterized Tests
@pytest.mark.parametrize("customer_type,years_active,expected_discount_rate", [
    ("regular", 0, 0.0),
    ("premium", 3, 0.10),
    ("premium", 5, 0.15),
    ("vip", 1, 0.20),
])
def test_process_order_applies_correct_discount_by_customer_tier(
    customer_type, years_active, expected_discount_rate
):
    customer = Customer(type=customer_type, years_active=years_active)
    order = Order(amount=1000)

    result = processor.process_order(customer, order)

    expected_discount_amount = 1000 * expected_discount_rate
    assert result.discount_amount == expected_discount_amount
```

**Impact**: Four separate test cases with clear names. Each runs independently. No conditional logic in test.

---

### L3 Test Smells (Organization)

#### 7. Mystery Guest

**Problem**: Test depends on external files or hidden dependencies not visible in test code, making tests fragile and hard to understand.

**Detection**:
- `File.ReadAllText()`, `fs.readFileSync()` in tests reading external files
- Database queries executing before test setup
- Configuration files loaded from disk
- HTTP calls to external services during test
- Dependencies on file system state or environment variables

**Solution**:
- Inline test data directly into test constants
- Make dependencies explicit in test setup
- Use test doubles (mocks, stubs) for external dependencies
- Avoid file system and network dependencies in unit tests

**Example (C#)**:
```csharp
// ❌ Before: Mystery Guest
[Fact]
public void ImportOrder_ValidOrderFile_CreatesOrder()
{
    // Where does this file come from? What's in it?
    var orderData = File.ReadAllText("test-data/valid-order.json");

    var result = _importer.ImportOrder(orderData);

    Assert.NotNull(result);
    Assert.Equal("ORD-123", result.OrderId);
}

// ✅ After: Explicit Setup
[Fact]
public void ImportOrder_ValidOrderJson_CreatesOrderWithCorrectId()
{
    const string VALID_ORDER_JSON = @"{
        ""orderId"": ""ORD-123"",
        ""customerId"": ""CUST-456"",
        ""items"": [
            { ""sku"": ""ABC"", ""quantity"": 1, ""price"": 100 }
        ]
    }";

    var result = _importer.ImportOrder(VALID_ORDER_JSON);

    Assert.NotNull(result);
    Assert.Equal("ORD-123", result.OrderId);
}
```

**Impact**: Test is self-contained. Reader sees exactly what data is being tested without checking external files.

---

#### 8. Test Class Bloat

**Problem**: Single test class contains tests for multiple unrelated concerns, making it hard to locate specific tests and slowing test execution.

**Detection**:
- Test class with 15+ test methods
- Test class name is generic (e.g., `UserServiceTests`)
- Tests cover CRUD + email + file upload + payments in one class
- Hard to find test for specific feature
- Class becomes merge conflict hotspot

**Solution**:
- Split test class by feature or concern
- Use focused test class names describing what they test
- Group related tests together
- Enables parallel test execution

**Example (Python/pytest)**:
```python
# ❌ Before: Test Class Bloat
class TestUserService:
    # CRUD operations (5 tests)
    def test_create_user(self): ...
    def test_read_user(self): ...
    def test_update_user(self): ...
    def test_delete_user(self): ...
    def test_list_users(self): ...

    # Email notifications (8 tests)
    def test_send_welcome_email(self): ...
    def test_send_password_reset_email(self): ...
    def test_email_validation(self): ...
    # ... 5 more email tests

    # Profile images (6 tests)
    def test_upload_profile_image(self): ...
    def test_resize_profile_image(self): ...
    # ... 4 more image tests

    # Payment processing (7 tests)
    def test_add_payment_method(self): ...
    def test_charge_customer(self): ...
    # ... 5 more payment tests

# ✅ After: Split by Concern
class TestUserRepository:
    """Tests for user CRUD operations"""
    def test_create_user_with_valid_data_saves_to_database(self): ...
    def test_read_user_by_id_returns_correct_user(self): ...
    def test_update_user_modifies_existing_record(self): ...
    def test_delete_user_removes_from_database(self): ...
    def test_list_users_returns_paginated_results(self): ...

class TestUserNotificationService:
    """Tests for user email notifications"""
    def test_send_welcome_email_on_user_registration(self): ...
    def test_send_password_reset_email_with_token(self): ...
    def test_validate_email_address_format(self): ...
    # ... other notification tests

class TestUserProfileImageService:
    """Tests for user profile image management"""
    def test_upload_profile_image_stores_in_blob_storage(self): ...
    def test_resize_profile_image_to_standard_dimensions(self): ...
    # ... other image tests

class TestUserPaymentService:
    """Tests for user payment processing"""
    def test_add_payment_method_validates_card(self): ...
    def test_charge_customer_processes_payment(self): ...
    # ... other payment tests
```

**Impact**: Tests are easier to locate. Classes can be tested in parallel. Clear responsibility per test class.

---

#### 9. General Fixture

**Problem**: Shared test fixture (setup method) creates data used by only some tests, leading to over-setup and test coupling.

**Detection**:
- `SetUp` / `beforeEach` method creates many objects
- Only some tests use all the setup data
- Tests must navigate through irrelevant setup to understand what they need
- Changing fixture breaks unrelated tests

**Solution**:
- Move to per-test setup methods
- Use test-specific fixtures (pytest fixtures, xUnit class fixtures)
- Only set up what each test actually needs
- Prefer explicit over implicit setup

**Example (C#/xUnit)**:
```csharp
// ❌ Before: General Fixture
public class OrderProcessorTests
{
    private Customer _customer;
    private Order _order;
    private PaymentMethod _paymentMethod;
    private ShippingAddress _address;

    public OrderProcessorTests()
    {
        // Over-setup: Not all tests need all this
        _customer = new Customer { Type = "premium", YearsActive = 5 };
        _order = new Order { Amount = 1000 };
        _paymentMethod = new PaymentMethod { Type = "CreditCard" };
        _address = new ShippingAddress { Country = "US", State = "CA" };
    }

    [Fact]
    public void CalculateDiscount_PremiumCustomer_Applies15Percent()
    {
        // Only needs _customer and _order, not payment/address
        var result = _processor.CalculateDiscount(_customer, _order);
        Assert.Equal(150, result);
    }

    [Fact]
    public void CalculateShipping_USAddress_UsesStandardRate()
    {
        // Only needs _address, not customer/order/payment
        var result = _processor.CalculateShipping(_address);
        Assert.Equal(10, result);
    }
}

// ✅ After: Per-Test Setup
public class OrderProcessorTests
{
    private Customer CreatePremiumCustomer() =>
        new Customer { Type = "premium", YearsActive = 5 };

    private Order CreateHighValueOrder() =>
        new Order { Amount = 1000 };

    private ShippingAddress CreateUSAddress() =>
        new ShippingAddress { Country = "US", State = "CA" };

    [Fact]
    public void CalculateDiscount_PremiumCustomer_Applies15Percent()
    {
        var customer = CreatePremiumCustomer();
        var order = CreateHighValueOrder();

        var result = _processor.CalculateDiscount(customer, order);

        Assert.Equal(150, result);
    }

    [Fact]
    public void CalculateShipping_USAddress_UsesStandardRate()
    {
        var address = CreateUSAddress();

        var result = _processor.CalculateShipping(address);

        Assert.Equal(10, result);
    }
}
```

**Impact**: Each test sets up only what it needs. Test intent is clearer. No coupling through shared fixture.

---

## Integration with TDD Cycle

### When to Apply Test Refactoring

**Every TDD Cycle (Phase 6 - REFACTOR_CONTINUOUS):**
- Apply L1 (naming) to test code immediately after green
- Apply L2 (complexity reduction) to test code in same refactor phase
- Apply L3 (organization) if test class becoming large

**Workflow**:
```
1. PREPARE   → Enable one acceptance test
2. RED(A)    → Acceptance test fails (expected)
3. RED(U)    → Write failing unit test
4. GREEN     → Minimum code to pass
5. REVIEW    → Check test quality, coverage
6. REFACTOR  → Apply L1+L2+L3 to BOTH production AND test code ← HERE
7. L4        → Optional architecture refactoring
8. COMMIT    → Save progress
```

### Test Refactoring Safety Protocol

**Before refactoring tests:**
1. All tests must be GREEN
2. No pending changes to production code
3. Have clear rollback point (git commit)

**During test refactoring:**
1. Refactor ONE test at a time
2. Run ALL tests after each test refactoring
3. If tests fail → REVERT immediately
4. Only commit when all tests GREEN

**After test refactoring:**
1. All tests still GREEN
2. Test coverage unchanged or improved
3. Test execution time same or better

### Continuous vs Periodic Refactoring

**L1-L2: Continuous (Every Cycle)**
- Rename obscure tests immediately
- Extract duplicated test setup as soon as noticed
- Add assertion messages when tests become unclear

**L3: Periodic (Sprint Boundaries)**
- Split large test classes when >15 tests
- Reorganize test fixtures quarterly
- Review test organization at retrospectives

---

## Best Practices

### Test Refactoring Safety

**Golden Rule**: Never refactor test code at the same time as production code.

**Safe refactoring sequence**:
1. Refactor production code → tests GREEN
2. Commit production code changes
3. Refactor test code → tests still GREEN
4. Commit test code changes

**Unsafe pattern** (avoid):
- Changing production code AND test structure simultaneously
- No way to know if tests fail due to production bug or test refactoring error

### When to Extract vs Inline

**Extract helper when**:
- Same setup appears in 3+ tests
- Setup is complex (>5 lines)
- Setup has clear business meaning (CreatePremiumCustomer)

**Inline when**:
- Setup is trivial (1-2 lines)
- Extraction would obscure test intent
- Setup is unique to single test

**Example**:
```csharp
// ✅ GOOD: Extract complex setup
var customer = CreatePremiumCustomerWith5YearsLoyalty();

// ✅ ALSO GOOD: Inline trivial setup
var customer = new Customer { Id = "123" };

// ❌ BAD: Extract trivial setup (over-engineering)
var customer = CreateCustomerWithId123(); // Unnecessary helper
```

### Test Data Builders

**Use builder pattern for complex test objects**:

```csharp
// Test Data Builder
public class CustomerBuilder
{
    private string _type = "regular";
    private int _years = 0;

    public CustomerBuilder Premium()
    {
        _type = "premium";
        return this;
    }

    public CustomerBuilder WithYears(int years)
    {
        _years = years;
        return this;
    }

    public Customer Build() =>
        new Customer { Type = _type, YearsActive = _years };
}

// Usage in tests
[Fact]
public void ProcessOrder_PremiumCustomer_AppliesDiscount()
{
    var customer = new CustomerBuilder()
        .Premium()
        .WithYears(5)
        .Build();

    var result = _processor.ProcessOrder(customer, order);

    Assert.Equal(150, result.DiscountAmount);
}
```

**When to use builders**:
- Objects with many optional fields
- Need multiple variations of same object
- Object construction is complex

**When NOT to use builders**:
- Simple objects (1-3 fields)
- Object only used once
- Builder would be more complex than direct construction

### Avoiding Test Fragility

**Fragile tests** break when production code changes in ways that don't affect business behavior.

**Make tests resilient**:

1. **Test behavior, not implementation**:
   ```csharp
   // ❌ FRAGILE: Tests implementation
   Assert.Equal("SELECT * FROM users WHERE id = 1", query.ToSql());

   // ✅ RESILIENT: Tests behavior
   var user = repository.GetUserById(1);
   Assert.Equal("John", user.Name);
   ```

2. **Avoid over-specification**:
   ```csharp
   // ❌ FRAGILE: Over-specified
   Assert.Equal(new DateTime(2025, 1, 1, 10, 30, 15, 123), result.Timestamp);

   // ✅ RESILIENT: Specify what matters
   Assert.Equal(new DateTime(2025, 1, 1), result.Timestamp.Date);
   ```

3. **Use semantic assertions**:
   ```csharp
   // ❌ FRAGILE: String comparison
   Assert.Contains("Error", response.Body);

   // ✅ RESILIENT: Semantic check
   Assert.True(response.IsError);
   Assert.Equal(ErrorCode.InvalidInput, response.ErrorCode);
   ```

---

## Summary

### Key Takeaways

1. **Test code is first-class code** → Apply same quality standards as production code
2. **L1-L3 every cycle** → Test refactoring is part of TDD refactor phase, not optional
3. **One test at a time** → Refactor incrementally, keep tests green
4. **Test behavior, not implementation** → Make tests resilient to refactoring
5. **Clarity over cleverness** → Prefer explicit, readable tests over DRY

### Refactoring Checklist

**Before starting test refactoring**:
- [ ] All tests GREEN
- [ ] Production code committed
- [ ] Clear rollback point

**L1 (Naming) applied**:
- [ ] Test names reveal business scenarios
- [ ] No hard-coded magic numbers in tests
- [ ] Assertion messages explain business rules
- [ ] No commented-out test code

**L2 (Complexity) applied**:
- [ ] Each test verifies one behavior
- [ ] No duplicated test setup (extracted to helpers)
- [ ] No conditional logic in tests (use parameterized tests)
- [ ] Test setup is focused and minimal

**L3 (Organization) applied**:
- [ ] Test classes focused on single concern (≤15 tests per class)
- [ ] No mystery guests (external file dependencies)
- [ ] No general fixtures (per-test setup instead)
- [ ] Tests grouped by feature

**After test refactoring**:
- [ ] All tests still GREEN
- [ ] Test coverage unchanged or improved
- [ ] Commit test refactoring changes

---

**This guide completes the L1-L3 test refactoring methodology. For L4-L6 (advanced test patterns), see test-patterns-catalog.md.**
