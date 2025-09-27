# Mikado-Systematic Refactorer Collaboration Framework

## Overview

This document describes the collaboration system between the **mikado-refactoring-specialist-enhanced** agent and the **systematic-refactorer** agent for complex architectural refactorings. The collaboration enables systematic dependency discovery through Mikado Method while leveraging comprehensive refactoring knowledge for precise code transformations.

## Quick Reference for Agents

**Mikado Agent - Use this file for**:
- Creating properly nested dependency trees
- Annotating nodes with `[RefactoringTechnique | AtomicTransformation | CodeSmellTarget]` format
- Identifying true leaves vs blocked dependencies
- Handoff protocols and tree validation

**Systematic Refactorer - Use this file for**:
- Understanding Mikado tree node structure and execution waves
- Mapping refactoring techniques to embedded knowledge base
- Creating commit messages with proper Mikado references
- Synchronizing progress between both tracking systems

## Collaboration Architecture

### Agent Roles

**Mikado Agent (Explorer)**:
- Performs exhaustive dependency discovery using enhanced Mikado Method
- Creates concrete tree nodes with refactoring mechanics annotations
- Identifies true leaves ready for implementation
- Maintains discovery audit trail through commit tracking

**Systematic Refactorer (Executor)**:
- Receives tree with embedded refactoring technique specifications
- Executes leaves using comprehensive refactoring knowledge base (22 code smells, 60+ techniques)
- Applies atomic transformations with test-driven safety
- Maintains systematic refactoring progress tracking

## Unified Workflow Process

### Phase 1: Mikado Exploration (Enhanced Agent)

**1.1 Goal Definition with Business Value**
```yaml
GOAL: "Customer order processing uses repository pattern for improved testability and maintainability"
BUSINESS_VALUE: "Enables faster feature development and reduces bug risk in order processing"
SCOPE: "OrderController, OrderService, database integration"
```

**1.2 Exhaustive Dependency Discovery**
```bash
# Mikado agent attempts naive implementation
# Discovers dependencies and commits each finding:

git commit -m "Discovery: OrderController.ProcessOrder() requires IOrderRepository.SaveOrder() method in src/Repositories/IOrderRepository.cs [Extract Interface | Extract | Data Class]"

git commit -m "Discovery: SqlOrderRepository needs IDbContext dependency [Move Method | Move | Feature Envy]"

git commit -m "Discovery: Order entity missing validation for repository pattern [Extract Method | Extract | Long Method]"
```

**1.3 Correct Dependency Tree with Proper Nesting**
```
Goal: Replace direct database calls in OrderController with repository pattern
├── Update OrderController to use IOrderRepository [Replace Parameter with Method | Move | Feature Envy]
│   ├── Implement SqlOrderRepository : IOrderRepository [Move Method | Move | Feature Envy]
│   │   ├── Create IOrderRepository interface [Extract Interface | Extract | Data Class] ← TRUE LEAF
│   │   │   ├── Define GetOrderById(int orderId) → Order? method signature [Extract Method | Extract | Long Method]
│   │   │   ├── Define SaveOrder(Order order) → Task method signature [Extract Method | Extract | Long Method]
│   │   │   └── Define DeleteOrder(int orderId) → Task<bool> method signature [Extract Method | Extract | Long Method]
│   │   ├── Add constructor SqlOrderRepository(IDbContext context) [Introduce Parameter Object | Extract | Primitive Obsession]
│   │   ├── Implement GetOrderById method [Replace Temp with Query | Extract | Long Method]
│   │   └── Implement SaveOrder with error handling [Extract Method | Extract | Long Method]
│   └── Register IOrderRepository in DI container [Introduce Parameter Object | Extract | Primitive Obsession]
└── Remove direct IDbContext dependency [Safe Delete | Safe Delete | Dead Code]
```

**1.4 True Leaves Identification**
```yaml
TRUE_LEAVES: # Zero prerequisites - ready for execution
  - "Create IOrderRepository interface [Extract Interface | Extract | Data Class]"
  - "Define GetOrderById(int orderId) → Order? method signature [Extract Method | Extract | Long Method]"
  - "Define SaveOrder(Order order) → Task method signature [Extract Method | Extract | Long Method]"
  - "Define DeleteOrder(int orderId) → Task<bool> method signature [Extract Method | Extract | Long Method]"

BLOCKED_NODES: # Have prerequisites that must be completed first
  - "Implement SqlOrderRepository : IOrderRepository" ← blocked by IOrderRepository interface creation
  - "Update OrderController to use IOrderRepository" ← blocked by SqlOrderRepository implementation
  - "Remove direct IDbContext dependency" ← blocked by OrderController update
```

### Phase 2: Systematic Execution (Systematic Refactorer)

**2.1 Tree Reception and Validation**
```yaml
RECEIVED_TREE:
  total_nodes: 10
  true_leaves: 4  # Only nodes with zero prerequisites
  blocked_nodes: 6
  refactoring_annotations: "100% coverage"
  dependency_relationships: "Correctly nested"
```

**2.2 Bottom-Up Execution Sequence**
```yaml
EXECUTION_ORDER: # Execute true leaves first, then newly unblocked nodes
  WAVE_1: # Initial true leaves (interface methods)
    - "Create IOrderRepository interface [Extract Interface | Extract | Data Class]"
    - "Define GetOrderById(int orderId) → Order? method signature [Extract Method | Extract | Long Method]"
    - "Define SaveOrder(Order order) → Task method signature [Extract Method | Extract | Long Method]"
    - "Define DeleteOrder(int orderId) → Task<bool> method signature [Extract Method | Extract | Long Method]"

  WAVE_2: # Unblocked after Wave 1 completion (interface exists)
    - "Add constructor SqlOrderRepository(IDbContext context) [Introduce Parameter Object | Extract | Primitive Obsession]"
    - "Implement GetOrderById method [Replace Temp with Query | Extract | Long Method]"
    - "Implement SaveOrder with error handling [Extract Method | Extract | Long Method]"

  WAVE_3: # Unblocked after Wave 2 completion (implementation exists)
    - "Register IOrderRepository in DI container [Introduce Parameter Object | Extract | Primitive Obsession]"

  WAVE_4: # Unblocked after Wave 3 completion (DI registered)
    - "Update OrderController to use IOrderRepository [Replace Parameter with Method | Move | Feature Envy]"

  WAVE_5: # Final cleanup (controller updated)
    - "Remove direct IDbContext dependency [Safe Delete | Safe Delete | Dead Code]"
```

**2.3 Progressive Wave Execution**
```bash
# WAVE 1 - Interface Creation (True Leaves)
git commit -m "refactor(level-4): Create IOrderRepository interface with method signatures

- Applied: Extract Interface technique from embedded knowledge base
- Target: Data Class (OrderController directly using DbContext)
- Files: src/Repositories/IOrderRepository.cs
- Tests: All 45 tests passing ✅
- Mikado: Interface creation wave completed - unlocks implementation"

# WAVE 2 - Implementation (Now Unblocked)
git commit -m "refactor(level-3): Implement SqlOrderRepository with IOrderRepository interface

- Applied: Move Method technique from embedded knowledge base
- Target: Feature Envy (OrderController accessing DbContext directly)
- Files: src/Infrastructure/SqlOrderRepository.cs
- Tests: All 48 tests passing ✅
- Mikado: Implementation wave completed - unlocks DI registration"

# WAVE 3 - DI Registration (Now Unblocked)
git commit -m "refactor(level-4): Register IOrderRepository in DI container

- Applied: Introduce Parameter Object technique from embedded knowledge base
- Target: Primitive Obsession (manual dependency management)
- Files: src/Startup.cs
- Tests: All 50 tests passing ✅
- Mikado: DI registration completed - unlocks controller update"

# WAVE 4 - Controller Update (Now Unblocked)
git commit -m "refactor(level-3): Update OrderController to use IOrderRepository dependency

- Applied: Replace Parameter with Method technique from embedded knowledge base
- Target: Feature Envy (Controller using infrastructure directly)
- Files: src/Controllers/OrderController.cs, tests/OrderControllerTests.cs
- Tests: All 52 tests passing ✅
- Mikado: Controller update completed - unlocks cleanup"

# WAVE 5 - Final Cleanup (Now Unblocked)
git commit -m "refactor(level-1): Remove direct IDbContext dependency from OrderController

- Applied: Safe Delete atomic transformation from embedded knowledge base
- Target: Dead Code (unused DbContext field and constructor parameter)
- Files: src/Controllers/OrderController.cs
- Tests: All 52 tests passing ✅
- Mikado: Repository pattern implementation COMPLETE"
```

### Phase 3: Dependency Resolution Tracking

**3.1 Progressive Node Unlocking**
```yaml
INITIAL_STATE:
  true_leaves: 4  # Interface definition leaves
  blocked_nodes: 6

AFTER_WAVE_1:
  completed: ["Create IOrderRepository interface", "Define method signatures"]
  newly_unblocked: ["SqlOrderRepository implementation methods"]
  still_blocked: 3

AFTER_WAVE_2:
  completed: 7
  newly_unblocked: ["Register IOrderRepository in DI container"]
  still_blocked: 2

AFTER_WAVE_3:
  completed: 8
  newly_unblocked: ["Update OrderController to use IOrderRepository"]
  still_blocked: 1

AFTER_WAVE_4:
  completed: 9
  newly_unblocked: ["Remove direct IDbContext dependency"]
  still_blocked: 0

FINAL_STATE:
  completed: 10
  blocked_nodes: 0
  goal_achieved: true
```

## Collaboration Benefits

### 1. **Correct Dependency Sequencing**
- Mikado Method discovers actual prerequisites through failed attempts
- Proper tree nesting shows parent-child dependencies
- Systematic refactorer executes in proper bottom-up dependency order
- No premature attempts to implement dependent nodes

### 2. **Progressive Unblocking**
- Each completed leaf unlocks its parent nodes
- Wave-based execution ensures correct implementation sequence
- Clear progress visibility for stakeholders

### 3. **Knowledge Base Integration**
- Tree nodes reference specific refactoring techniques
- Embedded knowledge base provides step-by-step mechanics
- Atomic transformations ensure safe dependency resolution

### 4. **Safety Through Prerequisites**
- Cannot execute dependent nodes before prerequisites
- Test safety maintained at each wave
- Rollback affects only current wave, not entire tree

## Example Dependency Patterns

### Pattern 1: Interface Extraction Prerequisites
```
Update Consumer to use Interface
├── Implement Interface
│   ├── Create Interface ← TRUE LEAF
│   ├── Implement Method A
│   └── Implement Method B
└── Register Interface in DI
```

### Pattern 2: Strategy Pattern Prerequisites
```
Replace Switch with Strategy Pattern
├── Update Consumer to use Strategy
│   ├── Create Strategy Factory
│   │   ├── Create Strategy Interface ← TRUE LEAF
│   │   ├── Implement Strategy A
│   │   └── Implement Strategy B
│   └── Register Strategies in DI
└── Remove Switch Statement
```

### Pattern 3: Extract Class Prerequisites
```
Update Original Class to use New Class
├── Create New Class ← TRUE LEAF
├── Move Method A to New Class
├── Move Method B to New Class
└── Remove Duplicate Methods from Original Class
```

## Enhanced Collaboration Protocols (v2.0)

Based on production findings, the following protocols have been implemented to ensure robust collaboration:

### 1. Mikado Enhanced Agent Improvements

#### **Corrected Algorithm Sequence**
```
EXPERIMENT → LEARN → GRAPH → COMMIT GRAPH → REVERT
```
**Previously Wrong**: EXPERIMENT → LEARN → REVERT → GRAPH
**Production Impact**: Premature reverts were losing discovery progress

#### **Mandatory Tree File Persistence**
- **Location**: `docs/mikado/<goal-name>.mikado.md`
- **Format**: Checkbox-based tree with 4-space indentation
- **Tracking**: Individual node completion and dependency relationships
- **Updates**: Real-time progress tracking with proper nesting validation

#### **Enhanced Discovery Commit Protocol**
- **Discovery Commits**: Use `feat(mikado): discover dependencies for <goal>`
- **Progress Commits**: Use `docs(mikado): update progress for <goal-name>`
- **Separation**: Discovery commits separate from tree file updates
- **Audit Trail**: Complete commit history of exploration process

### 2. Systematic Refactorer Agent Improvements

#### **Enforced Code Smell Detection**
- **Phase 1**: MANDATORY detection and annotation of ALL 22 code smell types
- **Searchable Comments**: `//CODE SMELL(S): <SmellType> - <Description>`
- **Complete Annotation**: ALL source files must be scanned before refactoring begins
- **Validation**: Search for existing annotations to verify completion

#### **Strict Level Progression Validation**
```bash
# CRITICAL: Level Progression Validation
❌ NEVER attempt Level 4 (Primitive Obsession, abstractions) before Level 1-3 complete
❌ NEVER attempt Level 5-6 (patterns, SOLID) before Level 1-4 complete
✅ VALIDATE completion evidence in git history before proceeding to higher levels

# PROGRESSION VALIDATION CHECKLIST:
- [ ] Search for `git log --grep="refactor(level-1)"` - evidence of Level 1 completion
- [ ] Search for `git log --grep="refactor(level-2)"` - evidence of Level 2 completion
- [ ] Search for `git log --grep="refactor(level-3)"` - evidence of Level 3 completion
- [ ] Only proceed to Level 4+ after ALL previous levels show commit evidence
```

#### **Mandatory Pre-Commit Test Validation**
```bash
# ABSOLUTE RULE: Validation by tests must happen BEFORE commit

PRE-COMMIT VALIDATION CHECKLIST:
- [ ] Compilation Check: dotnet build OR equivalent - ALL MUST pass
- [ ] Unit Test Execution: dotnet test OR equivalent - ALL MUST pass
- [ ] Integration Test Execution: ALL integration tests MUST pass
- [ ] Quality Gates: Linting, formatting, static analysis - ALL MUST pass
- [ ] No Skipped Tests: Verify zero tests are skipped during execution
- [ ] Zero Test Failures: Confirm 100% test pass rate before commit

COMMIT BLOCKING CONDITIONS (DO NOT COMMIT if ANY exist):
❌ ANY compilation errors - fix ALL build errors first
❌ ANY failing tests - fix ALL test failures first
❌ ANY skipped tests - ensure ALL tests execute successfully
❌ ANY quality gate failures - fix ALL linting/formatting issues first

COMMIT AUTHORIZATION: Commit happens only and only if NO compilation errors AND NO failing tests exist
```

### 3. Improved Handoff Protocols

#### **Mikado → Systematic Handoff**
1. **Tree Validation**: Verify proper checkbox format and nesting
2. **Annotation Verification**: Confirm all refactoring mechanics annotations present
3. **True Leaf Identification**: Validate leaves have no dependencies
4. **Progress Baseline**: Document current tree state for systematic tracking

#### **Systematic → Mikado Handoff**
1. **Completion Confirmation**: Update tree checkboxes after successful refactoring
2. **Parent Unblocking**: Mark parent nodes as unblocked when prerequisites complete
3. **Progress Synchronization**: Sync systematic level completion with tree progress
4. **Wave Advancement**: Signal readiness for next wave execution

### 4. Safety and Quality Protocols

#### **Test-Driven Safety**
- **"Stay in Green" Methodology**: ALL tests must pass before ANY commit
- **Atomic Transformations**: One refactoring technique at a time
- **Immediate Rollback**: Revert immediately if ANY test fails
- **Progressive Validation**: Validate each wave before advancing

#### **Quality Assurance**
- **Mandatory Annotations**: COMPLETE code smell detection before execution
- **Level Progression**: STRICT enforcement of 1→2→3→4→5→6 progression
- **Compilation Gates**: ZERO tolerance for build errors
- **Test Coverage**: 100% test pass rate maintained throughout

### 5. Production Lessons Learned

#### **Critical Failures Prevented**
- **Algorithm Sequence Error**: Fixed premature revert losing discovery progress
- **Missing Tree Files**: Prevented loss of dependency tracking
- **Level Skipping**: Blocked attempts to apply advanced patterns without foundation
- **Unsafe Commits**: Prevented commits with failing tests or build errors

#### **Robustness Improvements**
- **Comprehensive Validation**: Multiple checkpoints prevent invalid states
- **Progressive Safety**: Each phase validated before advancing
- **Evidence-Based Progression**: Git history provides proof of completion
- **Real-Time Tracking**: Live progress updates prevent state drift

This enhanced collaboration framework ensures reliable, safe, and systematic execution of complex refactorings through proper dependency management and rigorous safety protocols.

This collaboration framework ensures that dependencies are properly nested and executed in the correct sequence, with true leaves at the deepest level of nesting and dependent operations properly structured as their parents.