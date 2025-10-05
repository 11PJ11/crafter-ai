---
agent-activation:
  required: true
  agent-id: software-crafter
  agent-name: "Crafty"
  agent-command: "*refactor"
  auto-activate: true
---

**⚠️ AGENT ACTIVATION REQUIRED**

This task requires the **Crafty** agent (software-crafter) for execution.

**To activate**: Type `@software-crafter` in the conversation.

Once activated, use the agent's `*help` command to see available operations.

---

# DW-REFACTOR: Systematic Code Analysis and Refactoring Execution

## Overview

Execute systematic refactoring of existing codebases through progressive code quality improvement, Mikado Method planning, and six-level refactoring hierarchy implementation.

## Command Syntax

```bash
# Analysis and planning
dw-refactor --levels=1,2,3 --plan=true --mikado=true [target]
dw-refactor --analyze --scope=file|module|project --output=docs/dw/refactoring/analysis.md

# Execution
dw-refactor --execute=docs/dw/refactoring/analysis.md [options]
dw-refactor --apply=docs/dw/refactoring/mikado-graph.md --parallel-change=true
```

## Mandatory Pre-Execution Steps

1. **Codebase Analysis**: Validate target codebase and establish baseline metrics
2. **Agent Activation**: Activate software-crafter (Crafty) with complete refactoring methodology
3. **Backup Creation**: Create git backup and establish rollback strategy
4. **Documentation Structure**: Ensure docs/dw/refactoring/ directory exists

## Command Parameters

### Analysis Parameters

- `--levels=N,N,N`: Target refactoring levels (1-6, comma-separated)
- `--scope=TARGET`: Analysis scope (file, module, project, system)
- `--plan=BOOL`: Generate refactoring plan (default: false)
- `--mikado=BOOL`: Use Mikado Method for complex refactorings (default: false)
- `--analyze`: Perform code quality analysis without execution
- `--output=FILE`: Output analysis results to docs/dw/refactoring/ (default: docs/dw/refactoring/analysis.md)

### Execution Parameters

- `--execute=FILE`: Execute refactoring plan from docs/dw/refactoring/ file
- `--apply=FILE`: Apply Mikado refactoring graph from docs/dw/refactoring/ file
- `--parallel-change=BOOL`: Use parallel change pattern for safety (default: true)
- `--auto-commit=BOOL`: Auto-commit after each successful refactoring (default: true)
- `--validate=BOOL`: Run validation after each change (default: true)

## Execution Flow

### Phase 1: Codebase Analysis and Quality Assessment

**Primary Agent**: software-crafter (Crafty)
**Command**: `*detect-smells`

**Six-Level Refactoring Assessment**:

```
🔍 REFACTOR WAVE - SYSTEMATIC CODE QUALITY IMPROVEMENT

Progressive refactoring hierarchy for comprehensive code improvement:

Level 1: 🟨 Readability (Foundation)
- Clean comments, dead code, magic strings, bad naming
- Scope optimization and clarity improvements

Level 2: 🟢 Complexity Reduction (Simplification)
- Long method extraction, duplication elimination
- Conditional simplification and complexity metrics

Level 3: 🟢 Responsibility Organization (Structure)
- Class size reduction, coupling optimization
- Feature envy resolution, intimacy reduction

Level 4: 🟢 Abstraction Refinement (Architecture)
- Parameter object creation, value objects
- Primitive obsession elimination

Level 5: 🔵 Pattern Application (Design)
- Strategy, State, Command pattern implementation
- Polymorphism over conditionals

Level 6: 🔵 SOLID++ Principles (Advanced)
- Single Responsibility, Interface Segregation
- Liskov Substitution, Dependency Inversion
```

**Analysis Output Structure**:

```yaml
analysis_results:
  scope_assessment:
    files_analyzed: "Number of files in analysis scope"
    complexity_metrics: "Cyclomatic complexity, cognitive load, nesting depth"
    quality_indicators: "Maintainability index, test coverage, documentation"
    technical_debt_estimate: "Hours to address identified issues"

  level_1_issues:
    comments: "Obsolete, how-comments, missing documentation"
    dead_code: "Unused methods, classes, imports, variables"
    magic_strings: "Hard-coded values requiring extraction"
    naming: "Unclear, misleading, or non-domain names"

  level_2_issues:
    long_methods: "Methods exceeding complexity thresholds"
    duplicated_code: "Identical or similar code blocks"
    complexity_hotspots: "High cyclomatic complexity areas"

  level_3_issues:
    large_classes: "Classes violating Single Responsibility"
    feature_envy: "Methods operating on other classes' data"
    inappropriate_intimacy: "High coupling between classes"
    data_classes: "Classes with only data, no behavior"

  level_4_issues:
    long_parameter_lists: "Methods with too many parameters"
    data_clumps: "Related data appearing together repeatedly"
    primitive_obsession: "Overuse of primitive types for domain concepts"

  level_5_opportunities:
    switch_statements: "Conditionals suitable for Strategy pattern"
    state_machines: "Complex state-dependent behavior"
    command_structures: "Operations that could be encapsulated"

  level_6_violations:
    srp_violations: "Classes with multiple reasons to change"
    interface_issues: "Fat interfaces, refused bequest"
    dependency_problems: "Concrete dependencies, inversion opportunities"
```

### Phase 2: Refactoring Strategy Planning

**Agent**: software-crafter (Crafty)
**Command**: `*progressive`

**Planning Decision Matrix**:

```yaml
refactoring_strategy_selection:
  simple_refactoring:
    criteria: "Single file, levels 1-2, low complexity"
    approach: "Direct systematic refactoring with immediate execution"
    tools: "Six-level hierarchy, automated validation"

  complex_refactoring:
    criteria: "Multiple files, levels 3-6, high complexity, architectural changes"
    approach: "Mikado Method with discovery-tracking and visual planning"
    tools: "Enhanced Mikado graph, parallel change patterns, staged execution"

  hybrid_approach:
    criteria: "Mixed complexity, partial architectural impact"
    approach: "Systematic refactoring with Mikado planning for complex parts"
    tools: "Combined methodology, selective tool application"
```

### Phase 3: Mikado Method Integration (for Complex Refactorings)

**Primary Agent**: software-crafter (Crafty)
**Secondary Agent**: architecture-diagram-manager (Archer)
**Command**: `*mikado`

**Enhanced Mikado Refactoring Process**:

```yaml
mikado_refactoring_execution:
  discovery_phase:
    exploration_commits: "Track every refactoring attempt and outcome"
    dependency_mapping: "Exhaustive analysis of refactoring dependencies"
    blocker_identification: "Catalog all obstacles and prerequisites"

  graph_construction:
    concrete_nodes: "Imperative, actionable refactoring directives"
    dependency_edges: "Clear prerequisite relationships"
    visual_representation: "Architecture diagrams showing refactoring flow"

  execution_strategy:
    leaf_first: "Execute leaf nodes (no dependencies) first"
    progressive_validation: "Test and validate after each node completion"
    rollback_capability: "Git-based rollback for failed attempts"
    stakeholder_communication: "Clear commit messages documenting progress"
```

### Phase 4: Systematic Refactoring Execution

**Agent**: software-crafter (Crafty)
**Command**: `*refactor`

**Execution Strategy Based on Complexity**:

**For Simple Refactorings (Levels 1-2)**:

```yaml
immediate_execution:
  approach: "Direct application with real-time validation"
  process:
    - "Apply refactoring transformation"
    - "Run automated tests to ensure no regression"
    - "Validate code quality improvement metrics"
    - "Commit successful changes with descriptive messages"
  safety_measures:
    - "One refactoring at a time"
    - "Immediate rollback on test failures"
    - "Quality gate validation before commit"
```

**For Complex Refactorings (Levels 3-6)**:

```yaml
staged_execution:
  approach: "Parallel change pattern with staged migration"
  process:
    - "EXPAND: Create new structure alongside existing"
    - "MIGRATE: Gradually move consumers to new structure"
    - "CONTRACT: Remove old structure after migration complete"
  safety_measures:
    - "Both old and new structures work during migration"
    - "Progressive consumer migration with validation"
    - "Comprehensive testing at each stage"
```

### Phase 5: Quality Validation and Metrics

**Agent**: software-crafter (Crafty)
**Command**: `*quality-metrics`

**Validation Framework**:

```yaml
quality_validation:
  metrics_comparison:
    before_metrics: "Baseline complexity, maintainability, test coverage"
    after_metrics: "Post-refactoring quality measurements"
    improvement_analysis: "Quantitative improvement assessment"

  regression_testing:
    unit_tests: "All existing unit tests must pass"
    integration_tests: "System integration validation"
    acceptance_tests: "Business functionality verification"

  architectural_validation:
    design_principles: "SOLID principles compliance check"
    pattern_implementation: "Design pattern correctness validation"
    coupling_analysis: "Coupling and cohesion metrics improvement"
```

## Output Artifacts

All output files are created in `docs/dw/refactoring/` directory:

### Analysis Phase Deliverables

1. **docs/dw/refactoring/analysis.md** - Comprehensive code quality assessment
2. **docs/dw/refactoring/quality-metrics.md** - Before/after metrics and improvement tracking
3. **docs/dw/refactoring/plan.md** - Detailed execution plan with priorities
4. **docs/dw/refactoring/technical-debt-assessment.md** - Debt quantification and payoff strategy

### Planning Phase Deliverables

1. **docs/dw/refactoring/mikado-graph.md** - Visual refactoring dependency graph (if --mikado=true)
2. **docs/dw/refactoring/roadmap.md** - Strategic refactoring sequence
3. **docs/dw/refactoring/risk-assessment.md** - Refactoring risks and mitigation strategies
4. **docs/dw/refactoring/parallel-change-plan.md** - Safe transformation strategy

### Execution Phase Deliverables

1. **docs/dw/refactoring/execution-log.md** - Detailed execution log with outcomes
2. **docs/dw/refactoring/quality-improvement-report.md** - Metrics-based improvement validation
3. **docs/dw/refactoring/regression-test-results.md** - Comprehensive testing validation
4. **docs/dw/refactoring/stakeholder-summary.md** - Executive summary of improvements achieved

## Quality Gates

### Pre-Execution Validation

- [ ] **Baseline Established**: Current state committed and metrics captured
- [ ] **Test Suite Complete**: Comprehensive test coverage for refactoring scope
- [ ] **Backup Strategy**: Git-based rollback strategy confirmed
- [ ] **Stakeholder Buy-in**: Refactoring objectives and timeline approved

### Execution Validation

- [ ] **No Regression**: All existing tests continue to pass
- [ ] **Quality Improvement**: Measurable code quality metrics improvement
- [ ] **Design Compliance**: Adherence to design principles and patterns
- [ ] **Documentation Updated**: Code documentation reflects refactoring changes

### Completion Validation

- [ ] **Objectives Met**: All specified refactoring levels successfully applied
- [ ] **Performance Maintained**: No performance regression introduced
- [ ] **Maintainability Improved**: Demonstrable maintainability enhancement
- [ ] **Technical Debt Reduced**: Quantified technical debt reduction achieved

## Example Usage Scenarios

### Basic Analysis and Simple Refactoring

```bash
# Analyze file-level code quality issues
dw-refactor --analyze --scope=file --levels=1,2 --output=docs/dw/refactoring/user-service-analysis.md src/UserService.cs

# Execute simple readability and complexity improvements (auto-commits by default)
dw-refactor --execute=docs/dw/refactoring/user-service-analysis.md
```

### Complex Architectural Refactoring

```bash
# Plan complex refactoring with Mikado Method
dw-refactor --scope=module --levels=3,4,5,6 --plan=true --mikado=true src/

# Execute planned refactoring with parallel change pattern (auto-commits by default)
dw-refactor --apply=docs/dw/refactoring/mikado-graph.md --parallel-change=true --validate=true
```

### Progressive Quality Improvement

```bash
# Start with foundation levels across project
dw-refactor --scope=project --levels=1,2 --plan=true

# Progress to architectural improvements
dw-refactor --scope=project --levels=3,4 --mikado=true --output=docs/dw/refactoring/architectural-improvements.md
```

## Success Criteria

- Code quality metrics demonstrably improved across targeted levels
- All existing functionality preserved (no regression)
- Technical debt reduced with quantifiable measurements
- Refactoring objectives achieved within planned timeline
- Stakeholder satisfaction with improved codebase maintainability

## Failure Recovery

If refactoring fails:

1. **Git Rollback**: Return to pre-refactoring baseline state
2. **Analysis Review**: Re-examine analysis for missed dependencies
3. **Strategy Adjustment**: Modify approach based on failure learnings
4. **Incremental Retry**: Attempt smaller, more focused refactoring scope

## Integration with 5D-WAVE Methodology

### DISCUSS Integration

- Stakeholder alignment on refactoring objectives and priorities
- Business impact assessment of technical debt reduction

### DESIGN Integration

- Architecture improvement planning and pattern application
- Design principle compliance validation

### DISTILL Integration

- Test-driven refactoring validation and acceptance criteria
- Quality gate definition for refactoring success

### DEVELOP Integration

- Implementation of refactoring changes with TDD approach
- Production service integration validation

### DEMO Integration

- Stakeholder demonstration of improved code quality
- Business value realization from technical debt reduction

## Next Command Options

**Continue Development**: `dw-develop` for implementing new features on improved codebase
**Architecture Review**: `dw-design` for architectural validation post-refactoring
**Quality Demo**: `dw-demo` for stakeholder presentation of improvements
