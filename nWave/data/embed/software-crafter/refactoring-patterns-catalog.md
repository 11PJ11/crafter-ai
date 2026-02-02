# Refactoring Patterns and Test Refactoring Knowledge

## Core Refactoring Patterns (Fowler catalog)

### Extract Function (workhorse refactoring)
Move code fragments to named function. Heuristic: if you need a comment to explain a block, extract to method with that explanation as name. Essential for TDD - extract to keep code at single abstraction level.

### Inline Function (inverse of Extract)
Remove unnecessary abstraction when body is as clear as name. Used in "inline then re-extract" dance: inline several functions, rethink decomposition, extract with better boundaries.

### Move Function
Relocate to more appropriate class/module. Addresses Feature Envy smell. Building block for extracting modules/microservices.

### Encapsulate Variable/Collection
Protect data from direct access. Encapsulate Collection: return unmodifiable view, not raw collection. Principle: objects expose behavior, not data. Prevents action-at-a-distance bugs.

### Conditional Logic Refactorings
Decompose Conditional: extract condition + branches to named functions showing intent.
Guard Clauses: handle exceptional cases early, return, leave main logic unnested.
Simpler conditionals = easier to test exhaustively.

### Compose Method (Kerievsky)
Transform method into composition of methods at same abstraction level. Repeated Extract Function until method body reads like pseudocode. Creates self-documenting code. Aligns with Single Responsibility Principle.

### Extract Class
Decompose Large Class by moving related data+methods to new class. Building block for architectural refactoring (bounded contexts, service extraction).

### Refactoring to Patterns (Kerievsky)
Don't design patterns upfront - refactor toward them as needs emerge:
- Extract Method repeatedly -> Compose Method -> Template Method
- Encapsulate Field + Move Method -> Strategy
- Extract Class + Move Method -> Decorator
Patterns are destinations arrived at through refactoring, not goals.

## Catalog Organization
basic: Extract Function, Inline Function
encapsulation: Encapsulate Variable, Encapsulate Collection
moving-features: Move Function/Method
organizing-data: Replace Primitive with Object
simplifying-conditional-logic: Decompose Conditional, Guard Clauses

## Key Principles
- Behavior-preserving: if behavior changes, it's not refactoring
- Automated refactoring (IDE) preferred over manual
- Refactoring is language-agnostic (2nd ed. JavaScript examples prove this)
- Cohesion and clarity over line-count thresholds
- Function size: Single Responsibility + Consistent Abstraction + Self-Documenting names

---

## Test Code Refactoring Patterns

### Test Code Smells
L1 (Naming): Obscure Test, Hard-Coded Test Data, Assertion Roulette
L2 (Complexity): Eager Test, Test Code Duplication, Conditional Test Logic
L3 (Organization): Mystery Guest, Test Class Bloat (>15 tests), General Fixture

### Pattern 1: Extract Test Helper
Duplicated setup across 3+ tests -> extract to business-meaningful helper (e.g., createPremiumCustomer()).
When: setup in 3+ tests, setup >5 lines, setup has business meaning.

### Pattern 2: Replace Mystery Guest
External file/DB dependency hidden from test -> inline test data as constants.
When: test reads files/queries DB. NOT for integration tests deliberately testing I/O.

### Pattern 3: Split Eager Test
Single test with multiple unrelated assertions -> split to one test per business scenario.
When: multiple assertions testing different concerns, test name uses "And".

### Pattern 4: Parameterize Conditional Logic
if/switch in tests -> parameterized tests using framework features.
When: conditional logic in tests, multiple similar tests differ only in inputs.

### Pattern 5: Split Test Class
15+ tests covering multiple features -> split by feature into focused test classes.
When: >15 tests, multiple features, finding specific test is difficult.

### Pattern 6: Inline General Fixture
Shared fixture creating objects not all tests need -> per-test setup helpers.
When: SetUp creates many objects, some tests don't use all, fixture changes break unrelated tests.

### Test Naming Conventions
C#/xUnit: MethodUnderTest_StateUnderTest_ExpectedBehavior
TypeScript/Jest: should_do_expected_thing_when_condition
Python/pytest: test_method_state_expected_behavior

### Integration with TDD Cycle
Apply during Phase 5 (REFACTOR_CONTINUOUS). Safety: refactor ONE test at a time. Run ALL tests after each change. Revert if any fails. Never refactor tests and production code simultaneously.

### Key Test Principles
Test code = first-class code, same quality standards. L1-L3 every cycle, not optional.
Clarity over DRY. Test behavior not implementation. Make tests resilient to refactoring.
