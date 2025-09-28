# DW-DEVELOP: Outside-In TDD Implementation with Systematic Refactoring

## Overview
Execute DEVELOP wave of 5D-Wave methodology through Outside-In TDD implementation with double-loop architecture, production service integration, and systematic refactoring.

## Mandatory Pre-Execution Steps
1. **DISTILL Wave Completion**: Validate acceptance test suite and production service patterns
2. **Agent Coordination**: Activate test-first-developer (Devon) and systematic-refactorer
3. **Implementation Foundation**: Ensure test infrastructure and service registration complete

## Execution Flow

### Phase 1: Outside-In TDD Foundation
**Primary Agent**: test-first-developer (Devon)
**Command**: `*develop`

**Double-Loop TDD Architecture**:
```
🧪 DEVELOP WAVE - OUTSIDE-IN TDD IMPLEMENTATION

Research-validated double-loop architecture drives implementation:

┌─────────────────────────────────────────────────────────────────────────────┐
│ OUTER LOOP: Acceptance Test Driven Development (ATDD) - Customer View       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ INNER LOOP: Unit Test Driven Development (UTDD) - Developer View     │  │
│  │  🔴 RED → 🟢 GREEN → 🔵 REFACTOR                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘

Outside-In Implementation Workflow:
1. Failing E2E test (OUTER LOOP) - Business specification
2. Unit test inner loops (INNER LOOP) - Technical implementation
3. Continuous refactoring using six-level hierarchy
4. Production service integration mandatory
5. One E2E test at a time to prevent commit blocks
```

**Implementation Strategy**:
- Start with failing E2E test representing user-facing feature
- Step down to unit tests when E2E test fails
- Write minimal code to make unit tests pass
- Return to E2E test and verify progress
- Repeat until acceptance test passes naturally

### Phase 2: Production Service Integration Validation
**Agent Command**: `*validate-production`

**Mandatory Production Integration Patterns**:
```csharp
// STEP METHOD PRODUCTION SERVICE INTEGRATION
[When("user performs business action")]
public async Task WhenUserPerformsBusinessAction()
{
    // MANDATORY: Call production services via dependency injection
    var service = _serviceProvider.GetRequiredService<IBusinessService>();
    _result = await service.PerformBusinessActionAsync(_testData);
}

// SERVICE REGISTRATION VALIDATION
services.AddScoped<IBusinessService, BusinessService>();
services.AddScoped<IRepository, ProductionRepository>();

// FORBIDDEN: Business logic in test infrastructure
// Test infrastructure provides setup/teardown ONLY
// Business logic must reside in production services
```

**Production Integration Validation Checkpoints**:
- [ ] Every step method contains `GetRequiredService<T>()` calls
- [ ] Production interfaces exist before step implementation
- [ ] Test infrastructure delegates to production services
- [ ] Business logic implemented in production services, not test code
- [ ] Real system integration, not mocked components

### Phase 3: One E2E Test at a Time Implementation
**Implementation Workflow**:
```csharp
// PHASE 3A: Single E2E Test Active
[Test]
public async Task UserCanRegisterAndLogin_BasicFlow()
{
    // ACTIVE TEST - Currently being implemented through Outside-In TDD
    Given_RegisteredUserWithValidCredentials();
    await When_UserAttemptsToLogin();
    await Then_LoginSucceedsAndUserRedirectedToDashboard();
}

[Test]
[Ignore("Temporarily disabled until implementation - will enable one at a time to avoid commit blocks")]
public async Task UserCanUpdateProfile_WithValidation()
{
    // NEXT TEST - Will enable after first test passes
}

// PHASE 3B: Implementation Through Inner TDD Loops
[Test]
public void UserService_Should_AuthenticateUser_WhenCredentialsValid()
{
    // Unit test driving UserService implementation
    var userService = new UserService(_mockRepository.Object);
    var result = await userService.AuthenticateAsync(validCredentials);
    Assert.That(result.IsSuccess, Is.True);
}
```

**Commit Requirements - NO EXCEPTIONS**:
- [ ] **Active E2E test must pass** (not ignored)
- [ ] **All other tests must pass**
- [ ] **All quality gates must pass**
- [ ] **No skipped tests in execution**
- [ ] **Pre-commit hooks must pass completely**

### Phase 4: Systematic Refactoring Integration
**Secondary Agent**: systematic-refactorer
**Command**: `*refactor`

**Six-Level Refactoring Hierarchy** - Applied during GREEN phases:
```yaml
level_1_readability:
  timing: "After each GREEN phase"
  focus: "Comments, dead code, naming, magic strings/numbers"
  actions:
    - "Remove obsolete and how-comments, keep only why/what"
    - "Remove unused methods, classes, imports, variables"
    - "Extract constants with meaningful names"
    - "Reduce variable and method scope to minimum necessary"

level_2_complexity:
  timing: "After each GREEN phase"
  focus: "Method extraction, duplication elimination"
  actions:
    - "Extract methods with business-meaningful names"
    - "Eliminate code duplication through extraction and abstraction"

level_3_responsibilities:
  timing: "Sprint boundaries"
  focus: "Class responsibilities, coupling reduction"
  actions:
    - "Break down classes using Single Responsibility Principle"
    - "Move methods to classes they interact with most"
    - "Reduce coupling between classes"
    - "Add behavior to data-only classes"

level_4_abstractions:
  timing: "Sprint boundaries"
  focus: "Parameter objects, value objects, abstractions"
  actions:
    - "Create parameter objects or builders"
    - "Group related data into cohesive objects"
    - "Create value objects for domain concepts"
    - "Remove unnecessary delegation layers"

level_5_patterns:
  timing: "Release preparation"
  focus: "Strategic design patterns"
  actions:
    - "Switch Statements → Strategy Pattern"
    - "Dictionary/Hashmap → Strategy Pattern"
    - "State Pattern for complex state-dependent behavior"
    - "Command Pattern for operation encapsulation"

level_6_solid:
  timing: "Release preparation"
  focus: "Advanced architectural principles"
  actions:
    - "Refused Bequest → Liskov Substitution + Interface Segregation"
    - "Divergent Change → Single Responsibility Principle"
    - "Shotgun Surgery → Single Responsibility Principle"
    - "Speculative Generality → YAGNI Principle"
```

### Phase 5: Hexagonal Architecture Implementation
**Agent Command**: `*implement-story`

**Hexagonal Architecture Patterns**:
```csharp
// CORE DOMAIN (Business Logic - Technology Independent)
public class OrderService : IOrderService
{
    private readonly IOrderRepository _repository;
    private readonly IPaymentGateway _paymentGateway;
    private readonly INotificationService _notificationService;

    public async Task<OrderResult> PlaceOrderAsync(OrderRequest request)
    {
        // Pure business logic - no technology concerns
        var order = Order.Create(request.UserId, request.Items);

        if (!order.IsValid())
            return OrderResult.Failure("Invalid order data");

        var payment = await _paymentGateway.ProcessPaymentAsync(order.Total);
        if (!payment.IsSuccessful)
            return OrderResult.Failure("Payment failed");

        await _repository.SaveAsync(order);
        await _notificationService.SendConfirmationAsync(order);

        return OrderResult.Success(order.Id);
    }
}

// PRIMARY ADAPTER (Inbound - REST Controller)
[ApiController]
[Route("api/[controller]")]
public class OrderController : ControllerBase
{
    private readonly IOrderService _orderService;

    [HttpPost]
    public async Task<IActionResult> PlaceOrder([FromBody] PlaceOrderRequest request)
    {
        var result = await _orderService.PlaceOrderAsync(request.ToOrderRequest());
        return result.IsSuccess
            ? Ok(result.OrderId)
            : BadRequest(result.ErrorMessage);
    }
}

// SECONDARY ADAPTER (Outbound - Database Repository)
public class SqlOrderRepository : IOrderRepository
{
    private readonly ApplicationDbContext _context;

    public async Task SaveAsync(Order order)
    {
        _context.Orders.Add(order.ToEntity());
        await _context.SaveChangesAsync();
    }
}
```

### Phase 6: Continuous Quality Gates
**Agent Command**: `*check-quality-gates`

**Mandatory Quality Validation**:
```yaml
quality_gates:
  technical_validation:
    - "All acceptance tests passing with production service integration"
    - "Unit test coverage ≥80% for critical business logic"
    - "Integration tests validating cross-component functionality"
    - "Code review completion with architect approval"
    - "Static analysis and security scan completion"
    - "Performance testing under realistic load conditions"

  architecture_compliance:
    - "Hexagonal architecture pattern adherence"
    - "Component boundary respect and interface compliance"
    - "Production service integration in all step methods"
    - "Dependency injection and inversion of control"
    - "Clean separation of concerns"

  business_validation:
    - "All user stories implemented with acceptance criteria met"
    - "Business rules validated through production services"
    - "Domain language consistency throughout codebase"
    - "Business outcomes measurable and verifiable"
```

## Advanced Implementation Patterns

### NotImplementedException Scaffolding
**Research-Validated Pattern**:
```csharp
// SCAFFOLDING PATTERN - "Write the Code You Wish You Had"
public async Task<PaymentResult> ProcessPaymentAsync(decimal amount)
{
    throw new NotImplementedException(
        "Payment processing not yet implemented - driven by outside-in TDD"
    );
}

// IMPLEMENTATION PRESSURE MAINTAINED
[Test]
public async void PaymentService_Should_ProcessPayment_WhenAmountValid()
{
    // Test drives implementation of NotImplementedException
    var service = new PaymentService(_mockGateway.Object);

    // This will fail with NotImplementedException initially
    var result = await service.ProcessPaymentAsync(100.00m);

    Assert.That(result.IsSuccess, Is.True);
}
```

### Natural Test Progression
**Correct E2E Test Evolution**:
1. **Initial State**: E2E test fails with NotImplementedException
2. **Unit Development**: Inner TDD loops implement production services
3. **Integration**: Services integrated through dependency injection
4. **Natural Success**: E2E test passes when implementation complete
5. **Next E2E**: Enable next test and repeat cycle

## Environment-Adaptive Testing Strategy

### Local Development Environment
**Configuration**: In-memory components for fast feedback (~100ms)
```csharp
// LOCAL DEVELOPMENT - Fast feedback with in-memory components
services.AddDbContext<ApplicationDbContext>(options =>
    options.UseInMemoryDatabase("TestDatabase"));
services.AddScoped<IPaymentGateway, InMemoryPaymentGateway>();
services.AddScoped<IEmailService, InMemoryEmailService>();
```

### CI/CD Pipeline Environment
**Configuration**: Production-like infrastructure (~2-5s)
```csharp
// CI/CD PIPELINE - Production-like validation
services.AddDbContext<ApplicationDbContext>(options =>
    options.UseSqlServer(connectionString));
services.AddScoped<IPaymentGateway, TestPaymentGateway>();
services.AddScoped<IEmailService, TestEmailService>();
```

## Build and Test Protocol

### Mandatory Build/Test Cycle
**After every RED-GREEN-REFACTOR cycle**:
```bash
# 1. BUILD: Exercise most recent logic
dotnet build --configuration Release --no-restore

# 2. TEST: Run tests with fresh build
dotnet test --configuration Release --no-build --verbosity minimal

# Continue TDD cycle or rollback if unexpected failure
```

## Output Artifacts

### Primary Implementation Deliverables
1. **PRODUCTION_CODE/** - Complete production implementation with hexagonal architecture
2. **ACCEPTANCE_TESTS/** - All acceptance tests passing with production service integration
3. **UNIT_TESTS/** - Comprehensive unit test suite with behavior-driven design
4. **INTEGRATION_TESTS/** - Cross-component integration validation
5. **REFACTORED_CODEBASE** - Code quality improvements through six-level hierarchy

### Quality Assurance Documentation
1. **IMPLEMENTATION_STATUS.md** - Current implementation progress and quality metrics
2. **REFACTORING_LOG.md** - Systematic refactoring improvements and rationale
3. **QUALITY_METRICS.md** - Test coverage, code quality, and performance metrics
4. **ARCHITECTURE_COMPLIANCE.md** - Hexagonal architecture adherence validation
5. **PRODUCTION_INTEGRATION_REPORT.md** - Service integration verification

### Technical Documentation
1. **API_DOCUMENTATION.md** - Complete API contracts and integration guides
2. **DOMAIN_MODEL.md** - Final domain model with business rules
3. **DEPLOYMENT_GUIDE.md** - Production deployment procedures and requirements
4. **OPERATIONAL_RUNBOOK.md** - Support and maintenance procedures

## Quality Gates

### Implementation Quality Validation
- [ ] **Acceptance Test Coverage**: All user stories have passing acceptance tests
- [ ] **Production Service Integration**: All step methods call real production services
- [ ] **Unit Test Coverage**: ≥80% coverage for business logic with behavior focus
- [ ] **Integration Test Validation**: Cross-component functionality verified
- [ ] **Architecture Compliance**: Hexagonal architecture patterns implemented

### Code Quality Validation
- [ ] **Refactoring Levels Applied**: Progressive refactoring through six-level hierarchy
- [ ] **Business Naming**: Domain language used throughout implementation
- [ ] **Clean Code Standards**: No how-comments, clear intent, minimal complexity
- [ ] **SOLID Principles**: Advanced architectural principles applied
- [ ] **Technical Debt Management**: Systematic debt elimination

### ATDD Compliance Validation
- [ ] **Outside-In Implementation**: E2E tests drive development through inner loops
- [ ] **One E2E at a Time**: Sequential implementation preventing commit blocks
- [ ] **Natural Progression**: Tests pass through implementation, not modification
- [ ] **Production Reality**: Real system integration, minimal test doubles
- [ ] **Customer-Developer-Tester**: Continuous collaboration maintained

## Handoff to DEMO Wave

### Handoff Package Preparation
**Content for feature-completion-coordinator (Dakota)**:
```yaml
implementation_package:
  working_implementation: "Complete production codebase with hexagonal architecture"
  test_coverage: "Comprehensive test suite with acceptance/unit/integration tests"
  production_integration: "All services integrated and calling real production code"
  architecture_compliance: "Verified hexagonal architecture with clean boundaries"
  quality_metrics: "Code quality metrics and refactoring improvements"
  operational_knowledge: "Deployment procedures and operational documentation"

quality_validation:
  all_tests_passing: "100% test success rate with production service integration"
  technical_debt_assessment: "Systematic refactoring completed through six levels"
  code_quality_metrics: "Static analysis, complexity, and maintainability scores"
  performance_validation: "Performance testing under realistic conditions"
  security_assessment: "Security implementation and vulnerability scanning"

business_value_evidence:
  acceptance_criteria_met: "All user stories completed with stakeholder validation"
  business_rules_implemented: "Domain logic implemented with business validation"
  user_experience_validated: "UX validation through working acceptance tests"
  business_outcomes_measurable: "Metrics and success criteria established"
```

### Production Readiness Preparation
**Ready for DEMO Wave**:
- Working implementation with production service integration
- Complete test coverage validating business outcomes
- Architecture compliance and quality metrics verified
- Operational procedures and documentation complete
- Business value demonstrable through working software

## Success Criteria
- Complete implementation through Outside-In TDD methodology
- All acceptance tests passing with production service integration
- Systematic refactoring applied through six-level hierarchy
- Hexagonal architecture implemented with clean boundaries
- One-at-a-time E2E test strategy executed successfully
- Production service integration validated and operational
- Quality gates passed with comprehensive validation
- Clear handoff package prepared for DEMO wave

## Failure Recovery
If DEVELOP wave fails:
1. **Test Failures**: Rollback to last green state and resume TDD cycle
2. **Integration Issues**: Validate service registration and dependency injection
3. **Architecture Violations**: Refactor to restore hexagonal boundaries
4. **Quality Gate Failures**: Address quality issues before proceeding
5. **Production Integration Problems**: Validate service interfaces and implementations

## Next Command
**Command**: `*dw-demo`
**Agent**: feature-completion-coordinator (Dakota)
**Wave**: DEMO