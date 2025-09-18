# /cai:architect - System Design (Wave 2)

```yaml
---
command: "/cai:architect"
category: "Architecture & Design"
purpose: "System architecture design and technology decisions"
argument-hint: "[system-context] --style microservices --focus scalability"
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

## Command Execution Pattern

### Basic Usage
```bash
/cai:architect [system-context]
/cai:architect [system-context] --style <pattern> --focus <quality> --interactive
```

### Key Options
- `--style <pattern>`: microservices, monolithic, serverless, event-driven, layered, hexagonal
- `--focus <quality>`: scalability, performance, security, maintainability, availability, resilience
- `--interactive`: Enable interactive architectural session with stakeholder collaboration
- `--validation`: Enable architectural validation and compliance checking
- `--diagrams`: Generate comprehensive architectural diagrams
- `--technology`: Include detailed technology selection and evaluation
- `--constraints`: Apply specific architectural constraints or requirements

### Activation Instructions
When this command is invoked:
1. Parse system context and architectural requirements
2. Invoke solution-architect agent for comprehensive design
3. Chain to technology-selector for stack evaluation
4. Use architecture-diagram-manager for visual documentation
5. Return complete architectural design with rationale

---

## 📖 Complete Documentation

**For comprehensive documentation, architectural patterns, and detailed usage information:**

```bash
/cai:man architect                # Full manual
/cai:man architect --examples     # Usage examples only
/cai:man architect --flags        # Flags and arguments only
```

**Quick Examples:**
- `/cai:architect "e-commerce platform" --style microservices --focus scalability` - Scalable microservices
- `/cai:architect "payment system" --style hexagonal --focus security --validation` - Secure clean architecture
- `/cai:architect "analytics" --style event-driven --interactive --diagrams` - Reactive system with visuals

**Related Commands:** `/cai:man start`, `/cai:man discuss`, `/cai:man develop`