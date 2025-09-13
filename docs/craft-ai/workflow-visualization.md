# AI-Craft Complete Workflow Visualization

## 🔄 Master Workflow Overview

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                              AI-CRAFT PIPELINE WORKFLOW                                 │
│                          Outside-In ATDD + Hexagonal Architecture                       │
└─────────────────────────────────────────────────────────────────────────────────────────┘

📋 BUSINESS REQUIREMENTS
        ↓
🔍 PHASE 1: REQUIREMENTS GATHERING
        ↓
🏗️ PHASE 2: ARCHITECTURE DESIGN  
        ↓
✅ PHASE 3: ACCEPTANCE TEST DESIGN
        ↓
🔄 PHASE 4: OUTSIDE-IN DEVELOPMENT (Double-Loop TDD)
        ↓
🧪 PHASE 5: MUTATION TESTING & VALIDATION
        ↓
♻️ COMPREHENSIVE REFACTORING (Level 1-6)
        ↓
📊 ARCHITECTURE UPDATE & TECHNICAL DEBT TRACKING
        ↓
🎯 FEATURE COMPLETE
```

## 📋 Phase 1: Requirements Gathering

```
┌──────────────────┐    requirements.md    ┌─────────────────────┐
│                  │ ──────────────────► │                     │
│ Business Analyst │                     │ Solution Architect  │
│                  │ ◄────────────────── │                     │
└──────────────────┘    feedback loop    └─────────────────────┘
         │                                          │
         │ INPUT:                                   │ OUTPUT:
         │ • Business needs                         │ • Structured requirements
         │ • Stakeholder requests                   │ • Acceptance criteria
         │ • User stories                           │ • Business rules
         │                                          │ • Success metrics

📝 ATDD DISCUSS PHASE: Requirements clarification with stakeholders
✅ Collaborative workshops, user story mapping, acceptance criteria definition
```

## 🏗️ Phase 2: Architecture Design

```
┌─────────────────────┐    architecture.md    ┌─────────────────────┐
│                     │ ──────────────────► │                     │
│ Solution Architect  │                     │ Acceptance Designer │
│                     │ ◄────────────────── │                     │
└─────────────────────┘    collaboration    └─────────────────────┘
         │                                           │
         │ INPUT:                                    │ OUTPUT:
         │ • Requirements                            │ • System architecture
         │ • User collaboration                      │ • Component boundaries
         │ • Technical constraints                   │ • ADRs & decisions
         │                                           │ • Integration patterns

🤝 USER COLLABORATION: Joint architecture definition sessions
🔧 Hexagonal Architecture + Vertical Slices + DDD Patterns
```

## ✅ Phase 3: Acceptance Test Design

```
┌─────────────────────┐  acceptance-tests.md  ┌──────────────────────┐
│                     │ ──────────────────► │                      │
│ Acceptance Designer │                     │ Test-First Developer │
│                     │ ◄────────────────── │                      │
└─────────────────────┘   environment choice └──────────────────────┘
         │                                           │
         │ CREATES:                                  │ RECEIVES:
         │ • BDD scenarios                           │ • Active E2E scenario
         │ • Given-When-Then tests                   │ • Business behavior specs
         │ • Environment choice consultation         │ • Architecture constraints
         │ • ONE active test at a time               │ • Public interface patterns

📋 ATDD DISTILL PHASE: Create acceptance tests from user perspective
🎯 Business-focused scenarios, environment-adaptive (in-memory local vs production CI/CD)
```

## 🔄 Phase 4: Outside-In Development (Double-Loop TDD)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            DOUBLE-LOOP TDD ARCHITECTURE                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ OUTER LOOP: E2E Acceptance Tests (Customer View - ATDD)                        │
│  ┌─────────────────────────────────────────────────────────────────────────┐    │
│  │ INNER LOOP: Unit Tests (Developer View - TDD)                          │    │
│  │  🔴 RED → 🟢 GREEN → 🔵 REFACTOR (Levels 1-3)                         │    │
│  └─────────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────────┘

┌──────────────────────┐  implementation-status.md  ┌─────────────────────────┐
│                      │ ──────────────────────► │                         │
│ Test-First Developer │                          │ Production Validator    │
│                      │ ◄────────────────────── │                         │
└──────────────────────┘   validation feedback    └─────────────────────────┘
         │                                                 │
         │ IMPLEMENTS:                                     │ VALIDATES:
         │ • Outside-in TDD                                │ • Production service calls
         │ • Hexagonal architecture                        │ • Architectural boundaries
         │ • Object Calisthenics (9 rules)                │ • ATDD compliance
         │ • DDD patterns                                  │ • Test effectiveness
         │ • Internal sealed classes                       │ • Integration patterns
         │ • Behavior-focused testing                      │

📋 ATDD DEVELOP PHASE: Outside-In TDD implementation with double-loop
🎯 One E2E test at a time, real system integration, NotImplementedException scaffolding
```

### 🏗️ Hexagonal Architecture Implementation

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          HEXAGONAL ARCHITECTURE LAYERS                          │
├─────────────────────────────────────────────────────────────────────────────────┤
│ E2E TESTS (Business Behavior Validation)                                       │
├─────────────────────────────────────────────────────────────────────────────────┤
│ APPLICATION SERVICES (Use Cases - Ports)                                       │
│ • IOrderService, IUserService (Public Interfaces)                              │
│ • OrderApplicationService (Internal Sealed - Orchestration Only)               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ DOMAIN SERVICES (Pure Business Logic)                                          │
│ • Order (Public Aggregate Root)                                                │
│ • OrderItem (Internal Sealed Entity)                                           │
│ • Money (Internal Sealed Value Object)                                         │
│ • OrderPricingService (Internal Sealed Domain Service)                         │
├─────────────────────────────────────────────────────────────────────────────────┤
│ INFRASTRUCTURE (Adapters + Integration Tests)                                  │
│ • DatabaseOrderRepository (Internal Sealed - Translation Only)                 │
│ • SmtpEmailService (Internal Sealed - No Business Logic)                      │
│ • Separate Integration Test Suite for Adapters                                 │
└─────────────────────────────────────────────────────────────────────────────────┘

VERTICAL SLICES: Complete business capabilities spanning all layers
TESTING STRATEGY: Public interfaces only, black box approach
```

### 🔬 Behavior-Focused Testing Strategy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            THREE TYPES OF BEHAVIORS                            │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 1. COMMAND BEHAVIOR (Changes System State)                                     │
│    • Given-When-Then structure with blank lines                                │
│    • Multiple asserts OK if validating same behavior                           │
│    • Focus: User-relevant state changes                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 2. QUERY BEHAVIOR (Projects System State)                                      │
│    • Given-Then structure (no separate When needed)                            │
│    • Focus: Business data projections                                          │
│    • Validate business-meaningful views                                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 3. PROCESS BEHAVIOR (Triggers Commands/Queries)                                │
│    • Complex Given-When-Then with orchestration validation                     │
│    • Multiple state checks for complete workflow                               │
│    • Focus: End-to-end business processes                                      │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🧪 Phase 5: Mutation Testing & Validation

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                    MUTATION TESTING QUALITY GATES                               │
├──────────────────────────────────────────────────────────────────────────────────┤
│ TRIGGER: Last acceptance test of feature passes                                 │
│                                                                                  │
│ 1. RUN MUTATION TESTING                                                         │
│    • dotnet stryker --project MyProject --test-projects MyProject.Tests        │
│    • Target: ≥75-80% overall, ≥90% critical paths                             │
│                                                                                  │
│ 2. ANALYZE SURVIVING MUTANTS                                                    │
│    • Add property-based tests for mathematical properties                       │
│    • Add model-based tests for state transitions                               │
│    • Eliminate critical surviving mutants                                       │
│                                                                                  │
│ 3. VALIDATE BEHAVIOR COVERAGE                                                   │
│    • All command behaviors tested (state changes)                              │
│    • All query behaviors tested (projections)                                  │
│    • All process behaviors tested (orchestration)                              │
│                                                                                  │
│ 4. QUALITY GATE APPROVAL                                                        │
│    • ✅ Mutation score achieved                                                 │
│    • ✅ Property tests complete                                                 │
│    • ✅ Model tests complete                                                    │
│    • ✅ Behavior coverage complete                                              │
│    • ✅ Ready for Level 4-6 refactoring                                        │
└──────────────────────────────────────────────────────────────────────────────────┘

📋 QUALITY VALIDATION: Ensure test effectiveness before advanced refactoring
🎯 Property-based testing, model-based testing, comprehensive behavior coverage
```

## ♻️ Comprehensive Refactoring (Level 1-6)

```
┌──────────────────────────────────────────────────────────────────────────────────┐
│                        SIX-LEVEL REFACTORING HIERARCHY                          │
├──────────────────────────────────────────────────────────────────────────────────┤
│ Level 1: 🟨 FOUNDATION (Immediate - Every GREEN)                               │
│ • Remove comments, dead code, magic numbers                                     │
│ • Apply domain naming, optimize scope                                           │
│                                                                                  │
│ Level 2: 🟢 COMPLEXITY REDUCTION (Immediate - Every GREEN)                     │
│ • Extract methods, eliminate duplication                                        │
│ • Apply Compose Method pattern                                                  │
│                                                                                  │
│ Level 3: 🟢 RESPONSIBILITY ORGANIZATION (Sprint Boundary)                      │
│ • Single Responsibility Principle                                               │
│ • Move behavior to appropriate classes                                          │
│                                                                                  │
│ Level 4: 🟢 ABSTRACTION REFINEMENT (Sprint Boundary + Mikado Method)          │
│ • Parameter objects, value objects                                              │
│ • Eliminate primitive obsession                                                 │
│ • MIKADO METHOD for complex changes spanning multiple classes                   │
│                                                                                  │
│ Level 5: 🔵 DESIGN PATTERN APPLICATION (Release Preparation + Mikado Method)   │
│ • Strategy, State, Command patterns                                             │
│ • Replace conditionals with polymorphism                                        │
│ • PARALLEL CHANGE pattern (EXPAND → MIGRATE → CONTRACT)                        │
│                                                                                  │
│ Level 6: 🔵 SOLID++ & CUPID PRINCIPLES (Release Preparation + Mikado Method)   │
│ • All SOLID principles + CUPID properties                                       │
│ • Object Calisthenics compliance (9 rules)                                     │
│ • DDD patterns with internal sealed classes                                     │
│ • SYSTEMATIC DEPENDENCY TRACKING with visual tree                               │
└──────────────────────────────────────────────────────────────────────────────────┘

🚨 BABY STEPS PROTOCOL (MANDATORY for Levels 4-6):
• Maximum 10 lines per change
• BUILD then TEST after EVERY change: `dotnet build` → `dotnet test`
• Exercise most recent logic with fresh build
• Commit locally after every GREEN
• If build/test fails: ROLLBACK → 5 Why Analysis → Update Mikado Tree → Fix → Retry

┌─────────────────────────────┐    refactoring-report.md    ┌──────────────────────────────┐
│                             │ ──────────────────────► │                              │
│ Comprehensive Refactoring   │                         │ Architecture Diagram        │
│ Specialist                  │ ◄────────────────────── │ Manager                      │
└─────────────────────────────┘    structure changes    └──────────────────────────────┘
              │                                                       │
              │ APPLIES:                                              │ UPDATES:
              │ • Progressive refactoring                             │ • Architecture diagrams
              │ • Both tests and source code                         │ • Component relationships
              │ • Architectural alignment                            │ • Integration patterns
              │ • Quality improvements                               │ • Visual documentation

📋 SYSTEMATIC IMPROVEMENT: Progressive enhancement with architectural compliance
🎯 Maintain green tests throughout, improve design quality at each level

## 🌳 Mikado Method Integration for Complex Refactorings

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           MIKADO METHOD WORKFLOW                               │
├─────────────────────────────────────────────────────────────────────────────────┤
│ TRIGGER: Level 4-6 refactorings affecting architecture or multiple classes     │
│                                                                                 │
│ 1. 🎯 GOAL DEFINITION                                                           │
│    • Define clear, specific refactoring objective                              │
│    • Assess impact: classes, tests, architectural changes                      │
│    • Validate adequate test coverage as safety net                             │
│                                                                                 │
│ 2. 🌳 MIKADO TREE CONSTRUCTION                                                  │
│    🎯 GOAL: Extract OrderPricingService                                        │
│    ├── 📋 Create IOrderPricingService interface                                │
│    ├── 📋 Implement OrderPricingService class                                  │
│    │   ├── 📋 Extract pricing logic from Order                                 │
│    │   └── 📋 Add pricing strategy support                                     │
│    ├── 📋 Update Order class to use service                                    │
│    └── 📋 Update all Order consumers                                           │
│                                                                                 │
│ 3. 🔄 PARALLEL CHANGE IMPLEMENTATION                                            │
│    • EXPAND: Add new alongside existing                                        │
│    • MIGRATE: Switch consumers one by one                                      │
│    • CONTRACT: Remove old implementation                                       │
│                                                                                 │
│ 4. 🚨 BABY STEPS PROTOCOL                                                       │
│    • Maximum 10 lines per change                                               │
│    • Run tests after EVERY change                                              │
│    • Commit locally after every GREEN                                          │
│    • Continue until refactoring phase complete                                 │
│                                                                                 │
│ 5. 🔍 FAILURE RECOVERY PROTOCOL                                                 │
│    🚨 Test Failure → ROLLBACK → 5 Why Analysis → Update Tree → Fix → Retry    │
│                                                                                 │
│ 6. 🎯 MIKADO MCP SERVER INTEGRATION (When Available)                           │
│    • Automated dependency tracking                                             │
│    • Visual tree management                                                    │
│    • Progress tracking with validation                                         │
│    • Risk assessment for changes                                               │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 🔄 Parallel Change Pattern Detail

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            PARALLEL CHANGE SAFETY                              │
├─────────────────────────────────────────────────────────────────────────────────┤
│ PHASE 1: EXPAND                                                                │
│ ┌─────────────────────────────────────────────────────────────────────────┐     │
│ │ // Keep existing implementation                                         │     │
│ │ public Money CalculatePrice() { /* existing logic */ }                 │     │
│ │                                                                         │     │
│ │ // Add new service-based approach                                       │     │
│ │ public Money CalculatePriceWithService()                               │     │
│ │ {                                                                       │     │
│ │     return _pricingService?.CalculatePrice(this)                       │     │
│ │         ?? CalculatePrice(); // Fallback to existing                   │     │
│ │ }                                                                       │     │
│ └─────────────────────────────────────────────────────────────────────────┘     │
│                                                                                 │
│ PHASE 2: MIGRATE                                                               │
│ ┌─────────────────────────────────────────────────────────────────────────┐     │
│ │ // Update consumers one by one                                          │     │
│ │ // Before: var price = order.CalculatePrice();                         │     │
│ │ // After:  var price = order.CalculatePriceWithService();              │     │
│ │                                                                         │     │
│ │ // Track migration progress in Mikado tree                             │     │
│ │ ✅ OrderApplicationService updated                                      │     │
│ │ ✅ OrderController updated                                              │     │
│ │ 📋 OrderTests update pending                                            │     │
│ └─────────────────────────────────────────────────────────────────────────┘     │
│                                                                                 │
│ PHASE 3: CONTRACT                                                              │
│ ┌─────────────────────────────────────────────────────────────────────────┐     │
│ │ // Remove old implementation when all consumers migrated                │     │
│ │ // public Money CalculatePrice() <- DELETE                              │     │
│ │                                                                         │     │
│ │ // Rename new method to final name                                      │     │
│ │ public Money CalculatePrice() // Was CalculatePriceWithService()       │     │
│ │ {                                                                       │     │
│ │     return _pricingService.CalculatePrice(this);                       │     │
│ │ }                                                                       │     │
│ └─────────────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### 🔍 5 Why Analysis Protocol

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                          SYSTEMATIC ROOT CAUSE ANALYSIS                        │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 🚨 TEST FAILURE DETECTED                                                        │
│                                                                                 │
│ IMMEDIATE ACTIONS:                                                              │
│ 1. 🔄 ROLLBACK: git checkout -- [modified files]                               │
│                                                                                 │
│ 2. 🔍 5 WHY ANALYSIS:                                                           │
│    WHY #1: Why did the test fail?                                              │
│    → [Direct cause: compilation error, assertion failure, etc.]                │
│                                                                                 │
│    WHY #2: Why does this condition exist?                                      │
│    → [Context: missing dependency, incorrect assumption, etc.]                 │
│                                                                                 │
│    WHY #3: Why do these conditions persist?                                    │
│    → [System: architecture constraint, design limitation, etc.]               │
│                                                                                 │
│    WHY #4: Why wasn't this anticipated?                                        │
│    → [Design: planning gap, complexity underestimation, etc.]                 │
│                                                                                 │
│    WHY #5: Why do these fundamental conditions exist?                          │
│    → [Root cause: architectural debt, missing abstraction, etc.]              │
│                                                                                 │
│ 3. 📝 UPDATE MIKADO TREE: Add discovered prerequisite                          │
│ 4. 🔧 APPLY FIX: Address root cause before retry                               │
│ 5. 🔄 RETRY: Attempt original change with prerequisite addressed               │
└─────────────────────────────────────────────────────────────────────────────────┘
```
```

## 📊 Architecture Update & Technical Debt Tracking

```
┌──────────────────────────────┐  architecture-diagrams.md  ┌─────────────────────────────┐
│                              │ ────────────────────────► │                             │
│ Architecture Diagram Manager │                           │ Technical Debt Tracker     │
│                              │ ◄──────────────────────── │                             │
└──────────────────────────────┘   debt prioritization    └─────────────────────────────┘
              │                                                       │
              │ CREATES:                                              │ MANAGES:
              │ • Updated architecture diagrams                       │ • Debt item tracking
              │ • Component relationship maps                         │ • Priority scoring
              │ • Integration pattern documentation                   │ • Resolution planning
              │ • Visual system overview                              │ • Continuous monitoring

📋 CONTINUOUS DOCUMENTATION: Keep architecture artifacts current
🎯 Visual system understanding, debt management, improvement planning
```

## 🎯 Quality Gates Integration

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                            8-STEP QUALITY VALIDATION                           │
├─────────────────────────────────────────────────────────────────────────────────┤
│ Step 1: ✅ SYNTAX VALIDATION (Language parsers, intelligent suggestions)       │
│ Step 2: ✅ TYPE CHECKING (Type compatibility, context-aware analysis)          │
│ Step 3: ✅ LINT COMPLIANCE (Code quality rules, refactoring suggestions)       │
│ Step 4: ✅ SECURITY SCANNING (Vulnerability assessment, OWASP compliance)      │
│ Step 5: ✅ TEST EXECUTION (≥80% unit, ≥70% integration coverage)              │
│ Step 6: ✅ PERFORMANCE BENCHMARKING (Response times, optimization)             │
│ Step 7: ✅ DOCUMENTATION COMPLETENESS (Accuracy, patterns validation)          │
│ Step 8: ✅ INTEGRATION TESTING (E2E validation, compatibility)                 │
└─────────────────────────────────────────────────────────────────────────────────┘

Applied at EVERY stage: Development → Validation → Refactoring → Documentation
```

## 🌍 Environment Strategy

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           DUAL-ENVIRONMENT TESTING                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ LOCAL DEVELOPMENT (User Choice)                                                │
│ ├── Option 1: In-Memory Components (~100ms feedback)                           │
│ │   • InMemoryUserRepository, InMemoryEmailService                            │
│ │   • Fastest feedback loop for TDD cycles                                     │
│ │                                                                              │
│ └── Option 2: Real Components Locally (~2-5s feedback)                        │
│     • DatabaseUserRepository, SmtpEmailService                                │
│     • More realistic integration testing                                       │
│                                                                                │
│ CI/CD PIPELINE (Always Production-Like)                                        │
│ • Real components mandatory: Database, SMTP, external services                │
│ • Production-like environment validation                                       │
│ • Same test scenarios, different infrastructure                               │
│                                                                                │
│ FRAMEWORK REQUIREMENTS                                                          │
│ • FREE only: NUnit, xUnit, NSubstitute, Testcontainers                       │
│ • NO paid: FluentAssertions, JustMock, commercial tools                       │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔄 File-Based Pipeline Coordination

```
📄 File Flow Through Pipeline:

requirements.md
    ↓ (Business Analyst → Solution Architect)
architecture.md  
    ↓ (Solution Architect → Acceptance Designer)
acceptance-tests.md
    ↓ (Acceptance Designer → Test-First Developer)
implementation-status.md
    ↓ (Test-First Developer → Production Validator)
integration-status.md
    ↓ (Production Validator → Quality Gates)
validation-report.md
    ↓ (Quality Gates → Comprehensive Refactoring)
refactoring-report.md
    ↓ (Comprehensive Refactoring → Architecture Updates)
architecture-diagrams.md + technical-debt.md
    ↓
🎯 FEATURE COMPLETE

📋 Context Optimization: Each agent reads specific input files, produces specific outputs
🎯 Maintains focus, reduces token usage, enables parallel processing
```

## 🚀 Deployment & Demo

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                              ATDD DEMO PHASE                                   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ 📋 STAKEHOLDER VALIDATION                                                       │
│ • Demonstrate completed feature                                                │
│ • Validate business requirements met                                           │
│ • Gather feedback for next iteration                                           │
│                                                                                  │
│ 🎯 BUSINESS OUTCOME VALIDATION                                                  │
│ • Acceptance criteria satisfied                                                │
│ • User workflows functioning                                                   │
│ • Business value delivered                                                     │
│                                                                                  │
│ 📊 QUALITY METRICS REVIEW                                                       │
│ • Test coverage achieved                                                        │
│ • Mutation testing scores                                                      │
│ • Architecture compliance                                                       │
│ • Technical debt status                                                        │
└─────────────────────────────────────────────────────────────────────────────────┘
```

## 🔧 Key Integrations & Principles

### ATDD Four-Stage Cycle
- **DISCUSS** → **DISTILL** → **DEVELOP** → **DEMO**
- Customer-developer-tester collaboration throughout
- Business-focused language and validation

### Object Calisthenics (All 9 Rules)
- One level indentation, no else, wrap primitives
- First-class collections, one dot per line, full names
- Small entities, max 2 variables, tell don't ask

### DDD + SOLID++ + CUPID
- Internal sealed as default, public only when needed
- Composable, Unix Philosophy, Predictable, Idiomatic, Domain-Based
- Aggregate boundaries, value objects, domain services

### Testing Excellence
- Test through public interfaces only (black box)
- One behavior per test (multiple asserts OK for same behavior)
- Mutation testing before advanced refactoring
- Property-based and model-based testing for edge cases

This comprehensive workflow ensures **world-class software development** with business focus, architectural excellence, and systematic quality improvement throughout the entire development lifecycle.