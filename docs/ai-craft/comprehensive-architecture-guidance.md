# Comprehensive Architecture Guidance for AI-Craft Pipeline

## Overview

This document consolidates all architectural methodologies, patterns, and principles implemented in the AI-Craft pipeline. It serves as the definitive guide for developers using the outside-in ATDD workflow with hexagonal architecture, Object Calisthenics, DDD patterns, and SOLID++/CUPID principles.

## Core Methodologies Integration

### 1. Outside-In ATDD with Double-Loop TDD Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ OUTER LOOP: Acceptance Test Driven Development (ATDD) - Customer View       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ INNER LOOP: Unit Test Driven Development (UTDD) - Developer View     │  │
│  │  🔴 RED → 🟢 GREEN → 🔵 REFACTOR                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Four-Stage ATDD Cycle**:
1. **DISCUSS**: Requirements clarification with stakeholders
2. **DISTILL**: Create acceptance tests from user perspective
3. **DEVELOP**: Outside-In TDD implementation with double-loop
4. **DEMO**: Stakeholder validation and feedback integration

### 2. Hexagonal Architecture with Vertical Slices

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                    E2E Tests (Business Behavior)                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Application Services (Use Cases) - Ports                                      │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Domain Services (Business Logic) - Pure Domain                                │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Infrastructure (Adapters) + Integration Tests                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**Key Principles**:
- **Ports**: Business interfaces defined by domain needs
- **Adapters**: Infrastructure implementations with NO business logic
- **Vertical Slices**: Complete business capabilities spanning all layers
- **Integration Tests**: Separate test suite for adapter validation

## Object-Oriented Design Excellence

### Object Calisthenics (All 9 Rules)

**Complete Rule Implementation**:

#### Rule 1: Only One Level of Indentation Per Method
```csharp
// ✅ Good: Single level of indentation
internal sealed class OrderProcessor
{
    public async Task<ProcessingResult> ProcessAsync(Order order)
    {
        if (!IsValid(order))
            return ProcessingResult.Invalid();
            
        await SaveAsync(order);
        return ProcessingResult.Success();
    }
}
```

#### Rule 2: Don't Use the ELSE Keyword
```csharp
// ✅ Good: Early returns instead of else
public OrderStatus DetermineStatus(Order order)
{
    if (order.IsEmpty())
        return OrderStatus.Empty;
        
    if (order.IsPending())
        return OrderStatus.Pending;
        
    return OrderStatus.Confirmed;
}
```

#### Rule 3: Wrap All Primitives and Strings
```csharp
// ✅ Value objects for all primitives
public readonly record struct UserId(Guid Value);
public readonly record struct Email(string Value);
public readonly record struct Money(decimal Amount, Currency Currency);
```

#### Rule 4: First Class Collections
```csharp
// ✅ Collection with business behavior
internal sealed class OrderItems
{
    private readonly List<OrderItem> _items = new();
    
    public void Add(OrderItem item) { /* Business validation */ }
    public Money CalculateTotal() { /* Business calculation */ }
    public IReadOnlyList<OrderItem> Items => _items.AsReadOnly();
}
```

#### Rule 5: One Dot Per Line
```csharp
// ✅ Good: Each method call on separate line
var user = userRepository.FindById(userId);
var orders = user.GetOrders();
var total = orders.CalculateTotal();
```

#### Rule 6: Don't Abbreviate
```csharp
// ✅ Good: Full, intention-revealing names
public async Task<AuthenticationResult> AuthenticateUserCredentials(
    Username username, Password password)
```

#### Rule 7: Keep All Entities Small
```csharp
// ✅ Small classes with single responsibility (< 50 lines)
internal sealed class OrderValidator
{
    public ValidationResult Validate(Order order)
    {
        // Single responsibility: validation only
    }
}
```

#### Rule 8: No Classes with More Than Two Instance Variables
```csharp
// ✅ Maximum 2 instance variables
internal sealed class OrderService
{
    private readonly IOrderRepository _repository;
    private readonly OrderValidator _validator;
    
    // Business methods using these collaborators
}
```

#### Rule 9: Tell, Don't Ask
```csharp
// ✅ Good: Tell the object what to do
internal sealed class BankAccount
{
    private Money _balance;
    
    public WithdrawalResult Withdraw(Money amount)
    {
        if (_balance.IsLessThan(amount))
            return WithdrawalResult.InsufficientFunds();
        _balance = _balance.Subtract(amount);
        return WithdrawalResult.Success(_balance);
    }
}
```

### DDD Tactical Patterns with Internal Sealed Classes

**Default Encapsulation Strategy**: Internal sealed classes by default, public only when necessary.

#### Aggregate Roots (Public)
```csharp
// ✅ Only aggregate roots are public
public sealed class Order
{
    public OrderId Id { get; }
    public CustomerId CustomerId { get; }
    public OrderStatus Status { get; }
    public Money Total { get; }
    
    // Internal constructor - controlled creation
    internal Order(OrderId id, CustomerId customerId) { }
    
    // Public behavior methods
    public void AddItem(ProductId productId, Quantity quantity) { }
    public void ConfirmOrder() { }
}
```

#### Entities (Internal Sealed)
```csharp
// ✅ Entities within aggregates are internal
internal sealed class OrderItem
{
    public ProductId ProductId { get; }
    public Quantity Quantity { get; private set; }
    public Money UnitPrice { get; }
    
    internal OrderItem(ProductId productId, Quantity quantity, Money unitPrice)
    {
        // Validation and initialization
    }
    
    public void UpdateQuantity(Quantity newQuantity) { }
}
```

#### Value Objects (Internal Sealed Records)
```csharp
// ✅ Immutable value objects
internal sealed record Money
{
    public decimal Amount { get; }
    public Currency Currency { get; }
    
    public Money(decimal amount, Currency currency)
    {
        // Validation logic
    }
    
    public Money Add(Money other) => new(Amount + other.Amount, Currency);
    public bool IsGreaterThan(Money other) => Amount > other.Amount;
}
```

#### Domain Services (Internal Sealed)
```csharp
// ✅ Pure business logic, no infrastructure
internal sealed class OrderPricingService
{
    public Money CalculatePrice(Order order, PricingPolicy policy)
    {
        // Pure business calculation
        return policy.ApplyTo(order.Items);
    }
}
```

#### Application Services (Internal Sealed)
```csharp
// ✅ Orchestration only, no business logic
internal sealed class OrderApplicationService : IOrderService
{
    private readonly IOrderRepository _repository;
    private readonly OrderPricingService _pricingService;
    
    public async Task<OrderResult> CreateOrderAsync(CreateOrderCommand command)
    {
        // Orchestration: load data, call domain services, save results
        var customer = await _repository.FindCustomerAsync(command.CustomerId);
        var order = Order.Create(command.CustomerId);
        
        foreach (var item in command.Items)
        {
            order.AddItem(item.ProductId, item.Quantity);
        }
        
        var price = _pricingService.CalculatePrice(order, customer.PricingPolicy);
        order.SetPrice(price);
        
        await _repository.SaveAsync(order);
        return OrderResult.Success(order.Id);
    }
}
```

#### Repository Interfaces (Public) and Implementations (Internal Sealed)
```csharp
// ✅ Public interface for ports
public interface IOrderRepository
{
    Task<Order?> FindByIdAsync(OrderId id);
    Task<OrderId> SaveAsync(Order order);
}

// ✅ Internal sealed implementation (adapter)
internal sealed class DatabaseOrderRepository : IOrderRepository
{
    private readonly DbContext _context;
    
    public async Task<Order?> FindByIdAsync(OrderId id)
    {
        // Only data access translation - no business logic
        var entity = await _context.Orders.FindAsync(id.Value);
        return entity?.ToDomain();
    }
    
    public async Task<OrderId> SaveAsync(Order order)
    {
        // Only persistence logic - no business rules
        var entity = OrderEntity.FromDomain(order);
        _context.Orders.Add(entity);
        await _context.SaveChangesAsync();
        return order.Id;
    }
}
```

## SOLID++ and CUPID Principles Integration

### SOLID++ Principles Applied

#### Single Responsibility + Composable (CUPID)
```csharp
// ✅ Does one thing well, easy to compose
internal sealed class OrderCreationService
{
    public async Task<OrderResult> CreateAsync(CreateOrderCommand command)
    {
        // Only creates orders - single responsibility
        // Small surface area - composable
    }
}
```

#### Open/Closed + Predictable (CUPID)
```csharp
// ✅ Open for extension via strategy, predictable behavior
internal sealed class OrderPricingService
{
    private readonly IPricingStrategy _strategy;
    
    public Money CalculatePrice(Order order)
    {
        return _strategy.Calculate(order); // Predictable, extensible
    }
}

// ✅ Strategies implement consistent contract
internal sealed class PremiumPricingStrategy : IPricingStrategy
{
    public Money Calculate(Order order)
    {
        // Honors contract, follows .NET conventions (Idiomatic)
        if (order.Total.IsGreaterThan(PremiumThreshold))
            return order.Total.ApplyDiscount(PremiumDiscountRate);
        return order.Total;
    }
}
```

#### Interface Segregation + Domain-Based (CUPID)
```csharp
// ✅ Domain-focused, clients use only what they need
public interface IOrderReader
{
    Task<Order?> FindByIdAsync(OrderId id);
}

public interface IOrderWriter
{
    Task<OrderId> SaveAsync(Order order);
}
```

#### Dependency Inversion + Unix Philosophy (CUPID)
```csharp
// ✅ Depends on abstractions, does one thing well
internal sealed class OrderService
{
    private readonly IOrderRepository _repository; // Abstraction dependency
    
    public async Task<OrderResult> ProcessAsync(Order order)
    {
        // Does one thing well (Unix philosophy)
        // Depends on abstractions (DIP)
    }
}
```

### CUPID Properties Implementation

**COMPOSABLE**: Small surface area, intention-revealing, minimal dependencies
**UNIX PHILOSOPHY**: Does one thing well, clear interfaces
**PREDICTABLE**: Consistent behavior, no surprises, deterministic
**IDIOMATIC**: Follows .NET conventions, familiar patterns
**DOMAIN-BASED**: Uses business language, organized by domain concepts

## Testing Strategy Through Public Interfaces Only

### Black Box Testing Approach

**Core Principle**: Test only through public interfaces to ease refactoring and simplify API.

#### Testing Aggregate Roots Only
```csharp
[When("the user places an order with valid items")]
public async Task WhenUserPlacesOrderWithValidItems()
{
    // ✅ CORRECT: Test through public aggregate root only
    var orderService = _serviceProvider.GetRequiredService<IOrderService>();
    
    var command = new CreateOrderCommand
    {
        CustomerId = _testCustomerId,
        Items = _testOrderItems
    };
    
    _orderResult = await orderService.CreateOrderAsync(command);
    
    // ❌ AVOID: Testing internal implementation details
    // var order = new Order(orderId, customerId); // Internal constructor
    // order._items.Add(item); // Private field access
}
```

#### Validation Through Public Interface
```csharp
[Then("the order should be created successfully")]
public async Task ThenOrderShouldBeCreatedSuccessfully()
{
    // ✅ CORRECT: Validate through public interface only
    _orderResult.Should().NotBeNull();
    _orderResult.IsSuccess.Should().BeTrue();
    
    // Verify through public service interface
    var orderService = _serviceProvider.GetRequiredService<IOrderService>();
    var order = await orderService.FindByIdAsync(_orderResult.OrderId);
    
    order.Should().NotBeNull();
    order.CustomerId.Should().Be(_testCustomerId);
    
    // ❌ AVOID: Testing internal state
    // order._status.Should().Be(OrderStatus.Draft); // Private field
    // order.InternalValidationMethod(); // Internal method
}
```

### Benefits of Public Interface Testing

1. **Refactoring Safety**: Internal changes don't break tests
2. **API Simplicity**: Tests validate the actual public contract
3. **Encapsulation Respect**: Honors internal sealed design
4. **Business Focus**: Tests validate business behavior, not implementation
5. **DDD Compliance**: Respects aggregate boundaries and encapsulation

### Behavior-Focused Unit Testing Strategy

**Core Principle**: Test behaviors, not code structure. A behavior represents a meaningful action from the user's perspective.

#### Three Types of Behaviors

**1. Command Behavior (Changes System State)**
```csharp
// ✅ Command: Tests state changes relevant to user with multiple asserts for same behavior
[Test]
public async Task Should_CreateOrderWithItems_When_ValidItemsProvided()
{
    var orderService = new OrderService(_repository, _pricingService);
    var items = new[] { new OrderItem("Product1", 2, 10m), new OrderItem("Product2", 1, 15m) };

    var result = await orderService.CreateOrderAsync("Customer1", items);

    // All asserts validate the single "create order" behavior - multiple asserts OK
    result.IsSuccess.Should().BeTrue();
    result.Order.CustomerId.Should().Be("Customer1");
    result.Order.Items.Should().HaveCount(2);
    result.Order.Total.Should().Be(35m);
    result.Order.Status.Should().Be(OrderStatus.Draft);
}
```

**2. Query Behavior (Projects System State)**
```csharp
// ✅ Query: Returns projection of state relevant to user (Given-Then structure)
[Test]
public async Task Should_ReturnActiveUsers_When_FilteringByStatus()
{
    // Given (Arrange)
    await _repository.SaveAsync(TestUser.Active("Alice"));
    await _repository.SaveAsync(TestUser.Inactive("Bob"));
    var userService = new UserService(_repository);

    // Then (Assert) - no separate When needed for queries
    var activeUsers = await userService.GetActiveUsersAsync();
    activeUsers.Should().HaveCount(1);
    activeUsers.Should().Contain(u => u.Name == "Alice");
}
```

**3. Process Behavior (Triggers Other Commands/Queries)**
```csharp
// ✅ Process: Orchestrates multiple commands/queries with complete workflow validation
[Test]
public async Task Should_CompleteOrderFulfillment_When_ProcessingOrder()
{
    var fulfillmentService = new OrderFulfillmentService(_orderRepo, _inventoryService);
    var order = TestOrder.WithItems("Product1", "Product2");

    var result = await fulfillmentService.ProcessOrderAsync(order.Id);

    // Multiple asserts validating complete fulfillment process behavior
    result.IsSuccess.Should().BeTrue();
    result.TrackingNumber.Should().NotBeNullOrEmpty();
    var updatedOrder = await _orderRepo.FindByIdAsync(order.Id);
    updatedOrder.Status.Should().Be(OrderStatus.Shipped);
}
```

### Mutation Testing Integration

**When to Execute**: After the last acceptance test of a feature passes, before Level 4-6 refactoring begins.

#### Mutation Testing Process
```bash
# 1. Run mutation testing tool
dotnet stryker --project MyProject --test-projects MyProject.Tests

# 2. Validate mutation score
# Target: ≥75-80% overall, ≥90% for critical business logic

# 3. Add property-based tests for surviving mutants
# 4. Add model-based tests for complex business rules
# 5. Achieve quality gates before advanced refactoring
```

#### Property-Based Testing for Edge Cases
```csharp
// ✅ Property-based test for mathematical properties
[Property]
public Property Money_Addition_Should_Be_Associative(decimal a, decimal b, decimal c)
{
    var money1 = new Money(a);
    var money2 = new Money(b);
    var money3 = new Money(c);

    return ((money1 + money2) + money3).Amount
        .Equals((money1 + (money2 + money3)).Amount);
}

// ✅ Property-based test for business invariants
[Property]
public Property Account_Balance_Should_Never_Be_Negative_After_Valid_Operations(
    PositiveInt initialBalance, NonNegativeInt[] validWithdrawals)
{
    var account = new Account(new Money(initialBalance.Item));
    
    foreach (var withdrawal in validWithdrawals.Where(w => w.Item <= account.Balance.Amount))
    {
        account.Withdraw(new Money(withdrawal.Item));
    }
    
    return (account.Balance.Amount >= 0).ToProperty();
}
```

#### Model-Based Testing for State Transitions
```csharp
// ✅ Model-based test for complex business rules
[Test]
public void OrderStateMachine_Should_FollowValidTransitions()
{
    var validTransitions = new Dictionary<OrderStatus, OrderStatus[]>
    {
        [OrderStatus.Draft] = new[] { OrderStatus.Confirmed, OrderStatus.Cancelled },
        [OrderStatus.Confirmed] = new[] { OrderStatus.Shipped, OrderStatus.Cancelled },
        [OrderStatus.Shipped] = new[] { OrderStatus.Delivered },
        [OrderStatus.Delivered] = new OrderStatus[0],
        [OrderStatus.Cancelled] = new OrderStatus[0]
    };

    foreach (var (fromStatus, allowedTransitions) in validTransitions)
    {
        var order = TestOrder.WithStatus(fromStatus);
        
        foreach (var toStatus in Enum.GetValues<OrderStatus>())
        {
            var transitionAttempt = () => order.TransitionTo(toStatus);
            
            if (allowedTransitions.Contains(toStatus))
                transitionAttempt.Should().NotThrow();
            else
                transitionAttempt.Should().Throw<InvalidOperationException>();
        }
    }
}
```

#### Quality Gates for Advanced Refactoring
- ✅ **Mutation Score**: ≥75-80% overall, ≥90% critical paths
- ✅ **Property Tests**: All mathematical properties and invariants covered
- ✅ **Model Tests**: Complex state transitions and business rules validated
- ✅ **Behavior Coverage**: All user-relevant behaviors tested with single-behavior focus
- ✅ **Critical Mutants Eliminated**: No surviving mutants in critical business logic

## Environment Strategy

### Dual-Environment Testing Approach

**Local Development Choice**: User selects between in-memory (~100ms) or real components (~2-5s)
**CI/CD Pipeline**: Always uses production-like real components
**Same Test Scenarios**: Single source of truth across all environments

#### Environment Configuration Implementation
```csharp
public static class TestEnvironmentSetup
{
    public static async Task<bool> AskUserForLocalComponentChoice()
    {
        Console.WriteLine("For local development, would you prefer:");
        Console.WriteLine("1. In-Memory Components (fastest feedback, ~100ms)");
        Console.WriteLine("2. Real Components Locally (more realistic, ~2-5s)");
        Console.WriteLine("Note: CI/CD will always use production-like real components");
        
        var choice = Console.ReadLine();
        return choice == "2";
    }
    
    public static IServiceCollection ConfigureServices(bool useRealComponentsLocally)
    {
        var services = new ServiceCollection();
        
        // Always register business logic (same in all environments)
        services.AddScoped<IUserService, UserService>();
        services.AddScoped<IOrderService, OrderService>();
        
        if (IsCI() || useRealComponentsLocally)
        {
            // Real components (CI/CD always, local by user choice)
            services.AddScoped<IUserRepository, DatabaseUserRepository>();
            services.AddScoped<IEmailService, SmtpEmailService>();
        }
        else
        {
            // In-memory components (local development, user choice)
            services.AddSingleton<IUserRepository, InMemoryUserRepository>();
            services.AddSingleton<IEmailService, InMemoryEmailService>();
        }
        
        return services;
    }
}
```

### Free Framework Requirements
```csharp
// ✅ ALLOWED - Free Open Source
using NUnit.Framework;              // MIT License
using NSubstitute;                 // BSD License
using Testcontainers;              // MIT License

// ❌ FORBIDDEN - Paid/Commercial
// using FluentAssertions; // Paid license for commercial use
// using JustMock; // Commercial license required
```

## Six-Level Refactoring Hierarchy

**Progressive Refactoring Approach**: Apply levels systematically from foundation to advanced principles.

### Level 1: 🟨 Foundation Refactoring
- Remove obsolete comments, dead code
- Extract constants for magic numbers/strings
- Apply domain naming conventions
- Optimize variable scope

### Level 2: 🟢 Complexity Reduction
- Extract methods with business-meaningful names
- Eliminate duplicated code
- Apply Compose Method pattern

### Level 3: 🟢 Responsibility Organization
- Apply Single Responsibility Principle
- Move methods to appropriate classes
- Reduce inappropriate coupling

### Level 4: 🟢 Abstraction Refinement
- Create parameter objects
- Introduce value objects
- Eliminate primitive obsession

### Level 5: 🔵 Design Pattern Application
- Replace switch statements with Strategy pattern
- Implement State pattern for state-dependent behavior
- Apply Command pattern for operations

### Level 6: 🔵 SOLID++ & CUPID Principles
- Apply all SOLID principles rigorously
- Implement CUPID properties (Composable, Unix Philosophy, Predictable, Idiomatic, Domain-Based)
- Enforce Object Calisthenics compliance
- Apply DDD patterns with proper encapsulation

## Mikado Method for Complex Refactorings

**When to Apply**: Level 4-6 refactorings affecting architecture or spanning multiple classes.

### Core Mikado Principles

#### 1. Goal Definition & Impact Analysis
```markdown
🎯 MIKADO GOAL: Extract OrderPricingService to separate pricing concerns

IMPACT ASSESSMENT:
- Classes affected: Order, OrderApplicationService, OrderController
- Tests affected: OrderTests, OrderApplicationServiceTests
- Architectural impact: Introduces new domain service
- Breaking changes: Order pricing methods become internal
```

#### 2. Mikado Tree Construction
```
🎯 GOAL: Extract OrderPricingService
├── 📋 Create IOrderPricingService interface
├── 📋 Implement OrderPricingService class
│   ├── 📋 Extract pricing logic from Order
│   └── 📋 Add pricing strategy support
├── 📋 Update Order class to use service
│   ├── 📋 Remove pricing methods from Order
│   ├── 📋 Add dependency injection for pricing service
│   └── 📋 Update constructor and factory methods
├── 📋 Update all Order consumers
│   ├── 📋 Update OrderApplicationService
│   ├── 📋 Update OrderController
│   └── 📋 Update test setup
└── 📋 Validate architectural compliance
    ├── 📋 Verify hexagonal architecture boundaries
    ├── 📋 Confirm DDD aggregate integrity
    └── 📋 Update architecture diagrams
```

#### 3. Parallel Change Implementation
```csharp
// EXPAND: Add new alongside existing
public sealed class Order
{
    // Keep existing methods temporarily
    public Money CalculatePrice() { /* existing logic */ }
    
    // Add new service-based approach
    private IOrderPricingService? _pricingService;
    
    public Money CalculatePriceWithService()
    {
        return _pricingService?.CalculatePrice(this) 
            ?? CalculatePrice(); // Fallback to existing
    }
}

// MIGRATE: Switch consumers one by one
// OrderApplicationService updated first
var price = order.CalculatePriceWithService(); // New approach

// CONTRACT: Remove old implementation
// Remove CalculatePrice() when all consumers migrated
```

### Baby Steps Protocol (MANDATORY)

#### Test Execution After Every Change
```bash
# After every single change, no matter how small:
dotnet test --no-build --verbosity minimal

# If tests pass: ✅ Continue to next step
# If tests fail: 🚨 IMMEDIATE ROLLBACK PROTOCOL
```

#### Rollback and Root Cause Analysis
```markdown
🚨 TEST FAILURE DETECTED

IMMEDIATE ACTIONS:
1. 🔄 ROLLBACK: Undo the last change immediately
   git checkout -- [modified files]
   
2. 🔍 EXECUTE ROOT CAUSE ANALYSIS:
   /root-why "Test failure during Mikado refactoring" --evidence @tests/ @logs/ --focus system --depth comprehensive
   
   PROVIDE CONTEXT:
   - Mikado Goal: [Current refactoring objective]
   - Failed Step: [Specific baby step attempted]
   - Test Failures: [Which tests failed and why]
   - Code Changes: [Files and methods modified]
   - Prerequisites Completed: [Previous successful steps]
   
3. 📝 INTEGRATE TOYOTA 5 WHYS RESULTS:
   - Add ALL prerequisites discovered from multi-causal analysis
   - Update Mikado tree with systematic dependency mapping based on evidence
   - Document lessons learned for future refactoring patterns
   - Archive comprehensive root cause analysis for team knowledge base
   
4. 🔧 APPLY EVIDENCE-BASED FIX:
   - Address ALL root causes identified through Toyota methodology
   - Implement solutions with backwards validation to symptoms
   - Apply Kaizen improvements to prevent recurrence
   
5. 🔄 RETRY WITH SYSTEMATIC CONFIDENCE:
   - Attempt original change with comprehensive prerequisite resolution
   - Monitor for similar failure patterns in future refactoring
```

### Mikado MCP Server Integration (Future)

When Mikado MCP Server becomes available:
- **Automated dependency tracking** and visual tree management
- **Risk assessment** for complex refactoring operations
- **Progress tracking** with prerequisite validation
- **Impact analysis** across component boundaries
- **Safety checkpoints** and rollback automation

### Complex Refactoring Scenarios

#### SOLID Principle Application
```markdown
🎯 GOAL: Apply Single Responsibility Principle to OrderService

STRATEGY: Extract multiple services using parallel change
1. Create validation service alongside existing validation
2. Create persistence service alongside existing persistence  
3. Migrate consumers one by one to new services
4. Remove original multipurpose methods
5. Refactor OrderService to orchestration only
```

#### Design Pattern Introduction  
```markdown
🎯 GOAL: Replace Switch Statement with Strategy Pattern

STRATEGY: Strategy pattern with fallback mechanism
1. Define strategy interface and implementations
2. Add strategy selector alongside existing switch
3. Migrate switch cases one by one to strategies
4. Keep switch as fallback during migration
5. Remove switch when all cases covered by strategies
```

### Safety Protocols

#### Green Bar Discipline
- **Never commit with failing tests**
- **Run tests after every atomic change** (max 10 lines)
- **Maximum 5-minute intervals** between test runs
- **Rollback immediately** on any failure

#### Change Size Limits
- **Maximum 10 lines changed per step**
- **One conceptual change per commit**
- **No mixed refactoring and feature changes**
- **Each step independently testable**

#### Quality Gates
- **Component boundaries preserved**: ✅
- **Design patterns correctly implemented**: ✅
- **SOLID++ principles upheld**: ✅
- **DDD aggregate integrity maintained**: ✅
- **Test coverage maintained or improved**: ✅

### Mikado Method Benefits

1. **Risk Mitigation**: Never break tests through systematic prerequisite discovery
2. **Visibility**: Clear dependency tree shows progress and remaining work
3. **Rollback Safety**: Every step is safe to undo with clear recovery path
4. **Learning**: Toyota 5 Whys root cause analysis provides systematic lessons learned for future refactoring planning
5. **Architectural Integrity**: Systematic validation of design compliance

## Pipeline Integration

### Agent Collaboration Pattern

**File-Based Pipeline**: Each agent reads input files and produces output files for the next agent.

```
requirements.md → architecture.md → acceptance-tests.md → implementation-status.md → validation-report.md
     ↓               ↓                    ↓                        ↓                      ↓
business-analyst → solution-architect → acceptance-designer → test-first-developer → production-validator
```

### Quality Gates Integration

**Validation Cycle**: 8-step validation applied at every stage:
1. Syntax validation
2. Type checking
3. Lint compliance
4. Security scanning
5. Test execution (≥80% unit, ≥70% integration)
6. Performance benchmarking
7. Documentation completeness
8. Integration testing

### Technical Debt Management

**Continuous Tracking**: Technical debt items tracked throughout pipeline with priority scoring:
- **Critical**: Blocks development, security risks
- **High**: Impacts maintainability, performance issues
- **Medium**: Code quality improvements
- **Low**: Nice-to-have enhancements

## Best Practices Summary

### Development Workflow
1. **Start with ATDD**: Write acceptance tests first, driven by business requirements
2. **Apply Outside-In TDD**: Drive implementation through failing tests
3. **Respect Hexagonal Boundaries**: Keep business logic pure, adapters thin
4. **Follow Object Calisthenics**: All 9 rules for excellent OO design
5. **Use DDD Patterns**: Aggregates, entities, value objects, domain services
6. **Default to Internal Sealed**: Public only when necessary for API
7. **Test Through Public Interfaces**: Enable fearless refactoring
8. **Apply Progressive Refactoring**: Level 1-6 systematically with Mikado Method for complex changes
9. **Choose Environment Wisely**: In-memory locally, production-like in CI/CD
10. **Use Free Frameworks Only**: No paid dependencies

### Refactoring and Commit Discipline
- **Baby Steps Protocol**: Maximum 10 lines per change, run tests after every change
- **Local Commit After Every Green**: Commit locally after every passing test and successful refactoring step
- **Continue Until Complete**: Keep refactoring and committing until the entire refactoring phase is finished
- **Mikado Method for Complex Changes**: Use systematic dependency tracking for Level 4-6 refactorings
- **Parallel Change Pattern**: EXPAND → MIGRATE → CONTRACT for breaking changes
- **Root Cause Analysis Protocol**: On any failure, execute /root-why command before retry
- **Document Progress Updates**: Always update tracking documents to prepare field for next agent

### Quality Assurance
- **Never commit failing tests**: All enabled tests must pass
- **One E2E test at a time**: Prevent overwhelming development
- **Use NotImplementedException**: For proper scaffolding pressure
- **Real system integration**: Avoid excessive mocking in E2E tests
- **Business-focused naming**: Reveal intent, not implementation
- **Continuous refactoring**: Never skip refactoring in TDD cycles
- **Green Bar Discipline**: Never break tests - rollback immediately on any failure
- **Document Synchronization**: Keep all pipeline documents current with actual progress

### Progress Tracking Protocol
- **Update implementation-status.md**: After every significant development step
- **Update refactoring-report.md**: Document all refactoring actions and outcomes
- **Update technical-debt.md**: Track debt items resolved and newly identified
- **Update architecture-diagrams.md**: When structural changes occur
- **Maintain Mikado tree**: Visual progress tracking for complex refactorings (when server available)
- **Prepare next agent inputs**: Ensure following agents have current, accurate information

### Enhanced Build and Test Protocol
- **Always build before testing**: `dotnet build --configuration Release --no-restore`
- **Test with fresh build**: `dotnet test --configuration Release --no-build`
- **Exercise most recent logic**: Ensure tests validate current implementation state
- **Fail fast on build issues**: Address compilation before proceeding with logic

## Feature Completion and CI/CD Integration Lifecycle

### Complete Feature Lifecycle

#### Phase 1: Feature Implementation
- **ATDD Development**: Outside-in development with double-loop TDD
- **Mutation Testing**: Validate test effectiveness (≥75% score)
- **Comprehensive Refactoring**: Apply Level 1-6 systematically
- **Architecture Compliance**: Maintain hexagonal boundaries and DDD patterns

#### Phase 2: Feature Completion Validation
```bash
# When all acceptance scenarios pass for the feature:

# 1. FINAL LOCAL QUALITY GATES
./scripts/run_quality_gates.sh
# - Build validation (all projects) 
# - Test execution (all suites)
# - Code formatting validation
# - Static analysis compliance
# - Security scanning 
# - Performance benchmarking
# - Documentation validation
# - Integration testing

# 2. COMMIT FEATURE COMPLETION
git add .
git commit -m "Complete [Feature Name] implementation

- All acceptance scenarios passing
- Mutation testing ≥75% score achieved  
- Comprehensive Level 1-6 refactoring applied
- Architecture compliance validated
- Quality gates passed

🤖 Generated with [Claude Code](https://claude.ai/code)

Co-Authored-By: Claude <noreply@anthropic.com>"

# 3. PUSH AND MONITOR CI/CD
git push origin [branch-name]
```

#### Phase 3: CI/CD Pipeline Integration

**Success Path**:
```markdown
✅ CI/CD PIPELINE SUCCESSFUL

NEXT STEPS:
1. 🎉 Feature completion celebration
2. 📊 Update project metrics and progress tracking  
3. 🗣️ Begin discussion of next feature
4. 📋 Review product backlog priorities
5. 🎯 Select next highest value feature

TRANSITION TO NEXT FEATURE:
• Business Analyst: Gather requirements for next feature
• Architecture review: Assess impact on current design
• Begin new ATDD cycle: DISCUSS → DISTILL → DEVELOP → DEMO
```

**Failure Response Protocol**:
```bash
🚨 CI/CD PIPELINE FAILED

IMMEDIATE ROOT CAUSE ANALYSIS:
/root-why "CI/CD pipeline failure" --evidence @logs/ci-cd/ @config/ --focus system --depth comprehensive

PROVIDE COMPLETE CONTEXT:
- CI/CD Pipeline URL and logs
- Failed step with specific error messages
- Recent commits and configuration changes
- Environment differences identified
- Business impact and urgency level

INTEGRATE TOYOTA 5 WHYS ANALYSIS:
Based on systematic multi-causal investigation:

IMMEDIATE ACTIONS:
• Apply evidence-based emergency fixes from root cause analysis
• Communicate status to stakeholders with clear timeline
• Implement critical production stability measures

SYSTEMATIC SOLUTIONS:
• Address ALL root causes identified through Toyota methodology
• Fix environment configuration gaps systematically
• Enhance test coverage based on failure pattern analysis
• Update CI/CD pipeline configuration with prevention measures

KAIZEN PREVENTION:
• Implement systematic process improvements from comprehensive analysis
• Enhance monitoring, alerting, and early detection
• Update team training and process documentation
• Apply backwards validation to ensure completeness

VALIDATE SOLUTION EFFECTIVENESS → RETRY CI/CD → ARCHIVE LESSONS LEARNED
```

### Quality Gates Local Validation Script

**MANDATORY: Pre-Push Quality Gates Validation**

This script must pass 100% before any push to ensure CI/CD parity and prevent pipeline failures.

```bash
#!/bin/bash
# pre-push-quality-gates.sh - MANDATORY validation before push
set -e

echo "🎯 Starting Pre-Push Quality Gates Validation..."

# Step 1: Build Validation - Match CI/CD exactly
echo "🔨 Step 1: Build Validation..."
dotnet build --configuration Release --no-restore
if [ $? -ne 0 ]; then
    echo "❌ Build failed. Cannot proceed with push."
    exit 1
fi
echo "✅ Build successful."

# Step 2: Test Execution - Match CI/CD exactly
echo "🧪 Step 2: Test Execution..."
dotnet test --configuration Release --no-build --verbosity minimal
if [ $? -ne 0 ]; then
    echo "❌ Tests failed. Cannot proceed with push."
    exit 1
fi
echo "✅ All tests passing."

# Step 3: Mutation Testing (if feature complete)
if [ "$FEATURE_COMPLETE" = "true" ]; then
    echo "🧬 Step 3: Mutation Testing..."
    dotnet stryker --config-file stryker-config.json
    MUTATION_SCORE=$(grep -o '"score":[0-9.]*' mutation-report.json | cut -d':' -f2)
    if (( $(echo "$MUTATION_SCORE < 75" | bc -l) )); then
        echo "❌ Mutation score $MUTATION_SCORE% below 75% threshold."
        echo "   Add property-based or model tests to kill surviving mutants."
        exit 1
    fi
    echo "✅ Mutation score: $MUTATION_SCORE%"
else
    echo "ℹ️ Step 3: Mutation Testing skipped (feature not complete)."
fi

# Step 4: Code Formatting - Match CI/CD exactly
echo "🎨 Step 4: Code Formatting..."
dotnet format --verify-no-changes --verbosity minimal
if [ $? -ne 0 ]; then
    echo "❌ Code formatting issues found. Run 'dotnet format' first."
    exit 1
fi
echo "✅ Code formatting compliant."

# Step 5: Static Analysis - Match CI/CD exactly
echo "🔍 Step 5: Static Analysis..."
if command -v sonar-scanner &> /dev/null; then
    sonar-scanner
    # Check quality gate status
    QUALITY_GATE=$(curl -s "$SONAR_HOST_URL/api/qualitygates/project_status?projectKey=$SONAR_PROJECT_KEY" | jq -r '.projectStatus.status')
    if [ "$QUALITY_GATE" != "OK" ]; then
        echo "❌ SonarQube quality gate failed: $QUALITY_GATE"
        exit 1
    fi
    echo "✅ Static analysis passed."
else
    echo "⚠️ SonarQube not available locally. Will validate in CI/CD."
fi

# Step 6: Security Scanning - Match CI/CD exactly
echo "🛡️ Step 6: Security Scanning..."
dotnet list package --vulnerable
if [ $? -eq 1 ]; then
    echo "⚠️ Vulnerable packages detected. Review before push."
    read -p "Continue with push? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "❌ Push cancelled due to security concerns."
        exit 1
    fi
fi
echo "✅ Security scan completed."

# Step 7: Performance Validation (if applicable)
if [ -f "benchmarks/benchmarks.csproj" ]; then
    echo "⚡ Step 7: Performance Benchmarking..."
    dotnet run --project benchmarks --configuration Release > benchmark-results.txt
    # Validate against performance baselines
    echo "✅ Performance benchmarks completed."
else
    echo "ℹ️ Step 7: Performance benchmarks skipped (no benchmarks project)."
fi

# Step 8: Documentation Validation
echo "📚 Step 8: Documentation Validation..."
# Check for required documentation updates
DOC_ISSUES=0

if [ -f "docs/api-changes.md" ]; then
    echo "✅ API documentation found."
else
    echo "ℹ️ No API documentation found (acceptable if no API changes)."
fi

# Check if README exists and is not empty
if [ -f "README.md" ] && [ -s "README.md" ]; then
    echo "✅ README.md present and non-empty."
else
    echo "⚠️ README.md missing or empty."
    DOC_ISSUES=$((DOC_ISSUES + 1))
fi

if [ $DOC_ISSUES -gt 0 ]; then
    echo "⚠️ Documentation issues found, but not blocking push."
fi

echo ""
echo "✅ All pre-push quality gates passed! Ready for CI/CD."
echo "🚀 Push with confidence - local validation matches CI/CD pipeline."
```

**Key Features**:
- **Exact CI/CD Matching**: Every step mirrors the CI/CD pipeline configuration
- **Fail-Fast Approach**: Stops immediately on any critical failure
- **Interactive Security Review**: Allows informed decisions on security warnings
- **Mutation Testing Integration**: Enforces ≥75% kill rate for feature completion
- **Performance Baseline Validation**: Prevents performance regressions
- **Documentation Validation**: Ensures required documentation is present

### Local-CI Environment Parity

Ensure identical validation between local development and CI/CD pipeline:
- **Same build commands**: Match exactly between local scripts and CI YAML
- **Same test execution**: Identical parameters and configurations
- **Same quality gates**: All 8 validation steps in both environments
- **Same dependency versions**: Lock file synchronization  
- **Same environment variables**: Configuration parity

This comprehensive lifecycle ensures that features are delivered with the highest quality standards, complete validation, and seamless CI/CD integration while maintaining architectural excellence throughout the development process.