# Enhanced Mikado Method Usage Guide

## Overview

The Enhanced Mikado refactoring specialist provides revolutionary improvements to systematic refactoring through discovery-tracking commits, exhaustive exploration, and concrete node specifications.

## Key Features

### 🔍 Discovery-Tracking Commits
- **Commit after every dependency discovery** for complete audit trail
- **Preserve exploration history** in git log for stakeholder communication
- **Enable interrupt/resume capability** at any discovery point
- **Create comprehensive audit trail** for refactoring decisions

### 🔬 Exhaustive Exploration Protocol
- **Continue exploration until NO new dependencies emerge**
- **Test every apparent leaf** to discover hidden dependencies
- **Distinguish false leaves from true leaves** through systematic testing
- **Map complete dependency landscape** before execution

### 🎯 Concrete Node Specification
- **Method-level specificity**: `ClassName.MethodName(parameter types) → ReturnType`
- **File locations**: `src/Services/UserService.cs, line 45`
- **Exact implementation details**: Parameter names, types, constraints
- **Actionable nodes**: Ready for immediate implementation

### ⚖️ Imperative Directive Compliance
- **Mandatory execution requirements**: All directives are REQUIRED and NON-NEGOTIABLE
- **YOU MUST/SHALL/WILL language**: Ensures reliable agent behavior
- **Comprehensive quality gates**: 100% green tests throughout all phases

## Usage Examples

### Basic Enhanced Mikado Refactoring

```bash
# Apply repository pattern to legacy controller
/cai:refactor "OrderController" --mikado-enhanced --validate

# Modernize authentication system with discovery tracking
/cai:refactor "authentication-system" --mikado-enhanced

# Systematic SOLID principles application
/cai:refactor "user-management" --mikado-enhanced --validate
```

### Complex Architectural Refactoring

```bash
# Extract microservices from monolith
/cai:refactor "payment-processing" --mikado-enhanced --level 5-6

# Legacy database integration modernization
/cai:refactor "data-access-layer" --mikado-enhanced --parallel-change
```

## Enhanced Process Workflow

### Phase 1: Goal Definition and Business Value Focus

**Input Example**:
```
Goal: Replace direct database calls in OrderController with repository pattern
```

**Enhanced Agent Process**:
1. **Formulates specific architectural objective** with business value
2. **Documents goal for stakeholder communication** and progress tracking
3. **Ensures goal is concrete enough** to know when completed

**Output Example**:
```
Business Goal: Customer orders are managed through clean repository interface
for improved testability and maintainability
```

### Phase 2: Discovery-Tracking Exploration

**Agent Process**:
1. **Attempts naive implementation** of repository pattern
2. **Captures ALL compilation and test failures** immediately
3. **Creates concrete prerequisite nodes** with method-level specificity
4. **Commits discovery with mandatory format**:
   ```bash
   git commit -m "Discovery: OrderController.GetOrder(int id) requires IOrderRepository.GetOrderById(int) method in src/Repositories/IOrderRepository.cs"
   ```
5. **Reverts ALL changes** to maintain clean state
6. **Repeats until NO new dependencies** discovered across ALL leaves

**Example Discovery Commits**:
```bash
"Discovery: SqlOrderRepository needs IDbContext dependency - verify registration in Startup.cs ConfigureServices"
"Discovery: Order entity missing validation attributes for repository pattern implementation"
"Discovery: False leaf - IOrderRepository creation blocked by missing Order.IsValid() method in src/Models/Order.cs"
"Discovery: No new dependencies found - exploration complete for repository pattern area"
"Ready: True leaves identified - 3 leaves ready for execution"
```

### Phase 3: Concrete Tree Construction

**Example Enhanced Tree Structure**:
```
Goal: Replace direct database calls in OrderController with repository pattern
├── Update OrderController constructor to use IOrderRepository
│   ├── Implement SqlOrderRepository : IOrderRepository
│   │   ├── Create IOrderRepository interface
│   │   │   ├── Define GetOrderById(int orderId) → Order? method signature
│   │   │   ├── Define SaveOrder(Order order) → Task method signature
│   │   │   └── Define DeleteOrder(int orderId) → Task<bool> method signature
│   │   ├── Add constructor SqlOrderRepository(IDbContext context)
│   │   │   └── Verify IDbContext is registered in DI container
│   │   │       └── Add services.AddDbContext<ApplicationDbContext>() in Startup.cs
│   │   ├── Implement GetOrderById method
│   │   │   ├── Add using statement for System.Linq in SqlOrderRepository.cs
│   │   │   └── Handle null order case with OrderNotFoundException
│   │   │       └── Create OrderNotFoundException class in src/Exceptions/OrderNotFoundException.cs
│   │   │           ├── Inherit from Exception base class
│   │   │           ├── Add constructor OrderNotFoundException(string message) : base(message)
│   │   │           └── Add constructor OrderNotFoundException(int orderId) : base($"Order with ID {orderId} not found")
│   │   ├── Implement SaveOrder method
│   │   │   ├── Add context.Orders.Update(order) call
│   │   │   └── Add await context.SaveChangesAsync() with error handling
│   │   │       └── Wrap in try-catch for DbUpdateException
│   │   └── Implement DeleteOrder method
│   │       ├── Find order by ID using context.Orders.FirstOrDefaultAsync(o => o.Id == orderId)
│   │       ├── Remove from context if found using context.Orders.Remove(order)
│   │       ├── Call await context.SaveChangesAsync()
│   │       └── Return bool indicating success (order != null)
│   ├── Register IOrderRepository in DI container
│   │   └── Add services.AddScoped<IOrderRepository, SqlOrderRepository>() in Startup.cs ConfigureServices line 45
│   └── Remove IDbContext _context field from OrderController
│       └── Update OrderController constructor to remove IDbContext context parameter
└── Update GetOrder method implementation
    └── Replace context.Orders.FirstOrDefault(o => o.Id == id) with await _repository.GetOrderById(id)
```

### Phase 4: Execution with Implementation Tracking

**True Leaf Implementation Process**:
1. **Select ONLY true leaves** with zero confirmed prerequisites
2. **Implement minimal possible change** (one method, one property, one line)
3. **Validate immediately** with full test execution and compilation
4. **Commit implementation**:
   ```bash
   git commit -m "Implement: IOrderRepository.GetOrderById(int orderId) method signature - interface prerequisite complete"
   ```
5. **Update tree marking node as completed** with timestamp
6. **Proceed bottom-up** to next confirmed true leaf

**Example Implementation Commits**:
```bash
"Implement: IOrderRepository.GetOrderById(int orderId) method signature - interface prerequisite complete"
"Implement: SqlOrderRepository.GetOrderById(int orderId) method with null handling - implementation prerequisite complete"
"Implement: OrderNotFoundException class in src/Exceptions/ - error handling prerequisite complete"
"Complete: OrderController repository pattern refactoring - all prerequisites satisfied"
```

## Quality Assurance

### Mandatory Green Bar Discipline
- **100% green tests throughout all phases**
- **Rollback immediately on ANY test failure**
- **Validate architectural compliance at each completion**
- **Preserve component boundaries and interfaces**

### Change Size Limits
- **One conceptual modification per commit**
- **Minimal possible change per step**
- **Independent testability for each step**
- **Atomic changes - no mixed refactoring and features**

### Safety and Validation Requirements
- **All tests passing before starting any exploration**
- **Architecture boundaries clearly defined and documented**
- **Git repository in clean state for commit tracking**
- **Comprehensive test coverage for refactoring target**

## Advanced Usage Patterns

### SOLID Principle Application

```bash
# Apply Single Responsibility Principle with discovery tracking
/cai:refactor "OrderController" --mikado-enhanced --level 6

# Goal: Extract multiple responsibilities from OrderController
# Enhanced Process:
# 1. Exploration Phase: Attempt SRP extraction → Discover all hidden dependencies → Commit each discovery
# 2. Dependency Mapping: Create concrete nodes for each responsibility extraction requirement
# 3. Execution Phase: Implement true leaves one by one with implementation commits
# 4. Validation: Ensure each extracted class has single, well-defined responsibility
```

### Design Pattern Introduction

```bash
# Replace switch statement with Strategy pattern
/cai:refactor "PaymentProcessor" --mikado-enhanced --pattern strategy

# Goal: Replace switch statement with Strategy pattern in PaymentProcessor
# Enhanced Process:
# 1. Exploration Phase: Attempt strategy extraction → Test every apparent strategy leaf → Commit discoveries
# 2. Complete Mapping: Build full dependency tree including interface, implementations, and factory
# 3. Execution Phase: Implement strategies bottom-up with mechanical precision
# 4. Migration: Replace switch cases one by one using parallel change pattern
```

### Hexagonal Architecture Boundary Refinement

```bash
# Extract domain service from anemic domain model
/cai:refactor "OrderManagement" --mikado-enhanced --architecture hexagonal

# Goal: Extract domain service from anemic domain model in OrderManagement
# Enhanced Process:
# 1. Exploration Phase: Attempt domain service extraction → Discover all business logic locations → Commit findings
# 2. Concrete Specification: Define exact method signatures and responsibility boundaries
# 3. Execution Phase: Move business logic incrementally with implementation tracking
# 4. Validation: Ensure clean separation between domain and infrastructure layers
```

## Troubleshooting

### Common Issues

#### Exploration Never Terminates
**Symptoms**: Continuous discovery of new dependencies
**Solution**: Check for circular dependencies, validate goal specificity
**Enhanced Agent Response**: Applies cycle detection and provides concrete breaking points

#### Abstract Node Descriptions
**Symptoms**: Vague tree nodes like "refactor authentication"
**Solution**: Enhanced agent enforces method-level specificity automatically
**Example Fix**: "Create UserService.HashPassword(string password) method returning string in src/Services/UserService.cs"

#### Test Failures During Execution
**Symptoms**: Tests break during implementation phase
**Solution**: Enhanced agent enforces green bar discipline with automatic rollback
**Recovery**: Automatic revert to last green state and re-evaluation of approach

### Best Practices

#### Before Starting
- Ensure comprehensive test coverage (≥80% for critical paths)
- Commit current working state with descriptive message
- Document current architecture and component boundaries
- Validate git repository is in clean state

#### During Refactoring
- Trust the enhanced agent's discovery process
- Review discovery commits for architectural insights
- Monitor progress through git log and tree updates
- Validate each implementation commit maintains green tests

#### After Completion
- Review complete git history for learning extraction
- Validate architectural goal achievement with evidence
- Document lessons learned for future similar refactorings
- Share discovery patterns with team for organizational learning

## Integration with ATDD Workflow

### Wave 4 Integration (Development Phase)

```bash
# Integrate enhanced Mikado with Outside-In TDD
/cai:develop "STORY-AUTH-001" --refactor-method mikado-enhanced

# Process:
# 1. Acceptance test fails due to architectural constraints
# 2. Enhanced Mikado agent systematically removes architectural blockers
# 3. Discovery commits track architectural evolution
# 4. Implementation commits show incremental progress
# 5. Final acceptance test passes naturally through improved architecture
```

### Continuous Refactoring Integration

```bash
# Progressive improvement during development cycles
/cai:refactor @src/ --mikado-enhanced --level 1-3 --iterative

# Pattern:
# - Level 1-2 refactoring after each TDD green phase
# - Level 3-4 refactoring at story completion
# - Level 5-6 refactoring with enhanced Mikado at epic completion
```

## Success Metrics

### Enhanced Mikado Refactoring Report Template

The enhanced agent automatically generates comprehensive reports including:

#### Discovery Phase Results
- **Total Discovery Commits**: Count with git log references
- **Hidden Dependencies Found**: Count and examples of false leaves
- **Exploration Cycles Required**: Count until stable tree achieved
- **Complete Dependency Tree Structure**: Concrete tree with unlimited nesting depth

#### Execution Phase Results
- **True Leaves Implemented**: Count in bottom-up order
- **Implementation Commits**: Count with git log references
- **Test Executions**: Count with 100% green requirement maintained
- **Execution Sequence**: Detailed implementation order with commit references

#### Enhanced Protocol Compliance
- ✅ **Discovery-Tracking Commits**: Complete audit trail preserved
- ✅ **Exhaustive Exploration**: No hidden dependencies remain
- ✅ **Concrete Node Specification**: Method-level implementation guidance
- ✅ **Imperative Directive Compliance**: All MUST/SHALL requirements followed

#### Stakeholder Communication Value
- **Progress Visibility**: Git log provides real-time complexity understanding
- **Business Value Demonstration**: Goal achievement with stakeholder language
- **Learning Capture**: Patterns available for future similar refactorings
- **Audit Trail**: Complete decision and implementation history

This enhanced approach revolutionizes systematic refactoring through discovery-tracking commits, exhaustive exploration, and concrete specification while maintaining the highest safety and quality standards with complete stakeholder communication capability.