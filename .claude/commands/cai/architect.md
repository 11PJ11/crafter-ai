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
- `--style monolithic`: Monolithic architecture pattern
- `--style serverless`: Serverless architecture pattern
- `--style event-driven`: Event-driven architecture pattern
- `--style layered`: Layered architecture pattern
- `--style hexagonal`: Hexagonal architecture pattern

### Quality Attributes Focus
- `--focus performance`: Performance-optimized architecture
- `--focus scalability`: Scalability-focused design
- `--focus security`: Security-first architecture
- `--focus maintainability`: Maintainability-focused design
- `--focus reliability`: Reliability and fault-tolerance focus
- `--focus cost`: Cost-optimized architecture

### Design Process Control
- `--interactive`: Enable decision trees with numbered options
- `--workshop`: Full architectural decision workshop
- `--evaluation`: Technology evaluation and comparison
- `--validation`: Architecture validation against requirements

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

ARGUMENTS: create the commands under the @.claude\commands\cai\ folder so we can install them together with the rest