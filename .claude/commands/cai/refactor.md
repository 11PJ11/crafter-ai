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
  - `--level 2`: Complexity (method extraction, duplication)
  - `--level 3`: Responsibilities (class breakdown, coupling)
  - `--level 4`: Abstractions (parameter objects, value objects)
  - `--level 5`: Patterns (Strategy, State, Command)
  - `--level 6`: SOLID (advanced architectural principles)

### Complex Refactoring Control
- `--mikado`: Use Mikado Method for complex architectural changes
- `--parallel-change`: Apply parallel change pattern for breaking changes
- `--tree`: Generate and display Mikado dependency tree
- `--baby-steps`: Use baby steps protocol for safety

### Validation and Safety
- `--validate`: Add comprehensive validation steps
- `--test-first`: Ensure tests pass before refactoring
- `--rollback`: Create rollback points
- `--dry-run`: Show planned changes without execution

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

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest