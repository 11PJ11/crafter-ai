---
agent-activation:
  required: true
  agent-id: software-crafter
  agent-name: "Crafty"
  agent-command: "*mikado"
  auto-activate: true
---

**⚠️ AGENT ACTIVATION REQUIRED**

This task requires the **Crafty** agent (software-crafter) for execution.

**To activate**: Type `@software-crafter` in the conversation.

Once activated, use the agent's `*help` command to see available operations.

---

# MIKADO: Complex Refactoring Roadmaps with Visual Tracking

## Overview

Execute complex refactoring operations using enhanced Mikado Method with discovery-tracking commits, exhaustive exploration, and visual architecture coordination.

## Mandatory Pre-Execution Steps

1. **Mikado Agent Activation**: Activate software-crafter (Crafty) with complete Mikado Method methodology
2. **Architecture Integration**: Coordinate with architecture-diagram-manager for visual tracking
3. **Baseline Establishment**: Create pre-refactoring baseline and commit current state

## Execution Flow

### Phase 1: Enhanced Mikado Method Activation

**Primary Agent**: software-crafter (Crafty)
**Command**: `*mikado`

**Enhanced Mikado Methodology**:

```
🌳 MIKADO METHOD - SYSTEMATIC COMPLEX REFACTORING

Revolutionary implementation with discovery-tracking commits and exhaustive exploration:

ENHANCED FEATURES:
- Discovery-tracking commits capture every exploration attempt
- Exhaustive exploration ensures all dependencies identified
- Concrete node specification with imperative directives
- Stakeholder communication through commit messages
- Complete audit trail of refactoring decisions
- Parallel change pattern integration for safe transformation

Mikado Method handles complex architectural refactorings that span multiple classes.
```

**Enhanced Discovery Process**:

```yaml
discovery_tracking_methodology:
  exploration_commit_pattern:
    purpose: "Track every exploration attempt, even failed ones"
    commit_format: "🔍 Explore: [Concrete imperative directive] - [Outcome]"
    examples:
      - "🔍 Explore: Extract UserService interface - Revealed 15 coupling points"
      - "🔍 Explore: Move validation to domain layer - Blocked by database dependencies"
      - "🔍 Explore: Replace inheritance with composition - Success, ready for implementation"

  exhaustive_exploration_protocol:
    principle: "Leave no stone unturned in dependency analysis"
    approach:
      - "Attempt every possible refactoring direction"
      - "Document all discovered dependencies and blockers"
      - "Track exploration depth and complexity"
      - "Identify optimal refactoring sequence"

  concrete_node_specification:
    directive_format: "Imperative action statements that are immediately actionable"
    examples:
      - "Extract IUserRepository interface"
      - "Move EmailValidator to Domain.Validation namespace"
      - "Replace UserType enum with UserRole value object"
      - "Inline TemporaryDataHolder class"
```

### Phase 2: Mikado Graph Construction with Visual Integration

**Primary Agent**: software-crafter (Crafty)
**Secondary Agent**: architecture-diagram-manager (Archer)
**Command**: `*create-tree`

**Mikado Graph Visualization**:

```yaml
mikado_graph_structure:
  goal_node:
    definition: "The target architectural state we want to achieve"
    specification: "Concrete, measurable, and time-bound objective"
    example: "Replace legacy UserManager with hexagonal architecture pattern"

  dependency_nodes:
    definition: "Prerequisites that must be completed before goal achievement"
    discovery_method: "Exhaustive exploration with discovery-tracking commits"
    specification_requirements:
      - "Imperative action statements"
      - "Clear success criteria"
      - "Estimated complexity and effort"
      - "Dependencies on other nodes"

  exploration_nodes:
    definition: "Failed attempts and learning captured through discovery commits"
    purpose: "Preserve organizational learning and prevent repeated failures"
    tracking: "Commit hash references to exploration attempts"

visual_integration:
  dependency_diagrams:
    purpose: "Visualize Mikado graph structure and dependencies"
    format: "Interactive SVG with clickable nodes and commit references"
    stakeholder_view: "Business-friendly representation of refactoring progress"

  progress_tracking:
    purpose: "Real-time visualization of refactoring completion"
    indicators: "Color-coded nodes (red=blocked, yellow=in-progress, green=complete)"
    timeline: "Estimated completion dates and critical path analysis"
```

### Phase 3: Parallel Change Implementation

**Agent**: software-crafter (Crafty)
**Command**: `*execute-leaves`

**Parallel Change Strategy**:

```yaml
parallel_change_execution:
  expand_phase:
    description: "Create new implementation alongside existing code"
    safety_approach: "Both old and new implementations work simultaneously"
    implementation_steps:
      - "Create new interfaces and classes without breaking existing code"
      - "Implement new functionality with comprehensive test coverage"
      - "Validate new implementation works correctly in isolation"
      - "Establish migration path and compatibility layer"

  migrate_phase:
    description: "Gradually switch consumers to new implementation"
    incremental_approach: "One consumer at a time with validation at each step"
    migration_steps:
      - "Identify all consumers of old implementation"
      - "Create migration plan with risk assessment"
      - "Switch consumers one by one with validation"
      - "Monitor system behavior after each migration"

  contract_phase:
    description: "Remove old implementation once migration complete"
    cleanup_approach: "Systematic removal with safety validation"
    cleanup_steps:
      - "Verify all consumers successfully migrated"
      - "Remove old implementation code and tests"
      - "Clean up temporary compatibility layers"
      - "Update documentation and architecture diagrams"
```

### Phase 4: Discovery-Tracking Commit Strategy

**Agent**: software-crafter (Crafty)
**Command**: `*track-discovery`

**Enhanced Commit Strategy**:

```bash
# DISCOVERY COMMITS - Track every exploration attempt
git commit -m "🔍 Explore: Extract IPaymentService interface
- Discovered: 12 classes directly depend on PaymentService
- Blocker: PaymentService tightly coupled to EmailService
- Next: Need to extract IEmailService first
- Learning: Circular dependency between Payment and Notification"

# IMPLEMENTATION COMMITS - Actual refactoring work
git commit -m "✅ Extract IEmailService interface
- Completed prerequisite for Payment service extraction
- Created interface with 3 core methods
- Updated 8 consuming classes to use interface
- All tests passing, ready for next Mikado node"

# STAKEHOLDER COMMITS - Business communication
git commit -m "🎯 Milestone: User management refactoring 40% complete
- Business Impact: Reduced coupling enables feature velocity
- Technical Progress: 4 of 10 Mikado nodes completed
- Next Phase: Payment service extraction (Est. 2 days)
- Risk Status: Green - no blockers identified"
```

### Phase 5: Progressive Refactoring Integration

**Agent**: software-crafter (Crafty)
**Command**: `*progressive`

**Mikado + Systematic Refactoring Integration**:

```yaml
collaboration_patterns:
  mikado_leads_strategy:
    responsibility: "Overall refactoring roadmap and dependency management"
    scope: "Complex, multi-class architectural changes"
    output: "Mikado graph with concrete actionable nodes"

  systematic_refactorer_executes_nodes:
    responsibility: "Execute individual Mikado nodes using six-level hierarchy"
    scope: "Code quality improvements within each node"
    integration: "Apply Level 1-6 refactoring during node implementation"

  combined_safety_protocol:
    mikado_safety: "Parallel change pattern prevents breaking changes"
    systematic_safety: "Progressive refactoring maintains code quality"
    combined_approach: "Safe transformation with continuous quality improvement"

refactoring_level_integration:
  node_implementation_process:
    1. "Mikado node specification (concrete imperative directive)"
    2. "Systematic refactoring Level 1-2 (readability and complexity)"
    3. "Mikado parallel change implementation (expand-migrate-contract)"
    4. "Systematic refactoring Level 3-4 (responsibilities and abstractions)"
    5. "Mikado dependency validation and graph update"
    6. "Systematic refactoring Level 5-6 (patterns and SOLID principles)"
```

## Advanced Mikado Method Features

### Exhaustive Exploration Protocol

```yaml
exploration_methodology:
  systematic_investigation:
    approach: "Attempt every possible refactoring direction"
    documentation: "Record all attempts, successes, and failures"
    learning_capture: "Preserve organizational knowledge through commits"

  exploration_categories:
    structural_explorations:
      - "Class extraction and interface creation attempts"
      - "Method movement and responsibility redistribution"
      - "Inheritance hierarchy modifications"
      - "Composition vs inheritance trade-offs"

    behavioral_explorations:
      - "Algorithm improvements and optimization attempts"
      - "Error handling and resilience enhancements"
      - "Performance optimization experiments"
      - "Security hardening and validation improvements"

    architectural_explorations:
      - "Design pattern application experiments"
      - "Component boundary redefinition attempts"
      - "Integration pattern modifications"
      - "Data access layer restructuring"
```

### Stakeholder Communication Framework

```yaml
stakeholder_communication:
  business_stakeholder_updates:
    frequency: "Weekly milestone commits"
    content: "Business impact, progress percentage, timeline updates"
    format: "Non-technical language with clear business value"

  technical_stakeholder_updates:
    frequency: "Daily discovery and implementation commits"
    content: "Technical progress, dependencies discovered, implementation details"
    format: "Technical details with architectural context"

  management_stakeholder_updates:
    frequency: "Sprint boundary milestone commits"
    content: "Risk assessment, resource needs, timeline adjustments"
    format: "Executive summary with decision requirements"
```

## Risk Management and Safety Protocols

### Mikado Method Risk Mitigation

```yaml
risk_mitigation_strategies:
  discovery_risk_management:
    incomplete_exploration: "Exhaustive exploration protocol prevents missed dependencies"
    analysis_paralysis: "Time-boxed exploration with mandatory decision points"
    scope_creep: "Concrete node specification limits implementation scope"

  implementation_risk_management:
    breaking_changes: "Parallel change pattern ensures system always works"
    integration_failures: "Incremental migration with validation at each step"
    rollback_complexity: "Discovery commits provide detailed rollback guidance"

  organizational_risk_management:
    knowledge_loss: "Discovery commits capture all learning and context"
    team_coordination: "Stakeholder communication commits align expectations"
    timeline_uncertainty: "Progressive exploration provides accurate estimates"
```

## Output Artifacts

### Mikado Method Deliverables

1. **MIKADO_GRAPH.svg** - Visual representation of refactoring dependencies
2. **DISCOVERY_LOG.md** - Complete exploration history with commit references
3. **REFACTORING_ROADMAP.md** - Prioritized sequence of refactoring nodes
4. **PARALLEL_CHANGE_PLAN.md** - Detailed implementation strategy for each node
5. **STAKEHOLDER_UPDATES.md** - Communication history and progress tracking

### Integration Documentation

1. **ARCHITECTURE_EVOLUTION.md** - Before/after architecture comparison
2. **QUALITY_IMPROVEMENTS.md** - Code quality metrics and improvements
3. **RISK_ASSESSMENT.md** - Risk analysis and mitigation strategies
4. **LESSONS_LEARNED.md** - Organizational learning and best practices
5. **FUTURE_ROADMAP.md** - Next iteration planning and opportunities

## Quality Gates

### Mikado Method Validation

- [ ] **Complete Exploration**: All dependencies identified through exhaustive exploration
- [ ] **Concrete Specifications**: All nodes have imperative, actionable directives
- [ ] **Discovery Tracking**: All exploration attempts documented with commits
- [ ] **Visual Integration**: Mikado graph visualized and stakeholder-accessible
- [ ] **Safety Protocol**: Parallel change pattern implemented for all nodes

### Integration Quality Validation

- [ ] **Systematic Refactoring**: Six-level hierarchy applied during node implementation
- [ ] **Architecture Compliance**: Refactoring aligns with architectural design
- [ ] **Test Coverage**: All refactoring validated through comprehensive testing
- [ ] **Performance Validation**: No performance degradation from refactoring
- [ ] **Stakeholder Communication**: Regular updates and alignment maintained

## Success Criteria

- Complex refactoring completed using enhanced Mikado Method
- All dependencies identified through exhaustive exploration
- Discovery commits provide complete audit trail and learning
- Parallel change pattern ensures system stability throughout
- Visual tracking and stakeholder communication effective
- Integration with systematic refactoring maintains code quality
- Organizational learning captured and preserved

## Failure Recovery

If Mikado refactoring fails:

1. **Exploration Incomplete**: Continue exhaustive exploration to identify missed dependencies
2. **Implementation Blocked**: Use discovery commits to understand blockers and adjust plan
3. **System Instability**: Leverage parallel change rollback to restore stability
4. **Stakeholder Misalignment**: Review communication commits and realign expectations
5. **Quality Degradation**: Engage systematic-refactorer for code quality restoration

## Integration with Other Agents

### Cross-Agent Collaboration

```yaml
agent_integration:
  walking_skeleton_helper:
    collaboration: "Validate refactoring against end-to-end architecture"
    use_case: "Ensure refactoring doesn't break critical system flows"

  root_cause_analyzer:
    collaboration: "Analyze complex problems requiring refactoring"
    use_case: "Use root cause analysis to identify refactoring priorities"

  test_first_developer:
    collaboration: "Ensure refactoring maintains ATDD compliance"
    use_case: "Validate refactoring preserves acceptance test coverage"
```

## Methodology Completion

**Enhanced Mikado Method successfully executed with complete organizational learning, stakeholder communication, and architectural improvement.**
