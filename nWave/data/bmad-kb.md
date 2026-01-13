# BMAD Knowledge Base - nWave Methodology

## Overview

This is the comprehensive knowledge base for the BMAD nWave expansion pack, specializing in Acceptance Test Driven Development (ATDD) with visual architecture lifecycle management. The nWave methodology implements a systematic DISCUSS→DESIGN→DISTILL→DEVELOP→DEMO approach with customer-developer-tester collaboration, Outside-In TDD, and production service integration patterns.

### Key Features of nWave Methodology

- **ATDD Foundation**: Customer-developer-tester collaboration throughout all phases
- **Visual Architecture Lifecycle**: Comprehensive stakeholder communication through visual documentation
- **Outside-In TDD**: Double-loop architecture with production service integration
- **Systematic Quality**: Progressive refactoring and evidence-based improvement
- **Production Focus**: Real system integration and business value delivery

### Methodology Focus

- **Target Approach**: ATDD-driven development with hexagonal architecture
- **Wave Strategy**: Sequential phases with cross-wave coordination and visual documentation
- **Development Philosophy**: Business-driven development with customer collaboration and real system validation
- **Quality Framework**: Test-driven development with systematic refactoring and production service integration
- **Architecture**: Hexagonal architecture with ports/adapters and visual stakeholder communication

### When to Use nWave Methodology

- **Customer Collaboration Projects**: Strong stakeholder involvement and business domain complexity
- **Quality-Critical Systems**: Production readiness and systematic quality requirements
- **Visual Communication Needs**: Multiple stakeholder groups requiring architectural understanding
- **ATDD Adoption**: Teams adopting or improving acceptance test driven development practices
- **Legacy Modernization**: Brownfield projects requiring systematic improvement and stakeholder alignment

## Core Methodology Principles

### 1. ATDD Foundation (Acceptance Test Driven Development)

**Customer-Developer-Tester Collaboration**:

- **Three Amigos Approach**: Regular collaboration between business stakeholders, developers, and testers
- **Business Language Preservation**: Domain terminology maintained from requirements through implementation
- **Specification by Example**: Concrete examples drive understanding and validation
- **Living Documentation**: Acceptance tests serve as current system documentation

**Implementation Patterns**:

```yaml
atdd_collaboration:
  customer_role:
    - Business requirement definition and validation
    - Domain expertise and business rule clarification
    - Acceptance criteria approval and business value confirmation

  developer_role:
    - Technical feasibility assessment and implementation
    - Business requirement translation to technical solution
    - Production service integration and system implementation

  tester_role:
    - Test scenario design and automation
    - Quality perspective and edge case identification
    - Validation framework and acceptance criteria verification
```

### 2. nWave Sequential Methodology

**DISCUSS Wave - Requirements and Collaboration**:

- **Stakeholder Alignment**: Customer-developer-tester collaboration establishment
- **Business Domain Understanding**: Domain modeling and ubiquitous language development
- **Requirements Engineering**: User stories with acceptance criteria in Given-When-Then format
- **Risk Assessment**: Technical and business risk identification with mitigation strategies

**DESIGN Wave - Architecture with Visual Communication**:

- **Hexagonal Architecture**: Ports and adapters design with clean business logic separation
- **Visual Architecture Lifecycle**: Stakeholder-specific diagrams and evolution tracking
- **Technology Selection**: ATDD-compatible technology stack with production service integration
- **Component Boundaries**: Clear separation of concerns and integration patterns

**DISTILL Wave - Acceptance Test Creation**:

- **Given-When-Then Scenarios**: Business-focused acceptance test creation
- **Production Service Integration Patterns**: Real system integration through dependency injection
- **One-E2E-at-a-Time Strategy**: Sequential test implementation to prevent commit blocks
- **Business Validation Criteria**: Measurable success criteria and KPI integration

**DEVELOP Wave - Outside-In TDD Implementation**:

- **Double-Loop TDD**: ATDD outer loop driving UTDD inner loop implementation
- **Production Service Integration**: Step methods calling real production services via dependency injection
- **Systematic Refactoring**: Progressive Level 1-6 refactoring hierarchy application
- **Business-Driven Naming**: Domain language preservation throughout technical implementation

**DEMO Wave - Production Readiness and Stakeholder Validation**:

- **Production Deployment**: Operational system with monitoring and support procedures
- **Stakeholder Demonstration**: Business value validation with customer feedback integration
- **Operational Knowledge Transfer**: Support team training and maintenance procedure documentation
- **Business Impact Measurement**: ROI validation and success metric achievement

### 3. Visual Architecture Lifecycle Management

**Stakeholder-Specific Communication**:

- **Executive Views**: Strategic overview, investment analysis, and business value visualization
- **Technical Views**: Implementation details, integration patterns, and architectural decisions
- **Operational Views**: Deployment topology, monitoring architecture, and support procedures
- **Business Views**: Process workflows, capability mapping, and customer journey visualization

**Implementation Reality Synchronization**:

- **Automated Generation**: Code-to-diagram and configuration-to-diagram automation
- **Continuous Validation**: Real-time accuracy checking and divergence detection
- **Evolution Tracking**: Version-controlled diagram changes with impact analysis
- **Stakeholder Communication**: Change notification and approval workflows

### 4. Production Service Integration Patterns

**Mandatory Integration Patterns**:

```csharp
// REQUIRED: Step methods must call production services
public async Task UserRegistersNewAccount()
{
    var userService = _serviceProvider.GetRequiredService<IUserService>();
    var result = await userService.RegisterUserAsync(_currentUser);

    if (!result.IsSuccess)
    {
        throw new InvalidOperationException($"Registration failed: {result.ErrorMessage}");
    }
}

// FORBIDDEN: Business logic in step methods
public async Task UserRegistersNewAccount()
{
    // ❌ This is test infrastructure business logic
    _testDatabase.Users.Add(_currentUser);
    _testDatabase.SaveChanges();
}
```

**Anti-Pattern Prevention**:

- **Test Infrastructure Boundary**: Test environment limited to setup/teardown only
- **Production Service Delegation**: All business operations through production services
- **Minimal Mocking**: Mocks only for external system boundaries
- **Real System Integration**: Database and service operations use actual implementations

## Technology Integration Patterns

### .NET/C# Integration

**Dependency Injection for ATDD**:

```csharp
// Production service registration
services.AddScoped<IUserService, UserService>();
services.AddScoped<IOrderService, OrderService>();
services.AddDbContext<BusinessDbContext>(options =>
    options.UseSqlServer(connectionString));

// Test configuration with production services
services.AddScoped<IEmailService, TestEmailService>(); // Only external boundaries
```

**Hexagonal Architecture Implementation**:

```csharp
// Business logic (hexagon center)
public class UserService : IUserService
{
    private readonly IUserRepository _repository;
    private readonly IDomainEventPublisher _eventPublisher;

    // Business logic without infrastructure dependencies
}

// Infrastructure adapters (hexagon edges)
public class SqlUserRepository : IUserRepository
{
    // Database-specific implementation
}
```

### React/TypeScript Integration

**Component Architecture for ATDD**:

```typescript
// Business-focused component with testable patterns
export const UserRegistrationForm: FC<Props> = ({ onSubmit }) => {
  // Component logic focuses on business workflow
  const handleRegistration = async (userData: UserRegistrationData) => {
    // Business validation and workflow
    await onSubmit(userData);
  };
};

// ATDD integration through business service calls
export const UserRegistrationContainer: FC = () => {
  const userService = useService<IUserService>("UserService");

  const handleUserRegistration = async (userData: UserRegistrationData) => {
    // Production service integration
    await userService.registerUser(userData);
  };
};
```

### Node.js/Express Integration

**Service Architecture for ATDD**:

```javascript
// Business service layer
class UserService {
  constructor(userRepository, eventPublisher) {
    this.userRepository = userRepository;
    this.eventPublisher = eventPublisher;
  }

  async registerUser(userData) {
    // Business logic without infrastructure dependencies
    const user = await this.userRepository.create(userData);
    await this.eventPublisher.publish(new UserRegistered(user));
    return user;
  }
}

// ATDD step method integration
class UserRegistrationSteps {
  constructor(serviceProvider) {
    this.serviceProvider = serviceProvider;
  }

  async userRegistersWithValidData() {
    const userService = this.serviceProvider.get("UserService");
    await userService.registerUser(this.currentUserData);
  }
}
```

## ATDD Implementation Patterns

### Given-When-Then Structure

**Business-Focused Scenarios**:

```gherkin
Feature: User Account Registration
  As a potential customer
  I want to register for an account
  So that I can access premium features

Scenario: Successful registration with valid information
  Given I am a new user with valid registration information
  When I submit the registration form
  Then I should receive a confirmation email
  And I should be able to log in with my credentials
  And my account should be marked as active
```

**Production Service Integration**:

```csharp
[Given("I am a new user with valid registration information")]
public void GivenNewUserWithValidInformation()
{
    _currentUser = TestDataBuilder.CreateValidUser();
    // Setup only - no business logic
}

[When("I submit the registration form")]
public async Task WhenSubmitRegistrationForm()
{
    // REQUIRED: Call production service
    var userService = _serviceProvider.GetRequiredService<IUserService>();
    _registrationResult = await userService.RegisterUserAsync(_currentUser);
}

[Then("I should receive a confirmation email")]
public async Task ThenShouldReceiveConfirmationEmail()
{
    // Validate through production services
    var emailService = _serviceProvider.GetRequiredService<IEmailService>();
    var sentEmails = await emailService.GetSentEmailsAsync(_currentUser.Email);

    sentEmails.Should().ContainSingle(email =>
        email.Subject.Contains("confirmation"));
}
```

### Outside-In TDD Implementation

**Double-Loop Architecture**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ OUTER LOOP: Acceptance Test Driven Development (ATDD) - Customer View       │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │ INNER LOOP: Unit Test Driven Development (UTDD) - Developer View     │  │
│  │  🔴 RED → 🟢 GREEN → 🔵 REFACTOR                                      │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
```

**Implementation Process**:

1. **Start with failing E2E test**: Business scenario from customer perspective
2. **Step down to unit tests**: When E2E test fails, write unit tests for missing behavior
3. **Implement minimal production code**: Make unit tests pass
4. **Refactor continuously**: Improve design while keeping tests green
5. **Return to E2E test**: Verify progress toward E2E test success
6. **Repeat until E2E passes**: Complete feature implementation

### NotImplementedException Scaffolding

**Scaffolding Pattern for Interface Discovery**:

```csharp
// Step method calls desired production service interface
[When("I submit the registration form")]
public async Task WhenSubmitRegistrationForm()
{
    var userService = _serviceProvider.GetRequiredService<IUserService>();
    _result = await userService.RegisterUserAsync(_currentUser);
}

// Interface implementation starts with scaffolding
public class UserService : IUserService
{
    public async Task<RegistrationResult> RegisterUserAsync(User user)
    {
        throw new NotImplementedException(
            "User registration business logic - validate user data, check for duplicates, create account");
    }
}
```

## Visual Architecture Patterns

### Stakeholder-Specific Diagrams

**Executive Dashboard Components**:

- **System Context**: Business value and strategic alignment
- **Investment Analysis**: Technology ROI and resource allocation
- **Risk Heat Map**: Risk mitigation and compliance status
- **Strategic Roadmap**: Timeline and milestone tracking

**Technical Documentation Components**:

- **Component Architecture**: Detailed system structure and patterns
- **Sequence Diagrams**: Interaction flows and API specifications
- **Deployment Architecture**: Infrastructure and topology
- **Integration Patterns**: Service integration and data flows

**Operational Runbook Components**:

- **Infrastructure Topology**: Deployment and monitoring view
- **Monitoring Architecture**: Observability and alerting
- **Security Controls**: Security implementation and compliance
- **Support Procedures**: Incident response and maintenance

### Automated Generation Patterns

**Code-to-Diagram Generation**:

```yaml
generation_pipeline:
  source_analysis:
    - Parse source code for component structure
    - Extract interface definitions and dependencies
    - Identify design patterns and architectural styles
    - Map business logic to architectural components

  diagram_synthesis:
    - Apply stakeholder-specific templates
    - Generate multiple views from unified model
    - Ensure consistency across diagram types
    - Create interactive and accessible formats
```

## Systematic Refactoring Hierarchy

### Level 1-2: Foundation (Applied Continuously)

- **Comments**: Remove how-comments, keep only why/what
- **Dead Code**: Remove unused methods, classes, variables
- **Magic Strings/Numbers**: Extract constants with meaningful names
- **Long Methods**: Extract methods with business-meaningful names
- **Duplicated Code**: Eliminate duplication through abstraction

### Level 3-4: Organization (Applied at Sprint Boundaries)

- **Class Responsibilities**: Apply Single Responsibility Principle
- **Feature Envy**: Move methods to classes they interact with most
- **Parameter Objects**: Group related parameters into cohesive objects
- **Data Clumps**: Create value objects for related data

### Level 5-6: Advanced Patterns (Applied at Release Preparation)

- **Strategy Pattern**: Replace switch statements with polymorphism
- **State Pattern**: Handle complex state-dependent behavior
- **SOLID Compliance**: Resolve violations of SOLID principles
- **Design Pattern Application**: Apply appropriate architectural patterns

## Production Readiness Patterns

### Monitoring and Observability

**Comprehensive Monitoring Stack**:

```yaml
observability_architecture:
  metrics:
    - Business KPIs and success criteria
    - Application performance metrics
    - Infrastructure health monitoring
    - User experience and adoption metrics

  logging:
    - Structured logging with correlation IDs
    - Business event logging and audit trails
    - Error tracking and alerting
    - Compliance and regulatory logging

  tracing:
    - Distributed tracing for complex workflows
    - User journey tracking and analysis
    - Performance bottleneck identification
    - Service dependency mapping
```

### Deployment and Operations

**Production Deployment Patterns**:

- **Blue-Green Deployment**: Zero-downtime deployment with quick rollback
- **Canary Releases**: Gradual rollout with performance monitoring
- **Feature Flags**: Controlled feature activation and A/B testing
- **Infrastructure as Code**: Automated provisioning and configuration

**Operational Excellence**:

- **Runbook Automation**: Automated incident response and recovery
- **Capacity Planning**: Predictive scaling and resource optimization
- **Security Monitoring**: Continuous security validation and threat detection
- **Business Continuity**: Disaster recovery and backup automation

## Best Practices and Guidelines

### ATDD Best Practices

1. **Customer Collaboration**:
   - Schedule regular three-amigos sessions
   - Use example mapping for requirements clarification
   - Maintain customer involvement throughout development
   - Validate business value delivery continuously

2. **Specification Quality**:
   - Write tests in business language
   - Focus on business outcomes, not technical implementation
   - Use concrete examples to clarify abstract requirements
   - Maintain traceability from business objectives to acceptance criteria

3. **Production Integration**:
   - Always call production services in step methods
   - Limit test infrastructure to setup/teardown only
   - Use real implementations over mocks wherever possible
   - Validate business behavior through actual system execution

### Visual Architecture Best Practices

1. **Stakeholder Communication**:
   - Create audience-specific views and presentations
   - Use business language in diagrams for business stakeholders
   - Provide technical detail for implementation teams
   - Include operational procedures for support teams

2. **Implementation Synchronization**:
   - Automate diagram generation from code and configuration
   - Validate diagram accuracy regularly
   - Track architectural evolution and changes
   - Communicate changes to affected stakeholders

3. **Evolution Management**:
   - Version control all architectural diagrams
   - Maintain architectural baselines and milestones
   - Document architectural decisions and rationale
   - Analyze architectural trends and patterns

### Production Service Integration Best Practices

1. **Service Architecture**:
   - Design services for both production use and test integration
   - Use dependency injection for service access in tests
   - Implement hexagonal architecture with clear boundaries
   - Separate business logic from infrastructure concerns

2. **Test Integration**:
   - Call production services through \_serviceProvider.GetRequiredService<T>()
   - Avoid business logic in test infrastructure
   - Use minimal mocking limited to external system boundaries
   - Validate end-to-end business workflows through real services

3. **Quality Assurance**:
   - Implement static analysis for production service integration patterns
   - Monitor test-production service interaction at runtime
   - Validate architectural compliance through automated checks
   - Maintain comprehensive integration test coverage

## Common Pitfalls and Anti-Patterns

### ATDD Anti-Patterns to Avoid

1. **Customer Disconnection**: Developing without regular customer feedback and validation
2. **Technical Language Creep**: Replacing business language with technical jargon in tests
3. **Test-Code Disconnect**: Writing tests that don't drive actual implementation
4. **Specification Gaps**: Incomplete or ambiguous acceptance criteria
5. **Mock Overuse**: Excessive mocking instead of real system integration

### Visual Architecture Anti-Patterns to Avoid

1. **Diagram-Reality Divergence**: Visual documentation not reflecting actual implementation
2. **Stakeholder Confusion**: Diagrams not understandable by target audiences
3. **Update Lag**: Diagrams not keeping pace with system changes
4. **Over-Engineering Visualization**: Too much detail hindering communication
5. **Tool Complexity**: Diagram tools too complex for stakeholder adoption

### Production Service Integration Anti-Patterns to Avoid

1. **Test Infrastructure Business Logic**: Implementing business logic in test support code
2. **Service Bypass**: Step methods not calling actual production services
3. **Excessive Mocking**: Over-reliance on mocks instead of real service integration
4. **Test-Only Code Paths**: Code paths that only execute in test environment
5. **Configuration Mismatch**: Test environment not production-like enough

## Success Metrics and Validation

### ATDD Success Metrics

- **Customer Satisfaction**: ≥90% stakeholder satisfaction with collaboration and outcomes
- **Business Alignment**: 100% of features traceable to business requirements
- **Test Automation**: ≥95% of acceptance criteria automated and passing
- **Production Integration**: 100% of step methods calling production services

### Visual Architecture Success Metrics

- **Stakeholder Comprehension**: ≥95% stakeholder understanding of visual architecture
- **Diagram Accuracy**: ≥98% accuracy between diagrams and implementation
- **Communication Effectiveness**: Stakeholder decisions enabled by visual architecture
- **Evolution Tracking**: Architectural changes properly communicated and documented

### Production Readiness Success Metrics

- **System Reliability**: ≥99.9% uptime with comprehensive monitoring
- **Business Value**: Measurable achievement of business success criteria
- **Operational Excellence**: Support team confident in system maintenance
- **User Adoption**: ≥80% target user adoption with positive engagement

This knowledge base provides the foundation for effective software development using the nWave methodology with comprehensive ATDD integration, visual architecture lifecycle management, and production service integration patterns for business value delivery and operational excellence.
