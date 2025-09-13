# AI-Craft System Architecture

## System Overview

AI-Craft implements a sophisticated ATDD (Acceptance Test Driven Development) pipeline through specialized AI agent orchestration with clean context isolation and systematic quality assurance.

### Core Architecture Principles
- **Single Responsibility Principle**: Each agent has one focused responsibility
- **Clean Context Isolation**: Agents receive only essential context for their tasks
- **File-Based Handoffs**: Structured communication between pipeline stages
- **Wave Processing**: Fixed sequence with quality gates at boundaries
- **Systematic Quality**: Progressive validation and refactoring

## Component Architecture

### Agent Network Structure
```
AI-Craft Agent Network (33+ Agents)
├── Requirements Analysis (5) - Blue Family 🟦
├── Architecture Design (3) - Orange Family 🟧
├── Test Design (1) - Bright Red Family ❤️
├── Development (1) - Dark Green Family 🟢
├── Quality Validation (8) - Bright Red Family ❤️
├── Refactoring (2) - Light Blue Family 🔵
├── Coordination (11) - Gray/Brown Family ⚫
└── Configuration (1) - System Configuration ⚙️
```

### Five-Stage ATDD Pipeline
```
DISCUSS → ARCHITECT → DISTILL → DEVELOP → DEMO
   ↓         ↓         ↓         ↓        ↓
Wave 1    Wave 2    Wave 3    Wave 4    Wave 5
Requirements Architecture Test Design Implementation Validation
Analysis    Design    Creation   & Quality    & Completion
```

### Wave Processing Architecture

#### Wave Coordination Principles
1. **Fixed Sequence**: No workflow variations, consistent ATDD progression
2. **Clean Context Isolation**: Each agent starts fresh with role-specific context
3. **File-Based Handoffs**: Agents communicate through structured output files
4. **Specialized Delegation**: Task tool invocation with minimal context
5. **Quality Gates**: Validation checkpoints at each wave boundary

#### Context Isolation Implementation
- **Input Context**: Distilled, role-specific information only
- **Output Files**: Structured deliverables for next wave
- **Context Cleanup**: No cross-contamination between waves
- **Agent Specialization**: Domain-focused expertise

## Service Boundaries and Responsibilities

### Requirements Analysis Domain (Blue Family 🟦)
- **Business Analyst** 🔵💼: Business requirements gathering and stakeholder collaboration
- **Technical Stakeholder** 🔷⚡: Technical feasibility validation and constraint analysis
- **User Experience Designer** 🟦🎨: User journey mapping and UX acceptance criteria (conditional)
- **Security Expert** 🔹🛡️: Security threat modeling and compliance requirements (conditional)
- **Legal Compliance Advisor** 💙⚖️: Regulatory compliance and legal requirement analysis (conditional)

### Architecture Design Domain (Orange Family 🟧)
- **Solution Architect** 🟠🏗️: Collaborative architectural design with user input and ADR creation
- **Technology Selector** 🟧🔧: Technology stack evaluation with trade-off analysis
- **Architecture Diagram Manager** 🔶📐: Visual architecture documentation and evolution tracking

### Test Design Domain (Bright Red Family ❤️)
- **Acceptance Designer** ❤️🧪: Architecture-informed acceptance test scenario creation

### Development Domain (Dark Green Family 🟢)
- **Test-First Developer** 🌿💻: Outside-in TDD implementation with production service integration

### Quality Validation Domain (Bright Red Family ❤️)
- **Test Execution Validator** ❤️✅: Test suite validation and ATDD compliance
- **Mutation Testing Coordinator** 🧬🧬: Test effectiveness enhancement and coverage validation
- **Code Quality Validator** 💖🔍: Static analysis, formatting, and complexity metrics
- **Architecture Compliance Validator** 💕🏛️: Component boundaries and architectural patterns
- **Security Performance Validator** 💗🚀: Security standards and performance benchmarks
- **Production Service Integrator** 💓🔗: Production service integration validation
- **Hexagonal Architecture Enforcer** 💘⬢: Hexagonal architecture boundary validation
- **Commit Readiness Coordinator** 💝🎯: Overall commit orchestration and final validation

### Refactoring Domain (Light Blue Family 🔵)
- **Systematic Refactorer** 💙🔄: Level 1-6 progressive refactoring execution
- **Mikado Refactoring Specialist** 🟦🌳: Complex architectural refactoring using Mikado Method

### Coordination Domain (Gray/Brown Family ⚫)
- **ATDD Cycle Coordinator** ⚫🎭: Five-stage ATDD workflow orchestration
- **ATDD Wave Coordinator** ⚪🌊: Fixed ATDD workflow with wave processing and context isolation
- **ATDD Command Processor** 🔷💻: Command processing with intelligent project analysis
- **Walking Skeleton Helper** 🟤🚶: Minimal end-to-end implementation guide (Alistair Cockburn)
- **Production Readiness Helper** 🤎🚀: Rapid go-live acceleration with quality safeguards
- **Feature Completion Coordinator** 🔘🏁: End-to-end feature completion workflow management
- **Feature Completion Manager** ⚪✔️: Feature completion detection and cleanup
- **Pipeline State Manager** 🔵💾: Pipeline state persistence and resumption logic
- **CI/CD Integration Manager** 🔴⚙️: CI/CD pipeline monitoring and failure recovery
- **Technical Debt Tracker** 🟫📊: Technical debt registry and management
- **Root Cause Analyzer** 🔲🔍: Toyota 5 Whys systematic root cause analysis

## Integration Points

### Command Interface Integration
```
User Command: cai/atdd "feature description"
     ↓
ATDD Command Processor (intelligent project analysis)
     ↓
ATDD Wave Coordinator (workflow orchestration)
     ↓
Specialized Agents (domain-focused execution)
     ↓
File-Based Outputs (structured handoffs)
```

### Claude Code Integration
- **Command Recognition**: Pattern matching for `cai/atdd` commands
- **Agent Delegation**: Automatic delegation to atdd-command-processor
- **Context Management**: Integration with Claude Code's session management
- **Tool Coordination**: Access to Read, Write, Edit, Grep, Glob, Task tools

### Configuration System Integration
```
Constants.md (centralized configuration)
     ↓
All Agents (@constants.md reference)
     ↓
Standardized Paths (${DOCS_PATH}, ${REQUIREMENTS_FILE}, etc.)
     ↓
Easy Maintenance (change once, update everywhere)
```

## Technology Stack

### Core Technologies
- **Agent Framework**: Claude Code with Task tool delegation
- **Configuration Management**: Markdown-based constants with variable substitution
- **File System**: Structured documentation in `docs/craft-ai/`
- **Version Control**: Git integration for commit orchestration
- **Quality Assurance**: Multi-agent validation network

### Communication Protocols
- **Agent-to-Agent**: File-based handoffs with structured formats
- **User-to-System**: Command interface with natural language processing
- **System-to-User**: Progress reporting and validation feedback
- **Context Passing**: Clean isolation with essential information only

### Data Flow Architecture
```
Input (User Command/Project Analysis)
     ↓
Context Distillation (Essential information extraction)
     ↓
Wave Processing (Sequential agent execution)
     ↓
File-Based Handoffs (Structured output files)
     ↓
Quality Gates (Validation checkpoints)
     ↓
Final Output (Completed feature with documentation)
```

## Architecture Decision Records (ADRs)

### ADR-001: Single Responsibility Principle for Agents
- **Decision**: Split complex agents into focused, single-responsibility agents
- **Context**: Original 4 agents had multiple responsibilities causing complexity
- **Consequences**: 33+ agents with clear boundaries, better maintainability
- **Status**: Implemented

### ADR-002: Wave Processing with Clean Context Isolation
- **Decision**: Implement fixed-sequence waves with context isolation
- **Context**: Context pollution between agents caused confusion and inefficiency
- **Consequences**: Cleaner agent execution, better quality, resumable workflows
- **Status**: Implemented

### ADR-003: File-Based Agent Communication
- **Decision**: Use structured files for inter-agent communication
- **Context**: Direct agent-to-agent communication created tight coupling
- **Consequences**: Loose coupling, clear interfaces, auditable communication
- **Status**: Implemented

### ADR-004: Conditional Specialist Agent Activation
- **Decision**: Activate specialist agents based on project requirements
- **Context**: Not all projects need UX, security, or legal expertise
- **Consequences**: Flexible specialization without unnecessary overhead
- **Status**: Implemented

### ADR-005: Centralized Configuration System
- **Decision**: Use constants.md with variable substitution for all path references
- **Context**: Hardcoded paths in 45+ locations made maintenance difficult
- **Consequences**: Easy reconfiguration, consistent paths, maintainable system
- **Status**: Implemented

### ADR-006: Command Interface with Intelligent Analysis
- **Decision**: Implement `cai/atdd` command with automatic project analysis
- **Context**: Manual workflow initiation was error-prone and inefficient
- **Consequences**: Intelligent entry point detection, better user experience
- **Status**: Implemented

## Quality Attribute Scenarios

### Performance
- **Scenario**: User initiates workflow with `cai/atdd` command
- **Response**: System analyzes project and starts appropriate workflow within 5 seconds
- **Architecture Support**: Intelligent project analysis with cached results, parallel agent processing

### Scalability  
- **Scenario**: Multiple concurrent workflows in large projects
- **Response**: System handles up to 10 concurrent workflows with context isolation
- **Architecture Support**: Clean context isolation, file-based handoffs, stateless agents

### Maintainability
- **Scenario**: Developer needs to modify agent behavior
- **Response**: Changes isolated to single agent without affecting others
- **Architecture Support**: Single Responsibility Principle, clear interfaces, modular design

### Reliability
- **Scenario**: Workflow interruption or agent failure
- **Response**: System resumes from last completed wave with full context
- **Architecture Support**: Pipeline state management, file-based persistence, error recovery

### Security
- **Scenario**: Processing sensitive project information
- **Response**: Context isolation prevents information leakage between agents
- **Architecture Support**: Clean context boundaries, specialist security validation

### Usability
- **Scenario**: New user wants to start ATDD workflow
- **Response**: Single command with intelligent analysis guides optimal workflow
- **Architecture Support**: Command interface, project analysis, contextual help

## Implementation Guidelines

### Agent Development
1. **Single Responsibility**: Each agent has one focused purpose
2. **Context Minimalism**: Accept only essential information
3. **Structured Output**: Produce well-formatted files for handoffs
4. **Error Handling**: Provide clear error messages and recovery guidance
5. **Documentation**: Include clear role definition and usage patterns

### Wave Implementation
1. **Clean Context**: Start each wave with fresh, role-specific context
2. **Quality Gates**: Validate completion before next wave
3. **File Handoffs**: Use structured files for communication
4. **Progress Tracking**: Update pipeline state throughout execution
5. **Error Recovery**: Enable resumption from interruption points

### Configuration Management
1. **Constants Usage**: Reference `@constants.md` for all path configurations
2. **Variable Substitution**: Use `${VARIABLE_NAME}` for dynamic references
3. **Consistency**: All agents use standardized file locations and names
4. **Maintenance**: Update constants file for system-wide changes

### Quality Assurance
1. **Progressive Validation**: Implement Level 1-6 refactoring system
2. **Multi-Agent Validation**: Use 8-agent quality network for comprehensive coverage
3. **Evidence Collection**: Gather systematic evidence for all quality claims
4. **Continuous Improvement**: Learn from validation results for system enhancement

### Command Interface
1. **Intelligent Analysis**: Analyze existing project context before workflow initiation
2. **User Guidance**: Provide clear next steps and progress indicators
3. **Error Recovery**: Handle command failures gracefully with helpful suggestions
4. **Integration**: Work seamlessly with Claude Code's existing command system

---

**Architecture Status**: Production Ready ✅

**Last Updated**: 2025-01-13

**Managed By**: Solution Architect 🟠🏗️ with Technology Selector 🟧🔧 and Architecture Diagram Manager 🔶📐

**Input Sources**: Requirements analysis, user collaboration, system evolution feedback

**Output Target**: Test creation, development implementation, quality validation