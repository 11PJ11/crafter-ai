# Test Refactoring Quick Reference

## Overview

Test code is first-class code requiring same quality standards as production code. Apply L1-L3 refactoring to tests during REFACTOR_CONTINUOUS phase of TDD cycle.

**Key Principle**: Test refactoring is NOT optional - it's part of refactor phase discipline.

---

## Test Code Smell Quick List

### L1 Smells (Naming/Readability)

1. **Obscure Test** - Test name doesn't reveal business scenario
2. **Hard-Coded Test Data** - Magic numbers obscure business rules
3. **Assertion Roulette** - Multiple assertions without messages

### L2 Smells (Complexity)

4. **Eager Test** - Single test verifies multiple unrelated behaviors
5. **Test Code Duplication** - Repeated setup logic across tests
6. **Conditional Test Logic** - if/switch statements in tests

### L3 Smells (Organization)

7. **Mystery Guest** - External file dependencies
8. **Test Class Bloat** - 15+ tests in one class
9. **General Fixture** - Shared fixture for unrelated tests

---

## L1 Refactoring Patterns

### Pattern: Obscure Test → Clear Intent

**Problem**: Generic test names don't reveal what's being tested.

**Solution**: Use business-focused naming patterns.

```csharp
// ❌ Before
[Fact]
public void Test1()
{
    var customer = new Customer { Type = "premium", YearsActive = 5 };
    var order = new Order { Amount = 1000 };
    var result = _processor.ProcessOrder(customer, order);
    Assert.Equal(850, result.TotalWithDiscount);
}

// ✅ After
[Fact]
public void ProcessOrder_PremiumCustomerWith5YearsLoyalty_Applies15PercentDiscount()
{
    var customer = new Customer { Type = "premium", YearsActive = 5 };
    var order = new Order { Amount = 1000 };
    var result = _processor.ProcessOrder(customer, order);
    Assert.Equal(850, result.TotalWithDiscount);
}
```

**Naming Conventions**:
- C#/xUnit: `MethodUnderTest_StateUnderTest_ExpectedBehavior`
- TypeScript/Jest: `should_do_expected_thing_when_condition`
- Python/pytest: `test_method_state_expected_behavior`

---

### Pattern: Hard-Coded Test Data → Named Constants

**Problem**: Magic numbers don't reveal business meaning.

**Solution**: Extract to named constants showing business rules.

```csharp
// ❌ Before
Assert.Equal(850, result.Total); // What discount?

// ✅ After
const decimal ORDER_AMOUNT = 1000m;
const decimal TIER_3_DISCOUNT_RATE = 0.15m;
const decimal EXPECTED_TOTAL = ORDER_AMOUNT * (1 - TIER_3_DISCOUNT_RATE);
Assert.Equal(EXPECTED_TOTAL, result.Total);
```

---

### Pattern: Assertion Roulette → Descriptive Messages

**Problem**: Multiple assertions fail without context.

**Solution**: Add business-focused message to each assertion.

```csharp
// ❌ Before
Assert.Equal(850, result.Subtotal);
Assert.Equal(42.5, result.Tax);
Assert.True(result.IsEligibleForFreeShipping);

// ✅ After
Assert.Equal(850, result.Subtotal,
    "Premium customers receive 15% discount on orders over $500");
Assert.Equal(42.5, result.Tax,
    "Tax is 5% of discounted subtotal");
Assert.True(result.IsEligibleForFreeShipping,
    "Premium customers with orders over $500 qualify for free shipping");
```

---

## L2 Refactoring Patterns

### Pattern: Eager Test → Focused Tests

**Problem**: One test verifies multiple behaviors.

**Solution**: Split into one test per business scenario.

```typescript
// ❌ Before: Eager Test
it('ProcessOrderTest', () => {
    const result = processor.processOrder(customer, order);
    expect(result.discountAmount).toBe(150);  // Testing discount
    expect(result.shippingCost).toBe(0);      // Testing shipping
    expect(result.taxAmount).toBe(42.5);      // Testing tax
});

// ✅ After: Focused Tests
it('should apply 15% discount for premium customers', () => {
    const result = processor.processOrder(customer, order);
    expect(result.discountAmount).toBe(150);
});

it('should provide free express shipping for premium customers', () => {
    const result = processor.processOrder(customer, order);
    expect(result.shippingCost).toBe(0);
});

it('should calculate tax on discounted amount', () => {
    const result = processor.processOrder(customer, order);
    expect(result.taxAmount).toBe(42.5);
});
```

---

### Pattern: Test Duplication → Extract Helpers

**Problem**: Same setup code repeated across tests.

**Solution**: Extract business-meaningful helper methods.

```typescript
// ❌ Before: Duplicated Setup
it('should apply discount', () => {
    const customer = {
        id: '123', type: 'premium',
        yearsActive: 5, email: 'test@example.com'
    };
    const order = {
        id: '456', items: [{ sku: 'ABC', price: 1000 }]
    };
    const result = processor.processOrder(customer, order);
    expect(result.discountAmount).toBe(150);
});

it('should provide free shipping', () => {
    const customer = {
        id: '123', type: 'premium',
        yearsActive: 5, email: 'test@example.com'
    };
    const order = {
        id: '456', items: [{ sku: 'ABC', price: 1000 }]
    };
    const result = processor.processOrder(customer, order);
    expect(result.shippingCost).toBe(0);
});

// ✅ After: Extract Helpers
function createPremiumCustomer(): Customer {
    return { id: '123', type: 'premium', yearsActive: 5, email: 'test@example.com' };
}

function createHighValueOrder(): Order {
    return { id: '456', items: [{ sku: 'ABC', price: 1000 }] };
}

it('should apply discount', () => {
    const result = processor.processOrder(createPremiumCustomer(), createHighValueOrder());
    expect(result.discountAmount).toBe(150);
});

it('should provide free shipping', () => {
    const result = processor.processOrder(createPremiumCustomer(), createHighValueOrder());
    expect(result.shippingCost).toBe(0);
});
```

---

### Pattern: Conditional Logic → Parameterized Tests

**Problem**: if/switch in tests makes them non-deterministic.

**Solution**: Use parameterized test features.

```python
# ❌ Before: Conditional Logic
def test_discount_calculation():
    test_cases = [('regular', 0.0), ('premium', 0.15)]
    for customer_type, expected in test_cases:
        customer = Customer(type=customer_type)
        result = processor.process_order(customer, order)
        if expected > 0:
            assert result.discount == 1000 * expected
        else:
            assert result.discount == 0

# ✅ After: Parameterized
@pytest.mark.parametrize("customer_type,expected_rate", [
    ("regular", 0.0),
    ("premium", 0.15),
])
def test_applies_correct_discount_by_tier(customer_type, expected_rate):
    customer = Customer(type=customer_type)
    result = processor.process_order(customer, order)
    assert result.discount == 1000 * expected_rate
```

---

## L3 Refactoring Patterns

### Pattern: Mystery Guest → Explicit Setup

**Problem**: External file dependencies not visible in test.

**Solution**: Inline test data as constants.

```csharp
// ❌ Before: Mystery Guest
[Fact]
public void ImportOrder_ValidFile_CreatesOrder()
{
    var data = File.ReadAllText("test-data/order.json");
    var result = _importer.ImportOrder(data);
    Assert.Equal("ORD-123", result.OrderId);
}

// ✅ After: Explicit Setup
[Fact]
public void ImportOrder_ValidJson_CreatesOrderWithCorrectId()
{
    const string VALID_ORDER_JSON = @"{
        ""orderId"": ""ORD-123"",
        ""items"": [{ ""sku"": ""ABC"", ""quantity"": 1 }]
    }";
    var result = _importer.ImportOrder(VALID_ORDER_JSON);
    Assert.Equal("ORD-123", result.OrderId);
}
```

---

### Pattern: Test Class Bloat → Split Classes

**Problem**: One test class covers multiple concerns.

**Solution**: Split by feature into focused test classes.

```python
# ❌ Before: Test Class Bloat (31 tests)
class TestUserService:
    def test_create_user(self): ...
    def test_read_user(self): ...
    def test_update_user(self): ...
    def test_send_welcome_email(self): ...
    def test_upload_profile_image(self): ...
    def test_process_payment(self): ...
    # ... 25 more tests

# ✅ After: Split by Concern
class TestUserRepository:
    """CRUD operations - 5 tests"""
    def test_create_user_saves_to_database(self): ...
    def test_read_user_by_id_returns_user(self): ...

class TestUserNotificationService:
    """Email notifications - 8 tests"""
    def test_send_welcome_email_on_registration(self): ...

class TestUserProfileImageService:
    """Profile images - 6 tests"""
    def test_upload_image_stores_in_blob(self): ...

class TestUserPaymentService:
    """Payments - 7 tests"""
    def test_charge_customer_processes_payment(self): ...
```

---

### Pattern: General Fixture → Per-Test Setup

**Problem**: Shared fixture creates data not all tests need.

**Solution**: Per-test helper methods for focused setup.

```csharp
// ❌ Before: General Fixture
public class OrderTests
{
    private Customer _customer;
    private Order _order;
    private PaymentMethod _payment;
    private Address _address;

    public OrderTests()
    {
        _customer = new Customer { Type = "premium" };
        _order = new Order { Amount = 1000 };
        _payment = new PaymentMethod { Type = "Card" };
        _address = new Address { Country = "US" };
    }

    [Fact]
    public void CalculateDiscount_AppliesCorrectly()
    {
        // Only needs _customer and _order
        var result = _processor.CalculateDiscount(_customer, _order);
        Assert.Equal(150, result);
    }
}

// ✅ After: Per-Test Setup
public class OrderTests
{
    private Customer CreatePremiumCustomer() =>
        new Customer { Type = "premium" };

    private Order CreateHighValueOrder() =>
        new Order { Amount = 1000 };

    [Fact]
    public void CalculateDiscount_PremiumCustomer_AppliesCorrectly()
    {
        var customer = CreatePremiumCustomer();
        var order = CreateHighValueOrder();

        var result = _processor.CalculateDiscount(customer, order);

        Assert.Equal(150, result);
    }
}
```

---

## Quick Checklist

### L1 (Naming) Applied
- [ ] Test names reveal business scenarios (no Test1, TestMethod)
- [ ] No hard-coded magic numbers (extracted to named constants)
- [ ] Assertion messages explain business rules
- [ ] No commented test code

### L2 (Complexity) Applied
- [ ] Each test verifies one behavior (no eager tests)
- [ ] No duplicated setup (extracted to helpers)
- [ ] No conditional logic (use parameterized tests)
- [ ] Test setup is focused and minimal

### L3 (Organization) Applied
- [ ] Test classes ≤15 tests (split by concern if larger)
- [ ] No external file dependencies (inline test data)
- [ ] No shared fixtures for unrelated tests (per-test setup)
- [ ] Tests grouped by feature

---

## Integration with TDD

Apply test refactoring during **Phase 6 (REFACTOR_CONTINUOUS)** of 8-phase TDD cycle:

```
PREPARE → RED(A) → RED(U) → GREEN → REVIEW → REFACTOR_CONTINUOUS → REFACTOR_L4 → COMMIT
                                                      ↑
                                    Apply L1+L2+L3 to tests here
```

**Safety Protocol**:
1. All tests GREEN before refactoring
2. Refactor ONE test at a time
3. Run ALL tests after each change
4. Revert if any test fails
5. Commit when complete

---

## Key Principles

1. **Test code = First-class code** → Same quality standards
2. **L1-L3 every cycle** → Part of refactor phase, not optional
3. **One test at a time** → Keep tests green
4. **Clarity over DRY** → Prefer readable over clever
5. **Test behavior, not implementation** → Make tests resilient

---

**For comprehensive examples and advanced patterns, see full test-refactoring-guide.md**
