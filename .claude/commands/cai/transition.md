# /cai:transition - Planning to Execution Bridge

```yaml
---
command: "/cai:transition"
category: "Planning & Orchestration"
purpose: "Bridge planning phase to execution with context preservation"
wave-enabled: true
performance-profile: "complex"
---
```

## Overview

Critical phase transition management from planning phase to execution phase, ensuring seamless context preservation and proper document sharding for development readiness.

## Auto-Persona Activation
- **Phase Transition Manager**: Transition orchestration and validation (mandatory)
- **Story Context Manager**: Hyper-detailed story creation (mandatory)
- **Architect**: Architectural context preservation (conditional)
- **QA**: Quality validation during transition (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic transition planning and validation)
- **Secondary**: Context7 (transition patterns and best practices)
- **Avoided**: Magic (focuses on document processing over generation)

## Tool Orchestration
- **Task**: Specialized transition agents activation
- **Read**: Planning documents analysis and validation
- **Write**: Sharded documents and context-embedded stories
- **Edit**: Document refinement and context integration
- **Grep**: Context analysis and cross-reference validation

## Agent Flow
```yaml
phase-transition-manager:
  phase_1_validation:
    - Validates planning completeness (requirements, architecture, acceptance)
    - Assesses document quality against defined standards
    - Confirms stakeholder approval and sign-offs
    - Checks consistency across planning documents

  phase_2_preparation:
    - Analyzes sharding requirements based on project complexity
    - Executes epic-level document sharding
    - Executes story-level document sharding with context preservation
    - Executes architecture sharding by components and patterns

  phase_3_validation:
    - Validates context preservation across all sharded documents
    - Tests development readiness of story documents
    - Confirms wave coordinator can begin execution
    - Creates transition documentation and metadata

story-context-manager:
  context_embedding:
    - Creates hyper-detailed development stories
    - Embeds full architectural context and constraints
    - Includes implementation guidance and technical approach
    - Specifies detailed acceptance criteria and quality gates
    - Anticipates common pitfalls and provides prevention guidance
```

## Arguments

### Basic Usage
```bash
/cai:transition
```

### Advanced Usage
```bash
/cai:transition --validate --sharding <strategy> --context-level <depth>
```

### Validation Control
- `--validate`: Add comprehensive validation steps
  - Performs thorough planning completeness assessment across all required artifacts
  - Validates document quality, stakeholder approvals, and cross-document consistency
  - Includes context preservation validation and development readiness assessment
  - Ensures all quality gates are met before proceeding to execution phase
- `--dry-run`: Show planned transition without execution
  - Analyzes transition requirements and shows planned sharding strategy
  - Provides transition preview with context preservation assessment
  - Identifies potential issues and provides mitigation recommendations
  - Allows validation of transition approach before committing to execution
- `--rollback-points`: Create multiple rollback checkpoints
  - Creates git commits at each major transition milestone for safety
  - Enables rapid recovery if transition encounters issues or failures
  - Provides clear history of transition steps for debugging and analysis
  - Maintains clean rollback points for planning phase restoration if needed
- `--completeness-check`: Thorough planning completeness assessment
  - Validates all required planning artifacts are present and complete
  - Checks requirements, architecture, and acceptance criteria documentation quality
  - Ensures stakeholder approvals and sign-offs are properly documented
  - Provides comprehensive readiness assessment for execution phase transition

### Sharding Strategy
- `--sharding epic`: Focus on epic-level document breakdown
  - Breaks down requirements into epic-level documents with business context
  - Groups related user stories into cohesive business-focused epics
  - Maintains business value rationale and stakeholder context at epic level
  - Creates epic-to-architecture links for technical implementation guidance
- `--sharding story`: Detailed story-level sharding with context embedding
  - Creates self-contained development stories with embedded architectural context
  - Includes implementation guidance, technical approach, and quality requirements
  - Embeds acceptance criteria and validation requirements directly in stories
  - Provides comprehensive development guidance to prevent common pitfalls
- `--sharding architecture`: Component-level architecture sharding
  - Separates architecture documentation by system components and layers
  - Creates component-specific implementation guidance and constraints
  - Documents integration patterns, API specifications, and design decisions
  - Links architectural decisions to implementation stories and requirements
- `--sharding comprehensive`: Full multi-level sharding approach
  - Applies all sharding strategies (epic, story, and architecture) systematically
  - Creates complete document hierarchy with preserved context relationships
  - Maximizes development readiness through comprehensive context embedding
  - Provides full traceability from business requirements to technical implementation

### Context Preservation
- `--context-level minimal`: Basic context preservation
  - Maintains essential business and technical context during document sharding
  - Preserves critical cross-references and links between sharded documents
  - Focuses on immediate development needs with streamlined context
  - Suitable for smaller projects or well-understood domains
- `--context-level standard`: Standard context embedding
  - Includes comprehensive business context, architectural guidance, and acceptance criteria
  - Embeds implementation approach, testing strategy, and quality requirements
  - Provides balanced context depth for typical development scenarios
  - Ensures development teams have sufficient context for autonomous work
- `--context-level hyper-detailed`: Maximum context preservation
  - Creates exhaustively detailed development stories with complete embedded context
  - Includes business rationale, architectural constraints, implementation guidance
  - Embeds error prevention guidance, common pitfalls, and validation checkpoints
  - Provides maximum development autonomy through comprehensive context embedding
- `--preserve-links`: Maintain all cross-document references
  - Ensures all cross-references and links between documents are maintained
  - Creates bidirectional links between epics, stories, and architecture components
  - Maintains traceability from requirements through implementation to validation
  - Enables navigation between related documents during development process

## Planning Validation Framework

### Required Planning Artifacts
```yaml
requirements_documentation:
  required_files:
    - requirements.md: "Complete business requirements document"
    - stakeholder-analysis.md: "Stakeholder needs and constraints analysis"
    - business-constraints.md: "Business limitations and requirements"
  validation_criteria:
    - requirements_complete: "All user stories and acceptance criteria defined"
    - stakeholder_approval: "Key stakeholders have reviewed and approved"
    - constraints_documented: "All business and technical constraints identified"

architecture_documentation:
  required_files:
    - architecture.md: "Complete system architecture specification"
    - technology-decisions.md: "Technology stack and rationale"
    - architecture-diagrams.md: "Architecture diagrams and documentation"
  validation_criteria:
    - architecture_complete: "All system components and interactions defined"
    - technology_selected: "Technology stack chosen and documented"
    - patterns_documented: "Design patterns and decisions recorded"

acceptance_criteria:
  required_files:
    - acceptance-tests.md: "High-level acceptance test scenarios"
    - test-scenarios.md: "Detailed test scenarios and validation"
    - validation-criteria.md: "Quality gates and acceptance criteria"
  validation_criteria:
    - scenarios_comprehensive: "Test scenarios cover all major functionality"
    - criteria_measurable: "Acceptance criteria are specific and testable"
    - quality_gates_defined: "Performance, security, quality requirements specified"
```

### Planning Completeness Assessment
- **Document Quality Gates**: Requirements, architecture, and acceptance criteria quality
- **Stakeholder Validation**: Business, technical, and quality stakeholder approval
- **Cross-Document Consistency**: Alignment and consistency across all planning documents

## Document Sharding Strategy

### Epic-Level Sharding
```yaml
epic_sharding:
  source_document: "requirements.md"
  output_structure:
    - "epics/epic-{id}-{name}.md": "Business context and story grouping"
    - "epics/epic-{id}-context.md": "Epic context and cross-references"
  sharding_rules:
    - "Group related user stories into cohesive epics"
    - "Maintain business context and rationale for each epic"
    - "Include acceptance criteria and success metrics"
    - "Reference architectural components affected by epic"
```

### Story-Level Sharding
```yaml
story_sharding:
  source_documents:
    - "Epic documents from epic-level sharding"
    - "architecture.md"
    - "acceptance-tests.md"
  output_structure:
    - "stories/story-{id}-{name}.md": "Self-contained development story"
    - "stories/story-{id}-context.md": "Additional context and references"
  context_embedding:
    - "Create self-contained story documents with embedded context"
    - "Include relevant architectural context and constraints"
    - "Embed implementation guidance and technical approach"
    - "Specify detailed acceptance criteria and validation requirements"
```

### Architecture Sharding
```yaml
architecture_sharding:
  source_document: "architecture.md"
  output_structure:
    - "architecture/component-{name}.md": "Component-specific documentation"
    - "architecture/integration-{name}.md": "Integration pattern documentation"
    - "architecture/patterns-{category}.md": "Pattern-specific guidance"
  sharding_rules:
    - "Separate architecture by system components and layers"
    - "Document integration patterns and API specifications"
    - "Isolate architectural patterns and design decisions"
    - "Include implementation guidance for each architectural element"
```

## Context Preservation Mechanisms

### Cross-Reference System
```yaml
epic_to_story_links:
  format: "## Epic Context\n**Parent Epic**: [epic-name](../epics/epic-{id}-{name}.md)\n**Business Context**: {business-value}"
  purpose: "Maintain business context connection from epic to story"

story_to_architecture_links:
  format: "## Architectural Context\n**Affected Components**: {component-list}\n**Architecture Reference**: [component-name](../architecture/component-{name}.md)"
  purpose: "Connect story implementation to architectural decisions"

acceptance_criteria_links:
  format: "## Test Context\n**Acceptance Scenarios**: {scenario-references}\n**Quality Gates**: {quality-requirements}"
  purpose: "Embed acceptance criteria directly in development stories"
```

### Hyper-Detailed Story Template
- **Business Context**: User story, business value, success metrics
- **Architectural Context**: System components, integration points, technology stack
- **Implementation Guidance**: Development approach, code structure, testing strategy
- **Validation Embedded**: Acceptance criteria, quality gates, definition of done
- **Error Prevention**: Common pitfalls, implementation checkpoints, validation approach

## Quality Gates

### Transition Validation
- **Planning Completeness**: All required planning artifacts present and complete
- **Document Quality**: Planning documents meet defined quality standards
- **Stakeholder Approval**: All necessary stakeholder sign-offs documented
- **Cross-Document Consistency**: No major inconsistencies between planning documents

### Sharding Quality
- **Context Preservation**: All critical context preserved in sharded documents
- **Cross-References**: Proper links and references established between documents
- **Information Completeness**: No information loss during sharding process
- **Development Readiness**: Sharded stories contain sufficient detail for implementation

### Execution Readiness
- **Story Quality**: Stories are self-contained and implementation-ready
- **Architectural Integration**: Architecture context properly embedded
- **Acceptance Integration**: Validation criteria integrated into development stories
- **Wave Coordinator Readiness**: Execution phase can begin with available artifacts

## Output Artifacts

### Sharded Development Artifacts
- `${DOCS_PATH}/epics/`: Epic-level documents with business context
- `${DOCS_PATH}/stories/`: Hyper-detailed development stories with embedded context
- `${DOCS_PATH}/architecture/`: Component-level architecture documentation
- `${STATE_PATH}/phase-transition-complete.json`: Transition completion confirmation

### Transition Documentation
- **Transition Log**: Detailed record of transition process and decisions
- **Context Preservation Report**: Evidence of context preservation across documents
- **Sharding Analysis**: Analysis of sharding strategy and effectiveness
- **Execution Readiness Assessment**: Validation of development readiness

## Examples

### Standard Transition
```bash
/cai:transition --validate
```

### Comprehensive Sharding
```bash
/cai:transition --sharding comprehensive --context-level hyper-detailed
```

### Safe Transition with Rollback
```bash
/cai:transition --validate --rollback-points --dry-run
```

### Architecture-Focused Transition
```bash
/cai:transition --sharding architecture --preserve-links
```

### Quality-Validated Transition
```bash
/cai:transition --completeness-check --validate --context-level standard
```

## Comprehensive Usage Examples

### Comprehensive Transition Workflows
```bash
# Full transition with maximum validation and context preservation
/cai:transition --validate --sharding comprehensive --context-level hyper-detailed --preserve-links --completeness-check

# Safe transition with comprehensive rollback points
/cai:transition --validate --sharding comprehensive --rollback-points --context-level standard --preserve-links

# Preview comprehensive transition before execution
/cai:transition --dry-run --sharding comprehensive --context-level hyper-detailed --validate --completeness-check

# Enterprise-level transition with maximum context embedding
/cai:transition --sharding comprehensive --context-level hyper-detailed --preserve-links --validate --rollback-points
```

### Sharding Strategy Focused Transitions
```bash
# Epic-focused transition for business-driven development
/cai:transition --sharding epic --context-level standard --validate --preserve-links

# Story-level sharding with embedded development context
/cai:transition --sharding story --context-level hyper-detailed --validate --completeness-check

# Architecture-driven transition for technical implementation
/cai:transition --sharding architecture --context-level standard --preserve-links --validate

# Multi-level sharding with balanced context preservation
/cai:transition --sharding epic --sharding story --sharding architecture --context-level standard --validate
```

### Context Preservation Strategies
```bash
# Maximum context preservation for complex projects
/cai:transition --context-level hyper-detailed --preserve-links --validate --sharding comprehensive

# Minimal context for rapid development
/cai:transition --context-level minimal --sharding story --validate

# Standard context for typical development scenarios
/cai:transition --context-level standard --sharding comprehensive --preserve-links --validate

# Focused context preservation with architectural emphasis
/cai:transition --context-level standard --sharding architecture --preserve-links --completeness-check
```

### Validation-Focused Transitions
```bash
# Comprehensive validation before transition execution
/cai:transition --validate --completeness-check --dry-run --context-level standard --preserve-links

# Thorough planning validation with sharding preview
/cai:transition --completeness-check --validate --dry-run --sharding comprehensive

# Quality-focused transition with rollback safety
/cai:transition --validate --completeness-check --rollback-points --context-level standard

# Pre-execution validation with comprehensive assessment
/cai:transition --validate --completeness-check --dry-run --sharding comprehensive --context-level hyper-detailed
```

### Safe Transition Approaches
```bash
# Maximum safety with preview and rollback points
/cai:transition --dry-run --rollback-points --validate --completeness-check --context-level standard

# Safe comprehensive transition with checkpoints
/cai:transition --rollback-points --validate --sharding comprehensive --context-level standard --preserve-links

# Risk-averse transition with thorough validation
/cai:transition --dry-run --validate --completeness-check --rollback-points --context-level minimal

# Conservative transition approach with safety measures
/cai:transition --validate --rollback-points --context-level standard --preserve-links --completeness-check
```

### Project-Specific Transition Strategies
```bash
# Large enterprise project transition
/cai:transition --sharding comprehensive --context-level hyper-detailed --validate --preserve-links --rollback-points --completeness-check

# Rapid development project transition
/cai:transition --context-level minimal --sharding story --validate --preserve-links

# Complex architecture project transition
/cai:transition --sharding architecture --sharding comprehensive --context-level standard --preserve-links --validate

# Legacy modernization transition
/cai:transition --validate --completeness-check --sharding comprehensive --context-level hyper-detailed --rollback-points

# Regulatory compliance project transition
/cai:transition --validate --completeness-check --context-level hyper-detailed --preserve-links --rollback-points
```

### Team and Process Transitions
```bash
# Distributed team transition with maximum context
/cai:transition --context-level hyper-detailed --preserve-links --sharding comprehensive --validate --completeness-check

# Agile team transition with story focus
/cai:transition --sharding story --context-level standard --validate --preserve-links

# Cross-functional team transition
/cai:transition --sharding comprehensive --context-level standard --validate --preserve-links --completeness-check

# Knowledge transfer focused transition
/cai:transition --context-level hyper-detailed --sharding comprehensive --preserve-links --validate
```

### Integration Workflow Examples
```bash
# Complete ATDD workflow from planning to execution
/cai:discuss "requirements" --workshop --stories --stakeholders business,technical,ux
/cai:architect "system-design" --style microservices --focus scalability --workshop
/cai:transition --validate --sharding comprehensive --context-level hyper-detailed --preserve-links

# Requirements-driven transition workflow
/cai:discuss "business-requirements" --detailed --stories --acceptance
/cai:transition --sharding epic --sharding story --context-level standard --validate --preserve-links

# Architecture-first transition workflow
/cai:architect "technical-architecture" --style hexagonal --focus maintainability --validation
/cai:transition --sharding architecture --context-level standard --preserve-links --validate

# Quality-focused transition workflow
/cai:validate --architecture --quality --threshold standard --report
/cai:transition --validate --completeness-check --sharding comprehensive --context-level standard

# Planning validation to execution workflow
/cai:validate --full --threshold standard --report
/cai:transition --validate --completeness-check --sharding comprehensive --context-level hyper-detailed --preserve-links
```

### Domain-Specific Transition Examples
```bash
# Financial services transition with comprehensive validation
/cai:transition --validate --completeness-check --context-level hyper-detailed --preserve-links --rollback-points --sharding comprehensive

# Healthcare system transition with regulatory focus
/cai:transition --validate --completeness-check --context-level hyper-detailed --sharding comprehensive --preserve-links

# E-commerce platform transition with scalability focus
/cai:transition --sharding comprehensive --context-level standard --validate --preserve-links --rollback-points

# Enterprise integration transition with architecture emphasis
/cai:transition --sharding architecture --sharding comprehensive --context-level standard --preserve-links --validate

# Startup MVP transition with rapid development focus
/cai:transition --context-level minimal --sharding story --validate --preserve-links
```

### Error Prevention and Recovery
```bash
# Maximum error prevention with comprehensive validation
/cai:transition --validate --completeness-check --dry-run --rollback-points --context-level hyper-detailed

# Recovery-focused transition with multiple checkpoints
/cai:transition --rollback-points --validate --context-level standard --preserve-links --completeness-check

# Validation-heavy transition to prevent execution issues
/cai:transition --validate --completeness-check --dry-run --sharding comprehensive --context-level standard

# Conservative approach with maximum safety measures
/cai:transition --dry-run --validate --completeness-check --rollback-points --context-level minimal --preserve-links
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse transition context and validation requirements
2. Invoke phase-transition-manager agent for planning-to-execution bridge
3. Chain to story-context-manager agent for hyper-detailed stories
4. Execute context preservation and document sharding
5. Return validated transition with development-ready stories

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-transition-management:
    agent: phase-transition-manager
    task: |
      Bridge planning phase to execution with context preservation:
      - Validation: {validate_flag_status}
      - Planning Phase: {planning_completeness_check}
      - Execution Ready: {execution_readiness_assessment}

      Execute transition management including:
      - Validate planning completeness (requirements, architecture, acceptance)
      - Execute document sharding from epics to stories
      - Preserve architectural context during transition
      - Ensure BMAD-METHOD Web UI to IDE transition patterns

  step2-story-context:
    agent: story-context-manager
    task: |
      Create hyper-detailed development stories:
      - Review transition validation from phase-transition-manager
      - Create hyper-detailed development stories with embedded context
      - Include architectural context and implementation guidance
      - Add detailed acceptance criteria and quality gates

  step3-context-validation:
    agent: pipeline-state-manager
    task: |
      Ensure pipeline state continuity:
      - Validate context preservation across phase transition
      - Setup development phase state tracking
      - Prepare for resumable development workflow
      - Maintain cross-session continuity
```

### Arguments Processing
- Parse transition context and phase requirements
- Apply `--validate`, `--comprehensive` flags to validation depth
- Process `--context-preservation` flags for continuity
- Enable document sharding and story preparation

### Output Generation
Return validated transition including:
- Planning completeness validation with architectural context preserved
- Hyper-detailed development stories with embedded guidance
- Document sharding from epics to actionable stories
- Pipeline state setup for development phase execution