---
agent-activation:
  required: true
  agent-id: solution-architect
  agent-name: "Morgan"
  agent-command: "*design-architecture"
  auto-activate: true
---

**⚠️ AGENT ACTIVATION REQUIRED**

This task requires the **Morgan** agent (solution-architect) for execution.

**To activate**: Type `@solution-architect` in the conversation.

Once activated, use the agent's `*help` command to see available operations.

---

# DW-DESIGN: Architecture Design with Visual Representation

## Overview

Execute DESIGN wave of 5D-Wave methodology through comprehensive architecture design, technology selection, and visual representation creation.

## Mandatory Pre-Execution Steps

1. **DISCUSS Wave Completion**: Validate requirements documentation and stakeholder consensus
2. **Architecture Context Loading**: Ensure complete requirements package from business-analyst
3. **Agent Coordination**: Activate solution-architect (Morgan) and architecture-diagram-manager (Archer)

## Execution Flow

### Phase 1: Architecture Foundation Design

**Primary Agent**: solution-architect (Morgan)
**Command**: `*design-architecture`

**Architecture Design Process**:

```
🏛️ DESIGN WAVE - ARCHITECTURE FOUNDATION

Transform business requirements into robust technical architecture that balances:
- Business needs with technical excellence
- Scalability with maintainability
- Performance with security
- Innovation with stability

Architecture serves business objectives while enabling quality attributes.
```

**Design Inputs from DISCUSS Wave**:

- Structured requirements document with business context
- User stories with detailed acceptance criteria
- Domain model and ubiquitous language
- Business rules and validation scenarios
- Risk assessment and mitigation strategies
- Quality attribute requirements

### Phase 2: Technology Stack Selection

**Agent Command**: `*select-technology`

**Evaluation Framework**:

```yaml
technology_selection_criteria:
  business_alignment:
    - "Support for business requirements and capabilities"
    - "Time-to-market and development velocity impact"
    - "Total cost of ownership including licensing"
    - "Vendor stability and ecosystem maturity"

  technical_excellence:
    - "Performance characteristics and scalability potential"
    - "Security features and vulnerability track record"
    - "Integration capabilities and ecosystem compatibility"
    - "Development and operational tooling quality"

  team_readiness:
    - "Existing team skills and learning curve assessment"
    - "Community support and documentation quality"
    - "Hiring market availability for specialized skills"
    - "Training and skill development requirements"

  risk_assessment:
    - "Technology maturity and adoption rates"
    - "Vendor lock-in and migration complexity"
    - "Compliance and regulatory considerations"
    - "Long-term sustainability and evolution path"
```

### Phase 3: Component Boundary Definition

**Agent Command**: `*define-boundaries`

**Hexagonal Architecture Implementation**:

```yaml
hexagonal_architecture_design:
  core_business_logic:
    isolation: "Protect business logic from external technology concerns"
    implementation: "Domain model with business rules, technology-independent"

  primary_ports:
    description: "Interfaces for driving the application (inbound)"
    examples: ["REST controllers", "GraphQL resolvers", "Message handlers"]
    design_principles:
      [
        "Business-focused operations",
        "Technology-agnostic",
        "Testable interfaces",
      ]

  secondary_ports:
    description: "Interfaces for driven adapters (outbound)"
    examples:
      ["Database repositories", "External service clients", "Email services"]
    design_principles:
      ["Dependency inversion", "Technology abstraction", "Mockable for testing"]

  adapters:
    primary_adapters: "Concrete implementations of inbound interfaces"
    secondary_adapters: "Concrete implementations of outbound interfaces"
    responsibilities:
      ["Protocol handling", "Data transformation", "External integration"]
```

### Phase 4: Integration Pattern Design

**Agent Command**: `*design-integration`

**Integration Architecture**:

- Synchronous integration patterns (REST APIs, GraphQL)
- Asynchronous integration patterns (Message queues, Event streaming)
- Data integration and consistency strategies
- Error handling and resilience patterns

### Phase 5: Visual Architecture Creation

**Secondary Agent**: architecture-diagram-manager (Archer)
**Command**: `*create-diagrams`

**Diagram Generation Process**:

```yaml
architecture_visualization:
  component_diagrams:
    purpose: "Show system components and relationships"
    generation_triggers: ["Architecture design completion"]
    stakeholders: ["Architects", "Developers", "Technical leads"]

  deployment_diagrams:
    purpose: "Visualize system deployment and infrastructure"
    generation_triggers: ["Infrastructure decisions", "Deployment strategy"]
    stakeholders: ["DevOps", "Architects", "Operations teams"]

  sequence_diagrams:
    purpose: "Show interaction flows and message passing"
    generation_triggers: ["Workflow design", "API documentation"]
    stakeholders: ["Developers", "Integration teams"]

  custom_5d_wave_diagrams:
    wave_flow_diagram: "Visualize 5D-Wave methodology progression"
    agent_collaboration_diagram: "Show agent interactions and patterns"
    architecture_evolution_timeline: "Track architectural changes over time"
```

## Architecture Quality Attribute Design

### Performance Architecture

**Design Strategies**:

- Response time optimization through efficient algorithms and caching
- Scalability design with horizontal and vertical scaling patterns
- Database optimization and query performance
- Resource utilization and capacity planning

### Security Architecture

**Security by Design**:

- Authentication and authorization patterns
- Data protection and encryption strategies
- Security boundary enforcement
- Threat modeling and vulnerability assessment

### Reliability Architecture

**Fault Tolerance Design**:

- Circuit breaker and retry mechanisms
- Graceful degradation and failover strategies
- Health checks and monitoring integration
- Disaster recovery and backup procedures

## Architectural Decision Records (ADR)

### Decision Documentation Framework

```yaml
adr_structure:
  title: "Short noun phrase describing the architectural decision"
  status: "Proposed, Accepted, Deprecated, or Superseded"
  context: "Forces and constraints driving the need for this decision"
  decision: "The architectural decision and its rationale"
  consequences: "Expected outcomes, both positive and negative"

decision_categories:
  structural_decisions: "Component organization and system structure"
  technology_decisions: "Framework, library, and platform selections"
  integration_decisions: "Communication patterns and protocols"
  deployment_decisions: "Infrastructure and operational choices"
```

## Risk Assessment and Mitigation

### Architectural Risk Analysis

**Risk Categories**:

1. **Technical Risks** - Technology selection, performance, security
2. **Integration Risks** - External dependencies, API compatibility
3. **Operational Risks** - Deployment complexity, monitoring gaps
4. **Business Risks** - Time-to-market, cost, stakeholder alignment

**Risk Mitigation Strategies**:

- Risk avoidance through architectural choices
- Risk mitigation through redundancy and fallbacks
- Risk transfer through managed services and SLAs
- Risk acceptance with monitoring and contingency plans

## Output Artifacts

### Primary Architecture Deliverables

1. **ARCHITECTURE_DESIGN.md** - Comprehensive system architecture
2. **TECHNOLOGY_STACK.md** - Complete technology selection with rationale
3. **COMPONENT_BOUNDARIES.md** - Detailed component and service boundaries
4. **INTEGRATION_PATTERNS.md** - Integration architecture and API design
5. **ARCHITECTURAL_DECISIONS.md** - Complete ADR documentation

### Visual Architecture Documentation

1. **COMPONENT_ARCHITECTURE.svg** - System component diagrams
2. **DEPLOYMENT_ARCHITECTURE.svg** - Infrastructure and deployment diagrams
3. **SEQUENCE_DIAGRAMS.svg** - Critical workflow interaction diagrams
4. **INTEGRATION_DIAGRAMS.svg** - External system integration visualization
5. **5D_WAVE_FLOW.svg** - Methodology progression visualization

### Quality Attribute Documentation

1. **PERFORMANCE_ARCHITECTURE.md** - Performance design and benchmarks
2. **SECURITY_ARCHITECTURE.md** - Security design and threat model
3. **RELIABILITY_ARCHITECTURE.md** - Fault tolerance and recovery design
4. **SCALABILITY_DESIGN.md** - Scaling patterns and capacity planning

## Quality Gates

### Architecture Quality Validation

- [ ] **Business Alignment**: Architecture supports all business requirements
- [ ] **Quality Attributes**: Performance, security, reliability requirements addressed
- [ ] **Technology Selection**: Appropriate technology choices with clear rationale
- [ ] **Component Boundaries**: Clear separation of concerns and responsibilities
- [ ] **Integration Design**: Robust integration patterns and error handling

### Visual Architecture Validation

- [ ] **Diagram Completeness**: All critical architectural views documented
- [ ] **Stakeholder Comprehension**: Diagrams accessible to intended audiences
- [ ] **Technical Accuracy**: Diagrams accurately represent design decisions
- [ ] **Evolution Readiness**: Diagrams prepared for implementation tracking

### ATDD Design Foundation

- [ ] **Testability**: Architecture supports comprehensive testing strategies
- [ ] **Hexagonal Boundaries**: Clear ports and adapters for test isolation
- [ ] **Production Service Integration**: Architecture enables real service testing
- [ ] **Quality Gate Support**: Architecture supports validation checkpoints

## Architecture Review and Validation

### Design Review Process

**Participants**: Solution architect, Technical leads, Security specialist, Operations representative
**Focus Areas**:

- Requirement alignment and business capability support
- Quality attribute satisfaction and trade-off analysis
- Technology selection rationale and risk assessment
- Implementation feasibility and team readiness

### Architecture Compliance Framework

**Validation Mechanisms**:

- Architecture testing and compliance monitoring
- Code analysis for boundary adherence
- Integration testing for pattern validation
- Performance testing for quality attribute verification

## Handoff to DISTILL Wave

### Handoff Package Preparation

**Content for acceptance-designer (Quinn)**:

```yaml
architecture_package:
  architecture_design: "ARCHITECTURE_DESIGN.md with component specifications"
  component_boundaries: "COMPONENT_BOUNDARIES.md with interface definitions"
  technology_stack: "TECHNOLOGY_STACK.md with implementation constraints"
  integration_patterns: "INTEGRATION_PATTERNS.md with API contracts"
  quality_attributes: "Quality attribute scenarios and acceptance criteria"
  security_architecture: "SECURITY_ARCHITECTURE.md with access control design"

visual_architecture:
  component_diagrams: "System architecture visualization"
  sequence_diagrams: "Workflow interaction documentation"
  integration_diagrams: "External system integration visualization"
  deployment_diagrams: "Infrastructure and operational architecture"

testing_foundation:
  hexagonal_architecture: "Ports and adapters for test isolation"
  component_interfaces: "Clear boundaries for integration testing"
  quality_scenarios: "Performance, security, reliability test scenarios"
  integration_contracts: "API and service contract specifications"

atdd_preparation:
  testable_architecture: "Architecture designed for comprehensive testing"
  production_service_patterns: "Real service integration capabilities"
  validation_strategies: "Quality attribute testing approaches"
  acceptance_criteria: "Architecture-level acceptance criteria"
```

### Architecture-Informed Test Design

**Test Architecture Guidance**:

- Component boundary testing strategies
- Integration point validation approaches
- Quality attribute testing scenarios
- Production service integration patterns

## Success Criteria

- Comprehensive architecture design addressing all requirements
- Technology stack selected with clear rationale and risk assessment
- Component boundaries defined with hexagonal architecture principles
- Integration patterns designed for reliability and maintainability
- Visual architecture documentation complete and accessible
- Quality attributes addressed with measurable criteria
- Architecture review completed with stakeholder approval
- Clear handoff package prepared for DISTILL wave

## Failure Recovery

If DESIGN wave fails:

1. **Requirements Gaps**: Return to DISCUSS wave for clarification
2. **Technology Risks**: Reassess technology choices and alternatives
3. **Architecture Complexity**: Simplify design while maintaining requirements
4. **Stakeholder Concerns**: Facilitate architecture review and consensus

## Next Command

**Command**: `*dw-distill`
**Agent**: acceptance-designer (Quinn)
**Wave**: DISTILL
