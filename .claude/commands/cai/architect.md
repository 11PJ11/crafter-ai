# /cai:architect - Intelligent System Design (Wave 2)

```yaml
---
command: "/cai:architect"
category: "Architecture & Design"
purpose: "Intelligent system architecture design with modern patterns and stakeholder collaboration"
argument-hint: "[system-context] --style vertical-slice --focus scalability --interactive"
wave-enabled: true
performance-profile: "complex"
---
```

## Overview

Comprehensive intelligent system architecture design and technology decision-making for ATDD Wave 2 (ARCHITECT phase). Features modern architectural patterns, intelligent pattern selection, stakeholder collaboration workflows, and implementation guidance.

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

## Command Execution Pattern

### Basic Usage
```bash
/cai:architect [system-context]
/cai:architect [system-context] --style <pattern> --focus <quality> --interactive
```

### Architectural Patterns
- `--style <pattern>`:
  - **Modern**: `vertical-slice`, `hexagonal`, `event-sourcing`, `reactive`, `cqrs`
  - **Hybrid**: `vsa-hexagonal`, `cqrs-eventsourcing`, `reactive-microservices`
  - **Traditional**: `microservices`, `monolithic`, `serverless`, `event-driven`, `layered`

### Quality Focus Areas
- `--focus <quality>`:
  - **Performance**: `scalability`, `performance`, `throughput`, `low-latency`
  - **Reliability**: `availability`, `resilience`, `fault-tolerance`, `disaster-recovery`
  - **Development**: `maintainability`, `testability`, `team-velocity`, `feature-independence`
  - **Security**: `security`, `compliance`, `data-protection`, `threat-mitigation`

### Collaboration & Analysis
- `--interactive`: Enable stakeholder collaboration with structured interview process
- `--clarify`: Generate clarification questions for requirements gathering
- `--validate`: Enable architectural pattern compliance and validation checking
- `--trade-offs`: Include detailed trade-off analysis with quantitative criteria
- `--migration`: Include migration strategy from current to target architecture

### Documentation & Implementation
- `--diagrams`: Generate comprehensive architectural diagrams with multiple viewpoints
- `--technology`: Include technology selection with pattern-specific recommendations
- `--implementation`: Provide detailed implementation guidance and best practices
- `--constraints`: Apply specific architectural constraints or regulatory requirements
- `--adr`: Generate Architecture Decision Records with rationale documentation

## Intelligent Pattern Selection Framework

### Decision Matrix for Pattern Selection

**Complexity Assessment**:
- **Simple** (Single feature, <3 developers): `layered`, `vertical-slice`
- **Moderate** (Multiple features, 3-10 developers): `hexagonal`, `vsa-hexagonal`, `microservices`
- **Complex** (Enterprise scale, >10 developers): `event-sourcing`, `cqrs-eventsourcing`, `reactive-microservices`

**Quality Attribute Mapping**:
- **Feature Independence + Team Velocity**: `vertical-slice`, `vsa-hexagonal`
- **Testability + Maintainability**: `hexagonal`, `clean-architecture`
- **High Throughput + Scalability**: `event-driven`, `reactive`, `cqrs`
- **Audit + Compliance + Data Integrity**: `event-sourcing`, `cqrs-eventsourcing`
- **Fault Tolerance + Resilience**: `reactive`, `reactive-microservices`

**Team Structure Considerations**:
- **Single Team**: `modular-monolith`, `vertical-slice`
- **Multiple Feature Teams**: `vertical-slice`, `vsa-hexagonal`, `microservices`
- **Platform + Domain Teams**: `hexagonal`, `event-driven`, `reactive-microservices`

### Stakeholder Collaboration Workflow

**Phase 1: Context Discovery**
- Business domain complexity and change frequency
- Team structure, size, and technical expertise
- Existing infrastructure and technology constraints
- Performance, scalability, and availability requirements

**Phase 2: Requirements Clarification**
Generate targeted questions based on initial context:
- "What's the primary business driver: speed of delivery, scalability, or maintainability?"
- "How often do business rules change, and how complex are they?"
- "Are there clear feature boundaries that different teams could own?"
- "What's your expected read/write ratio and consistency requirements?"

**Phase 3: Pattern Recommendation**
- Multi-criteria decision analysis with weighted factors
- Trade-off assessment with quantitative impact analysis
- Risk evaluation for architectural decisions
- Migration complexity from current state

**Phase 4: Implementation Planning**
- Technology stack recommendations aligned with patterns
- Development workflow and team collaboration strategies
- Testing strategies and quality assurance approaches
- Deployment and operational considerations

### Activation Instructions
When this command is invoked:
1. **Context Analysis**: Parse system context, assess complexity, and identify quality attributes
2. **Stakeholder Collaboration**: Execute structured interview process if `--interactive` or `--clarify` enabled
3. **Pattern Selection**: Apply decision framework to recommend optimal architectural patterns
4. **Solution Design**: Invoke solution-architect agent for comprehensive design with selected patterns
5. **Technology Integration**: Chain to technology-selector for pattern-aligned stack evaluation
6. **Documentation**: Use architecture-diagram-manager for visual documentation and ADR generation
7. **Validation**: Apply architectural compliance checking if `--validate` enabled
8. **Implementation Guidance**: Provide detailed implementation roadmap and best practices

## Modern Architectural Patterns Reference

### Vertical Slice Architecture (VSA)
**When to Use**: Feature independence, parallel team development, frequent business rule changes
**Benefits**: High feature cohesion, reduced cross-feature coupling, faster feature delivery
**Implementation**: Organize code by features/use cases rather than technical layers
**Technology Alignment**: Works with any tech stack, particularly effective with CQRS
**Trade-offs**: Potential code duplication vs. faster independent development

### Hexagonal Architecture (Ports & Adapters)
**When to Use**: High testability requirements, external system integration, DDD implementation
**Benefits**: Business logic isolation, easy testing with adapters, technology independence
**Implementation**: Core domain with ports (interfaces) and adapters (implementations)
**Technology Alignment**: Dependency injection containers, interface-based design
**Trade-offs**: Additional abstraction layers vs. improved maintainability and testability

### Event-Driven Architecture (EDA)
**When to Use**: Loose coupling requirements, asynchronous processing, system integration
**Benefits**: System decoupling, scalability, eventual consistency handling
**Implementation**: Event producers, event brokers, event consumers with event stores
**Technology Alignment**: Apache Kafka, RabbitMQ, AWS EventBridge, Azure Event Grid
**Trade-offs**: Eventual consistency complexity vs. system scalability and resilience

### Event Sourcing
**When to Use**: Audit requirements, complex business rules, time-based analysis needs
**Benefits**: Complete audit trail, state reconstruction, temporal queries
**Implementation**: Event store, event handlers, projection builders, snapshot strategies
**Technology Alignment**: EventStore, Apache Kafka, DynamoDB streams, PostgreSQL events
**Trade-offs**: Storage overhead and complexity vs. auditability and flexibility

### CQRS (Command Query Responsibility Segregation)
**When to Use**: Different read/write requirements, complex domain logic, performance optimization
**Benefits**: Optimized read/write models, scalability, clear command/query separation
**Implementation**: Separate command and query models, different data stores, event coordination
**Technology Alignment**: Separate read/write databases, event streaming, caching layers
**Trade-offs**: Model duplication and synchronization vs. optimized performance and clarity

### Reactive Architecture
**When to Use**: High concurrency, fault tolerance, elastic scaling requirements
**Benefits**: Responsive, resilient, elastic, message-driven system characteristics
**Implementation**: Asynchronous message passing, backpressure handling, circuit breakers
**Technology Alignment**: Akka, Spring WebFlux, RxJava, reactive streams implementations
**Trade-offs**: Programming model complexity vs. system resilience and performance

### Hybrid Patterns

**VSA + Hexagonal (vsa-hexagonal)**
- Feature slices with hexagonal boundaries for external integration
- Best for: Teams wanting feature independence with clean external boundaries

**CQRS + Event Sourcing (cqrs-eventsourcing)**
- Commands generate events, queries use optimized projections
- Best for: Complex domains requiring audit trails and performance optimization

**Reactive + Microservices (reactive-microservices)**
- Microservices implementing reactive principles for resilience
- Best for: Distributed systems requiring fault tolerance and elastic scaling

### Clarification Questions Framework

**Business Context Assessment**:
1. "What's the primary business goal: fast time-to-market, operational excellence, or innovation?"
2. "How frequently do business requirements change (daily, weekly, monthly, quarterly)?"
3. "What's the acceptable downtime and data loss tolerance for this system?"
4. "Are there regulatory compliance requirements (GDPR, SOX, HIPAA, PCI-DSS)?"

**Technical Requirements Analysis**:
1. "What's your expected system load: users, transactions/second, data volume?"
2. "What are your consistency requirements: strong consistency or eventual consistency acceptable?"
3. "Do you need real-time processing or is batch processing sufficient?"
4. "What's your disaster recovery requirement: RPO and RTO targets?"

**Team and Organizational Factors**:
1. "How many developers will work on this system simultaneously?"
2. "What's the team's experience with distributed systems and event-driven architectures?"
3. "Do you have separate teams for different features or a single cross-functional team?"
4. "What's your infrastructure automation and DevOps maturity level?"

**Integration and Technology Context**:
1. "How many external systems need integration and what protocols do they use?"
2. "Do you have existing event streaming or message queue infrastructure?"
3. "What are your technology constraints or preferences (cloud provider, languages)?"
4. "What's your budget for infrastructure and operational complexity?"

### Risk Assessment Framework

**Low Risk Patterns** (Simple implementation, proven practices):
- Layered Architecture for simple applications
- Vertical Slice for feature-focused development
- Basic Hexagonal for testability improvement

**Medium Risk Patterns** (Moderate complexity, established patterns):
- Microservices for team scaling
- Event-Driven for system integration
- CQRS for read/write optimization

**High Risk Patterns** (High complexity, specialized expertise required):
- Event Sourcing for audit-critical systems
- Reactive for high-concurrency requirements
- Complex hybrid patterns for enterprise scenarios

---

## 📖 Complete Documentation

**For comprehensive documentation, architectural patterns, and detailed usage information:**

```bash
/cai:man architect                # Full manual
/cai:man architect --examples     # Usage examples only
/cai:man architect --flags        # Flags and arguments only
```

**Quick Examples:**

**Modern Patterns:**
- `/cai:architect "feature-rich app" --style vertical-slice --focus team-velocity --interactive` - Feature-independent development
- `/cai:architect "payment system" --style hexagonal --focus testability --implementation --adr` - Clean testable architecture
- `/cai:architect "audit system" --style event-sourcing --focus compliance --trade-offs` - Event-sourced audit trail
- `/cai:architect "high-traffic api" --style reactive --focus resilience --technology` - Reactive high-performance system

**Hybrid Approaches:**
- `/cai:architect "enterprise platform" --style vsa-hexagonal --focus maintainability --migration` - Feature slices with clean boundaries
- `/cai:architect "analytics platform" --style cqrs-eventsourcing --focus performance --validation` - Optimized read/write with audit
- `/cai:architect "distributed system" --style reactive-microservices --focus fault-tolerance --diagrams` - Resilient microservices

**Stakeholder Collaboration:**
- `/cai:architect "new project" --clarify --interactive --constraints regulatory` - Requirements gathering session
- `/cai:architect "legacy modernization" --migration --trade-offs --implementation` - Modernization strategy

**Related Commands:** `/cai:man start`, `/cai:man discuss`, `/cai:man develop`