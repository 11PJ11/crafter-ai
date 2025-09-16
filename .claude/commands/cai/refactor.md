# /cai:refactor - Systematic Refactoring

```yaml
---
command: "/cai:refactor"
category: "Quality & Enhancement"
purpose: "Systematic code refactoring from Level 1-6 or complex Mikado Method"
wave-enabled: true
performance-profile: "optimization"
---
```

## Overview

Comprehensive refactoring command supporting progressive Level 1-6 refactoring and complex architectural changes using the Mikado Method.

## Auto-Persona Activation
- **Refactorer**: Code quality specialist (mandatory)
- **Architect**: Architectural refactoring guidance (Level 4-6)
- **Performance**: Performance optimization (conditional)
- **Security**: Security improvement (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic refactoring analysis and planning)
- **Secondary**: Context7 (refactoring patterns and best practices)
- **Avoided**: Magic (focuses on existing code over generation)

## Tool Orchestration
- **Read**: Code analysis and pattern detection
- **Edit**: Single-file refactoring changes
- **MultiEdit**: Batch refactoring across multiple files
- **Grep**: Code smell detection and pattern analysis
- **Bash**: Test execution and validation
- **Write**: New abstraction creation (Level 4-6)

## Agent Flow
```yaml
systematic-refactorer:
  level_1_readability: "Comments, dead code, naming, magic strings"
  level_2_complexity: "Method extraction, duplication elimination"
  level_3_responsibilities: "Class breakdown, coupling reduction"
  level_4_abstractions: "Parameter objects, value objects"
  level_5_patterns: "Strategy, State, Command patterns"
  level_6_solid: "SOLID principles application"

mikado-refactoring-specialist:
  complex_changes: "Multi-class architectural refactorings"
  parallel_change: "Breaking change management"
  dependency_management: "Systematic prerequisite handling"
```

## Arguments

### Basic Usage
```bash
/cai:refactor [target] [level]
```

### Advanced Usage
```bash
/cai:refactor [target] --level <1-6> --mikado --parallel-change --validate
```

### Target Specification
- `[target]`: File, class, or module to refactor
- `@<path>`: Specific path for refactoring
- `--scope <level>`: file, module, project, or system

### Refactoring Level Control
- `--level <1-6>`: Specify refactoring level
  - `--level 1`: Readability (comments, naming, dead code)
    - Remove obsolete how-comments and dead code
    - Extract constants for magic strings and numbers
    - Apply domain-driven naming conventions
    - Optimize variable scope and eliminate unnecessary complexity
  - `--level 2`: Complexity (method extraction, duplication)
    - Extract methods to reduce long method code smell
    - Eliminate duplicated code through extraction and abstraction
    - Decompose complex conditionals into readable methods
    - Apply Compose Method pattern for single-level abstraction
  - `--level 3`: Responsibilities (class breakdown, coupling)
    - Extract classes to apply Single Responsibility Principle
    - Move methods to reduce feature envy and inappropriate intimacy
    - Reduce coupling between classes through interface design
    - Apply proper responsibility distribution across components
  - `--level 4`: Abstractions (parameter objects, value objects)
    - Introduce parameter objects to reduce long parameter lists
    - Replace data clumps with cohesive value objects
    - Replace primitive obsession with domain-specific types
    - Remove middle man anti-pattern and unnecessary indirection
  - `--level 5`: Patterns (Strategy, State, Command)
    - Replace switch statements and conditionals with Strategy pattern
    - Apply State pattern for complex state-dependent behavior
    - Use Command pattern to encapsulate operations as objects
    - Apply Factory patterns for complex object creation scenarios
  - `--level 6`: SOLID (advanced architectural principles)
    - Apply Single Responsibility Principle to eliminate divergent change
    - Ensure Open/Closed Principle through extension over modification
    - Validate Liskov Substitution Principle in inheritance hierarchies
    - Apply Interface Segregation to prevent refused bequest
    - Use Dependency Inversion to reduce coupling to concretions

### Complex Refactoring Control
- `--mikado`: Use Mikado Method for complex architectural changes
  - Applies systematic dependency tree construction for complex refactoring
  - Enables parallel change patterns to manage breaking changes safely
  - Uses baby steps protocol to minimize risk during large architectural changes
  - Provides rollback capabilities and incremental progress tracking
- `--parallel-change`: Apply parallel change pattern for breaking changes
  - Uses Expand-Migrate-Contract pattern to minimize disruption
  - Maintains both old and new implementations during transition period
  - Enables gradual migration of consumers to new implementation
  - Provides safety net during breaking architectural changes
- `--tree`: Generate and display Mikado dependency tree
  - Visualizes refactoring dependencies and prerequisite relationships
  - Shows optimal execution order for complex multi-component changes
  - Identifies circular dependencies and potential blocking issues
  - Provides progress tracking for large-scale refactoring initiatives
- `--baby-steps`: Use baby steps protocol for safety
  - Enforces small, incremental changes with continuous validation
  - Maintains green tests throughout entire refactoring process
  - Enables rapid rollback if changes introduce failures or issues
  - Reduces cognitive load by focusing on one small change at a time

### Validation and Safety
- `--validate`: Add comprehensive validation steps
  - Validates code quality improvement through static analysis metrics
  - Ensures test coverage maintenance or improvement during refactoring
  - Applies mutation testing to validate test effectiveness after changes
  - Includes performance validation to prevent regression during optimization
- `--test-first`: Ensure tests pass before refactoring
  - Validates comprehensive test coverage before beginning refactoring
  - Runs full test suite to establish green baseline for safety
  - Identifies areas requiring additional test coverage before changes
  - Ensures refactoring safety net through robust test validation
- `--rollback`: Create rollback points
  - Creates git commits at each major refactoring milestone
  - Enables rapid recovery if refactoring introduces issues or failures
  - Provides clear history of incremental improvements for tracking
  - Maintains clean commit history with logical refactoring progression
- `--dry-run`: Show planned changes without execution
  - Analyzes code and shows planned refactoring actions without implementation
  - Provides impact assessment and change preview for validation
  - Allows review of refactoring strategy before committing to changes
  - Generates refactoring plan with estimated effort and risk assessment

## Six-Level Progressive Refactoring

### Level 1: 🟨 Foundation Refactoring (Readability)
**Focus**: Eliminate clutter, improve naming, remove dead code
```yaml
techniques:
  - Remove obsolete and how-comments
  - Extract constants for magic strings/numbers
  - Apply domain-driven naming
  - Remove dead code and unused imports
  - Optimize variable scope
```

### Level 2: 🟢 Complexity Reduction (Simplification)
**Focus**: Reduce complexity through extraction and elimination
```yaml
techniques:
  - Extract Method (long methods)
  - Eliminate duplicated code
  - Decompose complex conditionals
  - Apply Compose Method pattern
```

### Level 3: 🟢 Responsibility Organization
**Focus**: Proper responsibility distribution
```yaml
techniques:
  - Extract Class (large classes)
  - Move Method (feature envy)
  - Reduce inappropriate intimacy
  - Apply Single Responsibility Principle
```

### Level 4: 🟢 Abstraction Refinement
**Focus**: Create appropriate abstractions
```yaml
techniques:
  - Introduce Parameter Object
  - Replace Data Clumps with objects
  - Replace Primitive Obsession
  - Remove Middle Man antipattern
```

### Level 5: 🔵 Pattern Application
**Focus**: Strategic design pattern application
```yaml
techniques:
  - Replace Switch Statements with Strategy
  - Apply State Pattern for state-dependent behavior
  - Use Command Pattern for operations
  - Apply Factory patterns for creation
```

### Level 6: 🔵 SOLID++ Principles
**Focus**: Advanced architectural principles
```yaml
techniques:
  - Single Responsibility Principle
  - Open/Closed Principle
  - Liskov Substitution Principle
  - Interface Segregation Principle
  - Dependency Inversion Principle
```

## Mikado Method Integration

### When to Use Mikado
- Level 4-6 refactoring requiring architectural changes
- Multiple class modifications with complex dependencies
- Breaking changes requiring careful coordination
- High-risk refactoring with significant impact

### Mikado Process
1. **Goal Definition**: Define refactoring objective
2. **Tree Construction**: Build dependency tree
3. **Baby Steps Execution**: Small, safe changes
4. **Parallel Change Pattern**: Manage breaking changes
5. **Validation**: Continuous testing and verification

## Wave System Integration

**Wave Eligibility**: Complex refactoring across multiple components
**Wave Triggers**: Level 4-6 refactoring + multiple files + architectural impact

### Wave Orchestration
1. **Analysis Wave**: Code smell detection and categorization
2. **Planning Wave**: Refactoring strategy and level selection
3. **Preparation Wave**: Test setup and safety measures
4. **Execution Wave**: Systematic refactoring implementation
5. **Validation Wave**: Quality verification and impact assessment

## Quality Gates

### Pre-Refactoring
- **Test Coverage**: ≥80% coverage for refactoring target
- **Baseline Metrics**: Code quality and complexity measurements
- **Safety Net**: Comprehensive test suite validation
- **Backup Creation**: Version control state preservation

### During Refactoring
- **Continuous Testing**: Tests remain green throughout
- **Small Steps**: Incremental changes with frequent validation
- **Pattern Application**: Consistent application of refactoring techniques
- **Quality Monitoring**: Real-time quality metric tracking

### Post-Refactoring
- **Quality Improvement**: Measurable improvement in code metrics
- **Functionality Preservation**: All tests passing
- **Performance Validation**: No performance regression
- **Documentation Update**: Updated code and architectural documentation

## Examples

### Basic Code Cleanup
```bash
/cai:refactor "user-service" --level 2 --validate
```

### Complex Architectural Refactoring
```bash
/cai:refactor "authentication-system" --mikado --parallel-change
```

### Progressive Multi-Level Refactoring
```bash
/cai:refactor "core-domain" --level 1-4 --validate --test-first
```

### System-Wide Pattern Application
```bash
/cai:refactor @src/ --level 5 --pattern strategy --wave-mode auto
```

### Safe Complex Refactoring
```bash
/cai:refactor "legacy-module" --mikado --baby-steps --rollback
```

## Comprehensive Usage Examples

### Progressive Level-by-Level Refactoring
```bash
# Foundation cleanup - readability and dead code removal
/cai:refactor "user-management" --level 1 --validate --test-first

# Complexity reduction - method extraction and duplication elimination
/cai:refactor "payment-processor" --level 2 --validate --rollback

# Responsibility organization - class extraction and coupling reduction
/cai:refactor "order-service" --level 3 --validate --test-first --rollback

# Abstraction refinement - parameter objects and value objects
/cai:refactor "customer-domain" --level 4 --validate --dry-run

# Pattern application - Strategy, State, Command patterns
/cai:refactor "notification-system" --level 5 --validate --rollback --baby-steps

# SOLID principles - advanced architectural improvements
/cai:refactor "core-architecture" --level 6 --validate --test-first --rollback --dry-run
```

### Multi-Level Progressive Refactoring
```bash
# Complete progressive refactoring from foundation to patterns
/cai:refactor "legacy-billing-system" --level 1-5 --validate --test-first --rollback

# Foundation through abstraction refinement
/cai:refactor "data-access-layer" --level 1-4 --validate --baby-steps --rollback

# Pattern application and SOLID principles only
/cai:refactor "business-logic-core" --level 5-6 --validate --dry-run --test-first

# Comprehensive refactoring with all levels and safety measures
/cai:refactor "enterprise-integration" --level 1-6 --validate --test-first --rollback --baby-steps
```

### Mikado Method Complex Refactoring
```bash
# Basic Mikado Method for architectural changes
/cai:refactor "monolith-decomposition" --mikado --validate --rollback

# Mikado with parallel change for breaking modifications
/cai:refactor "api-versioning-refactor" --mikado --parallel-change --tree --validate

# Safe Mikado refactoring with baby steps
/cai:refactor "database-abstraction-layer" --mikado --baby-steps --rollback --validate

# Complex architectural transformation with dependency tree
/cai:refactor "service-oriented-architecture" --mikado --tree --parallel-change --validate --test-first
```

### Scope-Specific Refactoring
```bash
# Single file focused refactoring
/cai:refactor @src/services/UserService.ts --level 1-3 --validate

# Module-level refactoring with pattern application
/cai:refactor @src/modules/authentication/ --level 4-5 --validate --rollback

# Project-wide refactoring with SOLID principles
/cai:refactor --scope project --level 6 --validate --test-first --dry-run

# System-wide architectural refactoring
/cai:refactor --scope system --mikado --parallel-change --tree --validate
```

### Safety-Focused Refactoring
```bash
# Maximum safety with all validation steps
/cai:refactor "critical-payment-logic" --validate --test-first --rollback --baby-steps --dry-run

# Preview-only refactoring analysis
/cai:refactor "legacy-integration" --dry-run --level 1-6 --mikado

# Test-driven refactoring with comprehensive validation
/cai:refactor "core-business-rules" --test-first --validate --level 3-4 --rollback

# Incremental safe refactoring with rollback points
/cai:refactor "authentication-flow" --baby-steps --rollback --validate --level 2-3
```

### Pattern-Specific Refactoring
```bash
# Strategy pattern application for conditional logic
/cai:refactor "discount-calculation" --level 5 --pattern strategy --validate --rollback

# State pattern for state-dependent behavior
/cai:refactor "order-state-machine" --level 5 --pattern state --validate --test-first

# Command pattern for operation encapsulation
/cai:refactor "user-actions" --level 5 --pattern command --validate --rollback

# Factory pattern for complex object creation
/cai:refactor "entity-creation" --level 5 --pattern factory --validate --dry-run
```

### Domain-Driven Refactoring
```bash
# Business domain refactoring with domain modeling
/cai:refactor "customer-management" --level 3-4 --validate --focus domain --rollback

# Value object extraction and primitive obsession elimination
/cai:refactor "financial-calculations" --level 4 --validate --focus value-objects --test-first

# Domain service extraction and responsibility clarification
/cai:refactor "business-logic-core" --level 3-5 --validate --focus services --rollback

# Aggregate boundary refinement and domain modeling
/cai:refactor "order-management-domain" --level 4-6 --validate --focus aggregates --test-first
```

### Performance-Focused Refactoring
```bash
# Performance optimization with validation
/cai:refactor "data-processing-pipeline" --level 2-3 --validate --focus performance --rollback

# Algorithm efficiency improvement
/cai:refactor "search-algorithms" --level 2-5 --validate --focus algorithms --test-first

# Resource usage optimization
/cai:refactor "memory-intensive-operations" --level 1-3 --validate --focus resources --rollback

# Caching and optimization patterns
/cai:refactor "expensive-operations" --level 5 --pattern cache --validate --rollback
```

### Legacy System Modernization
```bash
# Legacy system modernization with Mikado Method
/cai:refactor "legacy-erp-module" --mikado --parallel-change --tree --validate --level 1-6

# Gradual legacy refactoring with safety measures
/cai:refactor "mainframe-integration" --level 1-4 --baby-steps --rollback --validate --test-first

# Legacy code quality improvement
/cai:refactor "vintage-codebase" --level 1-3 --validate --rollback --dry-run

# Legacy architecture modernization
/cai:refactor "monolithic-legacy-app" --mikado --level 4-6 --parallel-change --validate --rollback
```

### Integration Workflow Examples
```bash
# Code quality improvement before feature development
/cai:refactor "target-module" --level 1-3 --validate --rollback
/cai:develop "new-feature-implementation" --outside-in --real-system --validate

# Architectural refactoring before system enhancement
/cai:refactor "core-architecture" --mikado --level 4-6 --validate --test-first
/cai:architect "enhanced-system-design" --style microservices --focus scalability

# Legacy modernization workflow
/cai:brownfield "legacy-system-analysis" --focus debt --roadmap
/cai:refactor "identified-debt-areas" --mikado --level 1-6 --parallel-change --validate

# Quality-driven development workflow
/cai:refactor "existing-codebase" --level 1-4 --validate --test-first --rollback
/cai:develop "quality-improvements" --tdd-mode strict --mutation-testing --validate
```

### Team Coordination and Learning
```bash
# Learning-focused refactoring with comprehensive explanation
/cai:refactor "training-codebase" --level 1-3 --dry-run --validate --educational

# Code review preparation refactoring
/cai:refactor "review-candidate-code" --level 1-4 --validate --rollback --dry-run

# Pair programming refactoring session
/cai:refactor "collaborative-improvement" --level 2-4 --baby-steps --validate --interactive

# Mentoring-focused progressive refactoring
/cai:refactor "learning-project" --level 1-6 --validate --rollback --educational --baby-steps
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse refactoring target and complexity level
2. Invoke systematic-refactorer agent for progressive refactoring
3. Chain to mikado-refactoring-specialist agent for complex changes
4. Apply Level 1-6 refactoring with validation
5. Return systematically improved code with quality metrics

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-assessment:
    agent: systematic-refactorer
    task: |
      Execute Level 1-6 systematic refactoring:
      - Target: {parsed_target}
      - Level: {refactoring_level_if_specified}
      - Mikado Mode: {mikado_flag_status}

      Execute progressive refactoring including:
      - Level 1-2: Readability and complexity reduction
      - Level 3-4: Responsibilities and abstractions
      - Level 5-6: Patterns and SOLID principles

  step2-complex-refactoring:
    agent: mikado-refactoring-specialist
    condition: complex_architectural_changes || mikado_flag
    task: |
      Handle complex architectural refactoring:
      - Review systematic refactoring results
      - Apply Mikado Method for complex changes
      - Use parallel change patterns for breaking changes
      - Execute multi-class structural improvements

  step3-validation:
    agent: mutation-testing-coordinator
    task: |
      Validate refactoring quality and test effectiveness:
      - Execute mutation testing validation
      - Achieve target kill rates (≥75-80%)
      - Add property-based and model tests as needed
      - Ensure test effectiveness before advanced refactoring
```

### Arguments Processing
- Parse `[target]` argument for refactoring scope
- Apply `--level`, `--mikado`, `--parallel-change` flags to methodology
- Process `--validate`, `--safe-mode` flags for quality assurance
- Enable systematic progression through refactoring levels

### Output Generation
Return systematically refactored code including:
- Progressive Level 1-6 refactoring improvements
- Complex architectural changes via Mikado Method
- Validated test effectiveness through mutation testing
- Quality metrics demonstrating improvement