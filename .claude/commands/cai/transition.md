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
- `--dry-run`: Show planned transition without execution
- `--rollback-points`: Create multiple rollback checkpoints
- `--completeness-check`: Thorough planning completeness assessment

### Sharding Strategy
- `--sharding epic`: Focus on epic-level document breakdown
- `--sharding story`: Detailed story-level sharding with context embedding
- `--sharding architecture`: Component-level architecture sharding
- `--sharding comprehensive`: Full multi-level sharding approach

### Context Preservation
- `--context-level minimal`: Basic context preservation
- `--context-level standard`: Standard context embedding
- `--context-level hyper-detailed`: Maximum context preservation
- `--preserve-links`: Maintain all cross-document references

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

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest