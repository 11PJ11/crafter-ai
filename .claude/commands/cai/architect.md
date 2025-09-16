# /cai:architect - System Design (Wave 2)

```yaml
---
command: "/cai:architect"
category: "Architecture & Design"
purpose: "System architecture design and technology decisions"
wave-enabled: true
performance-profile: "complex"
---
```

## Overview

Comprehensive system architecture design and technology decision-making for ATDD Wave 2 (ARCHITECT phase).

## Auto-Persona Activation
- **Solution Architect**: System design and architectural patterns (mandatory)
- **Technology Selector**: Technology stack evaluation and selection
- **Architecture Diagram Manager**: Visual architecture documentation
- **Security Expert**: Security architecture (conditional)
- **Performance**: Performance architecture (conditional)

## MCP Server Integration
- **Primary**: Sequential (systematic architectural analysis and decision-making)
- **Secondary**: Context7 (architectural patterns and technology best practices)
- **Tertiary**: Magic (UI architecture for frontend-heavy systems)

## Tool Orchestration
- **Task**: Specialized architecture agents activation
- **Write**: Architecture documentation and decision records
- **Read**: Existing architecture and requirements analysis
- **Edit**: Architecture refinement and updates
- **Bash**: Technology evaluation and proof-of-concept execution

## Agent Flow
```yaml
solution-architect:
  - Creates comprehensive architectural design document
  - Defines system components and their responsibilities
  - Documents integration points and data flows
  - Establishes architectural patterns and constraints

technology-selector:
  - Evaluates technology stack options against requirements
  - Provides trade-off analysis with clear rationale
  - Considers performance, scalability, and maintainability
  - Documents technology decisions and alternatives

architecture-diagram-manager:
  - Creates visual architecture representations
  - Maintains architecture diagrams and documentation
  - Ensures diagrams stay current with design evolution
  - Provides multiple architectural viewpoints
```

## Arguments

### Basic Usage
```bash
/cai:architect [system-context]
```

### Advanced Usage
```bash
/cai:architect [system-context] --style <pattern> --focus <quality> --interactive
```

### System Context
- Natural language description of the system being architected
- Examples: "microservices with event sourcing", "monolithic web application", "serverless data processing pipeline"

### Architectural Styles
- `--style microservices`: Microservices architecture pattern
  - Design distributed systems with loose coupling and independent deployability
  - Emphasizes service boundaries, API contracts, and autonomous team ownership
  - Optimizes for scalability, technology diversity, and independent development cycles
  - Includes container orchestration, service mesh, and distributed data management
- `--style monolithic`: Monolithic architecture pattern
  - Design unified applications with single deployment unit
  - Emphasizes internal modularity, shared databases, and centralized governance
  - Optimizes for development simplicity, transaction consistency, and operational efficiency
  - Suitable for smaller teams, simpler deployment, and well-understood domains
- `--style serverless`: Serverless architecture pattern
  - Design function-based systems with auto-scaling and pay-per-use model
  - Emphasizes event-driven processing, stateless functions, and managed services
  - Optimizes for cost efficiency, automatic scaling, and reduced operational overhead
  - Includes Function-as-a-Service (FaaS) and Backend-as-a-Service (BaaS) components
- `--style event-driven`: Event-driven architecture pattern
  - Design reactive systems based on event production, detection, and consumption
  - Emphasizes loose coupling, asynchronous processing, and temporal decoupling
  - Optimizes for responsiveness, resilience, and system integration capabilities
  - Includes event sourcing, CQRS, and message streaming architectures
- `--style layered`: Layered architecture pattern
  - Design hierarchical systems with clear separation of concerns
  - Emphasizes abstraction levels, dependency direction, and modular organization
  - Optimizes for maintainability, testability, and clear architectural boundaries
  - Common layers: presentation, business logic, data access, infrastructure
- `--style hexagonal`: Hexagonal architecture pattern
  - Design ports and adapters systems with business logic isolation
  - Emphasizes dependency inversion, testability, and technology independence
  - Optimizes for business logic clarity, external system adaptability, and test automation
  - Separates core domain from infrastructure through ports and adapter interfaces

### Quality Attributes Focus
- `--focus performance`: Performance-optimized architecture
  - Prioritize response time, throughput, and resource utilization optimization
  - Design caching strategies, load balancing, and asynchronous processing patterns
  - Include performance budgets, scalability bottleneck analysis, and optimization roadmap
  - Apply performance measurement, monitoring, and continuous optimization practices
- `--focus scalability`: Scalability-focused design
  - Prioritize system capacity growth and load handling capabilities
  - Design horizontal scaling patterns, data partitioning, and distributed processing
  - Include capacity planning, auto-scaling mechanisms, and performance degradation handling
  - Apply load testing, capacity modeling, and scalability validation practices
- `--focus security`: Security-first architecture
  - Prioritize threat modeling, attack surface minimization, and defense-in-depth
  - Design authentication, authorization, data protection, and audit mechanisms
  - Include security controls, vulnerability management, and compliance requirements
  - Apply security testing, penetration testing, and continuous security monitoring
- `--focus maintainability`: Maintainability-focused design
  - Prioritize code clarity, modular design, and change accommodation
  - Design loosely coupled components, clear interfaces, and separation of concerns
  - Include technical debt management, refactoring strategies, and documentation standards
  - Apply code quality metrics, architectural fitness functions, and design reviews
- `--focus reliability`: Reliability and fault-tolerance focus
  - Prioritize system availability, error recovery, and graceful degradation
  - Design redundancy, circuit breakers, bulkhead patterns, and retry mechanisms
  - Include failure mode analysis, disaster recovery, and business continuity planning
  - Apply chaos engineering, fault injection testing, and reliability validation practices
- `--focus cost`: Cost-optimized architecture
  - Prioritize resource efficiency, operational cost management, and ROI optimization
  - Design right-sizing strategies, resource sharing, and cost-effective technology choices
  - Include cost monitoring, budget controls, and economic trade-off analysis
  - Apply cost modeling, usage optimization, and continuous cost management practices

### Design Process Control
- `--interactive`: Enable decision trees with numbered options
  - Provides step-by-step architectural decision guidance with user choice prompts
  - Shows alternative architectural approaches with pros/cons comparison
  - Allows iterative refinement of architectural decisions with stakeholder input
  - Enables collaborative decision-making with real-time feedback and validation
- `--workshop`: Full architectural decision workshop
  - Conducts comprehensive architectural design session with stakeholder collaboration
  - Facilitates requirements analysis, constraint identification, and solution exploration
  - Includes architecture option evaluation, trade-off analysis, and consensus building
  - Generates detailed architectural decision records with rationale and alternatives
- `--evaluation`: Technology evaluation and comparison
  - Performs systematic technology stack assessment against requirements and constraints
  - Analyzes technical fit, team expertise, community support, and long-term viability
  - Includes performance benchmarking, integration analysis, and cost comparison
  - Provides technology recommendation with detailed rationale and migration considerations
- `--validation`: Architecture validation against requirements
  - Validates architectural design completeness and consistency with business requirements
  - Performs architectural fitness function evaluation and constraint compliance checking
  - Includes stakeholder review, technical review, and architectural decision validation
  - Ensures traceability from requirements through architectural decisions to implementation

## Architectural Decision Framework

### Quality Attribute Analysis
```yaml
performance:
  requirements: "Response time, throughput, resource utilization"
  trade-offs: "Performance vs. maintainability, cost vs. speed"
  patterns: "Caching, load balancing, asynchronous processing"

scalability:
  requirements: "User load, data volume, geographic distribution"
  trade-offs: "Scalability vs. consistency, horizontal vs. vertical"
  patterns: "Microservices, event sourcing, CQRS, sharding"

security:
  requirements: "Authentication, authorization, data protection"
  trade-offs: "Security vs. usability, performance vs. protection"
  patterns: "Zero trust, defense in depth, principle of least privilege"

reliability:
  requirements: "Uptime, fault tolerance, recovery time"
  trade-offs: "Reliability vs. complexity, cost vs. redundancy"
  patterns: "Circuit breaker, bulkhead, retry, graceful degradation"
```

### Technology Selection Criteria
```yaml
evaluation_factors:
  technical_fit: "How well does the technology solve the problem?"
  team_expertise: "Does the team have experience with this technology?"
  community_support: "Is there active community and documentation?"
  long_term_viability: "Will this technology be supported long-term?"
  integration: "How well does it integrate with existing systems?"
  performance: "Does it meet performance requirements?"
  cost: "What are the licensing and operational costs?"
  learning_curve: "How quickly can the team become productive?"
```

### Interactive Decision Process
1. **System Context Analysis**: Understanding requirements and constraints
2. **Quality Attribute Prioritization**: Ranking important system qualities
3. **Architectural Style Selection**: Choosing appropriate architectural patterns
4. **Technology Stack Evaluation**: Comparing technology options
5. **Architecture Validation**: Validating design against requirements

## Architecture Documentation Structure

### System Overview
- **System Purpose**: High-level description of system goals
- **Key Quality Attributes**: Performance, scalability, security requirements
- **Architectural Constraints**: Technology, organizational, regulatory constraints
- **Stakeholder Concerns**: Different stakeholder perspectives and priorities

### Component Architecture
- **System Components**: Major system components and their responsibilities
- **Component Interactions**: How components communicate and collaborate
- **Data Flow**: Information flow through the system
- **Integration Points**: External system interactions

### Technology Architecture
- **Technology Stack**: Selected technologies with rationale
- **Deployment Architecture**: How system will be deployed and operated
- **Data Architecture**: Data storage, processing, and management approach
- **Security Architecture**: Security mechanisms and controls

### Decision Records
- **Architectural Decision Records (ADRs)**: Key decisions with context and rationale
- **Trade-off Analysis**: Decisions made and alternatives considered
- **Assumptions**: Assumptions made during architectural design
- **Risks and Mitigation**: Identified risks and mitigation strategies

## Quality Gates

### Architecture Completeness
- **Component Coverage**: All major system components identified and defined
- **Integration Points**: All external integrations documented
- **Quality Requirements**: All quality attributes addressed in design
- **Technology Decisions**: All major technology choices documented with rationale

### Architecture Quality
- **Consistency**: Architecture is internally consistent and coherent
- **Feasibility**: Architecture is technically and organizationally feasible
- **Scalability**: Design can accommodate expected growth and change
- **Traceability**: Architecture addresses all requirements from DISCUSS phase

### Documentation Quality
- **Clarity**: Architecture is clearly documented and understandable
- **Completeness**: All necessary architectural information is captured
- **Visual Representation**: Appropriate diagrams and visual aids included
- **Decision Rationale**: Clear rationale provided for key decisions

## Output Artifacts

### Architecture Documents
- `${DOCS_PATH}/architecture.md`: Comprehensive system architecture specification
- `${DOCS_PATH}/technology-decisions.md`: Technology stack decisions and rationale
- `${DOCS_PATH}/architecture-diagrams.md`: Visual architecture representations
- `${DOCS_PATH}/architectural-decisions/`: ADR repository for key decisions

### Visual Artifacts
- **System Context Diagram**: System boundaries and external interactions
- **Component Diagram**: Major components and their relationships
- **Deployment Diagram**: Infrastructure and deployment architecture
- **Sequence Diagrams**: Key interaction flows and scenarios

## Examples

### Microservices Architecture Design
```bash
/cai:architect "e-commerce platform with microservices" --style microservices --focus scalability
```

### Security-First Architecture
```bash
/cai:architect "financial trading system" --focus security --workshop --interactive
```

### Performance-Optimized Design
```bash
/cai:architect "real-time analytics platform" --focus performance --evaluation
```

### Legacy System Modernization
```bash
/cai:architect "modernize monolithic application" --style hexagonal --validation
```

### Event-Driven Architecture
```bash
/cai:architect "IoT data processing pipeline" --style event-driven --focus reliability --interactive
```

## Comprehensive Usage Examples

### Architectural Style Combinations
```bash
# Microservices with security focus and interactive design
/cai:architect "distributed payment system" --style microservices --focus security --interactive --workshop

# Serverless with cost optimization and technology evaluation
/cai:architect "document processing pipeline" --style serverless --focus cost --evaluation --validation

# Hexagonal architecture with maintainability focus
/cai:architect "legacy system modernization" --style hexagonal --focus maintainability --workshop --validation

# Event-driven with performance and reliability focus
/cai:architect "real-time recommendation engine" --style event-driven --focus performance --focus reliability --evaluation
```

### Quality Attribute Focused Design
```bash
# Performance-first architecture with comprehensive evaluation
/cai:architect "high-frequency trading platform" --focus performance --evaluation --workshop --validation

# Security-first design with interactive decision making
/cai:architect "healthcare data platform" --focus security --focus maintainability --interactive --workshop

# Cost-optimized serverless architecture
/cai:architect "batch processing system" --style serverless --focus cost --focus scalability --evaluation

# Reliability-focused monolithic design
/cai:architect "critical infrastructure monitoring" --style monolithic --focus reliability --focus security --validation
```

### Interactive Design Workflows
```bash
# Full architectural design workshop with stakeholder collaboration
/cai:architect "enterprise integration platform" --workshop --interactive --evaluation --validation

# Technology evaluation with interactive selection
/cai:architect "cloud migration architecture" --evaluation --interactive --focus cost --focus performance

# Validation-focused architecture review
/cai:architect "existing system assessment" --validation --workshop --focus maintainability --focus security
```

### Domain-Specific Architecture Examples
```bash
# Financial services architecture
/cai:architect "trading and settlement system" --style microservices --focus security --focus reliability --workshop --validation

# IoT and real-time systems
/cai:architect "smart city sensor network" --style event-driven --focus scalability --focus performance --evaluation --interactive

# E-commerce platform architecture
/cai:architect "multi-tenant marketplace" --style microservices --focus scalability --focus cost --workshop --evaluation

# Healthcare system architecture
/cai:architect "patient management system" --style layered --focus security --focus maintainability --interactive --validation

# Media and content delivery
/cai:architect "video streaming platform" --style serverless --focus performance --focus scalability --evaluation --workshop
```

### Legacy System Modernization Examples
```bash
# Monolith to microservices transformation
/cai:architect "modernize legacy ERP system" --style hexagonal --focus maintainability --workshop --evaluation --validation

# Database-centric to event-driven transformation
/cai:architect "transform batch processing to streaming" --style event-driven --focus performance --focus reliability --interactive --workshop

# On-premises to cloud architecture
/cai:architect "cloud migration strategy" --style serverless --focus cost --focus scalability --evaluation --validation

# Tightly-coupled to loosely-coupled architecture
/cai:architect "decouple monolithic application" --style microservices --focus maintainability --focus scalability --workshop --interactive
```

### Technology Evaluation Examples
```bash
# Comprehensive technology stack evaluation
/cai:architect "new product architecture" --evaluation --workshop --interactive --focus performance --focus cost

# Container orchestration evaluation
/cai:architect "containerized application platform" --style microservices --evaluation --focus scalability --focus maintainability --validation

# Database architecture evaluation
/cai:architect "data-intensive application" --evaluation --focus performance --focus reliability --workshop --interactive

# Cloud provider evaluation
/cai:architect "multi-cloud deployment strategy" --evaluation --focus cost --focus reliability --workshop --validation
```

### Integration Workflow Examples
```bash
# Architecture-driven development workflow
/cai:start "enterprise application modernization" --methodology atdd --interactive
/cai:architect "modernized system architecture" --style microservices --focus maintainability --workshop --validation

# Requirements-driven architecture workflow
/cai:discuss "system architecture requirements" --focus architecture --interactive
/cai:architect "requirements-based design" --interactive --workshop --evaluation --validation

# Security-focused architecture workflow
/cai:architect "secure system design" --focus security --workshop --validation --interactive
/cai:develop "security-first implementation" --validate --real-system --tdd-mode strict

# Performance-focused architecture workflow
/cai:architect "high-performance system" --focus performance --evaluation --workshop
/cai:develop "performance-optimized implementation" --validate --mutation-testing --coverage 95
```

## Command Execution Pattern

### Activation Instructions
When this command is invoked:
1. Parse system context and architectural requirements
2. Invoke solution-architect agent for architectural design
3. Chain to technology-selector agent for technology decisions
4. Complete with architecture-diagram-manager agent for visual documentation
5. Return comprehensive architectural design document

### Agent Invocation Workflow
```yaml
execution-flow:
  step1-design:
    agent: solution-architect
    task: |
      Create comprehensive system architecture design:
      - System Context: {parsed_system_context}
      - Style: {architectural_style_if_specified}
      - Focus: {focus_area_if_specified}

      Execute architectural design including:
      - System component identification and responsibility definition
      - Integration points and data flow documentation
      - Architectural patterns and constraints establishment
      - Quality attribute requirements and trade-offs

  step2-technology:
    agent: technology-selector
    task: |
      Evaluate and select technology stack:
      - Review architectural design from solution-architect
      - Analyze technology options against requirements and constraints
      - Provide trade-off analysis with clear rationale
      - Document technology decisions and alternatives considered

  step3-documentation:
    agent: architecture-diagram-manager
    task: |
      Create visual architecture documentation:
      - Synthesize architectural design and technology decisions
      - Generate system architecture diagrams and visual representations
      - Update architecture documentation with current state
      - Maintain visual consistency and documentation standards
```

### Arguments Processing
- Parse `[system-context]` argument for architectural scope
- Apply `--style`, `--focus`, `--evaluation` flags to agent tasks
- Process `--workshop`, `--validation` flags for interactive sessions
- Enable `--interactive` mode for stakeholder collaboration

### Output Generation
Return structured architectural design including:
- Comprehensive architectural design document
- Technology selection with rationale
- Visual architecture diagrams and documentation
- Architectural decision records (ADRs) with trade-off analysis